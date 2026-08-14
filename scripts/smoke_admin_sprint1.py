"""Admin_Sprint1 smoke — overview, roles, audit, content delete."""
import asyncio
import uuid

import httpx
from sqlalchemy import text

from app.postgresql.database import async_session_maker

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


def csrf_headers(cookies: httpx.Cookies) -> dict[str, str]:
    token = cookies.get("csrf_token")
    assert token, "missing csrf_token cookie"
    return {"X-CSRF-Token": token}


async def promote_admin(user_id: int) -> None:
    async with async_session_maker() as session:
        await session.execute(
            text(
                "INSERT INTO user_roles (user_id, role) VALUES (:uid, 'admin') "
                "ON CONFLICT DO NOTHING"
            ),
            {"uid": user_id},
        )
        await session.commit()


async def seed_pin_and_comment(user_id: int) -> dict[str, int]:
    async with async_session_maker() as session:
        pin_id = (
            await session.execute(
                text(
                    "INSERT INTO pins (user_id, title) VALUES (:uid, 'admin s1 smoke') "
                    "RETURNING id"
                ),
                {"uid": user_id},
            )
        ).scalar_one()
        comment_id = (
            await session.execute(
                text(
                    "INSERT INTO comments (user_id, pin_id, content, created_at) "
                    "VALUES (:uid, :pid, 'admin s1', now()) RETURNING id"
                ),
                {"uid": user_id, "pid": pin_id},
            )
        ).scalar_one()
        await session.commit()
        return {"pin": pin_id, "comment": comment_id}


async def register_and_login(
    client: httpx.AsyncClient, username: str
) -> tuple[int, httpx.Cookies]:
    response = await client.post(
        "/users/register", json={"username": username, "password": PASSWORD}
    )
    assert response.status_code == 201, response.text
    user_id = response.json()["id"]
    response = await client.post(
        "/users/login", json={"username": username, "password": PASSWORD}
    )
    assert response.status_code == 200, response.text
    return user_id, response.cookies


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as client:
        admin_id, _ = await register_and_login(client, f"adm_s1_a_{suffix}")
        target_id, _ = await register_and_login(client, f"adm_s1_t_{suffix}")
        owner_id, _ = await register_and_login(client, f"adm_s1_o_{suffix}")
        await promote_admin(admin_id)

        login = await client.post(
            "/users/login",
            json={"username": f"adm_s1_a_{suffix}", "password": PASSWORD},
        )
        assert login.status_code == 200, login.text
        admin_cookies = login.cookies

        target_login = await client.post(
            "/users/login",
            json={"username": f"adm_s1_t_{suffix}", "password": PASSWORD},
        )
        target_cookies = target_login.cookies
        forbidden = await client.get("/admin/overview", cookies=target_cookies)
        assert forbidden.status_code == 403, forbidden.text
        print("PASS non-admin overview 403")

        overview = await client.get("/admin/overview", cookies=admin_cookies)
        assert overview.status_code == 200, overview.text
        body = overview.json()
        for key in (
            "audit_events_24h",
            "open_copyright_reports",
            "open_job_reports",
            "open_kyc_requests",
        ):
            assert key in body and isinstance(body[key], int), body
        print("PASS overview", body)

        assign = await client.post(
            f"/admin/users/{target_id}/roles",
            json={"role": "seller"},
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert assign.status_code == 200, assign.text
        assert "seller" in assign.json()["roles"]
        print("PASS assign seller")

        self_assign = await client.post(
            f"/admin/users/{admin_id}/roles",
            json={"role": "seller"},
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert self_assign.status_code == 403, self_assign.text
        print("PASS self-assign blocked")

        revoke = await client.delete(
            f"/admin/users/{target_id}/roles/seller",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert revoke.status_code == 200, revoke.text
        assert "seller" not in revoke.json()["roles"]
        print("PASS revoke seller")

        audit = await client.get(
            "/admin/audit",
            params={"action": "role_assign", "limit": 20},
            cookies=admin_cookies,
        )
        assert audit.status_code == 200, audit.text
        assert any(
            r.get("action") == "role_assign" and r.get("target_id") == target_id
            for r in audit.json()
        )
        print("PASS audit filter role_assign")

        seeded = await seed_pin_and_comment(owner_id)
        pin_del = await client.delete(
            f"/admin/pin/{seeded['pin']}",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert pin_del.status_code == 204, pin_del.text
        print("PASS delete pin")

        seeded2 = await seed_pin_and_comment(owner_id)
        c_del = await client.delete(
            f"/admin/comment/{seeded2['comment']}",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert c_del.status_code == 204, c_del.text
        print("PASS delete comment")

    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
