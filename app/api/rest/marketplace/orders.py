"""Order + SePay helpers (Sprint4)."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery.tasks import send_email
from app.config import settings
from app.postgresql.models import (
    PaymentEventsOrm,
    PinLicenseAccessOrm,
    PinListingsOrm,
    PinOrdersOrm,
    PinsOrm,
    UsersOrm,
    LicenseCertificatesOrm,
)


def compute_charge_amount_vnd(price_minor: int, currency: str) -> int:
    if currency == "VND":
        return max(1, price_minor // 100)
    major = price_minor / 100.0
    return max(1, int(round(major * float(settings.MP_USD_TO_VND_RATE))))


def make_payment_code() -> str:
    return f"MP{uuid.uuid4().hex[:12].upper()}"


def payment_url_for(order: PinOrdersOrm) -> str:
    base = (settings.MP_SEPAY_PAYMENT_BASE_URL or "").rstrip("/")
    if base:
        return f"{base}?code={order.payment_code}&amount={order.charge_amount_vnd}"
    # Mock / local: point buyer at mock confirm hint
    return (
        f"{settings.FRONTEND_DOMAIN}/pin/{order.pin_id}"
        f"?order={order.id}&code={order.payment_code}&pay=1"
    )


def verify_sepay_signature(
    raw_body: bytes, signature: str | None, timestamp: str | None
) -> None:
    secret = settings.MP_SEPAY_WEBHOOK_SECRET
    if not secret:
        # Local smoke only: allow unsigned webhooks when mock+dev.
        if settings.DEV_MODE and settings.MP_SEPAY_MOCK:
            return
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="sepay_webhook_secret_not_configured",
        )
    if not signature or not timestamp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_signature")
    try:
        ts = int(timestamp)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad_timestamp") from e
    now = int(datetime.now(timezone.utc).timestamp())
    if abs(now - ts) > 300:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="expired_signature")
    expected = "sha256=" + hmac.new(
        secret.encode(), f"{ts}.".encode() + raw_body, hashlib.sha256
    ).hexdigest()
    if not secrets.compare_digest(expected, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_signature")


async def assert_buyer_can_checkout(
    db: AsyncSession, *, buyer_id: int, pin: PinsOrm, listing: PinListingsOrm
) -> UsersOrm:
    buyer = await db.get(UsersOrm, buyer_id)
    if buyer is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    if not buyer.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="email_not_verified"
        )
    if pin.user_id == buyer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="cannot_buy_own_pin")
    if listing.status != "listed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="listing_not_listed")
    owned = await db.scalar(
        select(PinLicenseAccessOrm.id).where(
            PinLicenseAccessOrm.user_id == buyer_id,
            PinLicenseAccessOrm.pin_id == pin.id,
        )
    )
    if owned is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="already_owned")
    return buyer


async def get_open_pending(
    db: AsyncSession, *, buyer_id: int, pin_id: int
) -> PinOrdersOrm | None:
    now = datetime.now(timezone.utc)
    return await db.scalar(
        select(PinOrdersOrm).where(
            PinOrdersOrm.buyer_user_id == buyer_id,
            PinOrdersOrm.pin_id == pin_id,
            PinOrdersOrm.status == "pending",
            PinOrdersOrm.expires_at > now,
        )
    )


async def create_or_reuse_order(
    db: AsyncSession, *, buyer_id: int, pin_id: int
) -> PinOrdersOrm:
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")
    listing = await db.scalar(
        select(PinListingsOrm).where(
            PinListingsOrm.pin_id == pin_id, PinListingsOrm.status == "listed"
        )
    )
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="listing_not_found")

    await assert_buyer_can_checkout(db, buyer_id=buyer_id, pin=pin, listing=listing)

    existing = await get_open_pending(db, buyer_id=buyer_id, pin_id=pin_id)
    if existing is not None:
        return existing

    ttl = max(1, int(settings.MP_ORDER_PENDING_TTL_MINUTES))
    now = datetime.now(timezone.utc)
    order = await db.scalar(
        pg_insert(PinOrdersOrm)
        .values(
            buyer_user_id=buyer_id,
            seller_user_id=listing.seller_user_id,
            pin_id=pin_id,
            listing_id=listing.id,
            price_minor=listing.price_minor,
            currency=listing.currency,
            charge_amount_vnd=compute_charge_amount_vnd(
                listing.price_minor, listing.currency
            ),
            payment_code=make_payment_code(),
            provider="sepay",
            status="pending",
            payout_status="pending",
            expires_at=now + timedelta(minutes=ttl),
        )
        .returning(PinOrdersOrm)
    )
    await db.commit()
    return order


async def mark_order_paid(
    db: AsyncSession,
    order: PinOrdersOrm,
    *,
    provider_event_id: str,
    payload: dict,
) -> PinOrdersOrm:
    """Idempotent paid + grant. Caller must commit."""
    # Dedup event first
    inserted = await db.execute(
        pg_insert(PaymentEventsOrm)
        .values(
            provider="sepay",
            provider_event_id=str(provider_event_id),
            order_id=order.id,
            payload=payload,
        )
        .on_conflict_do_nothing(
            constraint="uq_payment_events_provider_event"
        )
        .returning(PaymentEventsOrm.id)
    )
    event_id = inserted.scalar_one_or_none()
    if event_id is None:
        # duplicate webhook — reload order
        return await db.get(PinOrdersOrm, order.id)

    if order.status == "paid":
        return order
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"order_{order.status}"
        )

    order_id = order.id
    pct = max(0.0, min(100.0, float(settings.MP_PLATFORM_COMMISSION_PERCENT)))
    commission_minor = int(round(order.price_minor * pct / 100.0))
    seller_net = order.price_minor - commission_minor
    now = datetime.now(timezone.utc)

    updated = await db.scalar(
        update(PinOrdersOrm)
        .where(PinOrdersOrm.id == order_id, PinOrdersOrm.status == "pending")
        .values(
            status="paid",
            paid_at=now,
            commission_percent=pct,
            commission_minor=commission_minor,
            seller_net_minor=seller_net,
            payout_status="pending",
            updated_at=now,
        )
        .returning(PinOrdersOrm)
    )
    if updated is None:
        return await db.get(PinOrdersOrm, order_id)

    order = updated
    await db.execute(
        pg_insert(PinLicenseAccessOrm)
        .values(
            user_id=order.buyer_user_id,
            pin_id=order.pin_id,
            order_id=order.id,
        )
        .on_conflict_do_nothing(constraint="uq_pin_license_access_user_pin")
    )

    pin = await db.get(PinsOrm, order.pin_id)
    cert_code = f"LC{order.id:08d}{uuid.uuid4().hex[:6].upper()}"
    await db.execute(
        pg_insert(LicenseCertificatesOrm)
        .values(
            order_id=order.id,
            pin_id=order.pin_id,
            buyer_user_id=order.buyer_user_id,
            seller_user_id=order.seller_user_id,
            license_type="personal_use",
            content_sha256=pin.content_sha256 if pin else None,
            certificate_code=cert_code,
            paid_at=order.paid_at or now,
        )
        .on_conflict_do_nothing(constraint="uq_license_certificates_order_id")
    )

    await _notify_paid(db, order)
    return order


async def _notify_paid(db: AsyncSession, order: PinOrdersOrm) -> None:
    buyer = await db.get(UsersOrm, order.buyer_user_id)
    seller = await db.get(UsersOrm, order.seller_user_id)
    pin_link = f"{settings.FRONTEND_DOMAIN}/pin/{order.pin_id}"
    try:
        if buyer and buyer.email:
            send_email.delay(
                [buyer.email],
                "License purchase confirmed",
                {
                    "pin_id": order.pin_id,
                    "order_id": order.id,
                    "pin_link": pin_link,
                    "home_link": settings.FRONTEND_DOMAIN,
                },
                "mail_marketplace_order_paid_buyer.html",
            )
        if seller and seller.email:
            send_email.delay(
                [seller.email],
                "Your pin license was purchased",
                {
                    "pin_id": order.pin_id,
                    "order_id": order.id,
                    "pin_link": pin_link,
                    "seller_net_minor": order.seller_net_minor,
                    "currency": order.currency,
                    "home_link": settings.FRONTEND_DOMAIN,
                },
                "mail_marketplace_order_paid_seller.html",
            )
    except Exception:
        # Do not fail payment grant if broker/email is down
        pass


async def apply_sepay_webhook(db: AsyncSession, payload: dict) -> dict:
    transfer_type = payload.get("transferType")
    if transfer_type != "in":
        return {"success": True, "skipped": "not_in"}

    code = payload.get("code") or ""
    if not code and isinstance(payload.get("content"), str):
        # try extract MPxxxxxxxx from content
        content = payload["content"].upper()
        for part in content.replace(",", " ").split():
            if part.startswith("MP") and len(part) >= 8:
                code = part
                break
    if not code:
        return {"success": True, "skipped": "no_code"}

    amount = payload.get("transferAmount")
    try:
        amount_i = int(amount)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad_amount")

    event_id = payload.get("id")
    if event_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_event_id")

    order = await db.scalar(
        select(PinOrdersOrm).where(PinOrdersOrm.payment_code == str(code).upper())
    )
    if order is None:
        return {"success": True, "skipped": "unknown_code"}

    if order.charge_amount_vnd != amount_i:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="amount_mismatch")

    if order.status == "pending" and order.expires_at <= datetime.now(timezone.utc):
        await db.execute(
            update(PinOrdersOrm)
            .where(PinOrdersOrm.id == order.id)
            .values(status="cancelled", updated_at=datetime.now(timezone.utc))
        )
        await db.commit()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="order_expired")

    await mark_order_paid(
        db, order, provider_event_id=str(event_id), payload=payload
    )
    await db.commit()
    return {"success": True}


async def mock_mark_paid(db: AsyncSession, order_id: int, buyer_id: int) -> PinOrdersOrm:
    if not (settings.DEV_MODE and settings.MP_SEPAY_MOCK):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    order = await db.get(PinOrdersOrm, order_id)
    if order is None or order.buyer_user_id != buyer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order_not_found")
    if order.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"order_{order.status}")
    payload = {
        "id": f"mock-{order.id}-{uuid.uuid4().hex[:8]}",
        "transferType": "in",
        "transferAmount": order.charge_amount_vnd,
        "code": order.payment_code,
        "content": order.payment_code,
    }
    order = await mark_order_paid(
        db, order, provider_event_id=str(payload["id"]), payload=payload
    )
    await db.commit()
    return order


async def cancel_expired_pending_sync_style(db: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        update(PinOrdersOrm)
        .where(
            PinOrdersOrm.status == "pending",
            PinOrdersOrm.expires_at <= now,
        )
        .values(status="cancelled", updated_at=now)
    )
    await db.commit()
    return result.rowcount or 0
