# Dev plan checklist — Marketplace_Sprint4 (Phase 2.4 Order + SePay)

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Prerequisite:** Sprint3 CLOSED (`f2a3b4c5d6e7`)  
**Trạng thái:** **CLOSED** 2026-08-08 · Alembic `a3b4c5d6e7f8` · smoke `ALL_SMOKE_PASS`

**Baseline → target:** `f2a3b4c5d6e7` → `a3b4c5d6e7f8`

---

## P0 — Baseline

- [x] `alembic current` = `f2a3b4c5d6e7` (pre-upgrade)

---

## P1 — Schema + config

- [x] Models `pin_orders`, `payment_events`; FK `pin_license_access.order_id`
- [x] Alembic `a3b4c5d6e7f8`
- [x] Settings: TTL, USD rate, SePay mock/secret/base URL + `.env.example`

---

## P2 — Orders + SePay API

- [x] Create/reuse pending order + charge_vnd + payment_code
- [x] Gates: verified / self-buy / already owned / listed
- [x] Webhook idempotent + HMAC optional + CSRF exempt
- [x] Mock paid endpoint (mock mode)
- [x] Grant access + emails
- [x] purchase-state + get order

---

## P3 — Celery TTL

- [x] Beat task cancel expired pending

---

## P4 — FE PinView

- [x] Buy / pending / owned; open payment_url; mock pay (dev)

---

## P5 — Smoke + đóng

- [x] `scripts/smoke_marketplace_sprint4.py` → `ALL_SMOKE_PASS`
- [x] Trio CLOSED + README + Planing_docs sync

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-container python scripts/smoke_marketplace_sprint4.py
```
