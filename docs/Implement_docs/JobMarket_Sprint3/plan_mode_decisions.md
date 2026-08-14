# Plan mode decisions — JobMarket_Sprint3 (Phase 1.3)

> **Initiative:** JobMarket_Sprint3 — Explore JD + quản lý JD  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) (Plan #1 CHỐT 2026-08-01)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **chốt 2026-08-01** (quiz tech = all suggest). **Implement CLOSED** 2026-08-01 — Alembic `e5f6a7b8c9d0`.

---

## 0. Meta

| | |
|---|---|
| Initiative | JobMarket_Sprint3 — job_posts + Explore + JD detail + org tabs Đang tuyển / Quản lý JD |
| Stack | FastAPI + SQLAlchemy + Alembic + Postgres + Vue 3 + Pinia |
| Baseline Alembic head | `d4e5f6a7b8c9` |
| Hygiene | Không mở audit JD (BR out); ownership company/JD |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Gate: AC-01..15 chứng minh được (API smoke + FE thủ công Explore/detail/tabs). |
| P0-2 | Migration mới `down_revision = d4e5f6a7b8c9` → head mới (ví dụ `e5f6a7b8c9d0`). |
| P0-3 | Mở rộng `app/api/rest/job_market/`: file `sprint3_routes.py` (bare router) `include` từ `routes.py` giống Sprint2 — **không** package `/jobs` riêng. |
| P0-4 | **Không** mở rộng `audit_logs` action cho JD (T18). |
| P0-5 | Prove-done: `scripts/smoke_jobmarket_sprint3.py` → `ALL_SMOKE_PASS` + FE thủ công. |

---

## D* — Core technical

### Schema

| ID | Quyết định |
|----|------------|
| D1 | Bảng `job_posts`: `id`, `company_id` FK CASCADE, `title` String(200), `years_experience` Integer, `description` Text nullable, `requirements` Text nullable, `benefits` Text nullable, `salary_mode` String(20), `salary_min` Integer nullable, `salary_max` Integer nullable, `currency` String(3) default `VND`, `status` String(20) default `active`, `created_at` / `updated_at` timestamptz. Index `(company_id, status)`, `(status, created_at)`. |
| D2 | `salary_mode` CHECK IN (`love_it`, `range`). `currency` CHECK IN (`VND`, `USD`). `status` CHECK IN (`active`, `closed`). `years_experience` CHECK `>= 0`. |
| D3 | App validate: `love_it` → `salary_min`/`salary_max` phải null; `range` → ít nhất một trong min/max; nếu cả hai thì `max >= min`. Currency luôn set (default VND). |
| D4 | Bảng `job_post_locations`: `id`, `job_post_id` FK CASCADE, `source_branch_id` Integer nullable (FK `company_branches.id` ON DELETE SET NULL), snapshot `label` String(100) nullable, `address_line` String(300), `city` String(100) nullable, `country` String(10) nullable, `created_at`. Index `(job_post_id)`. |
| D5 | Tạo/PATCH locations: client gửi `branch_ids: int[]` (≥1); server đọc branches của **company owner**, copy snapshot; thay toàn bộ set location khi PATCH locations. |

### API

| ID | Quyết định |
|----|------------|
| D6 | Owner: `GET/POST /job-market/me/job-posts`; `GET/PATCH /job-market/me/job-posts/{id}`; `POST …/{id}/close`; `POST …/{id}/reopen`. Gate: `employer` + owned active company; 403 nếu không. |
| D7 | Close → `status=closed`; reopen → `status=active`. PATCH body không đổi status (chỉ close/reopen endpoints). |
| D8 | Đang tuyển: `GET /job-market/companies/{company_id}/job-posts` — default/query `status=active` (public-to-login). |
| D9 | Explore: `GET /job-market/explore/jobs` — require login; chỉ `active`; sort `created_at DESC`, `id DESC`. Query: `q` (title + company display_name ILIKE); `years_min` / `years_max` (filter `years_experience`); `salary_min` / `salary_max` (kích hoạt filter lương); `currency` optional (nếu có thì chỉ match JD cùng currency); `location` (ILIKE trên snapshot address_line/city/label). |
| D10 | Filter lương: nếu request có `salary_min` và/hoặc `salary_max` → `salary_mode = 'range'` + overlap với khoảng JD; **loại** `love_it`. Không có salary filter params → gồm cả `love_it`. |
| D11 | Detail: `GET /job-market/jobs/{id}` — login required. `active` → 200 mọi user login. `closed` → **404** non-owner; **200** nếu caller là owner company của JD. |
| D12 | Ownership helpers: `assert_job_post_company_owner` (404/403 pattern Sprint2). |
| D13 | Validation thiếu title/years/locations/salary_mode → 422/400 body rõ. |

### FE

| ID | Quyết định |
|----|------------|
| D14 | Routes: `/explore` (list), `/jobs/:id` (detail); Aside `RouterLink` Explore (icon PrimeIcons). |
| D15 | `UserView` org: tab **Đang tuyển** (mọi viewer khi `account_kind===organization`); tab **Quản lý JD** chỉ `isOwner`. Components dưới `vuejs/src/components/Auth/JobMarket/`. |
| D16 | Form JD: multi-select branches từ `GET /job-market/companies/{id}/branches` (hoặc list branches owner đã có); submit `branch_ids`. |
| D17 | JD detail: nút Apply disabled + text “Coming next”. |
| D18 | Explore UI: search + filter popup (years, salary range, location text); currency optional trong filter lương nếu gửi. |

### Prove / hygiene

| ID | Quyết định |
|----|------------|
| D19 | Smoke `scripts/smoke_jobmarket_sprint3.py` cover AC chính (owner CRUD/close/reopen; 403; explore filters; love_it excluded; closed detail 404 non-owner; company active list). |
| D20 | Không audit JD actions Sprint3. |

---

## Out of scope (tech)

- Apply / applications tables / notify / view-CV  
- Draft status; soft-delete JD  
- Audit HY-05 JD  
- Ranking / recommendation  

---

## Trace → checklist

Mọi D* / P0* map step trong `devplan_checklist.md` (P0–P8). Implement **chỉ** sau khi checklist tồn tại và user bắt đầu implement.
