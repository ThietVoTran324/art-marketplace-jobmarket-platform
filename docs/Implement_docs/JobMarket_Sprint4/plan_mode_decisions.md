# Plan mode decisions — JobMarket_Sprint4 (Phase 1.4 Apply pipeline)

> **Initiative:** JobMarket_Sprint4 — Apply + view-CV + notify + list ứng viên  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) (Plan #1 CHỐT Q1–Q63)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **chốt 2026-08-01** (quiz tech = all suggest T1–T52). **Implement CLOSED** 2026-08-01 — Alembic `f6a7b8c9d0e1`.

---

## 0. Meta

| | |
|---|---|
| Initiative | JobMarket_Sprint4 — job_applications + apply + view-CV + notify + HY-02 min |
| Stack | FastAPI + SQLAlchemy + Alembic + Postgres + Vue 3 + Celery + Redis SSE |
| Baseline Alembic head | `e5f6a7b8c9d0` |
| Hygiene | Không audit application; HY-02 SSE/mark-read ownership |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Gate: AC-01..26 (API smoke + FE Apply/view-CV/list). |
| P0-2 | Migration `down_revision = e5f6a7b8c9d0` → `f6a7b8c9d0e1`. |
| P0-3 | `sprint4_routes.py` include `/job-market`. |
| P0-4 | Không audit application. |
| P0-5 | Smoke `scripts/smoke_jobmarket_sprint4.py` → `ALL_SMOKE_PASS`. |

---

## D* — Core technical

### Schema

| ID | Quyết định |
|----|------------|
| D1 | `job_applications`: job_post_id CASCADE, applicant_user_id CASCADE, status, cover_note, cover_file_*, cv_source tab\|oneshot, source_cv_id SET NULL, cv snapshot fields, viewed_at, decided_at, timestamps. |
| D2 | Status CHECK submitted\|viewed\|rejected\|passed; cv_source CHECK tab\|oneshot. |
| D3 | Indexes (job_post_id, created_at), (applicant_user_id, job_post_id), (job_post_id, status); **partial unique** (applicant_user_id, job_post_id) WHERE status IN (submitted, viewed). |
| D4 | Apply: **copy** CV file vào `media/job_applications/{id}/`; snapshot; xóa tab CV không gãy. |
| D5 | `updates.metadata` JSONB nullable cho deep-link (job_id, application_id, username, …). |

### Limits / gates

| ID | Quyết định |
|----|------------|
| D6 | cover_note max 4000; MIME pdf/doc/docx; 5 MiB cover + oneshot (= CV_MAX_BYTES). |
| D7 | Email non-empty + verified; org → 403 org_cannot_apply; JD+company active. |
| D8 | XOR cv_id \| cv file; duplicate/passed/rejected rules → 409 codes. |

### API

| ID | Quyết định |
|----|------------|
| D9 | `POST /jobs/{id}/apply` multipart. |
| D10 | `GET /jobs/{id}` thêm `my_application` (đơn mới nhất caller). |
| D11 | `GET /me/job-posts/{id}/applications` owner; sort created_at DESC. |
| D12 | `POST …/applications/{id}/reject` \| `…/pass`; terminal 409; closed JD vẫn được. |
| D13 | `GET /applications/{id}/cv-view`; `…/cv/file`; `…/cover/file`. |
| D14 | First successful cv-view or cv/file → submitted→viewed + notify. |
| D15 | Helpers assert_application_company_owner. |

### Notify + HY-02

| ID | Quyết định |
|----|------------|
| D16 | Celery email templates; updates types job_application_*; Redis publish best-effort. |
| D17 | SSE stream require auth + path user_id == session; mark-read + get-by-id ownership. |

### FE

| ID | Quyết định |
|----|------------|
| D18 | JobDetail Apply modal; badge my_application; route `/applications/:id/cv`. |
| D19 | ManageJobsTab: list applicants + reject/pass + links. |
| D20 | Explore không Apply thẳng. |

### Prove

| ID | Quyết định |
|----|------------|
| D21 | smoke_jobmarket_sprint4.py covers AC chính. |
| D22 | Quiz tech all suggest T1–T52. |

---

## Out of scope (tech)

- Status history table; withdraw; all-my-apps; interview; chat–application; audit.
