# Plan mode decisions — Marketplace_Sprint2 (Phase 2.2 Listing + gate)

> **Initiative:** Marketplace_Sprint2 — eligibility + seller + pin_listings  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-08** — all suggest (Q1–Q5 A).

---

## 0. Meta

| | |
|---|---|
| Baseline Alembic | `d0e1f2a3b4c5` (Sprint1 CLOSED) |
| Target head | `e1f2a3b4c5d6` — `marketplace sprint2 listing gate` |
| Quiz lock | Q1A `pin_listings` · Q2A keep seller + block new list · Q3A `/marketplace` · Q4A minor units · Q5A CreatePin+PinView |
| Reuse | `assign_role` / `get_user_roles` (`app/api/rest/roles.py`); `pin_stats`; subscriptions count |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Gate AC-01..11; smoke C06/C07/C11 |
| P0-2 | Package `app/api/rest/marketplace/` + `include_router` trong `main.py`; prefix **`/marketplace`** |
| P0-3 | Config thresholds + defaults trên `settings` (env): `MP_ELIGIBILITY_MIN_PINS=5`, `MP_ELIGIBILITY_MIN_VIEWS=100`, `MP_ELIGIBILITY_MIN_FOLLOWERS=10` |
| P0-4 | Không SePay / orders / grant `pin_license_access` từ listing |
| P0-5 | Minimal `seller_payment_methods` trong cùng sprint (đủ P); Sprint3 mở rộng field/KYC |

---

## D* — Core technical

### Schema

| ID | Quyết định |
|----|------------|
| D1 | Bảng **`pin_listings`**: `id`, `pin_id` FK CASCADE **UNIQUE**, `seller_user_id` FK, `license_type` CHECK `personal_use`, `price_minor` INT NOT NULL CHECK `> 0`, `currency` CHECK IN (`USD`,`VND`) DEFAULT `USD`, `status` CHECK IN (`listed`,`unlisted`) DEFAULT `listed`, `created_at`, `updated_at`. Index `(seller_user_id, status)`, `(status)`. |
| D2 | Bảng **`seller_payment_methods`** (minimal): `id`, `user_id` FK CASCADE, `method_type` CHECK IN (`bank`,`e_wallet`), `display_name` String(100), `account_identifier` String(200) (STK/ví — plain text MVP), `is_active` bool default true, `created_at`. Index `(user_id)`. Không ví nội bộ / balance. |
| D3 | Không cột bán trên `pins` — mọi listing qua `pin_listings`. |

### Eligibility engine

| ID | Quyết định |
|----|------------|
| D4 | `N` = `COUNT(pins)` where `user_id`. `M` = `SUM(pin_stats.view_count)` join pins của user (null → 0). `K` = `COUNT(subscriptions)` where `following_id = user`. `P` = `COUNT(seller_payment_methods)` where `user_id` AND `is_active`. |
| D5 | `eligibility_ok` = N≥min_pins AND M≥min_views AND K≥min_followers AND P≥1. |
| D6 | `GET /marketplace/me/eligibility` → JSON từng criterion: `{code, current, threshold, passed}` + `eligible` bool + `has_seller_role` bool. |
| D7 | `POST /marketplace/me/enable-selling` — nếu không `eligibility_ok` → **400** `eligibility_not_met` + body breakdown; nếu ok → `assign_role(seller)` + 200. |
| D8 | Helper `assert_can_create_listing(db, user_id)`: cần role `seller` **và** `eligibility_ok`; else **403** `listing_blocked_below_threshold` hoặc `seller_required`. (Q2A: không revoke role.) |

### Listings API

| ID | Quyết định |
|----|------------|
| D9 | `POST /marketplace/pins/{pin_id}/listing` — body `price_minor`, `currency` optional default USD; require owner + D8; pin phải có `original_image` và `image`; upsert: nếu đã có row → set `listed` + update price; unique pin_id. |
| D10 | `PATCH /marketplace/listings/{id}` — owner seller: đổi `price_minor` / `currency` / `status` (`listed`↔`unlisted`). Re-`listed` cũng qua D8. |
| D11 | `GET /marketplace/pins/{pin_id}/listing` — public-to-auth: trả listing nếu `listed` (hoặc owner thấy cả unlisted). Include `price_minor`, `currency`, `license_type`, `seller_user_id`. |
| D12 | Enrich optional: field listing trên `GET /pins/{id}` **hoặc** FE gọi D11 riêng — **chọn FE gọi D11** để ít đụng pin routes (Sprint2). |
| D13 | C11: không endpoint “buy” Sprint2. FE ẩn CTA mua khi `authUserId === pin.user_id`. |

### Payment methods API (minimal)

| ID | Quyết định |
|----|------------|
| D14 | `GET/POST /marketplace/me/payment-methods`; `DELETE /marketplace/me/payment-methods/{id}` — chỉ own rows. |
| D15 | POST validate: `method_type`, `display_name`, `account_identifier` non-empty; max length theo schema. |

### FE

| ID | Quyết định |
|----|------------|
| D16 | **PinView:** panel eligibility / “Enable selling”; form giá + list/unlist nếu owner+seller; badge giá nếu listed (mọi viewer); **không** nút Buy cho owner; Buy stub disabled “Coming soon” optional cho non-owner khi listed. |
| D17 | **CreatePinView:** sau create thành công (hoặc toggle trước submit): nếu seller+eligible → option “List for sale” + price; gọi D9. |
| D18 | Hydrate roles đã có (`/users/me/roles`) — sau enable-selling refresh roles store. |

### Smoke

| ID | Quyết định |
|----|------------|
| D19 | `scripts/smoke_marketplace_sprint2.py`: seed user dưới ngưỡng → enable 400; bump counts/methods → enable 200 + seller role; create listing; non-owner POST listing 403; owner không “buy” path; dưới ngưỡng sau đó POST listing mới 403; `ALL_SMOKE_PASS`. |

---

## Out of scope (tech)

- Orders / SePay / webhook  
- `pin_license_access` grant từ pay  
- Commission % / payout job  
- Admin moderation listing  
- Refund  

---

## Trace → checklist

P0* / D* → `devplan_checklist.md` P0–P7.
