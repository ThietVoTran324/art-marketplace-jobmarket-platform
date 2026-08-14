# Plan mode decisions — Admin_Sprint1 (Phase 3.1 Core shell)

> **Initiative:** Admin shell + roles + audit + content + overview counts  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) — Plan #1 CHỐT (S3B)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-08** — `all suggest` Q1–Q9 A.

---

## 0. Meta

| | |
|---|---|
| Baseline Alembic | `b4c5d6e7f8a9` |
| Migration Sprint1 | **Không** — COUNT trên bảng sẵn |
| Quiz | Q1–Q9 **A** |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Nested `/admin` layout + children |
| P0-2 | `meta.requiresAdmin` + router `beforeEach` (fetch roles nếu store rỗng) → redirect `/` |
| P0-3 | `GET /admin/overview` một response counts |
| P0-4 | Metrics: `audit_events_24h`, `open_copyright_reports`, `open_job_reports`, `open_kyc_requests` |
| P0-5 | Roles/Audit/Content dùng API hiện có; Content = confirm modal + DELETE |
| P0-6 | FE: `views/admin/*` + `components/Admin/*` |
| P0-7 | Smoke API + checklist manual FE |

---

## D* — Core

| ID | Quyết định |
|----|------------|
| D1 | `GET /admin/overview` → `AdminOverviewOut` (4 int counts); `require_roles("admin")` |
| D2 | `open_kyc_requests` = status `pending` \| `need_more_info` trên `company_verification_requests` |
| D3 | `open_job_reports` = `job_post_reports.status = open` |
| D4 | `open_copyright_reports` = `copyright_reports.status = open` |
| D5 | `audit_events_24h` = `audit_logs.created_at >= now()-24h` |
| D6 | Routes FE: `/admin`, `/admin/roles`, `/admin/audit`, `/admin/content` |
| D7 | Aside: link Admin chỉ khi `hasRole('admin')` |
| D8 | Roles UI: user id + assign/revoke `admin|artist|employer|seller`; cấm self (API 403) |
| D9 | Audit UI: filters actor_user_id, action, target_type, target_id, date_from, date_to, limit, offset |
| D10 | Content: form pin_id / comment_id + confirm → DELETE |
| D11 | Nav JM/MP: disabled “Soon” trong Admin layout |
| D12 | `scripts/smoke_admin_sprint1.py` |

---

## Out of scope

Queue KYC/JD/copyright UI · unlist · work-exp list · payment admin · migration schema
