"""Job Market Sprint2 helpers (normalize, account kind, warnings)."""

from __future__ import annotations

import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.rest.roles import get_user_roles
from app.postgresql.models import CompaniesOrm

from .constants import DEFAULT_REGISTRATION_AUTHORITY

_SEPARATORS_RE = re.compile(r"[-\s.]+")


def normalize_registration_number(raw: str) -> str:
    """Trim, uppercase, strip allowed separators; keep leading zeros."""
    if raw is None:
        return ""
    cleaned = _SEPARATORS_RE.sub("", str(raw).strip()).upper()
    return cleaned


def default_authority(value: str | None) -> str:
    if value is None or not str(value).strip():
        return DEFAULT_REGISTRATION_AUTHORITY
    return str(value).strip()


async def resolve_account_kind(
    db: AsyncSession, user_id: int
) -> tuple[str, int | None]:
    """Return (account_kind, company_id). Org = employer + owned active company."""
    roles = await get_user_roles(db, user_id)
    if "employer" not in roles:
        return "personal", None

    company = await db.scalar(
        select(CompaniesOrm).where(
            CompaniesOrm.owner_user_id == user_id,
            CompaniesOrm.status.in_(("active", "suspended")),
        )
    )
    if company is None:
        return "personal", None
    return "organization", company.id


async def is_organization_user(db: AsyncSession, user_id: int) -> bool:
    kind, _ = await resolve_account_kind(db, user_id)
    return kind == "organization"


async def collect_name_domain_warnings(
    db: AsyncSession,
    display_name: str | None,
    domain: str | None,
    *,
    exclude_company_id: int | None = None,
) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    if display_name and str(display_name).strip():
        stmt = select(CompaniesOrm.id).where(
            CompaniesOrm.status == "active",
            func.lower(CompaniesOrm.display_name) == display_name.strip().lower(),
        )
        if exclude_company_id is not None:
            stmt = stmt.where(CompaniesOrm.id != exclude_company_id)
        if await db.scalar(stmt) is not None:
            warnings.append({"code": "duplicate_name"})

    if domain and str(domain).strip():
        stmt = select(CompaniesOrm.id).where(
            CompaniesOrm.status == "active",
            func.lower(CompaniesOrm.domain) == domain.strip().lower(),
        )
        if exclude_company_id is not None:
            stmt = stmt.where(CompaniesOrm.id != exclude_company_id)
        if await db.scalar(stmt) is not None:
            warnings.append({"code": "duplicate_domain"})
    return warnings


def looks_like_encrypted_pdf(raw: bytes) -> bool:
    if not raw.startswith(b"%PDF"):
        return False
    # Lightweight heuristic — full PDF parse deferred (no pypdf in deps).
    sample = raw[: min(len(raw), 200_000)]
    return b"/Encrypt" in sample
