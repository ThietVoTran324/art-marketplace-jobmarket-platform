# Dev plan checklist — JobMarket_Sprint1 (Artist foundation)

**Initiative:** JobMarket_Sprint1 — Phase 1.1 Artist foundation  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 chốt 2026-07-26)  
**SSOT kỹ thuật:** [plan_mode_decisions.md](plan_mode_decisions.md) + bảng T dưới đây  
**Phase map / sprint map:** Planing_docs job_market  
**Gate vào:** Phase 0 CLOSED ✅ · BR Sprint1 hoàn thiện ✅ · Plan #2 decisions chốt ✅  
**Trạng thái:** **CLOSED** 2026-07-26 — implement + smoke `scripts/smoke_jobmarket_sprint1.py` → `ALL_SMOKE_PASS`. Alembic head `c3d4e5f6a7b8`.

---

## Quy ước

- Chỉ tick `[x]` khi có prove-done runtime (hoặc verify ghi rõ).
- Hard stop: step hiện tại chưa pass → không sang step sau.
- Không mở scope Sprint2+ (KYC, JD, apply, approve notify).

---

## Quyết định kỹ thuật đã chốt (T1–T14)

| ID | Quyết định | Map |
|----|------------|-----|
| T1 | 3 bảng: `work_experiences`, `profile_credentials` (kind), `user_cvs` | D1–D5 |
| T2 | Work-exp: free-text company; status default `pending`; no approve API | D2–D3, D10 |
| T3 | Credentials: một bảng + `kind`; **owner CRUD** + admin override API | D4, D11–D12 |
| T4 | CV: max 3; PDF/DOC/DOCX; **5 MiB**; disk dưới `MEDIA_PATH/cvs/{user_id}/` | D5–D7 |
| T5 | Router prefix `/job-market` module mới + `main.py` include | P0-3 |
| T6 | List work-exp sort `start_date ASC`, `id ASC` | D8 |
| T7 | Email gate: `email` null/blank → 400 `email_required` (không cần verified) | D14 |
| T8 | Forbid client write `status=approved` trên work-exp Sprint1 | D10 |
| T9 | Không mở rộng audit action CHECK (HY-05 sau) | P0-4 |
| T10 | FE: Pinia roles hydrate; bỏ hardcode `danya` admin UI | D16–D17 |
| T11 | UserView tabs Experience / Credentials / CV(owner); pins giữ | D18 |
| T12 | Vue `/settings` stub hiring-rights; link Aside | D19, P0-5 |
| T13 | HY-01: avatar/banner upload ownership = JWT user | D21 |
| T14 | Alembic down_revision `b2c3d4e5f6a7` → head mới Sprint1 | P0-2 |

**Baseline migration head:** `b2c3d4e5f6a7` → **head sau sprint:** `c3d4e5f6a7b8` (`add job market sprint1 tables`).

---

## P0 — Runtime baseline

- [x] Docker stack healthy; `alembic current` = `b2c3d4e5f6a7`
- [x] Phase0 smoke (Sprint1–3) vẫn pass nếu còn script

### Guide

- Không sửa domain JM ở P0.
- Regression fail → sửa trước khi thêm bảng JM.

---

## P1 — Schema + migration (T1–T2, T14)

- [x] Models trong `app/postgresql/models.py`:
  - [x] `WorkExperiencesOrm` (+ CHECK employment_type, status)
  - [x] `ProfileCredentialsOrm` (+ CHECK kind)
  - [x] `UserCvsOrm`
- [x] Alembic revision mới (indexes theo plan_mode_decisions)
- [x] `alembic upgrade head` sạch; downgrade drop 3 tables

+ Verify: `\d work_experiences` / credentials / user_cvs trên Postgres.

### Guide

- Date columns: SQLAlchemy `Date` (không DateTime) cho start/end/occurred_on.
- `status` / `kind` / `employment_type`: DB CHECK + validate Pydantic.

---

## P2 — Ownership helpers + schemas + router skeleton (T5)

- [x] Helpers: `assert_work_exp_owner`, `assert_cv_owner` (404 nếu missing; 403 nếu sai owner — chọn **404** cho cross-user id để không leak, thống nhất với pin pattern nếu pin dùng 403 thì ghi rõ và giữ 403 “not owner”)
- [x] Pydantic schemas request/response gọn (không nhồi BR)
- [x] Package `app/api/rest/job_market/` với router(s); `app/main.py` `include_router`
- [x] Constants: CV max 3, 5 MiB, allowlist MIME/ext

+ Verify: app start; OpenAPI thấy prefix `/job-market`.

---

## P3 — Work-exp API (T2, T6, T8)

- [x] `GET /job-market/users/{user_id}/work-experiences` — public-to-auth users; sorted
- [x] `POST /job-market/me/work-experiences` — owner; force `pending`
- [x] `PATCH /job-market/me/work-experiences/{id}` — owner; không cho set `approved`
- [x] `DELETE /job-market/me/work-experiences/{id}` — owner
- [x] Validation `end_date >= start_date`

+ Verify: CRUD owner; visitor GET thấy status `pending`; non-owner PATCH → 403/404; sort đúng.

---

## P4 — Credentials API (T3)

- [x] `GET /job-market/users/{user_id}/credentials` (+ optional `kind`)
- [x] Owner `POST/PATCH/DELETE /job-market/me/credentials[/{id}]` (**corr 2026-07-27**)
- [x] Admin override `…/admin/users/{user_id}/credentials…` + `require_roles("admin")`
- [x] Non-owner mutate → 403

+ Verify: owner CRUD; visitor GET; non-owner PATCH 403; admin override vẫn được.

---

## P5 — CV API + email gate + disk (T4, T7)

- [x] `GET /job-market/me/cvs` — list metadata (không public)
- [x] `POST /job-market/me/cvs` — multipart; email gate; quota; type/size; save disk + row
- [x] `DELETE /job-market/me/cvs/{id}` — xóa row + file
- [x] `GET /job-market/me/cvs/{id}/file` — download owner
- [x] Non-owner list/delete/file → 403/404

+ Verify: 4th upload fail; no-email → 400; delete gỡ file; wrong user bị chặn.

---

## P6 — HY-01 avatar/banner (T13)

- [x] `POST /users/upload/{id}` và banner: JWT + `id == current_user`
- [x] Cross-user upload → 403

+ Verify: owner upload ok; user A upload vào id B → 403.

---

## P7 — Vue FE (T10–T12)

- [x] `authUserStore`: roles + `hasRole`; hydrate trong `Auth.vue` từ `/api/users/me/roles`
- [x] `CommentSection.vue`: admin UI theo `hasRole('admin')` (bỏ `danya`)
- [x] Components JobMarket: work-exp + **credentials owner CRUD** / visitor read; CV list upload delete (owner) + email CTA
- [x] `UserView.vue`: tabs Experience / Credentials / CV (CV owner-only)
- [x] `SettingsView.vue` + router `/settings` + Aside link; stub hiring-rights disabled
- [x] Aside / UserView / Settings dùng roles từ store

+ Verify thủ công: tabs hoạt động; visitor không thấy quản lý CV; Settings stub; admin comment delete vẫn hiện với user có role admin.

---

## P8 — Smoke + đóng sprint

- [x] Script `scripts/smoke_jobmarket_sprint1.py` (hoặc tương đương): work-exp CRUD/sort/status; credentials admin vs 403; CV quota/email/ownership; HY-01 403
- [x] Ghi Alembic head mới vào checklist header
- [x] Cập nhật PLANNING_TRIO / job_market README: Sprint1 implement CLOSED khi pass

### Guide

- CSRF: smoke dùng cookie + CSRF header như Phase0 scripts nếu `DEV_MODE`/interceptor yêu cầu.
- Không merge Marketplace / company tables.

---

## AC ↔ step map

| AC | Step chứng minh |
|----|-----------------|
| AC-01 | P7 tabs |
| AC-02 | P3 + P7 |
| AC-03 | P3 GET visitor |
| AC-04 | P3 create pending + free-text |
| AC-05–06 | P4 |
| AC-07–10 | P5 |
| AC-11 | P7 Settings |
| AC-12 | P7 roles hydrate |

---

> **CLOSED 2026-07-26.** Prove-done: `docker compose exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_jobmarket_sprint1.py` → `ALL_SMOKE_PASS`.
