# Marketplace_Sprint4 — CLOSED

**CLOSED** 2026-08-08 · Alembic **`a3b4c5d6e7f8`** · smoke `ALL_SMOKE_PASS`

| File | Role |
|------|------|
| [PLANNING_TRIO.md](PLANNING_TRIO.md) | Index |
| [business_requirement.md](business_requirement.md) | Plan #1 BR |
| [plan_mode_decisions.md](plan_mode_decisions.md) | Plan #2 tech (Q1–Q6 A + T2) |
| [devplan_checklist.md](devplan_checklist.md) | Checklist CLOSED |

## Shipped

- `pin_orders` + `payment_events`; grant via `pin_license_access`
- SePay webhook (HMAC optional) + `MP_SEPAY_MOCK` paid endpoint
- USD→VND charge (`MP_USD_TO_VND_RATE`); commission snapshot; no auto payout
- Celery beat cancel expired pending
- PinView Buy / pending / owned + mock pay

## Next

[`../Marketplace_Sprint5/`](../Marketplace_Sprint5/) — Copyright report + certificate
