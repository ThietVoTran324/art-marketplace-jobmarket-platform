# Plan mode decisions — Marketplace_Sprint3 (Phase 2.3 Payment methods)

> **Initiative:** Marketplace_Sprint3 — payout methods + commission config  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-08** — all suggest Q1–Q5 A.

---

## 0. Meta

| | |
|---|---|
| Baseline Alembic | `e1f2a3b4c5d6` |
| Target head | `f2a3b4c5d6e7` — `marketplace sprint3 payout methods` |
| Quiz | Q1A columns · Q2A is_primary · Q3A 403 last method · Q4A float % · Q5A /settings |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Mở rộng bảng `seller_payment_methods` hiện có (không bảng mới) |
| P0-2 | Không SePay / order / wallet balance |
| P0-3 | FE payout trên `/settings` section mới |

---

## D* — Core

| ID | Quyết định |
|----|------------|
| D1 | Thêm cột nullable: `bank_name` String(120), `account_holder` String(120), `is_primary` bool NOT NULL default false |
| D2 | Khi set `is_primary=true` trên method A → clear primary các method khác cùng user (active) |
| D3 | Create: nếu là method active đầu tiên → auto `is_primary=true` |
| D4 | `PATCH /marketplace/me/payment-methods/{id}` — update fields + `is_active` + `is_primary` |
| D5 | Delete hoặc deactivate (`is_active=false`) method: nếu sau thao tác `active_count==0` **và** user còn `pin_listings.status=listed` → **403** `cannot_remove_last_payout_while_listed` |
| D6 | Settings: `MP_PLATFORM_COMMISSION_PERCENT: float = 0.0` (0–100) |
| D7 | `GET /marketplace/me/payout-config` → `{ commission_percent, estimate_note }` + optional `net_minor` helper query `?price_minor=` |
| D8 | PaymentMethodIn/Out gồm bank_name, account_holder, is_primary |
| D9 | FE Settings: list methods, add form, set primary, deactivate/delete, show commission % |
| D10 | Smoke: primary unique; 403 last method with listed; commission endpoint |

---

## Out of scope

SePay · orders · refund · KYC bank nhà nước · ví nội bộ
