# Dev plan checklist — Admin_Sprint1 (Phase 3.1 Core shell)

**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Prerequisite:** System Admin BR CHỐT; head `b4c5d6e7f8a9`  
**Trạng thái:** **CLOSED** 2026-08-08 · smoke `ALL_SMOKE_PASS` · no new Alembic

**Baseline:** `b4c5d6e7f8a9`

---

## P0 — Docs

- [x] Plan #1 CHỐT (S3B; rest A)
- [x] Plan #2 CHỐT (Q1–Q9 A)

---

## P1 — Backend overview

- [x] `GET /admin/overview` + schema counts
- [x] Non-admin → 403

---

## P2 — FE shell

- [x] Router nested `/admin/*` + `requiresAdmin` guard
- [x] `AdminLayout` + `AdminNav` (Overview / Roles / Audit / Content + Soon JM/MP)
- [x] Aside link Admin (role-gated)

---

## P3 — FE pages

- [x] Overview: load counts
- [x] Roles: assign/revoke by user id
- [x] Audit: list + filters
- [x] Content: delete pin/comment + confirm

---

## P4 — Smoke + đóng

- [x] `scripts/smoke_admin_sprint1.py` → `ALL_SMOKE_PASS`
- [x] Trio CLOSED + Planing sync

## Manual FE (optional)

- [ ] Login admin → Aside shield → `/admin` counts
- [ ] Non-admin URL `/admin` → redirect Home
- [ ] Roles / Audit / Content happy path in browser
