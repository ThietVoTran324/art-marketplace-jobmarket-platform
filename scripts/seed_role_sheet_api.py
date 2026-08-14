"""Create one user per catalog role via HTTP API (+ Mailhog for email verify).

Bootstrap note: granting the first `admin` role cannot be done via API (chicken-egg).
This script registers the admin user via API, then calls grant_admin once for that
username only. All other roles/data go through HTTP validation paths.

Usage (host, stack up):
  python scripts/seed_role_sheet_api.py

Or in container:
  PYTHONPATH=/fastapi python scripts/seed_role_sheet_api.py
"""
from __future__ import annotations

import asyncio
import io
import re
import sys
import time
import uuid
from urllib.parse import urlparse

import httpx

BASE = "http://127.0.0.1:8000"
MAILHOG = "http://mailhog:8025"  # docker network; host may use localhost:8025
PASSWORD = "SheetPass123!"
SUFFIX = uuid.uuid4().hex[:6]


def csrf_headers(cookies: httpx.Cookies) -> dict[str, str]:
    token = cookies.get("csrf_token")
    if not token:
        raise RuntimeError("missing csrf_token cookie")
    return {"X-CSRF-Token": token}


def minimal_pdf() -> bytes:
    return b"%PDF-1.1\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


async def wait_mail_link(
    client: httpx.AsyncClient,
    to_email: str,
    *,
    path_contains: str,
    timeout_s: float = 45.0,
) -> str:
    deadline = time.time() + timeout_s
    needle = to_email.lower()
    while time.time() < deadline:
        r = await client.get(f"{MAILHOG}/api/v2/messages")
        r.raise_for_status()
        items = r.json().get("items") or []
        for msg in items:
            tos = []
            for t in msg.get("To") or []:
                mailbox = t.get("Mailbox", "")
                domain = t.get("Domain", "")
                tos.append(f"{mailbox}@{domain}".lower())
            if needle not in tos:
                continue
            body = (msg.get("Content") or {}).get("Body") or ""
            # Also scan MIME parts
            for part in ((msg.get("MIME") or {}).get("Parts") or []):
                body += "\n" + (part.get("Body") or "")
            pattern = rf'(https?://[^\s"\'<>]+{re.escape(path_contains)}[^\s"\'<>]*)'
            m = re.search(pattern, body)
            if m:
                return m.group(1).rstrip(')"\'>,')
        await asyncio.sleep(1.0)
    raise TimeoutError(f"no mail link ({path_contains}) for {to_email}")


async def register(
    client: httpx.AsyncClient, username: str, email: str
) -> dict:
    r = await client.post(
        f"{BASE}/users/register",
        json={"username": username, "password": PASSWORD, "email": email},
    )
    assert r.status_code == 201, r.text
    return r.json()


async def verify_account(client: httpx.AsyncClient, username: str, email: str) -> None:
    # Prefer same-token path as registration mail (API verify endpoint).
    try:
        from app.api.rest.utils import create_url_safe_token

        token = create_url_safe_token({"username": username})
        r = await client.get(f"{BASE}/users/verify/{token}")
        assert r.status_code in (200, 302), r.text
        return
    except Exception:
        pass
    link = await wait_mail_link(client, email, path_contains="/users/verify/")
    path = urlparse(link).path
    if not path.startswith("/"):
        path = "/" + path
    r = await client.get(f"{BASE}{path}")
    assert r.status_code in (200, 302), r.text


async def login(client: httpx.AsyncClient, username: str) -> httpx.Cookies:
    r = await client.post(
        f"{BASE}/users/login",
        json={"username": username, "password": PASSWORD},
    )
    assert r.status_code == 200, r.text
    return r.cookies


async def me(client: httpx.AsyncClient, cookies: httpx.Cookies) -> dict:
    r = await client.get(f"{BASE}/users/me", cookies=cookies)
    assert r.status_code == 200, r.text
    return r.json()


async def roles(client: httpx.AsyncClient, cookies: httpx.Cookies) -> list[str]:
    r = await client.get(f"{BASE}/users/me/roles", cookies=cookies)
    assert r.status_code == 200, r.text
    return list(r.json().get("roles") or [])


async def bootstrap_admin_role(username: str) -> None:
    """One-time role bootstrap (cannot assign first admin via API)."""
    import subprocess
    from pathlib import Path

    script = Path(__file__).resolve().parent / "grant_admin.py"
    proc = await asyncio.to_thread(
        subprocess.run,
        [sys.executable, str(script), username],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"grant_admin failed: {proc.stdout}\n{proc.stderr}"
        )
    print(proc.stdout.strip())


async def assign_role_api(
    client: httpx.AsyncClient,
    admin_cookies: httpx.Cookies,
    target_user_id: int,
    role: str,
) -> None:
    h = csrf_headers(admin_cookies)
    r = await client.post(
        f"{BASE}/admin/users/{target_user_id}/roles",
        cookies=admin_cookies,
        headers=h,
        json={"role": role},
    )
    assert r.status_code == 200, r.text


async def make_employer(
    client: httpx.AsyncClient,
    *,
    employer_cookies: httpx.Cookies,
    admin_cookies: httpx.Cookies,
    email: str,
) -> dict:
    eh = csrf_headers(employer_cookies)
    ah = csrf_headers(admin_cookies)
    reg = f"SHEET-{SUFFIX.upper()}"
    body = {
        "display_name": f"Sheet Co {SUFFIX}",
        "description": "Seed company for role sheet",
        "industry": "Design",
        "size_min": 1,
        "size_max": 20,
        "website": "https://sheet.example",
        "domain": "sheet.example",
        "registration_country": "VN",
        "registration_authority": "NATIONAL",
        "registration_type": "LLC",
        "registration_number_raw": reg,
        "signer_full_name": "Sheet Employer",
        "primary_document_language": "en",
        "company_email": email,
        "address_line": "1 Sheet St",
        "city": "HN",
        "branch_country": "VN",
    }
    r = await client.post(
        f"{BASE}/job-market/me/hiring-rights-requests",
        cookies=employer_cookies,
        headers=eh,
        json=body,
    )
    assert r.status_code == 201, r.text
    req = r.json()
    request_id = req["id"]

    # Confirm company email via same token helper as mail link (API endpoint).
    from app.api.rest.utils import create_url_safe_token

    emp_me = await me(client, employer_cookies)
    token = create_url_safe_token(
        {"request_id": request_id, "user_id": emp_me["id"]},
        expiration=86400,
    )
    conf = await client.get(
        f"{BASE}/job-market/kyc/confirm-email/{token}",
        follow_redirects=False,
    )
    assert conf.status_code in (200, 302), conf.text

    files = {"file": ("biz.pdf", io.BytesIO(minimal_pdf()), "application/pdf")}
    up = await client.post(
        f"{BASE}/job-market/me/hiring-rights-requests/{request_id}/documents",
        cookies=employer_cookies,
        headers=eh,
        data={"doc_type": "business_registration_document"},
        files=files,
    )
    assert up.status_code == 201, up.text

    appr = await client.post(
        f"{BASE}/job-market/admin/hiring-rights-requests/{request_id}/approve",
        cookies=admin_cookies,
        headers=ah,
    )
    assert appr.status_code == 200, appr.text
    return await me(client, employer_cookies)


async def main() -> int:
    sheet: list[dict] = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        health = await client.get(f"{BASE}/health")
        assert health.status_code == 200, "API not healthy"

        specs = [
            ("admin", f"sheet_admin_{SUFFIX}"),
            ("artist", f"sheet_artist_{SUFFIX}"),
            ("employer", f"sheet_employer_{SUFFIX}"),
            ("seller", f"sheet_seller_{SUFFIX}"),
        ]

        created: dict[str, dict] = {}
        for role_key, username in specs:
            email = f"{username}@example.com"
            user = await register(client, username, email)
            await verify_account(client, username, email)
            cookies = await login(client, username)
            profile = await me(client, cookies)
            created[role_key] = {
                "username": username,
                "email": email,
                "password": PASSWORD,
                "user_id": profile["id"],
                "cookies": cookies,
                "verified": profile.get("verified"),
            }
            print(f"registered+verified {role_key}: {username} id={profile['id']}")

        # Bootstrap admin role (only non-API step)
        await bootstrap_admin_role(created["admin"]["username"])
        admin_cookies = await login(client, created["admin"]["username"])
        created["admin"]["cookies"] = admin_cookies
        admin_roles = await roles(client, admin_cookies)
        assert "admin" in admin_roles, admin_roles

        # Seller via admin API
        await assign_role_api(
            client,
            admin_cookies,
            created["seller"]["user_id"],
            "seller",
        )

        # Employer via full KYC API path
        emp_profile = await make_employer(
            client,
            employer_cookies=created["employer"]["cookies"],
            admin_cookies=admin_cookies,
            email=created["employer"]["email"],
        )

        # Artist: default role only (re-login refresh)
        for role_key in ("admin", "artist", "employer", "seller"):
            cookies = await login(client, created[role_key]["username"])
            profile = await me(client, cookies)
            role_list = await roles(client, cookies)
            row = {
                "role_target": role_key,
                "user_id": profile["id"],
                "username": created[role_key]["username"],
                "email": created[role_key]["email"],
                "password": PASSWORD,
                "verified": profile.get("verified"),
                "roles": sorted(role_list),
                "account_kind": profile.get("account_kind"),
                "company_id": profile.get("company_id"),
            }
            if role_key == "employer":
                row["account_kind"] = emp_profile.get("account_kind")
                row["company_id"] = emp_profile.get("company_id")
                # refresh employer after approve
                cookies = await login(client, created["employer"]["username"])
                profile = await me(client, cookies)
                role_list = await roles(client, cookies)
                row["roles"] = sorted(role_list)
                row["account_kind"] = profile.get("account_kind")
                row["company_id"] = profile.get("company_id")
                row["verified"] = profile.get("verified")
            sheet.append(row)

    print("\n=== ROLE ACCOUNT SHEET ===")
    print(f"password (all): {PASSWORD}")
    print(f"suffix: {SUFFIX}")
    print("-" * 72)
    for row in sheet:
        print(
            f"{row['role_target']:10} | id={row['user_id']:<6} | "
            f"{row['username']:<28} | {row['email']:<36} | "
            f"roles={row['roles']} | kind={row['account_kind']} | "
            f"company_id={row['company_id']}"
        )
    print("-" * 72)
    print("NOTES:")
    print("- artist: default role after register+verify (API only)")
    print("- admin: register+verify API, then one grant_admin bootstrap for role")
    print("- seller: admin POST /admin/users/{id}/roles {seller}")
    print("- employer: KYC submit + mail confirm + doc upload + admin approve (API)")
    print("SHEET_OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except Exception as exc:
        print(f"SHEET_FAIL: {exc}", file=sys.stderr)
        raise
