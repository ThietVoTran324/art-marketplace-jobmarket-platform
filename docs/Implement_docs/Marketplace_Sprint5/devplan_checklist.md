# Dev plan checklist — Marketplace_Sprint5 (Phase 2.5 Copyright)

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Prerequisite:** Sprint4 CLOSED (`a3b4c5d6e7f8`)  
**Trạng thái:** **CLOSED** 2026-08-08 · Alembic `b4c5d6e7f8a9` · smoke `ALL_SMOKE_PASS`

**Baseline → target:** `a3b4c5d6e7f8` → `b4c5d6e7f8a9`

---

## P0 — Baseline

- [x] `alembic current` = `a3b4c5d6e7f8` (pre-upgrade)

---

## P1 — Schema + config

- [x] `pins.content_sha256`; listing attestation cols; `copyright_reports`; `license_certificates`
- [x] Alembic `b4c5d6e7f8a9`
- [x] `MP_ATTESTATION_VERSION` + `.env.example`

---

## P2 — Hash + listing attest + certificate on paid

- [x] Celery `generate_pin_preview` writes SHA-256
- [x] List/relist requires attestation
- [x] Certificate row on paid

---

## P3 — Report + admin API

- [x] User create report
- [x] Admin list + resolve/dismiss

---

## P4 — FE PinView

- [x] Attest checkbox; report; certificate when owned

---

## P5 — Smoke + đóng

- [x] `scripts/smoke_marketplace_sprint5.py` → `ALL_SMOKE_PASS`
- [x] Trio CLOSED + Planing_docs sync
