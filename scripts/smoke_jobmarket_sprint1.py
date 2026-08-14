"""JobMarket Sprint1 smoke tests (work-exp, credentials, CV, HY-01)."""
import asyncio
import uuid

import httpx
from sqlalchemy import text

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


async def set_email(user_id: int, email: str) -> None:
    async with async_session_maker() as session:
        await session.execute(
            text("UPDATE users SET email = :email, verified = true WHERE id = :uid"),
            {"email": email, "uid": user_id},
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


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    results: list[str] = []

    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as client:
        owner_id, owner_cookies = await register_and_login(client, f"jm1owner_{suffix}")
        await set_email(owner_id, f"jm1owner_{suffix}@example.com")
        other_id, other_cookies = await register_and_login(client, f"jm1other_{suffix}")
        admin_id, admin_cookies = await register_and_login(client, f"jm1admin_{suffix}")
        await promote_admin(admin_id)

        # Re-login admin so roles are fresh (roles already in DB)
        login = await client.post(
            "/users/login",
            json={"username": f"jm1admin_{suffix}", "password": PASSWORD},
        )
        admin_cookies = login.cookies

        oh = csrf_headers(owner_cookies)
        ah = csrf_headers(admin_cookies)
        xh = csrf_headers(other_cookies)

        # --- Work-exp CRUD + sort ---
        r1 = await client.post(
            "/job-market/me/work-experiences",
            cookies=owner_cookies,
            headers=oh,
            json={
                "company_name": "Beta Co",
                "employment_type": "full-time",
                "title": "Designer",
                "location": "HN",
                "start_date": "2022-01-01",
                "end_date": "2023-01-01",
            },
        )
        assert r1.status_code == 201, r1.text
        assert r1.json()["status"] == "pending"
        we_old = r1.json()["id"]

        r2 = await client.post(
            "/job-market/me/work-experiences",
            cookies=owner_cookies,
            headers=oh,
            json={
                "company_name": "Alpha Co",
                "employment_type": "part-time",
                "title": "Intern",
                "start_date": "2020-06-01",
                "end_date": None,
            },
        )
        assert r2.status_code == 201, r2.text
        we_new = r2.json()["id"]

        listed = await client.get(
            f"/job-market/users/{owner_id}/work-experiences",
            cookies=other_cookies,
        )
        assert listed.status_code == 200, listed.text
        rows = listed.json()
        assert [r["start_date"] for r in rows] == ["2020-06-01", "2022-01-01"]
        assert all(r["status"] == "pending" for r in rows)
        results.append("work_exp_crud_sort_ok")

        forbid = await client.patch(
            f"/job-market/me/work-experiences/{we_old}",
            cookies=other_cookies,
            headers=xh,
            json={"title": "Hacked"},
        )
        assert forbid.status_code in (403, 404), forbid.text
        results.append("work_exp_owner_block_ok")

        # --- Credentials owner CRUD (+ admin override still allowed) ---
        owner_cred = await client.post(
            "/job-market/me/credentials",
            cookies=owner_cookies,
            headers=oh,
            json={
                "kind": "education",
                "title": "BS Art",
                "organization": "Uni",
                "occurred_on": "2019-05-01",
            },
        )
        assert owner_cred.status_code == 201, owner_cred.text
        cred_id = owner_cred.json()["id"]

        steal_cred = await client.patch(
            f"/job-market/me/credentials/{cred_id}",
            cookies=other_cookies,
            headers=xh,
            json={"title": "Hacked"},
        )
        assert steal_cred.status_code in (403, 404), steal_cred.text

        patch_cred = await client.patch(
            f"/job-market/me/credentials/{cred_id}",
            cookies=owner_cookies,
            headers=oh,
            json={"title": "BFA Art"},
        )
        assert patch_cred.status_code == 200, patch_cred.text
        assert patch_cred.json()["title"] == "BFA Art"

        non_admin = await client.post(
            f"/job-market/admin/users/{owner_id}/credentials",
            cookies=owner_cookies,
            headers=oh,
            json={"kind": "award", "title": "Prize"},
        )
        assert non_admin.status_code == 403, non_admin.text

        admin_cred = await client.post(
            f"/job-market/admin/users/{owner_id}/credentials",
            cookies=admin_cookies,
            headers=ah,
            json={"kind": "award", "title": "Admin Prize"},
        )
        assert admin_cred.status_code == 201, admin_cred.text

        creds = await client.get(
            f"/job-market/users/{owner_id}/credentials",
            cookies=other_cookies,
        )
        assert creds.status_code == 200
        assert len(creds.json()) == 2
        results.append("credentials_owner_crud_ok")

        # --- CV email gate / quota / ownership ---
        no_email_upload = await client.post(
            "/job-market/me/cvs",
            cookies=other_cookies,
            headers=xh,
            files={
                "file": ("cv.pdf", b"%PDF-1.4 smoke", "application/pdf"),
            },
        )
        assert no_email_upload.status_code == 400, no_email_upload.text
        assert no_email_upload.json()["detail"] == "email_required"
        results.append("cv_email_gate_ok")

        for i in range(3):
            up = await client.post(
                "/job-market/me/cvs",
                cookies=owner_cookies,
                headers=oh,
                files={
                    "file": (f"cv{i}.pdf", b"%PDF-1.4 content " + str(i).encode(), "application/pdf"),
                },
            )
            assert up.status_code == 201, up.text

        fourth = await client.post(
            "/job-market/me/cvs",
            cookies=owner_cookies,
            headers=oh,
            files={"file": ("cv4.pdf", b"%PDF-1.4 x", "application/pdf")},
        )
        assert fourth.status_code == 400, fourth.text
        assert fourth.json()["detail"] == "cv_quota_exceeded"
        results.append("cv_quota_ok")

        owner_list = await client.get("/job-market/me/cvs", cookies=owner_cookies)
        assert owner_list.status_code == 200
        assert len(owner_list.json()) == 3
        cv_id = owner_list.json()[0]["id"]

        other_list = await client.get("/job-market/me/cvs", cookies=other_cookies)
        assert other_list.status_code == 200
        assert other_list.json() == []

        steal = await client.delete(
            f"/job-market/me/cvs/{cv_id}",
            cookies=other_cookies,
            headers=xh,
        )
        assert steal.status_code in (403, 404), steal.text
        results.append("cv_owner_block_ok")

        delete_ok = await client.delete(
            f"/job-market/me/cvs/{cv_id}",
            cookies=owner_cookies,
            headers=oh,
        )
        assert delete_ok.status_code == 204, delete_ok.text
        results.append("cv_delete_ok")

        # --- HY-01 avatar ownership ---
        tiny_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        cross = await client.post(
            f"/users/upload/{owner_id}",
            cookies=other_cookies,
            headers=xh,
            files={"file": ("a.png", tiny_png, "image/png")},
        )
        assert cross.status_code == 403, cross.text
        results.append("hy01_upload_block_ok")

        # cleanup work-exp
        await client.delete(
            f"/job-market/me/work-experiences/{we_old}",
            cookies=owner_cookies,
            headers=oh,
        )
        await client.delete(
            f"/job-market/me/work-experiences/{we_new}",
            cookies=owner_cookies,
            headers=oh,
        )
        await client.delete(
            f"/job-market/me/credentials/{cred_id}",
            cookies=owner_cookies,
            headers=oh,
        )
        await client.delete(
            f"/job-market/admin/users/{owner_id}/credentials/{admin_cred.json()['id']}",
            cookies=admin_cookies,
            headers=ah,
        )

    print("PASS:", ", ".join(results))
    print("ALL_SMOKE_PASS")


if __name__ == "__main__":
    asyncio.run(main())
