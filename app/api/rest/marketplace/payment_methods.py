"""Helpers for seller payment methods (Sprint3)."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.postgresql.models import PinListingsOrm, SellerPaymentMethodsOrm


async def count_active_methods(db: AsyncSession, user_id: int) -> int:
    return int(
        await db.scalar(
            select(func.count())
            .select_from(SellerPaymentMethodsOrm)
            .where(
                SellerPaymentMethodsOrm.user_id == user_id,
                SellerPaymentMethodsOrm.is_active.is_(True),
            )
        )
        or 0
    )


async def count_listed_pins(db: AsyncSession, user_id: int) -> int:
    return int(
        await db.scalar(
            select(func.count())
            .select_from(PinListingsOrm)
            .where(
                PinListingsOrm.seller_user_id == user_id,
                PinListingsOrm.status == "listed",
            )
        )
        or 0
    )


async def assert_can_drop_active_method(
    db: AsyncSession, user_id: int, *, remaining_active_after: int
) -> None:
    if remaining_active_after > 0:
        return
    listed = await count_listed_pins(db, user_id)
    if listed > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="cannot_remove_last_payout_while_listed",
        )


async def clear_other_primaries(
    db: AsyncSession, user_id: int, keep_method_id: int | None = None
) -> None:
    stmt = (
        update(SellerPaymentMethodsOrm)
        .where(
            SellerPaymentMethodsOrm.user_id == user_id,
            SellerPaymentMethodsOrm.is_primary.is_(True),
        )
        .values(is_primary=False)
    )
    if keep_method_id is not None:
        stmt = stmt.where(SellerPaymentMethodsOrm.id != keep_method_id)
    await db.execute(stmt)


async def get_owned_method(
    db: AsyncSession, user_id: int, method_id: int
) -> SellerPaymentMethodsOrm:
    row = await db.scalar(
        select(SellerPaymentMethodsOrm).where(SellerPaymentMethodsOrm.id == method_id)
    )
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="payment_method_not_found"
        )
    return row
