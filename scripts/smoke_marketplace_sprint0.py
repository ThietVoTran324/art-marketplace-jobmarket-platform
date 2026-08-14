"""Marketplace Sprint0 smoke — created_at, pin_stats durable views, unique like/follow."""
from __future__ import annotations

import asyncio
import uuid

import httpx
from sqlalchemy import text

from app.celery.tasks import user_view_pin
from app.postgresql.database import async_session_maker

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


def csrf_headers(cookies: httpx.Cookies) -> dict[str, str]:
    token = cookies.get("csrf_token")
    assert token, "missing csrf_token cookie"
    return {"X-CSRF-Token": token}


async def register_and_login(client: httpx.AsyncClient, username: str) -> tuple[int, httpx.Cookies]:
    r = await client.post(
        "/users/register", json={"username": username, "password": PASSWORD}
    )
    assert r.status_code == 201, r.text
    uid = r.json()["id"]
    r = await client.post(
        "/users/login", json={"username": username, "password": PASSWORD}
    )
    assert r.status_code == 200, r.text
    return uid, r.cookies


async def alembic_head() -> str:
    async with async_session_maker() as session:
        row = await session.execute(text("SELECT version_num FROM alembic_version"))
        return row.scalar_one()


async def get_pin_created_at(pin_id: int):
    async with async_session_maker() as session:
        return await session.scalar(
            text("SELECT created_at FROM pins WHERE id = :pid"), {"pid": pin_id}
        )


async def get_view_count(pin_id: int) -> int:
    async with async_session_maker() as session:
        val = await session.scalar(
            text("SELECT view_count FROM pin_stats WHERE pin_id = :pid"),
            {"pid": pin_id},
        )
        return int(val or 0)


async def purge_user_views(user_id: int) -> None:
    async with async_session_maker() as session:
        await session.execute(
            text("DELETE FROM users_view_pins WHERE user_id = :uid"),
            {"uid": user_id},
        )
        await session.commit()


async def main() -> None:
    head = await alembic_head()
    assert head == "c9d0e1f2a3b4", f"expected alembic c9d0e1f2a3b4, got {head}"

    suffix = uuid.uuid4().hex[:8]
    owner_name = f"mp0_owner_{suffix}"
    viewer_name = f"mp0_viewer_{suffix}"

    async with httpx.AsyncClient(base_url=BASE, timeout=60.0) as client:
        owner_id, owner_cookies = await register_and_login(client, owner_name)
        viewer_id, viewer_cookies = await register_and_login(client, viewer_name)
        owner_h = csrf_headers(owner_cookies)
        viewer_h = csrf_headers(viewer_cookies)

        # Create pin (JSON) — seeds pin_stats + created_at
        r = await client.post(
            "/pins/",
            headers=owner_h,
            cookies=owner_cookies,
            json={"title": "mp0 smoke", "description": "s0"},
        )
        assert r.status_code == 201, r.text
        pin = r.json()
        pin_id = pin["id"]
        assert pin.get("created_at"), f"missing created_at in response: {pin}"
        assert await get_pin_created_at(pin_id) is not None

        async with async_session_maker() as session:
            stats_row = await session.scalar(
                text("SELECT view_count FROM pin_stats WHERE pin_id = :pid"),
                {"pid": pin_id},
            )
        assert stats_row is not None, "pin_stats row missing after create"
        assert int(stats_row) == 0

        # Durable view: first view increments; purge users_view_pins keeps count
        before = await get_view_count(pin_id)
        user_view_pin.run(viewer_id, pin_id)
        after_view = await get_view_count(pin_id)
        assert after_view == before + 1, f"view_count {before} -> {after_view}"

        await purge_user_views(viewer_id)
        after_purge = await get_view_count(pin_id)
        assert after_purge == after_view, "pin_stats must survive users_view_pins purge"

        # Duplicate like → 409
        r = await client.post(
            f"/likes/pin/{pin_id}", headers=viewer_h, cookies=viewer_cookies
        )
        assert r.status_code == 201, r.text
        r = await client.post(
            f"/likes/pin/{pin_id}", headers=viewer_h, cookies=viewer_cookies
        )
        assert r.status_code == 409, r.text
        assert r.json()["detail"] == "already_liked"

        # Duplicate follow → 409
        r = await client.post(
            f"/subscription/{owner_id}", headers=viewer_h, cookies=viewer_cookies
        )
        assert r.status_code == 201, r.text
        r = await client.post(
            f"/subscription/{owner_id}", headers=viewer_h, cookies=viewer_cookies
        )
        assert r.status_code == 409, r.text
        assert r.json()["detail"] == "already_following"

    print("ALL_SMOKE_PASS")
    print(f"alembic_head={head} pin_id={pin_id}")


if __name__ == "__main__":
    asyncio.run(main())
