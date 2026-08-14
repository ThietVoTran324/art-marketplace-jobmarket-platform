# Dev plan checklist — JobMarket_Sprint2 (Company + hiring-rights KYC)

**Initiative:** JobMarket_Sprint2 — Phase 1.2 Company + hiring-rights KYC  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 chốt 2026-07-27)  
**SSOT kỹ thuật:** [plan_mode_decisions.md](plan_mode_decisions.md) + bảng T dưới đây  
**Phase map / sprint map:** Planing_docs job_market  
**Gate vào:** Sprint1 CLOSED ✅ · BR Sprint2 hoàn thiện ✅ · Plan #2 decisions chốt ✅  
**Trạng thái:** **CLOSED** 2026-07-28 — implement + smoke `scripts/smoke_jobmarket_sprint2.py` → `ALL_SMOKE_PASS`. Alembic head `d4e5f6a7b8c9`.

---

## Quy ước

- Chỉ tick `[x]` khi có prove-done runtime (hoặc verify ghi rõ).
- Hard stop: step hiện tại chưa pass → không sang step sau.
- Không mở scope Sprint3+ (JD, Explore, apply) hay Marketplace.

---

## Quyết định kỹ thuật đã chốt (T1–T18)

| ID | Quyết định | Map |
|----|------------|-----|
| T1 | 4 bảng: `companies`, `company_branches`, `company_verification_requests`, `company_verification_documents` | D7–D15 |
| T2 | Legal unique `(country, authority, type, normalized)`; authority default `NATIONAL`; soft-delete không giải phóng key | D8–D10 |
| T3 | Multi-pending cùng `company_id`; approve atomic + auto-reject siblings | D14, D19–D23 |
| T4 | Org identity computed (`employer` + owned active company); hydrate `account_kind` / `company_id` trên `/users/me` | D1–D3 |
| T5 | Artist data giữ DB; FE ẩn JM artist tabs khi org; public artist lists → `[]` | D4–D6 |
| T6 | KYC docs private `MEDIA_PATH/kyc/{request_id}/`; PDF/JPG/PNG; 15 MiB; max 5/nhóm; max 15/request | D15–D17 |
| T7 | Normalize registration number helper | D18 |
| T8 | Email confirm in-scope; approve chặn nếu chưa confirm | D24–D27 |
| T9 | Router mở rộng `/job-market` (KYC me + admin + company + confirm) | D28–D32, P0-3 |
| T10 | Ownership: `assert_kyc_request_owner`, `assert_company_owner` | D33 |
| T11 | Submit: verified email; `business_registration_document` bắt buộc; translation nếu không English | D24, D34 |
| T12 | Name/domain trùng → `warnings` only | D31 |
| T13 | HY-05: `kyc_submit` / `kyc_approve` / `kyc_reject` / `kyc_need_more_info` | D35–D37, P0-4 |
| T14 | Admin API-only (không Admin UI) | P0-5 |
| T15 | FE Settings KYC thật; UserView Company tab khi org | D38–D41 |
| T16 | Alembic `c3d4e5f6a7b8` → head mới Sprint2 | P0-2 |
| T17 | Smoke `scripts/smoke_jobmarket_sprint2.py` | P0-6 |
| T18 | Grant `employer` qua `assign_role` + audit `role_assign` sẵn có | D3 |

**Baseline migration head:** `c3d4e5f6a7b8` → **head sau sprint:** `d4e5f6a7b8c9` (`add job market sprint2 companies kyc tables`).

---

## P0 — Runtime baseline

- [x] Docker stack healthy; `alembic current` = `c3d4e5f6a7b8` (pre-upgrade)
- [x] Sprint1 smoke vẫn pass: `scripts/smoke_jobmarket_sprint1.py` → `ALL_SMOKE_PASS` (post-Sprint2 regression)

### Guide

- Không sửa domain KYC/company ở P0.
- Regression fail → sửa trước khi thêm bảng Sprint2.

---

## P1 — Schema + migration (T1–T2, T16)

- [x] Models trong `app/postgresql/models.py`:
  - [x] `CompaniesOrm` (+ CHECK status; unique legal key)
  - [x] `CompanyBranchesOrm`
  - [x] `CompanyVerificationRequestsOrm` (+ CHECK status)
  - [x] `CompanyVerificationDocumentsOrm` (+ CHECK doc_type)
- [x] Partial unique owner (1 company / owner_user_id khi not null)
- [x] Alembic revision `d4e5f6a7b8c9`; widen audit CHECK cùng revision (T13)
- [x] `alembic upgrade head` sạch

+ Verify: migration applied; head `d4e5f6a7b8c9`.

---

## P2 — Normalize + ownership + constants + schemas (T7, T10)

- [x] `normalize_registration_number(raw)`
- [x] Helpers: `assert_kyc_request_owner`, `assert_company_owner`
- [x] `resolve_account_kind(user_id)`
- [x] Constants + Pydantic schemas Sprint2

+ Verify: smoke + imports OK.

---

## P3 — KYC submit + docs API (T3, T6, T9, T11)

- [x] `GET/POST /job-market/me/hiring-rights-requests`
- [x] Conflict rules + multi-pending
- [x] Docs upload/list/delete/download owner
- [x] Preconditions 400 codes
- [x] `write_audit` `kyc_submit`

+ Verify: smoke multi-pending / ownership / preconditions.

---

## P4 — Company email confirm (T8)

- [x] Template `mail_company_email_confirm.html`
- [x] Celery send after submit
- [x] `GET /job-market/kyc/confirm-email/{token}`
- [x] Resend confirm endpoint

+ Verify: smoke approve blocked until confirm; token confirm works.

---

## P5 — Admin decide + approve atomic (T3, T14, T18)

- [x] Admin list / need-more-info / reject / approve
- [x] Auto-reject siblings; assign employer
- [x] Non-admin 403; unconfirmed approve 400

+ Verify: smoke approve atomic + roles.

---

## P6 — Company profile API + warnings (T4, T12)

- [x] `/users/me` `account_kind` / `company_id`
- [x] Company GET/PATCH + branches CRUD
- [x] Public artist lists for org → `[]`

+ Verify: smoke account_kind + mutate gate + empty lists.

---

## P7 — Audit HY-05 (T13)

- [x] VALID_ACTIONS + CHECK 4 KYC actions
- [x] Targets KYC/company
- [x] Smoke assert audit rows

---

## P8 — Vue FE (T15)

- [x] `authUserStore` account_kind / companyId
- [x] Settings KYC form
- [x] CompanyProfileTab + UserView org switch

+ Verify: FE shipped; API smoke covers AC; FE thủ công Settings/UserView khi cần.

---

## P9 — Smoke + đóng sprint

- [x] Script `scripts/smoke_jobmarket_sprint2.py` → `ALL_SMOKE_PASS`
- [x] Alembic head `d4e5f6a7b8c9` ghi checklist
- [x] Cập nhật PLANNING_TRIO / job_market README / sprint_map

---

## AC ↔ step map

| AC | Step chứng minh |
|----|-----------------|
| AC-01 | P3 preconditions |
| AC-02 | P3 reuse candidate / no spawn |
| AC-03 | P3 multi-pending + P5 admin choose |
| AC-04 | P3 active block |
| AC-05 | P3 reject reuse |
| AC-06 | P3 doc ownership |
| AC-07 | P5 docs/translation gate on approve |
| AC-08 | P5 approve grant + org |
| AC-09 | P5 admin API / non-admin 403 |
| AC-10 | P6 company mutate 403 |
| AC-11 | P6 warnings (API) |
| AC-12 | P3/P5/P7 audit |
| AC-13 | P8 Settings |
| AC-14 | P4 email confirm |
| AC-15 | P6 + P8 UserView org |

---

> **CLOSED 2026-07-28.** Prove-done: `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_jobmarket_sprint2.py` → `ALL_SMOKE_PASS`.
