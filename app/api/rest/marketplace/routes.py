from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import delete, func, insert, select, update

from app.api.rest.dependencies import db, user_id
from app.api.rest.marketplace.eligibility import (
    assert_can_create_listing,
    compute_eligibility,
)
from app.api.rest.marketplace.orders import (
    apply_sepay_webhook,
    create_or_reuse_order,
    get_open_pending,
    mock_mark_paid,
    payment_url_for,
    verify_sepay_signature,
)
from app.api.rest.marketplace.payment_methods import (
    assert_can_drop_active_method,
    clear_other_primaries,
    count_active_methods,
    get_owned_method,
)
from app.api.rest.marketplace.schemas import (
    CopyrightReportIn,
    CopyrightReportOut,
    EligibilityOut,
    EnableSellingOut,
    LicenseCertificateOut,
    ListingCreateIn,
    ListingOut,
    ListingPatchIn,
    OrderCreateOut,
    OrderOut,
    PaymentMethodIn,
    PaymentMethodOut,
    PaymentMethodPatchIn,
    PayoutConfigOut,
    PurchaseStateOut,
)
from app.api.rest.roles import assign_role
from app.config import settings
from app.postgresql.models import (
    CopyrightReportsOrm,
    LicenseCertificatesOrm,
    PinLicenseAccessOrm,
    PinListingsOrm,
    PinOrdersOrm,
    PinsOrm,
    SellerPaymentMethodsOrm,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/me/eligibility", response_model=EligibilityOut)
async def get_my_eligibility(user_id: user_id, db: db):
    result = await compute_eligibility(db, user_id)
    return result.as_dict()


@router.post("/me/enable-selling", response_model=EnableSellingOut)
async def enable_selling(user_id: user_id, db: db):
    result = await compute_eligibility(db, user_id)
    if not result.eligible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "eligibility_not_met",
                "eligibility": result.as_dict(),
            },
        )
    roles = await assign_role(db, user_id, "seller")
    await db.commit()
    return EnableSellingOut(roles=sorted(roles), eligible=True)


@router.get("/me/payout-config", response_model=PayoutConfigOut)
async def get_payout_config(
    user_id: user_id,
    price_minor: int | None = Query(default=None, gt=0),
):
    pct = float(settings.MP_PLATFORM_COMMISSION_PERCENT)
    pct = max(0.0, min(100.0, pct))
    out = PayoutConfigOut(
        commission_percent=pct,
        estimate_note="Platform fee applied at payout (Sprint4). No wallet balance.",
    )
    if price_minor is not None:
        commission_minor = int(round(price_minor * pct / 100.0))
        out.price_minor = price_minor
        out.commission_minor = commission_minor
        out.seller_net_minor = price_minor - commission_minor
    return out


@router.get("/me/payment-methods", response_model=list[PaymentMethodOut])
async def list_payment_methods(user_id: user_id, db: db):
    rows = await db.scalars(
        select(SellerPaymentMethodsOrm)
        .where(SellerPaymentMethodsOrm.user_id == user_id)
        .order_by(
            SellerPaymentMethodsOrm.is_primary.desc(),
            SellerPaymentMethodsOrm.id.desc(),
        )
    )
    return list(rows.all())


@router.post(
    "/me/payment-methods",
    response_model=PaymentMethodOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_method(body: PaymentMethodIn, user_id: user_id, db: db):
    active_before = await count_active_methods(db, user_id)
    make_primary = body.is_primary or active_before == 0
    if make_primary:
        await clear_other_primaries(db, user_id)

    row = await db.scalar(
        insert(SellerPaymentMethodsOrm)
        .values(
            user_id=user_id,
            method_type=body.method_type,
            display_name=body.display_name.strip(),
            account_identifier=body.account_identifier.strip(),
            bank_name=(body.bank_name or "").strip() or None,
            account_holder=(body.account_holder or "").strip() or None,
            is_active=True,
            is_primary=make_primary,
        )
        .returning(SellerPaymentMethodsOrm)
    )
    await db.commit()
    return row


@router.patch("/me/payment-methods/{method_id}", response_model=PaymentMethodOut)
async def patch_payment_method(
    method_id: int, body: PaymentMethodPatchIn, user_id: user_id, db: db
):
    row = await get_owned_method(db, user_id, method_id)
    values: dict = {}

    if body.display_name is not None:
        values["display_name"] = body.display_name.strip()
    if body.account_identifier is not None:
        values["account_identifier"] = body.account_identifier.strip()
    if body.bank_name is not None:
        values["bank_name"] = body.bank_name.strip() or None
    if body.account_holder is not None:
        values["account_holder"] = body.account_holder.strip() or None

    will_be_active = row.is_active if body.is_active is None else body.is_active
    if body.is_active is not None and body.is_active is False and row.is_active:
        remaining = await count_active_methods(db, user_id) - 1
        await assert_can_drop_active_method(
            db, user_id, remaining_active_after=remaining
        )
        values["is_active"] = False
        values["is_primary"] = False
    elif body.is_active is True:
        values["is_active"] = True

    if body.is_primary is True:
        if not will_be_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="inactive_cannot_be_primary",
            )
        await clear_other_primaries(db, user_id, keep_method_id=method_id)
        values["is_primary"] = True
    elif body.is_primary is False:
        values["is_primary"] = False

    if not values:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no_changes")

    row = await db.scalar(
        update(SellerPaymentMethodsOrm)
        .where(SellerPaymentMethodsOrm.id == method_id)
        .values(**values)
        .returning(SellerPaymentMethodsOrm)
    )
    await db.commit()
    return row


@router.delete("/me/payment-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(method_id: int, user_id: user_id, db: db):
    row = await get_owned_method(db, user_id, method_id)
    if row.is_active:
        remaining = await count_active_methods(db, user_id) - 1
        await assert_can_drop_active_method(
            db, user_id, remaining_active_after=remaining
        )
    await db.execute(
        delete(SellerPaymentMethodsOrm).where(SellerPaymentMethodsOrm.id == method_id)
    )
    await db.commit()
    return {"status": "ok"}


@router.get("/pins/{pin_id}/listing", response_model=ListingOut | None)
async def get_pin_listing(pin_id: int, user_id: user_id, db: db):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    listing = await db.scalar(
        select(PinListingsOrm).where(PinListingsOrm.pin_id == pin_id)
    )
    if listing is None:
        return None
    if listing.status != "listed" and listing.seller_user_id != user_id:
        return None
    return listing


@router.post(
    "/pins/{pin_id}/listing",
    response_model=ListingOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_relist_pin_listing(
    pin_id: int, body: ListingCreateIn, user_id: user_id, db: db
):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")
    if pin.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not pin owner")
    if not pin.original_image or not pin.image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="pin_media_incomplete"
        )
    if not body.attestation_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="attestation_required",
        )

    await assert_can_create_listing(db, user_id)

    existing = await db.scalar(
        select(PinListingsOrm).where(PinListingsOrm.pin_id == pin_id)
    )
    now = datetime.now(timezone.utc)
    attest_values = {
        "attestation_accepted": True,
        "attestation_version": settings.MP_ATTESTATION_VERSION,
        "attested_at": now,
    }
    if existing:
        listing = await db.scalar(
            update(PinListingsOrm)
            .where(PinListingsOrm.id == existing.id)
            .values(
                price_minor=body.price_minor,
                currency=body.currency,
                status="listed",
                license_type="personal_use",
                updated_at=now,
                **attest_values,
            )
            .returning(PinListingsOrm)
        )
    else:
        listing = await db.scalar(
            insert(PinListingsOrm)
            .values(
                pin_id=pin_id,
                seller_user_id=user_id,
                license_type="personal_use",
                price_minor=body.price_minor,
                currency=body.currency,
                status="listed",
                **attest_values,
            )
            .returning(PinListingsOrm)
        )
    await db.commit()
    return listing


@router.patch("/listings/{listing_id}", response_model=ListingOut)
async def patch_listing(listing_id: int, body: ListingPatchIn, user_id: user_id, db: db):
    listing = await db.scalar(
        select(PinListingsOrm).where(PinListingsOrm.id == listing_id)
    )
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="listing_not_found")
    if listing.seller_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not listing owner")

    values: dict = {"updated_at": datetime.now(timezone.utc)}
    if body.price_minor is not None:
        values["price_minor"] = body.price_minor
    if body.currency is not None:
        values["currency"] = body.currency
    if body.status is not None:
        if body.status == "listed":
            await assert_can_create_listing(db, user_id)
            if not body.attestation_accepted and not listing.attestation_accepted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="attestation_required",
                )
            if body.attestation_accepted:
                values["attestation_accepted"] = True
                values["attestation_version"] = settings.MP_ATTESTATION_VERSION
                values["attested_at"] = datetime.now(timezone.utc)
        values["status"] = body.status
    elif body.attestation_accepted is True:
        values["attestation_accepted"] = True
        values["attestation_version"] = settings.MP_ATTESTATION_VERSION
        values["attested_at"] = datetime.now(timezone.utc)

    if len(values) == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no_changes")

    listing = await db.scalar(
        update(PinListingsOrm)
        .where(PinListingsOrm.id == listing_id)
        .values(**values)
        .returning(PinListingsOrm)
    )
    await db.commit()
    return listing


def _order_out(order: PinOrdersOrm) -> OrderOut:
    data = OrderOut.model_validate(order)
    data.payment_url = payment_url_for(order)
    return data


@router.get("/pins/{pin_id}/purchase-state", response_model=PurchaseStateOut)
async def purchase_state(pin_id: int, user_id: user_id, db: db):
    owned = await db.scalar(
        select(PinLicenseAccessOrm.id).where(
            PinLicenseAccessOrm.user_id == user_id,
            PinLicenseAccessOrm.pin_id == pin_id,
        )
    )
    if owned is not None:
        return PurchaseStateOut(state="owned")

    pending = await get_open_pending(db, buyer_id=user_id, pin_id=pin_id)
    if pending is not None:
        return PurchaseStateOut(
            state="pending",
            order_id=pending.id,
            payment_code=pending.payment_code,
            payment_url=payment_url_for(pending),
            charge_amount_vnd=pending.charge_amount_vnd,
        )
    return PurchaseStateOut(state="none")


@router.post(
    "/pins/{pin_id}/orders",
    response_model=OrderCreateOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_pin_order(pin_id: int, user_id: user_id, db: db):
    before = await get_open_pending(db, buyer_id=user_id, pin_id=pin_id)
    order = await create_or_reuse_order(db, buyer_id=user_id, pin_id=pin_id)
    reused = before is not None and before.id == order.id
    url = payment_url_for(order)
    return OrderCreateOut(order=_order_out(order), payment_url=url, reused=reused)


@router.get("/me/orders/{order_id}", response_model=OrderOut)
async def get_my_order(order_id: int, user_id: user_id, db: db):
    order = await db.get(PinOrdersOrm, order_id)
    if order is None or order.buyer_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order_not_found")
    return _order_out(order)


@router.post("/me/orders/{order_id}/cancel", response_model=OrderOut)
async def cancel_my_order(order_id: int, user_id: user_id, db: db):
    order = await db.get(PinOrdersOrm, order_id)
    if order is None or order.buyer_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order_not_found")
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"order_{order.status}"
        )
    order = await db.scalar(
        update(PinOrdersOrm)
        .where(PinOrdersOrm.id == order_id)
        .values(status="cancelled", updated_at=datetime.now(timezone.utc))
        .returning(PinOrdersOrm)
    )
    await db.commit()
    return _order_out(order)


@router.post("/webhooks/sepay")
async def sepay_webhook(request: Request, db: db):
    import json

    raw = await request.body()
    verify_sepay_signature(
        raw,
        request.headers.get("X-SePay-Signature")
        or request.headers.get("x-sepay-signature"),
        request.headers.get("X-SePay-Timestamp")
        or request.headers.get("x-sepay-timestamp"),
    )
    try:
        payload = json.loads(raw.decode("utf-8") or "{}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_json"
        ) from e
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_json")
    return await apply_sepay_webhook(db, payload)


@router.post("/dev/mock-sepay-paid/{order_id}", response_model=OrderOut)
async def mock_sepay_paid(order_id: int, user_id: user_id, db: db):
    order = await mock_mark_paid(db, order_id, user_id)
    return _order_out(order)


@router.post(
    "/pins/{pin_id}/copyright-reports",
    response_model=CopyrightReportOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_copyright_report(
    pin_id: int, body: CopyrightReportIn, user_id: user_id, db: db
):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    window = max(1, int(settings.MP_COPYRIGHT_REPORT_WINDOW_SECONDS))
    max_reports = max(1, int(settings.MP_COPYRIGHT_REPORT_MAX))
    since = datetime.now(timezone.utc) - timedelta(seconds=window)
    recent = await db.scalar(
        select(func.count())
        .select_from(CopyrightReportsOrm)
        .where(
            CopyrightReportsOrm.reporter_user_id == user_id,
            CopyrightReportsOrm.created_at >= since,
        )
    )
    if int(recent or 0) >= max_reports:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="copyright_report_rate_limited",
        )

    row = await db.scalar(
        insert(CopyrightReportsOrm)
        .values(
            reporter_user_id=user_id,
            pin_id=pin_id,
            reason=body.reason.strip(),
            status="open",
        )
        .returning(CopyrightReportsOrm)
    )
    await db.commit()
    return row


@router.get("/me/certificates/by-pin/{pin_id}", response_model=LicenseCertificateOut | None)
async def get_my_certificate_for_pin(pin_id: int, user_id: user_id, db: db):
    row = await db.scalar(
        select(LicenseCertificatesOrm)
        .where(
            LicenseCertificatesOrm.pin_id == pin_id,
            LicenseCertificatesOrm.buyer_user_id == user_id,
        )
        .order_by(LicenseCertificatesOrm.id.desc())
    )
    return row


@router.get("/me/certificates/{order_id}", response_model=LicenseCertificateOut)
async def get_my_certificate(order_id: int, user_id: user_id, db: db):
    row = await db.scalar(
        select(LicenseCertificatesOrm).where(LicenseCertificatesOrm.order_id == order_id)
    )
    if row is None or row.buyer_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="certificate_not_found"
        )
    return row
