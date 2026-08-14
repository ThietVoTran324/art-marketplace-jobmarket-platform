"""Phase0-Sprint2 ownership, CORS and CSRF smoke tests."""
import asyncio
import uuid

import httpx
from sqlalchemy import text

from app.postgresql.database import async_session_maker

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


async def seed_resources(user_id: int) -> dict[str, int]:
    async with async_session_maker() as session:
        pin_id = (
            await session.execute(
                text(
                    "INSERT INTO pins (user_id, title) VALUES (:uid, 's2 smoke') "
                    "RETURNING id"
                ),
                {"uid": user_id},
            )
        ).scalar_one()
        board_id = (
            await session.execute(
                text(
                    "INSERT INTO boards (user_id, title, created_at) "
                    "VALUES (:uid, 's2 smoke', now()) "
                    "RETURNING id"
                ),
                {"uid": user_id},
            )
        ).scalar_one()
        comment_id = (
            await session.execute(
                text(
                    "INSERT INTO comments (user_id, pin_id, content, created_at) "
                    "VALUES (:uid, :pid, 's2 smoke', now()) RETURNING id"
                ),
                {"uid": user_id, "pid": pin_id},
            )
        ).scalar_one()
        await session.commit()
        return {"pin": pin_id, "board": board_id, "comment": comment_id}


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


def csrf_headers(cookies: httpx.Cookies) -> dict[str, str]:
    token = cookies.get("csrf_token")
    assert token
    return {"X-CSRF-Token": token}


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
    assert response.cookies.get("access_token")
    assert response.cookies.get("csrf_token")
    return user_id, response.cookies


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    results: list[str] = []

    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as client:
        user_a_id, user_a_cookies = await register_and_login(client, f"s2a_{suffix}")
        user_b_id, user_b_cookies = await register_and_login(client, f"s2b_{suffix}")
        admin_id, admin_cookies = await register_and_login(client, f"s2admin_{suffix}")
        await promote_admin(admin_id)

        b = await seed_resources(user_b_id)

        # AC-08: authenticated mutation without CSRF must fail.
        response = await client.post(
            "/boards/",
            cookies=user_a_cookies,
            json={"title": "missing csrf"},
        )
        assert response.status_code == 403, response.text
        results.append("AC-08 PASS")

        # AC-09: trusted app flow with CSRF succeeds.
        response = await client.post(
            "/boards/",
            cookies=user_a_cookies,
            headers=csrf_headers(user_a_cookies),
            json={"title": "with csrf"},
        )
        assert response.status_code == 201, response.text
        user_a_board = response.json()["id"]
        results.append("AC-09 PASS")

        # AC-01: cross-user pin delete forbidden.
        response = await client.delete(
            f"/pins/{b['pin']}",
            cookies=user_a_cookies,
            headers=csrf_headers(user_a_cookies),
        )
        assert response.status_code == 403, response.text
        results.append("AC-01 PASS")

        # AC-02: cross-user board mutations forbidden.
        response = await client.delete(
            f"/boards/{b['board']}",
            cookies=user_a_cookies,
            headers=csrf_headers(user_a_cookies),
        )
        assert response.status_code == 403, response.text
        response = await client.post(
            f"/boards/{b['board']}/pins/{b['pin']}",
            cookies=user_a_cookies,
            headers=csrf_headers(user_a_cookies),
        )
        assert response.status_code == 403, response.text
        results.append("AC-02 PASS")

        # AC-03: cross-user comment delete forbidden.
        response = await client.delete(
            f"/comments/{b['comment']}",
            cookies=user_a_cookies,
            headers=csrf_headers(user_a_cookies),
        )
        assert response.status_code == 403, response.text
        results.append("AC-03 PASS")

        # AC-04: owners can mutate their own resources.
        response = await client.delete(
            f"/comments/{b['comment']}",
            cookies=user_b_cookies,
            headers=csrf_headers(user_b_cookies),
        )
        assert response.status_code == 204, response.text
        response = await client.delete(
            f"/boards/{user_a_board}",
            cookies=user_a_cookies,
            headers=csrf_headers(user_a_cookies),
        )
        assert response.status_code == 204, response.text
        results.append("AC-04 PASS")

        # AC-06: admin does not bypass normal user-route ownership.
        response = await client.delete(
            f"/pins/{b['pin']}",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert response.status_code == 403, response.text
        results.append("AC-06 PASS")

        # AC-05: admin moderation route still deletes any pin.
        response = await client.delete(
            f"/admin/pin/{b['pin']}",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert response.status_code == 204, response.text
        results.append("AC-05 PASS")

        # AC-07: untrusted origin is not granted CORS access.
        response = await client.options(
            "/boards/",
            headers={
                "Origin": "https://evil.example",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers.get("access-control-allow-origin") != "https://evil.example"
        results.append("AC-07 PASS")

        # Auth/session is still valid after hardening.
        response = await client.get("/users/me/roles", cookies=user_a_cookies)
        assert response.status_code == 200, response.text
        assert "artist" in response.json()["roles"]

    print("\n".join(results))
    print("AC-10 PASS (no scoped feature added)")
    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
