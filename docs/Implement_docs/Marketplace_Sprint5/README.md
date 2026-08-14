# Marketplace_Sprint5 — CLOSED

**CLOSED** 2026-08-08 · Alembic **`b4c5d6e7f8a9`** · smoke `ALL_SMOKE_PASS`

| File | Role |
|------|------|
| [PLANNING_TRIO.md](PLANNING_TRIO.md) | Index |
| [business_requirement.md](business_requirement.md) | Plan #1 BR |
| [plan_mode_decisions.md](plan_mode_decisions.md) | Plan #2 tech |
| [devplan_checklist.md](devplan_checklist.md) | Checklist CLOSED |

## Shipped

- Listing attestation (`seller-rights-v1`)
- `pins.content_sha256` via Celery preview pipeline
- Copyright reports + `/admin/copyright-reports`
- `license_certificates` on paid; PinView certificate + report UI

## Marketplace Phase 2.x

Sprint0–5 implement **CLOSED**. Next work = ops/product backlog outside this phase map (VNPay, auto payout, Admin UI, etc.).

## Security Type 2 (defer — làm kèm sau)

Từ audit 2026-08-08 — **không** fix trong Sprint5 CLOSED:

| ID | Việc | Khi nào |
|----|------|---------|
| T2-01 | Resolve copyright → unlist / revoke license | Admin moderation product |
| T2-02 | Rate-limit tạo copyright report | Hardening |
| T2-08 | Admin UI queue copyright | ADM-* |

SSOT phân loại: [`../../Planing_docs/security_followups_type1_type2.md`](../../Planing_docs/security_followups_type1_type2.md).
