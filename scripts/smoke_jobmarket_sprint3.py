"""JobMarket Sprint3 smoke — job posts, explore, close/reopen, detail rules."""
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
    return (
        b"%PDF-1.1\n"
        b"1 0 obj<<>>endobj\n"
        b"trailer<<>>\n"
        b"%%EOF\n"
    )


async def become_org(
    client: httpx.AsyncClient,
    *,
    owner_cookies: httpx.Cookies,
    owner_headers: dict,
    owner_id: int,
    email: str,
    reg_number: str,
    admin_cookies: httpx.Cookies,
    admin_headers: dict,
    display_name: str = "Sprint3 Co",
) -> int:
    body = {
        "display_name": display_name,
        "description": "Studio",
        "industry": "Design",
        "size_min": 1,
        "size_max": 10,
        "website": "https://s3.example",
        "domain": f"s3-{reg_number.lower()}.example",
        "registration_country": "VN",
        "registration_authority": "NATIONAL",
        "registration_type": "LLC",
        "registration_number_raw": reg_number,
        "signer_full_name": "Owner Name",
        "primary_document_language": "en",
        "company_email": email,
        "address_line": "1 Main St",
        "city": "Hanoi",
        "branch_country": "VN",
    }
    r = await client.post(
        "/job-market/me/hiring-rights-requests",
        cookies=owner_cookies,
        headers=owner_headers,
        json=body,
    )
    assert r.status_code == 201, r.text
    req = r.json()

    token = create_url_safe_token(
        {"request_id": req["id"], "user_id": owner_id}, expiration=86400
    )
    conf = await client.get(
        f"/job-market/kyc/confirm-email/{token}", follow_redirects=False
    )
    assert conf.status_code in (200, 302), conf.text

    files = {"file": ("biz.pdf", io.BytesIO(minimal_pdf()), "application/pdf")}
    up = await client.post(
        f"/job-market/me/hiring-rights-requests/{req['id']}/documents",
        cookies=owner_cookies,
        headers=owner_headers,
        data={"doc_type": "business_registration_document"},
        files=files,
    )
    assert up.status_code == 201, up.text

    appr = await client.post(
        f"/job-market/admin/hiring-rights-requests/{req['id']}/approve",
        cookies=admin_cookies,
        headers=admin_headers,
    )
    assert appr.status_code == 200, appr.text
    return req["company_id"]


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    results: list[str] = []
    reg = f"33{suffix.upper()}"

    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as client:
        owner_id, owner_cookies = await register_and_login(client, f"jm3o_{suffix}")
        owner_email = f"jm3o_{suffix}@example.com"
        await set_email(owner_id, owner_email)
        oh = csrf_headers(owner_cookies)

        visitor_id, visitor_cookies = await register_and_login(
            client, f"jm3v_{suffix}"
        )
        await set_email(visitor_id, f"jm3v_{suffix}@example.com")
        vh = csrf_headers(visitor_cookies)

        admin_id, admin_cookies = await register_and_login(client, f"jm3a_{suffix}")
        await promote_admin(admin_id)
        login = await client.post(
            "/users/login",
            json={"username": f"jm3a_{suffix}", "password": PASSWORD},
        )
        admin_cookies = login.cookies
        ah = csrf_headers(admin_cookies)

        company_id = await become_org(
            client,
            owner_cookies=owner_cookies,
            owner_headers=oh,
            owner_id=owner_id,
            email=owner_email,
            reg_number=reg,
            admin_cookies=admin_cookies,
            admin_headers=ah,
            display_name=f"Acme {suffix}",
        )
        results.append("org_ready_ok")

        # Visitor cannot create job posts
        forbid = await client.post(
            "/job-market/me/job-posts",
            cookies=visitor_cookies,
            headers=vh,
            json={
                "title": "Nope",
                "years_experience": 1,
                "salary_mode": "love_it",
                "branch_ids": [1],
                "expires_at": future_expires_at(),
            },
        )
        assert forbid.status_code == 403, forbid.text
        results.append("non_owner_create_403_ok")

        branches = await client.get(
            f"/job-market/companies/{company_id}/branches",
            cookies=owner_cookies,
        )
        assert branches.status_code == 200 and branches.json(), branches.text
        branch_id = branches.json()[0]["id"]

        # Validation: missing locations
        bad_loc = await client.post(
            "/job-market/me/job-posts",
            cookies=owner_cookies,
            headers=oh,
            json={
                "title": "Designer",
                "years_experience": 2,
                "salary_mode": "range",
                "salary_min": 1000,
                "currency": "USD",
                "branch_ids": [],
                "expires_at": future_expires_at(),
            },
        )
        assert bad_loc.status_code == 422, bad_loc.text
        results.append("branch_ids_required_ok")

        love = await client.post(
            "/job-market/me/job-posts",
            cookies=owner_cookies,
            headers=oh,
            json={
                "title": f"Love Role {suffix}",
                "years_experience": 1,
                "description": "Passion",
                "salary_mode": "love_it",
                "currency": "VND",
                "branch_ids": [branch_id],
                "expires_at": future_expires_at(45),
            },
        )
        assert love.status_code == 201, love.text
        love_id = love.json()["id"]
        assert love.json()["locations"] and love.json()["locations"][0]["city"] == "Hanoi"
        results.append("create_love_it_ok")

        ranged = await client.post(
            "/job-market/me/job-posts",
            cookies=owner_cookies,
            headers=oh,
            json={
                "title": f"Paid Role {suffix}",
                "years_experience": 3,
                "salary_mode": "range",
                "salary_min": 1000,
                "salary_max": 2000,
                "currency": "USD",
                "branch_ids": [branch_id],
                "expires_at": future_expires_at(30),
            },
        )
        assert ranged.status_code == 201, ranged.text
        range_id = ranged.json()["id"]
        results.append("create_range_ok")

        # Explore: both active; response includes expires_at + application_count
        explore = await client.get(
            "/job-market/explore/jobs",
            cookies=visitor_cookies,
            params={"q": suffix},
        )
        assert explore.status_code == 200, explore.text
        explore_rows = explore.json()
        ids = {j["id"] for j in explore_rows}
        assert love_id in ids and range_id in ids
        by_id = {j["id"]: j for j in explore_rows}
        assert by_id[range_id].get("expires_at")
        assert "application_count" in by_id[range_id]
        # Suggest/search ranking: higher salary (range) before love_it (rank 0)
        ranked = [j["id"] for j in explore_rows if j["id"] in {love_id, range_id}]
        assert ranked[0] == range_id
        results.append("explore_includes_both_ok")

        # Client-side filters moved to FE; unused query params are ignored
        sal = await client.get(
            "/job-market/explore/jobs",
            cookies=visitor_cookies,
            params={"q": suffix, "salary_min": 1500, "salary_max": 2500, "currency": "USD"},
        )
        assert sal.status_code == 200, sal.text
        sal_ids = {j["id"] for j in sal.json()}
        assert love_id in sal_ids and range_id in sal_ids
        results.append("explore_ignores_server_salary_filter_ok")

        years = await client.get(
            "/job-market/explore/jobs",
            cookies=visitor_cookies,
            params={"q": suffix, "years_min": 3, "years_max": 3},
        )
        assert {j["id"] for j in years.json()} == {love_id, range_id}
        results.append("explore_ignores_server_years_filter_ok")

        loc = await client.get(
            "/job-market/explore/jobs",
            cookies=visitor_cookies,
            params={"q": suffix, "location": "Hanoi"},
        )
        assert love_id in {j["id"] for j in loc.json()}
        results.append("location_param_ignored_still_lists_ok")

        # Company active list
        hiring = await client.get(
            f"/job-market/companies/{company_id}/job-posts",
            cookies=visitor_cookies,
        )
        assert hiring.status_code == 200
        assert {j["id"] for j in hiring.json()} == {love_id, range_id}
        results.append("company_active_list_ok")

        # Detail active OK for visitor
        detail = await client.get(
            f"/job-market/jobs/{range_id}", cookies=visitor_cookies
        )
        assert detail.status_code == 200
        results.append("detail_active_ok")

        # Close → gone from explore; visitor detail 404; owner detail 200
        closed = await client.post(
            f"/job-market/me/job-posts/{range_id}/close",
            cookies=owner_cookies,
            headers=oh,
        )
        assert closed.status_code == 200 and closed.json()["status"] == "closed"

        explore2 = await client.get(
            "/job-market/explore/jobs",
            cookies=visitor_cookies,
            params={"q": suffix},
        )
        assert range_id not in {j["id"] for j in explore2.json()}
        assert love_id in {j["id"] for j in explore2.json()}

        miss = await client.get(
            f"/job-market/jobs/{range_id}", cookies=visitor_cookies
        )
        assert miss.status_code == 404

        owner_see = await client.get(
            f"/job-market/jobs/{range_id}", cookies=owner_cookies
        )
        assert owner_see.status_code == 200 and owner_see.json()["status"] == "closed"
        results.append("close_explore_and_detail_rules_ok")

        reopen = await client.post(
            f"/job-market/me/job-posts/{range_id}/reopen",
            cookies=owner_cookies,
            headers=oh,
        )
        assert reopen.status_code == 200 and reopen.json()["status"] == "active"
        results.append("reopen_ok")

        # Patch title
        patched = await client.patch(
            f"/job-market/me/job-posts/{love_id}",
            cookies=owner_cookies,
            headers=oh,
            json={"title": f"Love Role Updated {suffix}"},
        )
        assert patched.status_code == 200
        assert "Updated" in patched.json()["title"]
        results.append("patch_ok")

        # Visitor cannot close
        steal = await client.post(
            f"/job-market/me/job-posts/{love_id}/close",
            cookies=visitor_cookies,
            headers=vh,
        )
        assert steal.status_code in (403, 404)
        results.append("non_owner_close_forbidden_ok")

    for item in results:
        print("PASS:", item)
    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
