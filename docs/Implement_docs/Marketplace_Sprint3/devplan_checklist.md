# Dev plan checklist — Marketplace_Sprint3 (Phase 2.3 Payment methods)



**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  

**Prerequisite:** Sprint2 CLOSED (`e1f2a3b4c5d6`)  

**Trạng thái:** **CLOSED** 2026-08-08 · Alembic `f2a3b4c5d6e7` · smoke `ALL_SMOKE_PASS`



**Baseline → target:** `e1f2a3b4c5d6` → `f2a3b4c5d6e7`



---



## P0 — Baseline



- [x] `alembic current` = `e1f2a3b4c5d6` (pre-upgrade)



---



## P1 — Schema + config



- [x] Columns `bank_name`, `account_holder`, `is_primary` trên `seller_payment_methods`

- [x] `MP_PLATFORM_COMMISSION_PERCENT` settings + `.env.example`

- [x] Alembic `f2a3b4c5d6e7`



---



## P2 — API payment methods expand



- [x] Create/list/out schemas mở rộng

- [x] PATCH method; set primary clears others

- [x] First active → auto primary

- [x] Delete/deactivate last while listed → 403

- [x] `GET /marketplace/me/payout-config`



---



## P3 — FE Settings payout



- [x] Section payout trên `SettingsView.vue`



---



## P4 — Smoke + đóng



- [x] `scripts/smoke_marketplace_sprint3.py` → `ALL_SMOKE_PASS`

- [x] Trio CLOSED + README



```bash

docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-container python scripts/smoke_marketplace_sprint3.py

```

