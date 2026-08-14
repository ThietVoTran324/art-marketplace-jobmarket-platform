from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.postgresql.models import (
    BoardsOrm,
    CommentsOrm,
    CompaniesOrm,
    CompanyVerificationRequestsOrm,
    JobApplicationsOrm,
    JobPostsOrm,
    PinLicenseAccessOrm,
    PinsOrm,
    ProfileCredentialsOrm,
    UserCvsOrm,
    WorkExperiencesOrm,
)


async def assert_pin_owner(db: AsyncSession, pin_id: int, user_id: int) -> PinsOrm:
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")
    if pin.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not pin owner")
    return pin


async def user_can_access_pin_original(
    db: AsyncSession, pin: PinsOrm, user_id: int
) -> bool:
    if pin.user_id == user_id:
        return True
    access = await db.scalar(
        select(PinLicenseAccessOrm).where(
            PinLicenseAccessOrm.pin_id == pin.id,
            PinLicenseAccessOrm.user_id == user_id,
        )
    )
    return access is not None


async def assert_can_access_pin_original(
    db: AsyncSession, pin_id: int, user_id: int
) -> PinsOrm:
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")
    if not await user_can_access_pin_original(db, pin, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="original_forbidden"
        )
    return pin


async def assert_board_owner(db: AsyncSession, board_id: int, user_id: int) -> BoardsOrm:
    board = await db.scalar(select(BoardsOrm).where(BoardsOrm.id == board_id))
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="board not found")
    if board.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not board owner")
    return board


async def assert_comment_author(
    db: AsyncSession, comment_id: int, user_id: int
) -> CommentsOrm:
    comment = await db.scalar(select(CommentsOrm).where(CommentsOrm.id == comment_id))
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="comment not found")
    if comment.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not comment author")
    return comment


async def assert_work_exp_owner(
    db: AsyncSession, work_exp_id: int, user_id: int
) -> WorkExperiencesOrm:
    row = await db.scalar(
        select(WorkExperiencesOrm).where(WorkExperiencesOrm.id == work_exp_id)
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="work experience not found"
        )
    if row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not work experience owner"
        )
    return row


async def assert_cv_owner(db: AsyncSession, cv_id: int, user_id: int) -> UserCvsOrm:
    row = await db.scalar(select(UserCvsOrm).where(UserCvsOrm.id == cv_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cv not found")
    if row.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not cv owner")
    return row


async def assert_credential_owner(
    db: AsyncSession, credential_id: int, user_id: int
) -> ProfileCredentialsOrm:
    row = await db.scalar(
        select(ProfileCredentialsOrm).where(ProfileCredentialsOrm.id == credential_id)
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="credential not found"
        )
    if row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not credential owner"
        )
    return row


async def assert_kyc_request_owner(
    db: AsyncSession, request_id: int, user_id: int
) -> CompanyVerificationRequestsOrm:
    row = await db.scalar(
        select(CompanyVerificationRequestsOrm).where(
            CompanyVerificationRequestsOrm.id == request_id
        )
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="kyc request not found"
        )
    if row.requester_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="kyc request not found"
        )
    return row


async def assert_company_owner(
    db: AsyncSession, company_id: int, user_id: int
) -> CompaniesOrm:
    row = await db.scalar(select(CompaniesOrm).where(CompaniesOrm.id == company_id))
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="company not found"
        )
    if row.owner_user_id != user_id or row.status not in ("active", "suspended"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not company owner"
        )
    return row


async def assert_job_post_company_owner(
    db: AsyncSession, job_post_id: int, user_id: int
) -> JobPostsOrm:
    from app.api.rest.roles import get_user_roles

    roles = await get_user_roles(db, user_id)
    if "employer" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="hiring_rights_required"
        )

    row = await db.scalar(select(JobPostsOrm).where(JobPostsOrm.id == job_post_id))
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="job post not found"
        )
    company = await db.scalar(
        select(CompaniesOrm).where(CompaniesOrm.id == row.company_id)
    )
    if (
        company is None
        or company.owner_user_id != user_id
        or company.status not in ("active", "suspended")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not company owner"
        )
    return row


async def assert_application_company_owner(
    db: AsyncSession, application_id: int, user_id: int
) -> JobApplicationsOrm:
    row = await db.scalar(
        select(JobApplicationsOrm).where(JobApplicationsOrm.id == application_id)
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="application not found"
        )
    await assert_job_post_company_owner(db, row.job_post_id, user_id)
    return row
