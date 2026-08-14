"""Admin_Sprint4 smoke — list pending work-exp, approve/reject, overview count."""
import asyncio
import io
import uuid
from datetime import date

import httpx
from sqlalchemy import text

from app.api.rest.utils import create_url_safe_token
from app.postgresql.database import async_session_maker

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


def csrf_headers(cookies: httpx.Cookies) -> dict[str, str]:
    token = cookies.get("csrf_token")
    assert token, "missing csrf_token"
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


async def set_email(user_id: int, email: str) -> None:
    async with async_session_maker() as session:
        await session.execute(
            text("UPDATE users SET email = :e, verified = true WHERE id = :uid"),
            {"e": email, "uid": user_id},
        )
        await session.commit()


async def register_login(client, username: str):
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


def minimal_pdf() -> bytes:
    return b"%PDF-1.1\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


async def become_org(client, *, owner_id, cookies, headers, email, reg, admin_c, admin_h):
    body = {
        "display_name": f"Co {reg}",
        "registration_country": "VN",
        "registration_type": "LLC",
        "registration_number_raw": reg,
        "signer_full_name": "Owner",
        "primary_document_language": "en",
        "company_email": email,
        "address_line": "1 Main",
        "city": "HN",
        "branch_country": "VN",
    }
    r = await client.post(
        "/job-market/me/hiring-rights-requests",
        cookies=cookies,
        headers=headers,
        json=body,
    )
    assert r.status_code == 201, r.text
    req = r.json()
    token = create_url_safe_token(
        {"request_id": req["id"], "user_id": owner_id}, expiration=86400
    )
    await client.get(f"/job-market/kyc/confirm-email/{token}", follow_redirects=False)
    up = await client.post(
        f"/job-market/me/hiring-rights-requests/{req['id']}/documents",
        cookies=cookies,
        headers=headers,
        data={"doc_type": "business_registration_document"},
        files={"file": ("biz.pdf", io.BytesIO(minimal_pdf()), "application/pdf")},
    )
    assert up.status_code == 201, up.text
    appr = await client.post(
        f"/job-market/admin/hiring-rights-requests/{req['id']}/approve",
        cookies=admin_c,
        headers=admin_h,
    )
    assert appr.status_code == 200, appr.text
    return req["company_id"]


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    async with httpx.AsyncClient(base_url=BASE, timeout=60.0) as client:
        admin_id, _ = await register_login(client, f"ad4a_{suffix}")
        await promote_admin(admin_id)
        login = await client.post(
            "/users/login",
            json={"username": f"ad4a_{suffix}", "password": PASSWORD},
        )
        admin_c = login.cookies
        ah = csrf_headers(admin_c)

        owner_id, owner_c = await register_login(client, f"ad4o_{suffix}")
        owner_email = f"ad4o_{suffix}@example.com"
        await set_email(owner_id, owner_email)
        oh = csrf_headers(owner_c)
        company_id = await become_org(
            client,
            owner_id=owner_id,
            cookies=owner_c,
            headers=oh,
            email=owner_email,
            reg=f"AD4{suffix.upper()}",
            admin_c=admin_c,
            admin_h=ah,
        )

        artist_id, artist_c = await register_login(client, f"ad4art_{suffix}")
        arh = csrf_headers(artist_c)
        we = await client.post(
            "/job-market/me/work-experiences",
            cookies=artist_c,
            headers=arh,
            json={
                "company_id": company_id,
                "employment_type": "full-time",
                "title": "Illustrator",
                "start_date": str(date(2024, 1, 1)),
                "end_date": None,
            },
        )
        assert we.status_code == 201, we.text
        we_id = we.json()["id"]
        assert we.json()["status"] == "pending"

        overview = await client.get("/admin/overview", cookies=admin_c)
        assert overview.status_code == 200, overview.text
        assert "open_work_exp_pending" in overview.json()
        assert overview.json()["open_work_exp_pending"] >= 1
        print("PASS overview work_exp count")

        listed = await client.get(
            "/job-market/admin/work-experiences",
            params={"status": "pending"},
            cookies=admin_c,
        )
        assert listed.status_code == 200, listed.text
        assert any(r["id"] == we_id for r in listed.json()), listed.text
        print("PASS admin list pending")

        forbidden = await client.get(
            "/job-market/admin/work-experiences",
            cookies=artist_c,
        )
        assert forbidden.status_code == 403, forbidden.text
        print("PASS non-admin 403")

        appr = await client.post(
            f"/job-market/admin/work-experiences/{we_id}/approve",
            cookies=admin_c,
            headers=ah,
        )
        assert appr.status_code == 200, appr.text
        assert appr.json()["status"] == "approved"
        print("PASS admin approve")

        # second WE for reject
        we2 = await client.post(
            "/job-market/me/work-experiences",
            cookies=artist_c,
            headers=arh,
            json={
                "company_id": company_id,
                "employment_type": "part-time",
                "title": "Designer",
                "start_date": str(date(2023, 1, 1)),
                "end_date": str(date(2023, 6, 1)),
            },
        )
        assert we2.status_code == 201, we2.text
        rej = await client.post(
            f"/job-market/admin/work-experiences/{we2.json()['id']}/reject",
            cookies=admin_c,
            headers=ah,
        )
        assert rej.status_code == 200, rej.text
        assert rej.json()["status"] == "rejected"
        print("PASS admin reject")

    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
