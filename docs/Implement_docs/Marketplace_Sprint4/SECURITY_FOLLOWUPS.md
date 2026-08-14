# Security / hardening notes — Marketplace_Sprint4 (CLOSED)

Sprint4 payment đã ship. **Type 1** payment defaults đã harden 2026-08-08 (`DEV_MODE`+mock gate, webhook fail-closed).

## Type 2 (defer)

| ID | Việc | Khi nào |
|----|------|---------|
| T2-07 | VNPay · auto bank payout · chargeback automation | Post-Sprint4 / payment expand |
| T2-03 | Tách `PIN_MEDIA_SIGNING_SECRET` (media ACL liên quan download sau paid) | Media hardening |

Xem [`../../Planing_docs/security_followups_type1_type2.md`](../../Planing_docs/security_followups_type1_type2.md).
