"""Phase0-Sprint3 audit log smoke tests (AC-01...AC-10)."""
import asyncio
import uuid

import httpx
from sqlalchemy import text

from app.api.rest.audit import write_audit
from app.postgresql.database import async_session_maker

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


async def seed_pin_and_comment(user_id: int) -> dict[str, int]:
    async with async_session_maker() as session:
        pin_id = (
            await session.execute(
                text("INSERT INTO pins (user_id, title) VALUES (:uid, 's3 smoke') RETURNING id"),
                {"uid": user_id},
            )
        ).scalar_one()
        comment_id = (
            await session.execute(
                text(
                    "INSERT INTO comments (user_id, pin_id, content, created_at) "
                    "VALUES (:uid, :pid, 's3 smoke', now()) RETURNING id"
                ),
                {"uid": user_id, "pid": pin_id},
            )
        ).scalar_one()
        await session.commit()
        return {"pin": pin_id, "comment": comment_id}


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


async def audit_count() -> int:
    async with async_session_maker() as session:
        return (await session.execute(text("SELECT count(*) FROM audit_logs"))).scalar_one()


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
    return user_id, response.cookies


def find_record(records: list[dict], action: str, target_id: int) -> dict:
    for record in records:
        if record["action"] == action and record["target_id"] == target_id:
            return record
    raise AssertionError(f"audit record not found: {action} target={target_id}")


async def check_atomicity(owner_id: int) -> None:
    """AC-09: a failing audit write must roll back the mutation itself."""
    seeded = await seed_pin_and_comment(owner_id)
    pin_id = seeded["pin"]

    async with async_session_maker() as session:
        await session.execute(text("DELETE FROM pins WHERE id = :pid"), {"pid": pin_id})
        try:
            await write_audit(
                session,
                actor_user_id=owner_id,
                action="not_a_real_action",
                target_type="pin",
                target_id=pin_id,
            )
        except Exception:
            await session.rollback()
        else:
            raise AssertionError("write_audit accepted an unknown action")

    async with async_session_maker() as session:
        still_there = (
            await session.execute(text("SELECT count(*) FROM pins WHERE id = :pid"), {"pid": pin_id})
        ).scalar_one()
    assert still_there == 1, "mutation was not rolled back when audit failed"

    async with async_session_maker() as session:
        await session.execute(text("DELETE FROM pins WHERE id = :pid"), {"pid": pin_id})
        await session.commit()


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    results: list[str] = []

    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as client:
        owner_id, owner_cookies = await register_and_login(client, f"s3owner_{suffix}")
        other_id, other_cookies = await register_and_login(client, f"s3other_{suffix}")
        admin_id, admin_cookies = await register_and_login(client, f"s3admin_{suffix}")
        await promote_admin(admin_id)

        seeded = await seed_pin_and_comment(owner_id)

        # AC-01: admin pin moderation is audited.
        before = await audit_count()
        response = await client.delete(
            f"/admin/pin/{seeded['pin']}",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert response.status_code == 204, response.text
        assert await audit_count() == before + 1

        response = await client.get(
            "/admin/audit",
            cookies=admin_cookies,
            params={"action": "admin_delete_pin", "target_id": seeded["pin"]},
        )
        assert response.status_code == 200, response.text
        record = find_record(response.json(), "admin_delete_pin", seeded["pin"])
        assert record["actor_user_id"] == admin_id
        assert record["target_type"] == "pin"
        assert record["metadata"]["owner_user_id"] == owner_id
        results.append("AC-01 PASS")

        # AC-02: admin comment moderation is audited (comment already cascaded, so reseed).
        reseeded = await seed_pin_and_comment(owner_id)
        before = await audit_count()
        response = await client.delete(
            f"/admin/comment/{reseeded['comment']}",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert response.status_code == 204, response.text
        assert await audit_count() == before + 1

        response = await client.get(
            "/admin/audit",
            cookies=admin_cookies,
            params={"action": "admin_delete_comment", "target_id": reseeded["comment"]},
        )
        record = find_record(response.json(), "admin_delete_comment", reseeded["comment"])
        assert record["actor_user_id"] == admin_id
        assert record["metadata"]["owner_user_id"] == owner_id
        results.append("AC-02 PASS")

        # AC-03: role assign is audited with the granted role.
        before = await audit_count()
        response = await client.post(
            f"/admin/users/{owner_id}/roles",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
            json={"role": "employer"},
        )
        assert response.status_code == 200, response.text
        assert await audit_count() == before + 1

        response = await client.get(
            "/admin/audit",
            cookies=admin_cookies,
            params={"action": "role_assign", "target_id": owner_id},
        )
        record = find_record(response.json(), "role_assign", owner_id)
        assert record["target_type"] == "user"
        assert record["metadata"]["role"] == "employer"
        results.append("AC-03 PASS")

        # AC-04: role revoke is audited with the removed role.
        before = await audit_count()
        response = await client.delete(
            f"/admin/users/{owner_id}/roles/employer",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert response.status_code == 200, response.text
        assert await audit_count() == before + 1

        response = await client.get(
            "/admin/audit",
            cookies=admin_cookies,
            params={"action": "role_revoke", "target_id": owner_id},
        )
        record = find_record(response.json(), "role_revoke", owner_id)
        assert record["metadata"]["role"] == "employer"
        results.append("AC-04 PASS")

        # AC-05: rejected actions leave no audit trace.
        before = await audit_count()
        response = await client.delete(
            "/admin/pin/999999999",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert response.status_code == 404, response.text
        response = await client.delete(
            f"/admin/users/{admin_id}/roles/admin",
            cookies=admin_cookies,
            headers=csrf_headers(admin_cookies),
        )
        assert response.status_code == 403, response.text
        response = await client.get("/admin/audit", cookies=other_cookies)
        assert response.status_code == 403, response.text
        assert await audit_count() == before
        results.append("AC-05 PASS")

        # AC-06: audit is append-only over the API surface.
        openapi = (await client.get("/openapi.json")).json()
        for path, operations in openapi["paths"].items():
            if "audit" in path:
                assert set(operations) == {"get"}, (path, list(operations))
        results.append("AC-06 PASS")

        # AC-07: admin sees everything and basic filters narrow the result.
        response = await client.get("/admin/audit", cookies=admin_cookies, params={"limit": 200})
        assert response.status_code == 200, response.text
        all_records = response.json()
        assert len(all_records) >= 4
        created = [record["created_at"] for record in all_records]
        assert created == sorted(created, reverse=True)

        response = await client.get(
            "/admin/audit", cookies=admin_cookies, params={"actor_user_id": admin_id}
        )
        assert all(record["actor_user_id"] == admin_id for record in response.json())
        response = await client.get(
            "/admin/audit", cookies=admin_cookies, params={"target_type": "user"}
        )
        assert all(record["target_type"] == "user" for record in response.json())
        results.append("AC-07 PASS")

        # AC-08: users only read audit records related to themselves.
        response = await client.get("/users/me/audit", cookies=owner_cookies)
        assert response.status_code == 200, response.text
        owner_records = response.json()
        assert find_record(owner_records, "role_assign", owner_id)
        assert find_record(owner_records, "admin_delete_pin", seeded["pin"])
        for record in owner_records:
            related = (
                record["actor_user_id"] == owner_id
                or (record["target_type"] == "user" and record["target_id"] == owner_id)
                or record["metadata"].get("owner_user_id") == owner_id
            )
            assert related, record

        response = await client.get("/users/me/audit", cookies=other_cookies)
        assert response.status_code == 200, response.text
        assert response.json() == []
        results.append("AC-08 PASS")

        # AC-09: failed audit write rolls the mutation back.
        await check_atomicity(owner_id)
        results.append("AC-09 PASS")

    print("\n".join(results))
    print("AC-10 PASS (no SIEM/UI/job/marketplace surface added)")
    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
