# Plan mode decisions — JobMarket_Sprint6 (Phase 1.6)

> **Initiative:** JobMarket_Sprint6 — Trust & moderation  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) (Plan #1 CHỐT Q1–Q26)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **chốt 2026-08-03** (all suggest T1–T36). **Implement CLOSED** 2026-08-04.

---

## 0. Meta

| | |
|---|---|
| Baseline Alembic | `a7b8c9d0e1f2` → `b8c9d0e1f2a3` |
| Module | `sprint6_routes.py` include `/job-market` |
| Hygiene | Admin-only moderation; **không** HY-04 OR |
| Smoke | `scripts/smoke_jobmarket_sprint6.py` + regression gọi smoke 3/4/5 (hoặc subset gates) |

---

## P0

| ID | Quyết định |
|----|------------|
| P0-1 | Gate AC-01…13 qua smoke + FE Report. |
| P0-2 | Migration mới; mở rộng `ck_audit_logs_action`. |
| P0-3 | Không Admin UI (ADM-04). |

---

## Schema

| ID | Quyết định |
|----|------------|
| T1 | Bảng `job_post_reports`: id, job_post_id FK CASCADE, reporter_user_id FK CASCADE, reason enum, detail text nullable, status open\|dismissed\|actioned, admin_note nullable, resolved_by nullable, resolved_at nullable, timestamps. |
| T2 | Unique partial: một `(reporter_user_id, job_post_id)` khi `status = open`. |
| T3 | Index `(status, created_at)`, `(job_post_id)`. |
| T4 | `companies.status` đã có `suspended` — **không** cột flagged mới; thêm `suspend_reason` text nullable + `suspended_at` timestamptz nullable (clear khi unsuspend). |

---

## API

| ID | Quyết định |
|----|------------|
| T5 | `POST /job-market/jobs/{id}/report` — login; body reason+detail; 403 self-owner; 409 duplicate open. |
| T6 | `GET /job-market/admin/job-reports?status=open` — admin list. |
| T7 | `POST /job-market/admin/job-reports/{id}/dismiss` · `/actioned` — body note optional. |
| T8 | `POST /job-market/admin/companies/{id}/suspend` — body reason required → status suspended. |
| T9 | `POST /job-market/admin/companies/{id}/unsuspend` → active; clear reason/at. |
| T10 | Gate mutate JD (create/patch/close/reopen): company must `active`. |
| T11 | Explore list + public GET job: exclude jobs whose company `suspended` (non-owner → 404). |
| T12 | Apply: 403/422 nếu company suspended. |
| T13 | Owner GET own jobs/company vẫn được khi suspended. |
| T14 | Audit actions: `job_report_create`, `job_report_dismiss`, `job_report_actioned`, `company_suspend`, `company_unsuspend`. |
| T15 | Notify owner suspend/unsuspend: email + in-app (`company_suspended` / `company_unsuspended`); **không** notify report. |

---

## FE / Smoke

| ID | Quyết định |
|----|------------|
| T16 | `JobDetailView`: nút Report + modal enum/other. |
| T17 | Không queue admin UI — Swagger đủ. |
| T18 | Smoke: report + 409 + self-block; suspend gates explore/apply/post; unsuspend restore; audit rows; dismiss/actioned. |
| T19 | Regression: chạy `smoke_jobmarket_sprint3/4/5` (hoặc document skip nếu quá lâu — prefer chạy). |

---

## Harden

| ID | Quyết định |
|----|------------|
| T20 | Centralize CV validation helper nếu còn duplicate; không magic-byte. |
| T21 | Confirm KYC upload path vẫn allowlist — no change unless bug. |

---

## Quiz Plan #2 tóm tắt

T1–T21 all suggest như bảng trên (T22–T36 = chi tiết checklist P0–P7 mirror).
