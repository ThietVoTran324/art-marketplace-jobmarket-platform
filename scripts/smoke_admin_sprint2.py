"""Admin_Sprint2 smoke — KYC docs list, need-more, credentials, JD dismiss, suspend."""
import asyncio
import io
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import text

from app.api.rest.utils import create_url_safe_token
from app.postgresql.database import async_session_maker

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


def future_expires_at(days: int = 30) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


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


async def register_and_login(
    client: httpx.AsyncClient, username: str
) -> tuple[int, httpx.Cookies]:
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


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    async with httpx.AsyncClient(base_url=BASE, timeout=60.0) as client:
        admin_id, _ = await register_and_login(client, f"ad2a_{suffix}")
        await promote_admin(admin_id)
        login = await client.post(
            "/users/login",
            json={"username": f"ad2a_{suffix}", "password": PASSWORD},
        )
        admin_c = login.cookies
        ah = csrf_headers(admin_c)

        owner_id, owner_c = await register_and_login(client, f"ad2o_{suffix}")
        owner_email = f"ad2o_{suffix}@example.com"
        await set_email(owner_id, owner_email)
        oh = csrf_headers(owner_c)

        # --- KYC submit + doc ---
        body = {
            "display_name": f"AdminS2 Co {suffix}",
            "registration_country": "VN",
            "registration_type": "LLC",
            "registration_number_raw": f"AD2{suffix.upper()}",
            "signer_full_name": "Owner",
            "primary_document_language": "en",
            "company_email": owner_email,
            "address_line": "1 Main",
            "city": "HN",
            "branch_country": "VN",
        }
        req = await client.post(
            "/job-market/me/hiring-rights-requests",
            cookies=owner_c,
            headers=oh,
            json=body,
        )
        assert req.status_code == 201, req.text
        request_id = req.json()["id"]
        company_id = req.json()["company_id"]

        token = create_url_safe_token(
            {"request_id": request_id, "user_id": owner_id}, expiration=86400
        )
        await client.get(
            f"/job-market/kyc/confirm-email/{token}", follow_redirects=False
        )

        up = await client.post(
            f"/job-market/me/hiring-rights-requests/{request_id}/documents",
            cookies=owner_c,
            headers=oh,
            data={"doc_type": "business_registration_document"},
            files={"file": ("biz.pdf", io.BytesIO(minimal_pdf()), "application/pdf")},
        )
        assert up.status_code == 201, up.text
        doc_id = up.json()["id"]

        docs = await client.get(
            f"/job-market/admin/hiring-rights-requests/{request_id}/documents",
            cookies=admin_c,
        )
        assert docs.status_code == 200, docs.text
        assert any(d["id"] == doc_id for d in docs.json()), docs.text
        print("PASS admin list kyc docs")

        file_r = await client.get(
            f"/job-market/admin/hiring-rights-requests/{request_id}/documents/{doc_id}/file",
            cookies=admin_c,
        )
        assert file_r.status_code == 200, file_r.text
        print("PASS admin download kyc doc")

        need = await client.post(
            f"/job-market/admin/hiring-rights-requests/{request_id}/need-more-info",
            cookies=admin_c,
            headers=ah,
            json={"note": "Please upload clearer scan"},
        )
        assert need.status_code == 200, need.text
        assert need.json()["status"] == "need_more_info"
        print("PASS need-more-info")

        # --- Credentials override ---
        target_id, _ = await register_and_login(client, f"ad2t_{suffix}")
        created = await client.post(
            f"/job-market/admin/users/{target_id}/credentials",
            cookies=admin_c,
            headers=ah,
            json={
                "kind": "education",
                "title": "BFA Design",
                "organization": "Art School",
            },
        )
        assert created.status_code == 201, created.text
        cred_id = created.json()["id"]

        listed = await client.get(
            f"/job-market/users/{target_id}/credentials",
            cookies=admin_c,
        )
        assert listed.status_code == 200, listed.text
        assert any(c["id"] == cred_id for c in listed.json())

        patched = await client.patch(
            f"/job-market/admin/users/{target_id}/credentials/{cred_id}",
            cookies=admin_c,
            headers=ah,
            json={"title": "BFA Design Updated"},
        )
        assert patched.status_code == 200, patched.text
        assert patched.json()["title"] == "BFA Design Updated"

        deleted = await client.delete(
            f"/job-market/admin/users/{target_id}/credentials/{cred_id}",
            cookies=admin_c,
            headers=ah,
        )
        assert deleted.status_code == 204, deleted.text
        print("PASS credentials admin CRUD")

        # --- Approve KYC then job + report ---
        appr = await client.post(
            f"/job-market/admin/hiring-rights-requests/{request_id}/approve",
            cookies=admin_c,
            headers=ah,
        )
        # may fail if still need_more — re-set pending via approve from need_more is allowed
        assert appr.status_code == 200, appr.text
        print("PASS approve after need-more")

        branches = await client.get(
            f"/job-market/companies/{company_id}/branches", cookies=owner_c
        )
        assert branches.status_code == 200, branches.text
        branch_id = branches.json()[0]["id"]
        job = await client.post(
            "/job-market/me/job-posts",
            cookies=owner_c,
            headers=oh,
            json={
                "title": f"Role {suffix}",
                "years_experience": 1,
                "salary_mode": "love_it",
                "currency": "VND",
                "branch_ids": [branch_id],
                "expires_at": future_expires_at(),
            },
        )
        assert job.status_code == 201, job.text
        job_id = job.json()["id"]

        reporter_id, reporter_c = await register_and_login(client, f"ad2r_{suffix}")
        await set_email(reporter_id, f"ad2r_{suffix}@example.com")
        rh = csrf_headers(reporter_c)
        rep = await client.post(
            f"/job-market/jobs/{job_id}/report",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "spam"},
        )
        assert rep.status_code == 201, rep.text
        report_id = rep.json()["id"]

        open_list = await client.get(
            "/job-market/admin/job-reports",
            params={"status": "open"},
            cookies=admin_c,
        )
        assert open_list.status_code == 200, open_list.text
        assert any(r["id"] == report_id for r in open_list.json())

        dismiss = await client.post(
            f"/job-market/admin/job-reports/{report_id}/dismiss",
            cookies=admin_c,
            headers=ah,
            json={"note": "not actionable"},
        )
        assert dismiss.status_code == 200, dismiss.text
        assert dismiss.json()["status"] == "dismissed"
        print("PASS job report dismiss")

        # second report for suspend path
        rep2 = await client.post(
            f"/job-market/jobs/{job_id}/report",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "scam"},
        )
        # may 409 if unique open reporter+job — create another reporter
        if rep2.status_code != 201:
            r2_id, r2_c = await register_and_login(client, f"ad2r2_{suffix}")
            await set_email(r2_id, f"ad2r2_{suffix}@example.com")
            r2h = csrf_headers(r2_c)
            rep2 = await client.post(
                f"/job-market/jobs/{job_id}/report",
                cookies=r2_c,
                headers=r2h,
                json={"reason": "scam"},
            )
        assert rep2.status_code == 201, rep2.text

        sus = await client.post(
            f"/job-market/admin/companies/{company_id}/suspend",
            cookies=admin_c,
            headers=ah,
            json={"reason": "spam hiring"},
        )
        assert sus.status_code == 200, sus.text
        assert sus.json()["status"] == "suspended"

        uns = await client.post(
            f"/job-market/admin/companies/{company_id}/unsuspend",
            cookies=admin_c,
            headers=ah,
        )
        assert uns.status_code == 200, uns.text
        assert uns.json()["status"] == "active"
        print("PASS suspend/unsuspend")

        # non-admin blocked on list docs
        forbidden = await client.get(
            f"/job-market/admin/hiring-rights-requests/{request_id}/documents",
            cookies=owner_c,
        )
        assert forbidden.status_code == 403, forbidden.text
        print("PASS non-admin docs 403")

    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
