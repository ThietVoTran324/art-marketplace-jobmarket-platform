"""JobMarket Sprint5 smoke — work-exp link, approve, employees, gates."""
import asyncio
import io
import uuid
from datetime import date
from pathlib import Path

import httpx
from sqlalchemy import text

from app.api.rest.utils import create_url_safe_token
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


async def set_email(user_id: int, email: str, verified: bool = True) -> None:
    async with async_session_maker() as session:
        await session.execute(
            text(
                "UPDATE users SET email = :email, verified = :verified WHERE id = :uid"
            ),
            {"email": email, "verified": verified, "uid": user_id},
        )
        await session.commit()


async def count_updates(user_id: int, update_type: str) -> int:
    async with async_session_maker() as session:
        row = await session.execute(
            text(
                "SELECT COUNT(*) FROM updates "
                "WHERE user_update_to_id = :uid AND update_type = :t"
            ),
            {"uid": user_id, "t": update_type},
        )
        return int(row.scalar_one())


async def count_audit(action: str, target_id: int) -> int:
    async with async_session_maker() as session:
        row = await session.execute(
            text(
                "SELECT COUNT(*) FROM audit_logs "
                "WHERE action = :a AND target_id = :tid"
            ),
            {"a": action, "tid": target_id},
        )
        return int(row.scalar_one())


async def register_and_login(client, username: str):
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
    files = {"file": ("biz.pdf", io.BytesIO(minimal_pdf()), "application/pdf")}
    up = await client.post(
        f"/job-market/me/hiring-rights-requests/{req['id']}/documents",
        cookies=cookies,
        headers=headers,
        data={"doc_type": "business_registration_document"},
        files=files,
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
    results = []

    async with httpx.AsyncClient(base_url=BASE, timeout=60.0) as client:
        admin_id, admin_c = await register_and_login(client, f"jm5ad_{suffix}")
        await promote_admin(admin_id)
        login = await client.post(
            "/users/login",
            json={"username": f"jm5ad_{suffix}", "password": PASSWORD},
        )
        admin_c = login.cookies
        ah = csrf_headers(admin_c)

        owner_id, owner_c = await register_and_login(client, f"jm5o_{suffix}")
        owner_email = f"jm5o_{suffix}@example.com"
        await set_email(owner_id, owner_email)
        oh = csrf_headers(owner_c)
        company_id = await become_org(
            client,
            owner_id=owner_id,
            cookies=owner_c,
            headers=oh,
            email=owner_email,
            reg=f"REG5{suffix.upper()}",
            admin_c=admin_c,
            admin_h=ah,
        )
        results.append("org_ok")

        artist_id, artist_c = await register_and_login(client, f"jm5a_{suffix}")
        await set_email(artist_id, f"jm5a_{suffix}@example.com")
        arth = csrf_headers(artist_c)

        stranger_id, stranger_c = await register_and_login(client, f"jm5s_{suffix}")
        sh = csrf_headers(stranger_c)

        # Off-system free-text: pending, no owner notify
        before = await count_updates(owner_id, "work_exp_pending")
        r = await client.post(
            "/job-market/me/work-experiences",
            cookies=artist_c,
            headers=arth,
            json={
                "company_name": "Offsystem LLC",
                "employment_type": "full-time",
                "title": "Designer",
                "start_date": "2024-01-01",
            },
        )
        assert r.status_code == 201, r.text
        assert r.json()["status"] == "pending"
        assert r.json()["company_id"] is None
        after = await count_updates(owner_id, "work_exp_pending")
        assert after == before
        results.append("offsystem_ok")

        # Suggest
        sug = await client.get(
            "/job-market/company-suggestions",
            cookies=artist_c,
            params={"q": f"Co REG5{suffix.upper()[:4]}"},
        )
        assert sug.status_code == 200, sug.text
        assert any(c["id"] == company_id for c in sug.json())
        results.append("suggest_ok")

        # On-system link + notify
        before = await count_updates(owner_id, "work_exp_pending")
        r = await client.post(
            "/job-market/me/work-experiences",
            cookies=artist_c,
            headers=arth,
            json={
                "company_id": company_id,
                "employment_type": "full-time",
                "title": "Illustrator",
                "start_date": "2023-06-01",
            },
        )
        assert r.status_code == 201, r.text
        we = r.json()
        we_id = we["id"]
        assert we["company_id"] == company_id
        assert we["status"] == "pending"
        after = await count_updates(owner_id, "work_exp_pending")
        assert after == before + 1
        results.append("onsystem_notify_ok")

        # Non-owner cannot approve
        bad = await client.post(
            f"/job-market/me/company/work-experiences/{we_id}/approve",
            cookies=stranger_c,
            headers=sh,
        )
        assert bad.status_code in (403, 404), bad.text
        results.append("non_owner_blocked")

        # Pending list + approve + audit + artist notify
        pend = await client.get(
            "/job-market/me/company/work-experiences/pending",
            cookies=owner_c,
        )
        assert pend.status_code == 200, pend.text
        assert any(x["id"] == we_id for x in pend.json())

        before_art = await count_updates(artist_id, "work_exp_approved")
        ap = await client.post(
            f"/job-market/me/company/work-experiences/{we_id}/approve",
            cookies=owner_c,
            headers=oh,
        )
        assert ap.status_code == 200, ap.text
        assert ap.json()["status"] == "approved"
        assert await count_audit("work_exp_approve", we_id) >= 1
        assert await count_updates(artist_id, "work_exp_approved") == before_art + 1
        results.append("approve_ok")

        # Idempotent approve
        ap2 = await client.post(
            f"/job-market/me/company/work-experiences/{we_id}/approve",
            cookies=owner_c,
            headers=oh,
        )
        assert ap2.status_code == 200, ap2.text
        results.append("approve_idempotent_ok")

        # Employees public list includes artist
        emp = await client.get(
            f"/job-market/companies/{company_id}/employees",
            cookies=stranger_c,
        )
        assert emp.status_code == 200, emp.text
        body = emp.json()
        assert body["employees_public"] is True
        assert any(e["user_id"] == artist_id for e in body["employees"])
        results.append("employees_public_ok")

        # Head CRUD
        head = await client.post(
            "/job-market/me/company/employee-heads",
            cookies=owner_c,
            headers=oh,
            json={"user_id": artist_id, "title": "Art Lead", "sort_order": 1},
        )
        assert head.status_code == 201, head.text
        head_id = head.json()["id"]
        emp2 = await client.get(
            f"/job-market/companies/{company_id}/employees",
            cookies=stranger_c,
        )
        assert any(h["id"] == head_id for h in emp2.json()["heads"])
        results.append("head_ok")

        # Private employees
        priv = await client.patch(
            "/job-market/me/company",
            cookies=owner_c,
            headers=oh,
            json={"employees_public": False},
        )
        assert priv.status_code == 200, priv.text
        assert priv.json()["employees_public"] is False
        blocked = await client.get(
            f"/job-market/companies/{company_id}/employees",
            cookies=stranger_c,
        )
        assert blocked.status_code == 403, blocked.text
        owner_see = await client.get(
            f"/job-market/companies/{company_id}/employees",
            cookies=owner_c,
        )
        assert owner_see.status_code == 200, owner_see.text
        results.append("private_ok")

        # Material edit resets + notify
        before = await count_updates(owner_id, "work_exp_pending")
        patch = await client.patch(
            f"/job-market/me/work-experiences/{we_id}",
            cookies=artist_c,
            headers=arth,
            json={"title": "Senior Illustrator"},
        )
        assert patch.status_code == 200, patch.text
        assert patch.json()["status"] == "pending"
        assert await count_updates(owner_id, "work_exp_pending") == before + 1
        results.append("material_reset_ok")

        # Reject + audit
        before_rej = await count_updates(artist_id, "work_exp_rejected")
        rej = await client.post(
            f"/job-market/me/company/work-experiences/{we_id}/reject",
            cookies=owner_c,
            headers=oh,
        )
        assert rej.status_code == 200, rej.text
        assert rej.json()["status"] == "rejected"
        assert await count_audit("work_exp_reject", we_id) >= 1
        assert await count_updates(artist_id, "work_exp_rejected") == before_rej + 1
        results.append("reject_ok")

        # Admin override approve
        r = await client.post(
            "/job-market/me/work-experiences",
            cookies=artist_c,
            headers=arth,
            json={
                "company_id": company_id,
                "employment_type": "part-time",
                "title": "Collab",
                "start_date": str(date.today().replace(year=date.today().year - 1)),
            },
        )
        assert r.status_code == 201, r.text
        we2 = r.json()["id"]
        adm = await client.post(
            f"/job-market/admin/work-experiences/{we2}/approve",
            cookies=admin_c,
            headers=ah,
        )
        assert adm.status_code == 200, adm.text
        assert adm.json()["status"] == "approved"
        results.append("admin_approve_ok")

        # Delete approved removes from employees (after making public again)
        await client.patch(
            "/job-market/me/company",
            cookies=owner_c,
            headers=oh,
            json={"employees_public": True},
        )
        d = await client.delete(
            f"/job-market/me/work-experiences/{we2}",
            cookies=artist_c,
            headers=arth,
        )
        assert d.status_code == 204, d.text
        emp3 = await client.get(
            f"/job-market/companies/{company_id}/employees",
            cookies=stranger_c,
        )
        assert not any(e["user_id"] == artist_id and e["work_experience_id"] == we2 for e in emp3.json()["employees"])
        results.append("delete_removes_ok")

    print("PASS:", ", ".join(results))
    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
