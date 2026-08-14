"""Admin_Sprint3 smoke — resolve→unlist, dismiss no-unlist, rate-limit."""
import asyncio
import uuid
from datetime import datetime, timezone

import httpx
from sqlalchemy import text

from app.config import settings
from app.postgresql.database import async_session_maker

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


def csrf_headers(cookies: httpx.Cookies) -> dict[str, str]:
    token = cookies.get("csrf_token")
    assert token, "missing csrf_token"
    return {"X-CSRF-Token": token}


async def register_login(client: httpx.AsyncClient, username: str) -> tuple[int, httpx.Cookies]:
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


async def seed_pin(user_id: int) -> int:
    async with async_session_maker() as session:
        pin_id = (
            await session.execute(
                text(
                    "INSERT INTO pins (user_id, title) VALUES (:uid, 'admin s3') "
                    "RETURNING id"
                ),
                {"uid": user_id},
            )
        ).scalar_one()
        await session.commit()
        return pin_id


async def seed_listing(pin_id: int, seller_id: int) -> int:
    async with async_session_maker() as session:
        listing_id = (
            await session.execute(
                text(
                    "INSERT INTO pin_listings "
                    "(pin_id, seller_user_id, license_type, price_minor, currency, status, "
                    "attestation_accepted, attestation_version, attested_at) "
                    "VALUES (:pid, :sid, 'personal_use', 100, 'USD', 'listed', "
                    "true, 'seller-rights-v1', now()) "
                    "RETURNING id"
                ),
                {"pid": pin_id, "sid": seller_id},
            )
        ).scalar_one()
        await session.commit()
        return listing_id


async def listing_status(pin_id: int) -> str | None:
    async with async_session_maker() as session:
        return (
            await session.execute(
                text("SELECT status FROM pin_listings WHERE pin_id = :pid"),
                {"pid": pin_id},
            )
        ).scalar_one_or_none()


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    async with httpx.AsyncClient(base_url=BASE, timeout=60.0) as client:
        admin_id, _ = await register_login(client, f"ad3a_{suffix}")
        await promote_admin(admin_id)
        login = await client.post(
            "/users/login",
            json={"username": f"ad3a_{suffix}", "password": PASSWORD},
        )
        admin_c = login.cookies
        ah = csrf_headers(admin_c)

        seller_id, _ = await register_login(client, f"ad3s_{suffix}")
        reporter_id, reporter_c = await register_login(client, f"ad3r_{suffix}")
        rh = csrf_headers(reporter_c)

        # Resolve → unlist
        pin_resolve = await seed_pin(seller_id)
        await seed_listing(pin_resolve, seller_id)
        rep = await client.post(
            f"/marketplace/pins/{pin_resolve}/copyright-reports",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "stolen artwork claim"},
        )
        assert rep.status_code == 201, rep.text
        report_id = rep.json()["id"]

        open_list = await client.get(
            "/admin/copyright-reports",
            params={"status": "open"},
            cookies=admin_c,
        )
        assert open_list.status_code == 200, open_list.text
        assert any(r["id"] == report_id for r in open_list.json())

        resolved = await client.patch(
            f"/admin/copyright-reports/{report_id}",
            cookies=admin_c,
            headers=ah,
            json={"status": "resolved", "admin_note": "confirmed"},
        )
        assert resolved.status_code == 200, resolved.text
        assert resolved.json()["status"] == "resolved"
        assert await listing_status(pin_resolve) == "unlisted"
        print("PASS resolve unlists listing")

        # Dismiss does not unlist
        pin_dismiss = await seed_pin(seller_id)
        await seed_listing(pin_dismiss, seller_id)
        rep_d = await client.post(
            f"/marketplace/pins/{pin_dismiss}/copyright-reports",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "false alarm report"},
        )
        assert rep_d.status_code == 201, rep_d.text
        dismissed = await client.patch(
            f"/admin/copyright-reports/{rep_d.json()['id']}",
            cookies=admin_c,
            headers=ah,
            json={"status": "dismissed"},
        )
        assert dismissed.status_code == 200, dismissed.text
        assert await listing_status(pin_dismiss) == "listed"
        print("PASS dismiss keeps listing")

        # Resolve without listing — OK
        pin_bare = await seed_pin(seller_id)
        rep_b = await client.post(
            f"/marketplace/pins/{pin_bare}/copyright-reports",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "no listing still ok"},
        )
        assert rep_b.status_code == 201, rep_b.text
        bare = await client.patch(
            f"/admin/copyright-reports/{rep_b.json()['id']}",
            cookies=admin_c,
            headers=ah,
            json={"status": "resolved"},
        )
        assert bare.status_code == 200, bare.text
        print("PASS resolve without listing")

        # Rate limit
        max_n = max(1, int(settings.MP_COPYRIGHT_REPORT_MAX))
        # already used 3 reports above from same reporter — create until limit
        used = 3
        while used < max_n:
            pid = await seed_pin(seller_id)
            r = await client.post(
                f"/marketplace/pins/{pid}/copyright-reports",
                cookies=reporter_c,
                headers=rh,
                json={"reason": f"rate fill {used} {datetime.now(timezone.utc)}"},
            )
            assert r.status_code == 201, r.text
            used += 1
        pid_over = await seed_pin(seller_id)
        over = await client.post(
            f"/marketplace/pins/{pid_over}/copyright-reports",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "should be rate limited now"},
        )
        assert over.status_code == 429, over.text
        assert over.json()["detail"] == "copyright_report_rate_limited"
        print("PASS rate-limit", max_n)

        forbidden = await client.get("/admin/copyright-reports", cookies=reporter_c)
        assert forbidden.status_code == 403, forbidden.text
        print("PASS non-admin 403")

    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
