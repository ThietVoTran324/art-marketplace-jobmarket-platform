"""Phase0-Sprint1 smoke prove-done. Run inside fastapi container."""
import asyncio
import uuid

import httpx
from sqlalchemy import text

from app.postgresql.database import async_session_maker

BASE = "http://127.0.0.1:8000"
suffix = uuid.uuid4().hex[:8]
admin_user = f"admin_{suffix}"
normal_user = f"user_{suffix}"
password = "TestPass123!"


def jar_from(resp: httpx.Response) -> httpx.Cookies:
    return resp.cookies


def csrf_headers(cookies: httpx.Cookies) -> dict[str, str]:
    token = cookies.get("csrf_token")
    assert token
    return {"X-CSRF-Token": token}


async def promote_admin(username: str) -> None:
    async with async_session_maker() as s:
        await s.execute(
            text(
                "INSERT INTO user_roles (user_id, role) "
                "SELECT id, 'admin' FROM users WHERE username = :u "
                "ON CONFLICT DO NOTHING"
            ),
            {"u": username},
        )
        await s.commit()


async def get_pin_id(username: str) -> int | None:
    async with async_session_maker() as s:
        row = await s.execute(
            text(
                "SELECT p.id FROM pins p JOIN users u ON u.id = p.user_id "
                "WHERE u.username = :u ORDER BY p.id DESC LIMIT 1"
            ),
            {"u": username},
        )
        r = row.first()
        return r[0] if r else None


async def create_pin_for(user_id: int) -> int:
    async with async_session_maker() as s:
        row = await s.execute(
            text(
                "INSERT INTO pins (user_id, title, description) "
                "VALUES (:uid, 'smoke', 'smoke') RETURNING id"
            ),
            {"uid": user_id},
        )
        pin_id = row.scalar_one()
        await s.commit()
        return pin_id


async def user_id_of(username: str) -> int:
    async with async_session_maker() as s:
        return await s.scalar(text("SELECT id FROM users WHERE username = :u"), {"u": username})


async def main() -> None:
    results = []
    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as client:
        # AC-01 register -> artist
        r = await client.post(
            "/users/register",
            json={"username": normal_user, "password": password},
        )
        assert r.status_code == 201, r.text
        normal_id = r.json()["id"]

        r = await client.post(
            "/users/register",
            json={"username": admin_user, "password": password},
        )
        assert r.status_code == 201, r.text
        admin_id = r.json()["id"]
        await promote_admin(admin_user)

        # login both
        r_admin = await client.post(
            "/users/login", json={"username": admin_user, "password": password}
        )
        assert r_admin.status_code == 200, r_admin.text
        admin_cookies = r_admin.cookies

        r_user = await client.post(
            "/users/login", json={"username": normal_user, "password": password}
        )
        assert r_user.status_code == 200, r_user.text
        user_cookies = r_user.cookies

        r = await client.get("/users/me/roles", cookies=user_cookies)
        assert r.status_code == 200, r.text
        assert r.json()["roles"] == ["artist"], r.json()
        results.append("AC-01 PASS")

        r = await client.get("/users/me/roles", cookies=admin_cookies)
        assert sorted(r.json()["roles"]) == ["admin", "artist"], r.json()
        results.append("AC-03-like PASS (admin+artist)")

        # create pins for ownership/moderation
        pin_normal = await create_pin_for(normal_id)
        pin_victim = await create_pin_for(admin_id)

        # AC-04 non-admin delete any -> 403
        r = await client.delete(
            f"/admin/pin/{pin_victim}",
            cookies=user_cookies,
            headers=csrf_headers(user_cookies),
        )
        assert r.status_code == 403, r.text
        results.append("AC-04 PASS")

        # AC-05 admin delete any -> 204
        r = await client.delete(
            f"/admin/pin/{pin_victim}",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert r.status_code == 204, r.text
        results.append("AC-05 PASS")

        # AC-06 owner deletes own pin via user route
        r = await client.delete(
            f"/pins/{pin_normal}",
            cookies=user_cookies,
            headers=csrf_headers(user_cookies),
        )
        assert r.status_code == 204, r.text
        results.append("AC-06 PASS")

        # AC-07 assign employer
        r = await client.post(
            f"/admin/users/{normal_id}/roles",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
            json={"role": "employer"},
        )
        assert r.status_code == 200, r.text
        assert "employer" in r.json()["roles"], r.json()
        results.append("AC-07 PASS")

        # AC-08 self-modify blocked
        r = await client.post(
            f"/admin/users/{admin_id}/roles",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
            json={"role": "seller"},
        )
        assert r.status_code == 403, r.text
        results.append("AC-08 PASS")

        # AC-09 seller assignable
        r = await client.post(
            f"/admin/users/{normal_id}/roles",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
            json={"role": "seller"},
        )
        assert r.status_code == 200, r.text
        assert "seller" in r.json()["roles"], r.json()
        results.append("AC-09 PASS")

        # AC-10 re-login
        r = await client.post(
            "/users/login", json={"username": normal_user, "password": password}
        )
        assert r.status_code == 200, r.text
        results.append("AC-10 PASS")

        # revoke role
        r = await client.delete(
            f"/admin/users/{normal_id}/roles/employer",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert r.status_code == 200, r.text
        assert "employer" not in r.json()["roles"], r.json()
        results.append("REVOKE PASS")

    # AC-02 backfill: existing users have artist
    async with async_session_maker() as s:
        missing = await s.scalar(
            text(
                "SELECT COUNT(*) FROM users u "
                "WHERE NOT EXISTS ("
                "  SELECT 1 FROM user_roles r WHERE r.user_id=u.id AND r.role='artist'"
                ")"
            )
        )
        assert missing == 0, missing
        results.append("AC-02 PASS")

    print("\n".join(results))
    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
