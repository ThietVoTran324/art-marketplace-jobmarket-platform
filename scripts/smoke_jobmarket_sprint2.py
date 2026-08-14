"""JobMarket Sprint2 smoke tests (KYC, multi-pending, approve, org profile)."""
import asyncio
import io
import uuid

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


async def confirm_request_sql(request_id: int) -> None:
    async with async_session_maker() as session:
        await session.execute(
            text(
                "UPDATE company_verification_requests "
                "SET company_email_confirmed_at = now() WHERE id = :rid"
            ),
            {"rid": request_id},
        )
        await session.commit()


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


def minimal_pdf() -> bytes:
    # Minimal valid-ish PDF without /Encrypt
    return (
        b"%PDF-1.1\n"
        b"1 0 obj<<>>endobj\n"
        b"trailer<<>>\n"
        b"%%EOF\n"
    )


async def submit_kyc(
    client: httpx.AsyncClient,
    cookies: httpx.Cookies,
    headers: dict,
    *,
    email: str,
    reg_number: str,
    display_name: str = "Acme Studio",
    language: str = "en",
) -> dict:
    body = {
        "display_name": display_name,
        "description": "Design studio",
        "industry": "Design",
        "size_min": 1,
        "size_max": 10,
        "website": "https://acme.example",
        "domain": "acme.example",
        "registration_country": "VN",
        "registration_authority": "NATIONAL",
        "registration_type": "LLC",
        "registration_number_raw": reg_number,
        "signer_full_name": "Owner Name",
        "primary_document_language": language,
        "company_email": email,
        "address_line": "1 Main St",
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
    return r.json()


async def upload_biz_doc(
    client: httpx.AsyncClient,
    cookies: httpx.Cookies,
    headers: dict,
    request_id: int,
    doc_type: str = "business_registration_document",
) -> None:
    files = {"file": ("biz.pdf", io.BytesIO(minimal_pdf()), "application/pdf")}
    data = {"doc_type": doc_type}
    r = await client.post(
        f"/job-market/me/hiring-rights-requests/{request_id}/documents",
        cookies=cookies,
        headers=headers,
        data=data,
        files=files,
    )
    assert r.status_code == 201, r.text


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    results: list[str] = []
    reg = f"00{suffix.upper()}"

    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as client:
        a_id, a_cookies = await register_and_login(client, f"jm2a_{suffix}")
        a_email = f"jm2a_{suffix}@example.com"
        await set_email(a_id, a_email)

        b_id, b_cookies = await register_and_login(client, f"jm2b_{suffix}")
        b_email = f"jm2b_{suffix}@example.com"
        await set_email(b_id, b_email)

        other_id, other_cookies = await register_and_login(client, f"jm2o_{suffix}")
        await set_email(other_id, f"jm2o_{suffix}@example.com")

        admin_id, admin_cookies = await register_and_login(client, f"jm2admin_{suffix}")
        await promote_admin(admin_id)
        login = await client.post(
            "/users/login",
            json={"username": f"jm2admin_{suffix}", "password": PASSWORD},
        )
        admin_cookies = login.cookies

        ah = csrf_headers(a_cookies)
        bh = csrf_headers(b_cookies)
        oh = csrf_headers(other_cookies)
        adh = csrf_headers(admin_cookies)

        # Precondition: unverified email
        unver_id, unver_cookies = await register_and_login(client, f"jm2u_{suffix}")
        await set_email(unver_id, f"jm2u_{suffix}@example.com", verified=False)
        uh = csrf_headers(unver_cookies)
        bad = await client.post(
            "/job-market/me/hiring-rights-requests",
            cookies=unver_cookies,
            headers=uh,
            json={
                "display_name": "X",
                "registration_country": "VN",
                "registration_type": "LLC",
                "registration_number_raw": f"BAD{suffix}",
                "signer_full_name": "X",
                "primary_document_language": "en",
                "company_email": f"jm2u_{suffix}@example.com",
            },
        )
        assert bad.status_code == 400 and bad.json()["detail"] == "email_not_verified"
        results.append("precondition_email_verified_ok")

        # Multi-pending same key
        req_a = await submit_kyc(
            client, a_cookies, ah, email=a_email, reg_number=reg, display_name="Acme A"
        )
        req_b = await submit_kyc(
            client, b_cookies, bh, email=b_email, reg_number=reg, display_name="Acme B"
        )
        assert req_a["company_id"] == req_b["company_id"]
        assert req_a["id"] != req_b["id"]

        mine_a = await client.get(
            "/job-market/me/hiring-rights-requests", cookies=a_cookies
        )
        assert mine_a.status_code == 200
        assert all(r["requester_user_id"] == a_id for r in mine_a.json())
        assert all(r["id"] != req_b["id"] for r in mine_a.json())
        results.append("multi_pending_no_identity_leak_ok")

        # Approve blocked without email confirm
        block = await client.post(
            f"/job-market/admin/hiring-rights-requests/{req_a['id']}/approve",
            cookies=admin_cookies,
            headers=adh,
        )
        assert block.status_code == 400
        assert block.json()["detail"] == "company_email_not_confirmed"
        results.append("approve_requires_email_confirm_ok")

        # Confirm via token endpoint
        token = create_url_safe_token(
            {"request_id": req_a["id"], "user_id": a_id}, expiration=86400
        )
        conf = await client.get(f"/job-market/kyc/confirm-email/{token}", follow_redirects=False)
        assert conf.status_code in (200, 302), conf.text

        await upload_biz_doc(client, a_cookies, ah, req_a["id"])
        await confirm_request_sql(req_b["id"])  # sibling also confirmed for fairness
        await upload_biz_doc(client, b_cookies, bh, req_b["id"])

        # Non-admin cannot approve
        forbid = await client.post(
            f"/job-market/admin/hiring-rights-requests/{req_a['id']}/approve",
            cookies=other_cookies,
            headers=oh,
        )
        assert forbid.status_code == 403
        results.append("non_admin_approve_403_ok")

        # Approve A → sibling B rejected
        appr = await client.post(
            f"/job-market/admin/hiring-rights-requests/{req_a['id']}/approve",
            cookies=admin_cookies,
            headers=adh,
        )
        assert appr.status_code == 200, appr.text
        assert appr.json()["status"] == "approved"

        sib = await client.get(
            f"/job-market/me/hiring-rights-requests/{req_b['id']}",
            cookies=b_cookies,
        )
        assert sib.status_code == 200
        assert sib.json()["status"] == "rejected"
        assert sib.json()["rejection_reason"] == "superseded_by_other_approval"
        results.append("approve_atomic_siblings_ok")

        me = await client.get("/users/me", cookies=a_cookies)
        assert me.status_code == 200
        assert me.json()["account_kind"] == "organization"
        assert me.json()["company_id"] == req_a["company_id"]
        results.append("account_kind_organization_ok")

        roles = await client.get("/users/me/roles", cookies=a_cookies)
        assert "employer" in roles.json()["roles"]

        # Company mutate owner ok; other 403
        patch = await client.patch(
            "/job-market/me/company",
            cookies=a_cookies,
            headers=ah,
            json={"description": "Updated org profile"},
        )
        assert patch.status_code == 200, patch.text

        patch_b = await client.patch(
            "/job-market/me/company",
            cookies=b_cookies,
            headers=bh,
            json={"description": "Nope"},
        )
        assert patch_b.status_code == 403
        results.append("company_mutate_owner_gate_ok")

        # Active key blocks new submit
        c_id, c_cookies = await register_and_login(client, f"jm2c_{suffix}")
        c_email = f"jm2c_{suffix}@example.com"
        await set_email(c_id, c_email)
        ch = csrf_headers(c_cookies)
        blocked = await client.post(
            "/job-market/me/hiring-rights-requests",
            cookies=c_cookies,
            headers=ch,
            json={
                "display_name": "Clone",
                "registration_country": "VN",
                "registration_type": "LLC",
                "registration_number_raw": reg,
                "signer_full_name": "C",
                "primary_document_language": "en",
                "company_email": c_email,
            },
        )
        assert blocked.status_code == 409
        results.append("active_key_block_ok")

        # Org artist lists empty
        we = await client.get(
            f"/job-market/users/{a_id}/work-experiences", cookies=other_cookies
        )
        assert we.status_code == 200 and we.json() == []
        results.append("org_artist_lists_empty_ok")

        # Doc ownership: other cannot download A's doc
        docs = await client.get(
            f"/job-market/me/hiring-rights-requests/{req_a['id']}/documents",
            cookies=a_cookies,
        )
        assert docs.status_code == 200 and docs.json()
        doc_id = docs.json()[0]["id"]
        steal = await client.get(
            f"/job-market/me/hiring-rights-requests/{req_a['id']}/documents/{doc_id}/file",
            cookies=other_cookies,
        )
        assert steal.status_code == 404
        results.append("kyc_doc_ownership_ok")

        # Audit actions present
        async with async_session_maker() as session:
            rows = (
                await session.execute(
                    text(
                        "SELECT action FROM audit_logs WHERE action LIKE 'kyc_%' "
                        "ORDER BY id DESC LIMIT 20"
                    )
                )
            ).fetchall()
            actions = {r[0] for r in rows}
            assert "kyc_submit" in actions
            assert "kyc_approve" in actions
            assert "kyc_reject" in actions
        results.append("audit_kyc_actions_ok")

        # Rejected reuse: need_more_info / reject path with new key
        reg2 = f"11{suffix.upper()}"
        req2 = await submit_kyc(
            client, c_cookies, ch, email=c_email, reg_number=reg2, display_name="Beta Co"
        )
        await confirm_request_sql(req2["id"])
        rej = await client.post(
            f"/job-market/admin/hiring-rights-requests/{req2['id']}/reject",
            cookies=admin_cookies,
            headers=adh,
            json={"reason": "incomplete"},
        )
        assert rej.status_code == 200
        req2b = await submit_kyc(
            client,
            c_cookies,
            ch,
            email=c_email,
            reg_number=reg2,
            display_name="Beta Co Again",
        )
        assert req2b["company_id"] == req2["company_id"]
        results.append("reject_reuse_candidate_ok")

    for item in results:
        print("PASS:", item)
    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
