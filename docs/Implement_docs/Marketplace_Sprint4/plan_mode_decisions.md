# Plan mode decisions — Marketplace_Sprint4 (Phase 2.4 Order + SePay)

> **Initiative:** Marketplace_Sprint4 — orders + SePay + grant access  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) — Plan #1 CHỐT  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-08** — all suggest Q1–Q6 A + **T2** (USD→VND charge).

---

## 0. Meta

| | |
|---|---|
| Baseline Alembic | `f2a3b4c5d6e7` |
| Target head | `a3b4c5d6e7f8` — `marketplace sprint4 orders sepay` |
| Quiz | Q1A reuse · Q2A payment_events · Q3A redirect/URL · Q4A Celery beat · Q5A email · Q6A pin_orders · T2 convert |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Một bảng `pin_orders` + `payment_events`; không payment-intent tách MVP |
| P0-2 | SePay webhook contract thật; `MP_SEPAY_MOCK=true` cho smoke local |
| P0-3 | T2: listing USD → `charge_amount_vnd` qua `MP_USD_TO_VND_RATE`; VND → major units |
| P0-4 | FE Buy trên PinView; trả `payment_url` / code (redirect hoặc mở tab) |
| P0-5 | Không refund state; không auto bank payout |

---

## D* — Core

| ID | Quyết định |
|----|------------|
| D1 | `pin_orders`: buyer/seller/pin/listing FKs; snapshot price/currency; `charge_amount_vnd`; `payment_code` UNIQUE; status `pending\|paid\|failed\|cancelled`; commission snapshot + `payout_status`; `expires_at`/`paid_at` |
| D2 | Create/reuse: nếu đã có `pending` cùng `(buyer,pin)` chưa hết hạn → reuse + trả lại payment info |
| D3 | Gate create: listing `listed`; buyer `verified`; buyer ≠ pin owner; chưa có `pin_license_access` |
| D4 | `payment_events`: UNIQUE `(provider, provider_event_id)`; store raw payload |
| D5 | Webhook SePay: CSRF-exempt; verify HMAC nếu secret set; match `code`/`payment_code`, `transferType=in`, amount; idempotent insert event rồi paid+grant |
| D6 | Paid → INSERT `pin_license_access` (unique); email buyer + seller; snapshot commission từ `MP_PLATFORM_COMMISSION_PERCENT` |
| D7 | Celery beat: cancel `pending` where `expires_at < now` |
| D8 | Mock: `POST /marketplace/dev/mock-sepay-paid/{order_id}` chỉ khi `MP_SEPAY_MOCK` |
| D9 | Routes: create order, get order, purchase-state, webhook, optional buyer cancel |
| D10 | Smoke: verified buyer; mock paid; access+original; webhook duplicate no double grant; self-buy/unverified blocked |

---

## Config

- `MP_ORDER_PENDING_TTL_MINUTES=30`
- `MP_USD_TO_VND_RATE=25000`
- `MP_SEPAY_MOCK=true` (dev)
- `MP_SEPAY_WEBHOOK_SECRET=` (optional HMAC)
- `MP_SEPAY_PAYMENT_BASE_URL=` (optional QR/payment page prefix; mock returns app URL)

---

## Out of scope

VNPay · refund · auto payout · cart · certificate
