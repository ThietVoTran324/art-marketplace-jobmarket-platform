"""JobMarket Sprint6 — job reports + company suspend."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from app.api.rest.audit import (
    ACTION_COMPANY_SUSPEND,
    ACTION_COMPANY_UNSUSPEND,
    ACTION_JOB_REPORT_ACTIONED,
    ACTION_JOB_REPORT_CREATE,
    ACTION_JOB_REPORT_DISMISS,
    TARGET_COMPANY,
    TARGET_JOB_REPORT,
    write_audit,
)
from app.api.rest.dependencies import db, require_roles, user_id
from app.postgresql.models import (
    CompaniesOrm,
    JobPostReportsOrm,
    JobPostsOrm,
    UsersOrm,
)

from .constants import (
    REPORT_STATUS_ACTIONED,
    REPORT_STATUS_DISMISSED,
    REPORT_STATUS_OPEN,
)
from .notify import notify_company_suspension
from .schemas import (
    CompanySuspendBody,
    JobReportCreate,
    JobReportOut,
    JobReportResolveBody,
)

router = APIRouter()
AdminUserId = Annotated[int, Depends(require_roles("admin"))]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _report_out(
    row: JobPostReportsOrm,
    *,
    job_title: str | None = None,
    company_id: int | None = None,
) -> JobReportOut:
    out = JobReportOut.model_validate(row)
    out.job_title = job_title
    out.company_id = company_id
    return out


@router.post(
    "/jobs/{job_post_id}/report",
    response_model=JobReportOut,
    status_code=status.HTTP_201_CREATED,
)
async def report_job(
    job_post_id: int, body: JobReportCreate, db: db, user_id: user_id
):
    job = await db.scalar(select(JobPostsOrm).where(JobPostsOrm.id == job_post_id))
    if job is None:
        raise HTTPException(status_code=404, detail="job post not found")

    company = await db.scalar(
        select(CompaniesOrm).where(CompaniesOrm.id == job.company_id)
    )
    if company is not None and company.owner_user_id == user_id:
        raise HTTPException(status_code=403, detail="cannot_report_own_job")

    existing = await db.scalar(
        select(JobPostReportsOrm).where(
            JobPostReportsOrm.job_post_id == job_post_id,
            JobPostReportsOrm.reporter_user_id == user_id,
            JobPostReportsOrm.status == REPORT_STATUS_OPEN,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="report_already_open")

    detail = body.detail.strip() if body.detail and body.detail.strip() else None
    row = JobPostReportsOrm(
        job_post_id=job_post_id,
        reporter_user_id=user_id,
        reason=body.reason,
        detail=detail,
        status=REPORT_STATUS_OPEN,
    )
    db.add(row)
    await db.flush()
    await write_audit(
        db,
        actor_user_id=user_id,
        action=ACTION_JOB_REPORT_CREATE,
        target_type=TARGET_JOB_REPORT,
        target_id=row.id,
        metadata={
            "job_post_id": job_post_id,
            "reason": body.reason,
        },
    )
    await db.commit()
    await db.refresh(row)
    return _report_out(
        row,
        job_title=job.title,
        company_id=job.company_id,
    )


@router.get("/admin/job-reports", response_model=list[JobReportOut])
async def admin_list_job_reports(
    db: db,
    admin_user_id: AdminUserId,
    status_filter: str | None = Query(default="open", alias="status"),
):
    _ = admin_user_id
    stmt = select(JobPostReportsOrm, JobPostsOrm.title, JobPostsOrm.company_id).join(
        JobPostsOrm, JobPostsOrm.id == JobPostReportsOrm.job_post_id
    )
    if status_filter is not None:
        if status_filter not in (
            REPORT_STATUS_OPEN,
            REPORT_STATUS_DISMISSED,
            REPORT_STATUS_ACTIONED,
        ):
            raise HTTPException(status_code=422, detail="invalid status")
        stmt = stmt.where(JobPostReportsOrm.status == status_filter)
    stmt = stmt.order_by(
        JobPostReportsOrm.created_at.asc(), JobPostReportsOrm.id.asc()
    )
    rows = (await db.execute(stmt)).all()
    return [
        _report_out(r, job_title=title, company_id=cid) for r, title, cid in rows
    ]


async def _resolve_report(
    db,
    *,
    report_id: int,
    admin_id: int,
    new_status: str,
    note: str | None,
    audit_action: str,
) -> JobReportOut:
    row = await db.scalar(
        select(JobPostReportsOrm).where(JobPostReportsOrm.id == report_id)
    )
    if row is None:
        raise HTTPException(status_code=404, detail="report not found")
    if row.status != REPORT_STATUS_OPEN:
        raise HTTPException(status_code=409, detail="report_not_open")

    row.status = new_status
    row.admin_note = note.strip() if note and note.strip() else None
    row.resolved_by = admin_id
    row.resolved_at = _now()
    row.updated_at = _now()

    job = await db.scalar(select(JobPostsOrm).where(JobPostsOrm.id == row.job_post_id))
    await write_audit(
        db,
        actor_user_id=admin_id,
        action=audit_action,
        target_type=TARGET_JOB_REPORT,
        target_id=row.id,
        metadata={"job_post_id": row.job_post_id, "status": new_status},
    )
    await db.commit()
    await db.refresh(row)
    return _report_out(
        row,
        job_title=job.title if job else None,
        company_id=job.company_id if job else None,
    )


@router.post(
    "/admin/job-reports/{report_id}/dismiss",
    response_model=JobReportOut,
)
async def admin_dismiss_report(
    report_id: int,
    db: db,
    admin_user_id: AdminUserId,
    body: JobReportResolveBody | None = None,
):
    note = body.note if body else None
    return await _resolve_report(
        db,
        report_id=report_id,
        admin_id=admin_user_id,
        new_status=REPORT_STATUS_DISMISSED,
        note=note,
        audit_action=ACTION_JOB_REPORT_DISMISS,
    )


@router.post(
    "/admin/job-reports/{report_id}/actioned",
    response_model=JobReportOut,
)
async def admin_action_report(
    report_id: int,
    db: db,
    admin_user_id: AdminUserId,
    body: JobReportResolveBody | None = None,
):
    note = body.note if body else None
    return await _resolve_report(
        db,
        report_id=report_id,
        admin_id=admin_user_id,
        new_status=REPORT_STATUS_ACTIONED,
        note=note,
        audit_action=ACTION_JOB_REPORT_ACTIONED,
    )


@router.post("/admin/companies/{company_id}/suspend", response_model=dict)
async def admin_suspend_company(
    company_id: int,
    body: CompanySuspendBody,
    db: db,
    admin_user_id: AdminUserId,
):
    company = await db.scalar(select(CompaniesOrm).where(CompaniesOrm.id == company_id))
    if company is None:
        raise HTTPException(status_code=404, detail="company not found")
    if company.status == "suspended":
        return {
            "id": company.id,
            "status": company.status,
            "suspend_reason": company.suspend_reason,
            "suspended_at": company.suspended_at,
        }
    if company.status != "active":
        raise HTTPException(status_code=422, detail="company_not_active")

    company.status = "suspended"
    company.suspend_reason = body.reason.strip()
    company.suspended_at = _now()
    company.updated_at = _now()

    await write_audit(
        db,
        actor_user_id=admin_user_id,
        action=ACTION_COMPANY_SUSPEND,
        target_type=TARGET_COMPANY,
        target_id=company.id,
        metadata={"reason": company.suspend_reason},
    )

    if company.owner_user_id is not None:
        owner = await db.scalar(
            select(UsersOrm).where(UsersOrm.id == company.owner_user_id)
        )
        if owner is not None:
            await notify_company_suspension(
                db,
                owner=owner,
                company_name=company.display_name,
                company_id=company.id,
                suspended=True,
                reason=company.suspend_reason,
            )

    await db.commit()
    await db.refresh(company)
    return {
        "id": company.id,
        "status": company.status,
        "suspend_reason": company.suspend_reason,
        "suspended_at": company.suspended_at,
    }


@router.post("/admin/companies/{company_id}/unsuspend", response_model=dict)
async def admin_unsuspend_company(
    company_id: int,
    db: db,
    admin_user_id: AdminUserId,
):
    company = await db.scalar(select(CompaniesOrm).where(CompaniesOrm.id == company_id))
    if company is None:
        raise HTTPException(status_code=404, detail="company not found")
    if company.status == "active":
        return {
            "id": company.id,
            "status": company.status,
            "suspend_reason": None,
            "suspended_at": None,
        }
    if company.status != "suspended":
        raise HTTPException(status_code=422, detail="company_not_suspended")

    company.status = "active"
    company.suspend_reason = None
    company.suspended_at = None
    company.updated_at = _now()

    await write_audit(
        db,
        actor_user_id=admin_user_id,
        action=ACTION_COMPANY_UNSUSPEND,
        target_type=TARGET_COMPANY,
        target_id=company.id,
        metadata={},
    )

    if company.owner_user_id is not None:
        owner = await db.scalar(
            select(UsersOrm).where(UsersOrm.id == company.owner_user_id)
        )
        if owner is not None:
            await notify_company_suspension(
                db,
                owner=owner,
                company_name=company.display_name,
                company_id=company.id,
                suspended=False,
            )

    await db.commit()
    await db.refresh(company)
    return {
        "id": company.id,
        "status": company.status,
        "suspend_reason": company.suspend_reason,
        "suspended_at": company.suspended_at,
    }
