# Plan mode decisions — JobMarket_Sprint1 (Phase 1.1)

> **Initiative:** JobMarket_Sprint1 — Artist foundation  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) (Plan #1 DONE)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **chốt 2026-07-26** — được implement theo checklist.

---

## 0. Meta

| | |
|---|---|
| Initiative | JobMarket_Sprint1 — Artist tabs + work-exp + CV + education admin |
| Profile Core | Schema + API + UserView tabs + Settings stub + roles hydrate |
| Profile Extend | Admin UI education; company suggest; approve/notify |
| Stack | FastAPI + SQLAlchemy + Alembic + Postgres + Vue 3 + Pinia |
| Baseline Alembic head | `b2c3d4e5f6a7` |
| Hygiene in-sprint | HY-06 (roles FE); HY-01 (avatar/banner ownership) khi đụng upload |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Gate Core: AC-01..12 chứng minh được (API smoke + FE thủ công tối thiểu tabs/stub/roles) |
| P0-2 | Migration mới revise `b2c3d4e5f6a7`; Docker `alembic upgrade head` trước prove-done |
| P0-3 | Router domain mới `app/api/rest/job_market/` (work_exp, education, cvs) + include trong `main.py`; không nhồi hết vào `users/routes.py` |
| P0-4 | Sprint1 **không** mở rộng `audit_logs` action CHECK (HY-05 để sprint trust/KYC/approve) |
| P0-5 | Settings **chưa có** → thêm route Vue `/settings` tối thiểu (stub hiring-rights only); link từ Aside |

---

## D* — Core technical

### Schema

| ID | Quyết định |
|----|------------|
| D1 | Bảng `work_experiences`: `id`, `user_id` FK CASCADE, `company_name` String(200), `employment_type` String(50), `title` String(200), `location` String(200) nullable, `start_date` Date, `end_date` Date nullable, `status` String(20) default `pending`, `created_at` / `updated_at` timestamptz. Index `(user_id, start_date)`. |
| D2 | `employment_type` CHECK IN (`full-time`,`part-time`,`hybrid`,`outsourcing`,`collaborator`). `status` CHECK IN (`pending`,`approved`). App luôn set `pending` khi create/update Sprint1 (không API approve). |
| D3 | **Không** cột `company_id` Sprint1 — chỉ free-text `company_name`. |
| D4 | Bảng **một** `profile_credentials`: `id`, `user_id` FK CASCADE, `kind` CHECK IN (`education`,`licensing`,`award`), `title` String(200), `organization` String(200) nullable, `occurred_on` Date nullable, `description` String(400) nullable, `created_at` / `updated_at`. Index `(user_id, kind)`. |
| D5 | Bảng `user_cvs`: `id`, `user_id` FK CASCADE, `original_filename` String(255), `stored_name` String(255) (relative path kiểu `cvs/{user_id}/{uuid}.ext`), `content_type` String(100), `size_bytes` Integer, `created_at`. Index `(user_id)`. Quota max **3** enforce ở app (count trước insert). |
| D6 | CV storage: `{MEDIA_PATH}/cvs/{user_id}/` + `save_file`; xóa DB row **và** file trên disk. |
| D7 | CV allowlist: extensions `.pdf`, `.doc`, `.docx`; content-types tương ứng `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`. **Size cap 5 MiB** (đọc stream, reject nếu vượt). |

### API

| ID | Quyết định |
|----|------------|
| D8 | Work-exp public: `GET /job-market/users/{user_id}/work-experiences` — list sort `start_date ASC`, `id ASC` tie-break. Auth optional theo pattern profile hiện có: **require login** giống các GET user khác nếu app đang auth-gate profile (khớp `user_id` dep hiện hành trên user routes). |
| D9 | Work-exp owner: `POST/PATCH/DELETE /job-market/me/work-experiences[/{id}]` — `user_id` từ JWT; PATCH/DELETE 404 nếu không tồn tại hoặc không thuộc owner (không lộ cross-user). |
| D10 | Validation work-exp: `end_date >= start_date` nếu `end_date` set; `employment_type`/`status` theo CHECK; create luôn `status=pending`; reject PATCH cố đổi `status` sang `approved` từ non-admin (Sprint1: **ignore/forbid status write** — client không set status). |
| D11 | Credentials public: `GET /job-market/users/{user_id}/credentials` (optional `?kind=`). |
| D12 | Credentials mutate: **owner** `POST/PATCH/DELETE /job-market/me/credentials[/{id}]`; admin override giữ `/job-market/admin/users/{user_id}/credentials…`. **Corr 2026-07-27.** |
| D13 | CV owner: `GET/POST /job-market/me/cvs`; `DELETE /job-market/me/cvs/{id}`; `GET /job-market/me/cvs/{id}/file` (download). Non-owner → 403/404 theo ownership helper. |
| D14 | Email gate upload CV: nếu `UsersOrm.email` null/blank → **400** body rõ (`email_required`); `verified` **không** bắt buộc Sprint1. |
| D15 | Ownership helpers mới trong `ownership.py` (hoặc module job_market): `assert_work_exp_owner`, `assert_cv_owner`. |

### FE

| ID | Quyết định |
|----|------------|
| D16 | Mở rộng `authUserStore`: `roles: string[]` + `setRoles` / `hasRole(role)`; hydrate trong `Auth.vue` (cùng lúc load me): `GET /api/users/me/roles`. |
| D17 | `CommentSection.vue`: thay `authUsername == 'danya'` bằng `hasRole('admin')`. |
| D18 | `UserView.vue`: thêm tabs **Experience** / **Credentials** / **CV** (CV chỉ khi `me.id === profileUser.id`); giữ Created/Saved/Liked/Boards. Components mới dưới `vuejs/src/components/Auth/JobMarket/`. |
| D19 | Route `SettingsView.vue` tại `/settings`; Aside link “Settings”. Nội dung Sprint1: stub card “Request hiring rights” disabled + “Coming next”. |
| D20 | Aside + UserView + Settings: đọc `roles` từ store (AC-12); không gọi roles API lẻ tẻ mỗi tab nếu Auth đã hydrate. |

### Hygiene

| ID | Quyết định |
|----|------------|
| D21 | HY-01: `POST /users/upload/{id}` và banner upload — require JWT + `id == current_user_id` (403 nếu khác). |

---

## Out of scope (tech)

- `companies` / suggest endpoint / `company_id` FK  
- Approve work-exp API + notify + audit actions mới  
- Employer CV read / apply  
- Admin UI Vue cho credentials  
- OR-semantics `require_roles` (HY-04)  
- Soft-delete CV / virus scan  

---

## Trace → checklist

Mọi D* / P0* map step trong `devplan_checklist.md` (P0–P7). Implement **chỉ** sau khi checklist tồn tại (file này + checklist = Plan #2 DONE).
