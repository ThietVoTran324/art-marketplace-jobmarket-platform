# Dev plan checklist — JobMarket_Sprint3 (Explore JD + quản lý JD)

**Initiative:** JobMarket_Sprint3 — Phase 1.3 Explore JD + quản lý JD  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 chốt 2026-08-01)  
**SSOT kỹ thuật:** [plan_mode_decisions.md](plan_mode_decisions.md) + bảng T dưới đây  
**Phase map / sprint map:** Planing_docs job_market  
**Gate vào:** Sprint2 CLOSED ✅ · BR Sprint3 hoàn thiện ✅ · Plan #2 decisions chốt ✅  
**Trạng thái:** **CLOSED** 2026-08-01 — implement + smoke `scripts/smoke_jobmarket_sprint3.py` → `ALL_SMOKE_PASS`. Alembic head `e5f6a7b8c9d0`.

---

## Quy ước

- Chỉ tick `[x]` khi có prove-done runtime (hoặc verify ghi rõ).
- Hard stop: step hiện tại chưa pass → không sang step sau.
- Không mở scope Sprint4+ (apply, notify, view-CV, list ứng viên).

---

## Quyết định kỹ thuật đã chốt (T1–T18)

| ID | Quyết định | Map |
|----|------------|-----|
| T1 | `job_posts` + `job_post_locations` (snapshot); Alembic từ `d4e5f6a7b8c9` | D1–D5, P0-2 |
| T2 | salary_mode `love_it`\|`range`; currency VND\|USD default VND; XOR validation | D2–D3 |
| T3 | years_experience int ≥ 0; status active\|closed | D1–D2 |
| T4 | branch_ids → server snapshot; PATCH locations = replace set | D4–D5, D15 |
| T5 | Owner API `/me/job-posts` + `close` / `reopen` | D6–D7 |
| T6 | `GET /companies/{id}/job-posts` (Đang tuyển active) | D8 |
| T7 | `GET /explore/jobs` login; sort created_at DESC; search/filters | D9–D10, D16 |
| T8 | Filter lương → chỉ `range` + overlap; loại love_it | D10 |
| T9 | `GET /jobs/{id}`: active 200; closed 404 non-owner / 200 owner | D11 |
| T10 | FE `/explore` + `/jobs/:id`; Aside Explore | D14 |
| T11 | UserView: Đang tuyển (all viewers org); Quản lý JD owner-only | D15 |
| T12 | Apply button disabled + Coming next | D17 |
| T13 | Không audit JD | D20, P0-4 |
| T14 | Router `sprint3_routes.py` include `/job-market` | P0-3 |
| T15 | Smoke `smoke_jobmarket_sprint3.py` | D19, P0-5 |
| T16 | Ownership assert job post company owner | D12 |
| T17 | Optional currency query khi filter lương | D9 |
| T18 | Quiz tech 2026-08-01 = all suggest | — |

**Baseline migration head:** `d4e5f6a7b8c9` → **head sau sprint:** `e5f6a7b8c9d0`.

---

## P0 — Runtime baseline

- [x] Docker stack healthy; `alembic current` = `d4e5f6a7b8c9` (pre-upgrade)
- [x] Sprint2 smoke vẫn pass nếu chạy regression (không bắt buộc re-run khi P6 green; baseline head verified)

### Guide

- Không sửa domain JD ở P0.

---

## P1 — Schema + migration (T1–T3)

- [x] Models: `JobPostsOrm`, `JobPostLocationsOrm` (+ CHECKs)
- [x] Alembic revision mới; `alembic upgrade head`

+ Verify: `\d job_posts` / `job_post_locations`.

---

## P2 — Helpers + schemas + sprint3 router skeleton (T14, T16)

- [x] `assert_job_post_company_owner` (và resolve owned company)
- [x] Pydantic create/update/out + Explore query params
- [x] `sprint3_routes.py` + include trong `routes.py`
- [x] Constants: salary modes, currencies, statuses

+ Verify: OpenAPI thấy endpoints `/job-market/me/job-posts`, `/explore/jobs`, `/jobs/{id}`.

---

## P3 — Owner job-posts API (T4–T5)

- [x] CRUD list/create/get/patch me
- [x] branch_ids → snapshot locations; ≥1
- [x] salary XOR validation; years ≥ 0
- [x] close / reopen
- [x] Non-owner / non-employer → 403

+ Verify: create OK; missing title/years/locations → 400/422; close ẩn khỏi explore (P4); reopen OK.

---

## P4 — Explore + company list + detail (T6–T9, T17)

- [x] `GET /explore/jobs` login + filters + sort
- [x] Salary filter excludes love_it
- [x] `GET /companies/{id}/job-posts` active
- [x] `GET /jobs/{id}` active/closed rules

+ Verify: smoke filters; closed 404 non-owner.

---

## P5 — Vue FE (T10–T12)

- [x] Routes `/explore`, `/jobs/:id`; Aside link
- [x] Explore list + search/filter UI
- [x] JD detail + Apply disabled
- [x] UserView tabs Đang tuyển + Quản lý JD (owner)
- [x] Manage form: branch multi-select, salary mode, currency dropdown

+ Verify thủ công: nav Explore; org tabs; create/close/reopen; visitor không thấy Quản lý.

---

## P6 — Smoke + đóng sprint

- [x] `scripts/smoke_jobmarket_sprint3.py` → `ALL_SMOKE_PASS`
- [x] Ghi Alembic head vào checklist header
- [x] Cập nhật PLANNING_TRIO / job_market README / sprint_map: Sprint3 CLOSED khi pass

### Guide

- CSRF + cookie như Sprint1/2 smokes.
- Không merge apply tables.

---

## AC ↔ step map

| AC | Step |
|----|------|
| AC-01–02 | P3 + P5 |
| AC-03–04 | P3 |
| AC-05–08 | P4 |
| AC-09 | P3 + P4 |
| AC-10–12, 15 | P5 |
| AC-13–14 | P3 |

---

> **CLOSED 2026-08-01.** Prove-done: `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_jobmarket_sprint3.py` → `ALL_SMOKE_PASS`. Alembic head `e5f6a7b8c9d0`.
