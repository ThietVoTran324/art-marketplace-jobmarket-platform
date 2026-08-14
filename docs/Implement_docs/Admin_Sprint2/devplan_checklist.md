# Dev plan checklist — Admin_Sprint2 (Phase 3.2 JM ops)

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Prerequisite:** Admin_Sprint1 CLOSED · head `b4c5d6e7f8a9`  
**Trạng thái:** **CLOSED** 2026-08-11 · smoke `ALL_SMOKE_PASS` · no new Alembic

---

## P0 — Docs

- [x] Plan #1 CHỐT
- [x] Plan #2 CHỐT (Q1–Q8 A)

---

## P1 — Backend

- [x] `GET /job-market/admin/hiring-rights-requests/{id}/documents`

---

## P2 — FE

- [x] Router + AdminNav JM links
- [x] AdminKycView
- [x] AdminCredentialsView
- [x] AdminJobReportsView
- [x] Overview deep-link KYC / JD

---

## P3 — Smoke + đóng

- [x] `scripts/smoke_admin_sprint2.py` → `ALL_SMOKE_PASS`
- [x] Trio CLOSED + Planing sync

## Manual FE (optional)

- [ ] `/admin/kyc` decide + open doc
- [ ] `/admin/credentials` CRUD
- [ ] `/admin/job-reports` dismiss + suspend
