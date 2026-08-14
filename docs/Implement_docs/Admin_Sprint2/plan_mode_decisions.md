# Plan mode decisions — Admin_Sprint2 (Phase 3.2 JM ops)

> **BR:** [business_requirement.md](business_requirement.md) — Plan #1 CHỐT  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-11** — `all suggest` Q1–Q8 A.

---

## 0. Meta

| | |
|---|---|
| Baseline Alembic | `b4c5d6e7f8a9` |
| Migration | **Không** |
| Quiz | Q1–Q8 **A** |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | `GET .../admin/hiring-rights-requests/{id}/documents` |
| P0-2 | FE blob download từ admin file URL |
| P0-3 | KYC list: GET không filter → FE mặc định open statuses |
| P0-4 | Credentials list: `GET /job-market/users/{id}/credentials` |
| P0-5 | 3 views + AdminNav JM links |
| P0-6 | Overview deep-link KYC / JD |
| P0-7 | `scripts/smoke_admin_sprint2.py` |

---

## D* — Core

| ID | Quyết định |
|----|------------|
| D1 | List docs admin mirror owner list; `require_roles("admin")` |
| D2 | Routes: `/admin/kyc`, `/admin/credentials`, `/admin/job-reports` |
| D3 | Need-more: FE bắt buộc note; reject: reason bắt buộc |
| D4 | JD: dismiss/actioned + optional note; suspend/unsuspend riêng + confirm + reason |
| D5 | Nav: bỏ “Job Market · Soon”; giữ Marketplace Soon |
| D6 | Smoke: list docs, need-more, credentials CRUD, dismiss report, suspend/unsuspend |

---

## Out of scope

Copyright UI · work-exp list · ADM-05 · auto-suspend · migration
