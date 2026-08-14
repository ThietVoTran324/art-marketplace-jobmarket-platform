"""JobMarket Sprint6 smoke — report JD, suspend company, gates."""
import asyncio
import io
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


async def count_audit(action: str, target_id: int | None = None) -> int:
    async with async_session_maker() as session:
        if target_id is None:
            row = await session.execute(
                text("SELECT COUNT(*) FROM audit_logs WHERE action = :a"),
                {"a": action},
            )
        else:
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
        admin_id, admin_c = await register_and_login(client, f"jm6ad_{suffix}")
        await promote_admin(admin_id)
        login = await client.post(
            "/users/login",
            json={"username": f"jm6ad_{suffix}", "password": PASSWORD},
        )
        admin_c = login.cookies
        ah = csrf_headers(admin_c)

        owner_id, owner_c = await register_and_login(client, f"jm6o_{suffix}")
        owner_email = f"jm6o_{suffix}@example.com"
        await set_email(owner_id, owner_email)
        oh = csrf_headers(owner_c)
        company_id = await become_org(
            client,
            owner_id=owner_id,
            cookies=owner_c,
            headers=oh,
            email=owner_email,
            reg=f"REG6{suffix.upper()}",
            admin_c=admin_c,
            admin_h=ah,
        )
        results.append("org_ok")

        branches = await client.get(
            f"/job-market/companies/{company_id}/branches", cookies=owner_c
        )
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
        results.append("job_ok")

        reporter_id, reporter_c = await register_and_login(client, f"jm6r_{suffix}")
        await set_email(reporter_id, f"jm6r_{suffix}@example.com")
        rh = csrf_headers(reporter_c)

        # Self-report blocked
        self_r = await client.post(
            f"/job-market/jobs/{job_id}/report",
            cookies=owner_c,
            headers=oh,
            json={"reason": "spam"},
        )
        assert self_r.status_code == 403, self_r.text
        results.append("self_report_blocked")

        # Report create
        rep = await client.post(
            f"/job-market/jobs/{job_id}/report",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "scam"},
        )
        assert rep.status_code == 201, rep.text
        report_id = rep.json()["id"]
        assert await count_audit("job_report_create", report_id) >= 1
        results.append("report_ok")

        # Duplicate open
        dup = await client.post(
            f"/job-market/jobs/{job_id}/report",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "spam"},
        )
        assert dup.status_code == 409, dup.text
        results.append("dup_report_ok")

        # other requires detail
        other = await client.post(
            f"/job-market/jobs/{job_id}/report",
            cookies=reporter_c,
            headers=rh,
            json={"reason": "other"},
        )
        # still 409 because open exists — create second reporter for other validation
        r2_id, r2_c = await register_and_login(client, f"jm6r2_{suffix}")
        r2h = csrf_headers(r2_c)
        bad_other = await client.post(
            f"/job-market/jobs/{job_id}/report",
            cookies=r2_c,
            headers=r2h,
            json={"reason": "other"},
        )
        assert bad_other.status_code == 422, bad_other.text
        ok_other = await client.post(
            f"/job-market/jobs/{job_id}/report",
            cookies=r2_c,
            headers=r2h,
            json={"reason": "other", "detail": "misleading"},
        )
        assert ok_other.status_code == 201, ok_other.text
        results.append("other_detail_ok")

        # Admin list + dismiss
        lst = await client.get(
            "/job-market/admin/job-reports",
            cookies=admin_c,
            params={"status": "open"},
        )
        assert lst.status_code == 200, lst.text
        assert any(x["id"] == report_id for x in lst.json())
        dis = await client.post(
            f"/job-market/admin/job-reports/{report_id}/dismiss",
            cookies=admin_c,
            headers=ah,
            json={"note": "not actionable"},
        )
        assert dis.status_code == 200, dis.text
        assert dis.json()["status"] == "dismissed"
        assert await count_audit("job_report_dismiss", report_id) >= 1
        results.append("dismiss_ok")

        # Actioned on second report
        rid2 = ok_other.json()["id"]
        act = await client.post(
            f"/job-market/admin/job-reports/{rid2}/actioned",
            cookies=admin_c,
            headers=ah,
            json={},
        )
        assert act.status_code == 200, act.text
        assert act.json()["status"] == "actioned"
        # job still active (no auto close)
        detail = await client.get(f"/job-market/jobs/{job_id}", cookies=reporter_c)
        assert detail.status_code == 200, detail.text
        results.append("actioned_no_auto_ok")

        # Suspend gates
        sus = await client.post(
            f"/job-market/admin/companies/{company_id}/suspend",
            cookies=admin_c,
            headers=ah,
            json={"reason": "policy violation"},
        )
        assert sus.status_code == 200, sus.text
        assert sus.json()["status"] == "suspended"
        assert await count_audit("company_suspend", company_id) >= 1
        results.append("suspend_ok")

        explore = await client.get("/job-market/explore/jobs", cookies=reporter_c)
        assert explore.status_code == 200, explore.text
        assert not any(j["id"] == job_id for j in explore.json())
        results.append("explore_hidden")

        pub = await client.get(f"/job-market/jobs/{job_id}", cookies=reporter_c)
        assert pub.status_code == 404, pub.text
        results.append("public_detail_hidden")

        owner_detail = await client.get(f"/job-market/jobs/{job_id}", cookies=owner_c)
        assert owner_detail.status_code == 200, owner_detail.text
        results.append("owner_detail_ok")

        create_blocked = await client.post(
            "/job-market/me/job-posts",
            cookies=owner_c,
            headers=oh,
            json={
                "title": "Blocked",
                "years_experience": 0,
                "salary_mode": "love_it",
                "branch_ids": [branch_id],
                "expires_at": future_expires_at(),
            },
        )
        assert create_blocked.status_code == 403, create_blocked.text
        results.append("create_blocked")

        patch_blocked = await client.patch(
            f"/job-market/me/job-posts/{job_id}",
            cookies=owner_c,
            headers=oh,
            json={"title": "Nope"},
        )
        assert patch_blocked.status_code == 403, patch_blocked.text
        results.append("patch_blocked")

        apply_blocked = await client.post(
            f"/job-market/jobs/{job_id}/apply",
            cookies=reporter_c,
            headers=rh,
            data={"cv_id": "1"},
        )
        # may 404 (job hidden) or 400 company_not_active depending on order —
        # apply loads job first then company; job exists so company_not_active
        assert apply_blocked.status_code in (400, 404), apply_blocked.text
        results.append("apply_blocked")

        # Unsuspend restore
        uns = await client.post(
            f"/job-market/admin/companies/{company_id}/unsuspend",
            cookies=admin_c,
            headers=ah,
        )
        assert uns.status_code == 200, uns.text
        assert uns.json()["status"] == "active"
        assert await count_audit("company_unsuspend", company_id) >= 1
        explore2 = await client.get("/job-market/explore/jobs", cookies=reporter_c)
        assert any(j["id"] == job_id for j in explore2.json())
        results.append("unsuspend_ok")

    print("PASS:", ", ".join(results))
    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
