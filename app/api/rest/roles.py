from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.postgresql.models import UserRolesOrm

VALID_ROLES = frozenset({"admin", "artist", "employer", "seller"})
DEFAULT_ROLE = "artist"


async def get_user_roles(db: AsyncSession, user_id: int) -> set[str]:
    rows = await db.scalars(select(UserRolesOrm.role).where(UserRolesOrm.user_id == user_id))
    return set(rows.all())


async def ensure_default_roles(db: AsyncSession, user_id: int) -> None:
    stmt = (
        pg_insert(UserRolesOrm)
        .values(user_id=user_id, role=DEFAULT_ROLE)
        .on_conflict_do_nothing(index_elements=["user_id", "role"])
    )
    await db.execute(stmt)


async def assign_role(db: AsyncSession, user_id: int, role: str) -> set[str]:
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"invalid role; must be one of {sorted(VALID_ROLES)}",
        )
    stmt = (
        pg_insert(UserRolesOrm)
        .values(user_id=user_id, role=role)
        .on_conflict_do_nothing(index_elements=["user_id", "role"])
    )
    await db.execute(stmt)
    return await get_user_roles(db, user_id)


async def revoke_role(db: AsyncSession, user_id: int, role: str) -> set[str]:
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"invalid role; must be one of {sorted(VALID_ROLES)}",
        )
    await db.execute(
        delete(UserRolesOrm).where(UserRolesOrm.user_id == user_id, UserRolesOrm.role == role)
    )
    return await get_user_roles(db, user_id)
