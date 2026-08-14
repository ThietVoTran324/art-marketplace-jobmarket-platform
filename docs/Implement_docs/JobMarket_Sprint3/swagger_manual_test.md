# Sprint3 — Manual / API testing guide

**Mục đích:** test done JobMarket_Sprint3 (Explore JD + quản lý JD) qua Swagger + FE.  
**Docs:** `http://localhost:8000/api/docs` (hoặc `/docs` tùy proxy).  
**FE:** `http://localhost:3000`  
**Accounts seed:** suffix `132502` · password `SheetPass123!`  
**Script seed:** `scripts/seed_role_sheet_api.py`  
**Smoke tự động (tham chiếu):** `scripts/smoke_jobmarket_sprint3.py` → `ALL_SMOKE_PASS`  
**Alembic head:** `e5f6a7b8c9d0`

---

## 0. Setup Swagger (mỗi lần đổi user)

Cookie session + CSRF (DEV_MODE):

1. Mở docs: `http://localhost:8000/api/docs`.
2. **Nếu login báo `CSRF validation failed`:** xóa cookies `localhost:8000` (`access_token` + `csrf_token`), rồi login lại.
3. `POST /users/login` — **không cần** field `email`:

```json
{
  "username": "sheet_employer_132502",
  "password": "SheetPass123!"
}
```

4. `GET /users/csrf` → copy `csrf_token`.
5. **Authorize** → scheme **CSRF token** → dán token → Authorize.
6. Mọi `POST/PATCH/DELETE` dùng cookie login + header `X-CSRF-Token`.

Đổi user: xóa cookies (hoặc logout) → login user khác → CSRF mới → Authorize lại.

---

## 1. Account sheet (đã seed)

| Role | Username | Password | Ghi chú |
|------|----------|----------|---------|
| admin | `sheet_admin_132502` | `SheetPass123!` | admin |
| artist | `sheet_artist_132502` | `SheetPass123!` | visitor Explore / Đang tuyển |
| employer (org) | `sheet_employer_132502` | `SheetPass123!` | owner · **company_id=4** (nếu seed cũ) |
| seller | `sheet_seller_132502` | `SheetPass123!` | không quản lý JD |

> Nếu `company_id` khác 4: `GET /users/me` sau login employer → lấy `company_id` thật, thay mọi chỗ `{company_id}` dưới đây.

**Preflight employer**

1. Login employer + CSRF.
2. `GET /users/me` → `account_kind=organization`, có `company_id`.
3. `GET /job-market/companies/{company_id}/branches` → **≥1 branch**. Nếu rỗng:

```json
POST /job-market/me/company/branches
{
  "label": "HQ",
  "address_line": "1 Test St",
  "city": "Hanoi",
  "country": "VN",
  "is_primary": true
}
```

Ghi lại `branch_id` (ví dụ `B1`).

---

## 2. Endpoint map (Sprint3)

| Method | Path | Ai gọi | Ghi chú |
|--------|------|--------|---------|
| GET | `/job-market/me/job-posts` | owner | list tất cả status; query `status=active\|closed` optional |
| POST | `/job-market/me/job-posts` | owner | tạo `active`; `branch_ids` ≥1 |
| GET | `/job-market/me/job-posts/{id}` | owner | |
| PATCH | `/job-market/me/job-posts/{id}` | owner | không đổi status qua PATCH |
| POST | `/job-market/me/job-posts/{id}/close` | owner | → `closed` |
| POST | `/job-market/me/job-posts/{id}/reopen` | owner | → `active` |
| GET | `/job-market/companies/{company_id}/job-posts` | login | default `status=active` (Đang tuyển) |
| GET | `/job-market/explore/jobs` | login | chỉ `active`; filters |
| GET | `/job-market/jobs/{id}` | login | active 200; closed → 404 non-owner / 200 owner |

**Out Sprint3 (không test như feature):** Apply thật, list ứng viên, audit JD, notify đăng/đóng.

---

## Track A — Owner CRUD + validation (AC-03, 04, 12, 14)

Login: `sheet_employer_132502` + CSRF. Lấy `B1` từ branches.

### A1. Tạo JD `range` + USD (happy)

`POST /job-market/me/job-posts`

```json
{
  "title": "Senior Designer Sprint3",
  "years_experience": 3,
  "description": "Lead visual work",
  "requirements": "Figma, portfolio",
  "benefits": "Hybrid",
  "salary_mode": "range",
  "salary_min": 1000,
  "salary_max": 2000,
  "currency": "USD",
  "branch_ids": [B1]
}
```

Expect: **201**; `status=active`; `currency=USD`; `locations[]` snapshot có `address_line` / `city`; `source_branch_id=B1`.  
Ghi `job_range_id`.

### A2. Tạo JD `love_it` + default VND (AC-12)

```json
{
  "title": "Intern Love-it Sprint3",
  "years_experience": 0,
  "description": "Passion first",
  "salary_mode": "love_it",
  "currency": "VND",
  "branch_ids": [B1]
}
```

Expect: **201**; `salary_min`/`salary_max` = `null`; `currency=VND`.  
Ghi `job_love_id`.

### A3. Validation lỗi rõ (AC-03 / AC-04)

| Case | Body / thay đổi | Expect |
|------|-----------------|--------|
| Thiếu title | `"title": ""` hoặc omit | **422** |
| Years âm | `"years_experience": -1` | **422** |
| `branch_ids: []` | empty array | **422** |
| Thiếu `salary_mode` | omit field | **422** |
| `love_it` + có min | `"salary_mode":"love_it","salary_min":100` | **422** |
| `range` không min/max | `"salary_mode":"range"` only | **422** |
| `range` max &lt; min | min 2000, max 1000 | **422** |
| `branch_ids` không thuộc company | id lạ | **400** |

### A4. List / get / patch owner (AC-14)

1. `GET /job-market/me/job-posts` → thấy cả `job_range_id` + `job_love_id`.
2. `GET /job-market/me/job-posts?status=active` → chỉ active.
3. `GET /job-market/me/job-posts/{job_range_id}` → 200.
4. `PATCH /job-market/me/job-posts/{job_range_id}`

```json
{
  "title": "Senior Designer Sprint3 UPDATED",
  "years_experience": 4
}
```

Expect: **200**; title/years đổi; `status` vẫn `active`.

5. Optional đổi locations (replace set):

```json
{
  "branch_ids": [B1]
}
```

(Nếu có thêm branch `B2`: gửi `[B1, B2]` → locations length = 2.)

---

## Track B — Gates non-owner (AC-01)

Login: `sheet_artist_132502` + CSRF.

1. `POST /job-market/me/job-posts` (body A1) → **403** `not company owner`.
2. `PATCH /job-market/me/job-posts/{job_range_id}` → **403** hoặc **404**.
3. `POST /job-market/me/job-posts/{job_range_id}/close` → **403** hoặc **404**.
4. `POST /job-market/me/job-posts/{job_range_id}/reopen` → **403** hoặc **404**.

Login seller (optional): cùng kỳ vọng 403 khi mutate.

---

## Track C — Explore + filters (AC-05..08)

Login: artist (hoặc bất kỳ user login) + CSRF **không bắt buộc** cho GET, nhưng session login **bắt buộc**.

### C1. Chỉ active + login (AC-05)

1. Không cookie / logout → `GET /job-market/explore/jobs` → **401**.
2. Login artist → `GET /job-market/explore/jobs` → **200**; mọi item `status=active`.
3. Search nhanh:

`GET /job-market/explore/jobs?q=Sprint3`

Expect: thấy `job_range_id` và `job_love_id` (cả hai còn active).

### C2. Search title + company (AC-06)

| Query | Expect |
|-------|--------|
| `q=UPDATED` (hoặc title patch) | khớp JD đã PATCH |
| `q=` display_name company (từ `GET /job-market/companies/{id}`) | thấy JD của DN đó |
| `q=zzzz-no-match-sprint3` | `[]` hoặc không chứa job vừa tạo |

### C3. Filter years / location (AC-07)

```
GET /job-market/explore/jobs?q=Sprint3&years_min=4&years_max=4
```

Expect: có `job_range_id` (đã patch years=4); **không** có `job_love_id` (years=0).

```
GET /job-market/explore/jobs?q=Sprint3&location=Hanoi
```

Expect: JD có snapshot city/address chứa `Hanoi` (đổi text nếu branch city khác).

### C4. Filter lương loại love_it (AC-08)

```
GET /job-market/explore/jobs?q=Sprint3&salary_min=1500&salary_max=2500&currency=USD
```

Expect:

- Có `job_range_id` (overlap 1000–2000 USD).
- **Không** có `job_love_id`.

```
GET /job-market/explore/jobs?q=Sprint3
```

(không salary params) → **có** lại `job_love_id`.

---

## Track D — Close / reopen + detail rules (AC-09)

### D1. Đóng (owner)

Login employer + CSRF.

`POST /job-market/me/job-posts/{job_range_id}/close`

Expect: **200**, `status=closed`.

### D2. Explore / Đang tuyển ẩn JD closed

1. Login artist:

`GET /job-market/explore/jobs?q=Sprint3` → **không** còn `job_range_id`; vẫn có `job_love_id` nếu còn active.

2. `GET /job-market/companies/{company_id}/job-posts` (default active) → không có `job_range_id`.

### D3. Detail closed: 404 visitor / 200 owner

1. Artist: `GET /job-market/jobs/{job_range_id}` → **404**.
2. Employer: `GET /job-market/jobs/{job_range_id}` → **200**, `status=closed`.
3. Artist: `GET /job-market/jobs/{job_love_id}` → **200** (active).

### D4. Reopen

Employer: `POST /job-market/me/job-posts/{job_range_id}/reopen` → **200** `active`.

Artist Explore lại → thấy `job_range_id`.

---

## Track E — Company Đang tuyển (AC-11)

Login artist:

`GET /job-market/companies/{company_id}/job-posts`

Expect: **200**; chỉ `active` của DN đó.

Optional owner:

`GET /job-market/companies/{company_id}/job-posts?status=closed` → 200 (owner).  
Artist cùng query `status=closed` → **403**.

---

## Track F — Snapshot location (AC-13)

1. Owner tạo JD với `branch_ids:[B1]`; ghi snapshot `address_line` / `city` trên response.
2. `PATCH /job-market/me/company/branches/{B1}` đổi `city` (vd `DaNang`) **hoặc** xóa branch nếu còn ≥1 branch khác.
3. `GET /job-market/jobs/{job_id}` (owner/visitor tùy status) → location trên JD **vẫn** địa chỉ cũ (snapshot).
4. Explore `location=` text cũ vẫn khớp; text city mới (nếu chỉ đổi branch, chưa PATCH JD) **không** bắt buộc khớp JD cũ.

---

## Track G — FE manual (AC-02, 10, 15)

Base: `http://localhost:3000` · login cookie như app thường.

### G1. Aside Explore (AC-15)

1. Login bất kỳ (artist/employer).
2. Aside có icon briefcase → `/explore`.
3. List load; search + Filters (years, salary, currency, location) hoạt động tương tự Track C.

### G2. JD detail Apply wire (AC-10)

1. Click một JD active → `/jobs/{id}`.
2. Thấy title, company, locations, salary, mô tả…
3. Nút **Apply** hiện nhưng **disabled**; text **Coming next**.

### G3. Org tabs (AC-02, AC-11)

1. Login artist → mở profile employer (`/user/{employer_username}`).
2. Thấy tab **Đang tuyển** → list JD active; click → detail.
3. **Không** thấy tab **Quản lý JD**.
4. Login employer → profile mình: thấy **Đang tuyển** + **Quản lý JD**.
5. Quản lý JD: New job (branch multi-select, salary mode, currency) → Create → Close → Reopen → Edit.

### G4. Visitor không mutate qua UI

Artist trên profile org người khác: không có form tạo/đóng JD.

---

## 3. Checklist AC nhanh

| AC | Pass? | Cách chứng minh |
|----|-------|-----------------|
| AC-01 | ☐ | Track B |
| AC-02 | ☐ | Track G3 |
| AC-03 | ☐ | Track A3 title/years |
| AC-04 | ☐ | Track A3 locations/salary |
| AC-05 | ☐ | Track C1 |
| AC-06 | ☐ | Track C2 |
| AC-07 | ☐ | Track C3 |
| AC-08 | ☐ | Track C4 |
| AC-09 | ☐ | Track D |
| AC-10 | ☐ | Track G2 |
| AC-11 | ☐ | Track E + G3 |
| AC-12 | ☐ | Track A1/A2 |
| AC-13 | ☐ | Track F |
| AC-14 | ☐ | Track A4 |
| AC-15 | ☐ | Track G1 |

---

## 4. Pitfalls thường gặp

| Triệu chứng | Nguyên nhân / xử lý |
|-------------|---------------------|
| `CSRF validation failed` | Xóa cookies → login → CSRF → Authorize lại (giống Sprint2) |
| 401 Explore | Chưa login |
| 403 tạo JD | Không phải employer org / chưa KYC approve |
| 422 `branch_ids` | Quên lấy branch thật của company; hoặc `[]` |
| 400 branch invalid | `branch_id` thuộc company khác |
| Explore không thấy JD vừa tạo | Đang filter lương (loại love_it) hoặc JD đã close; thử `q=` title unique |
| Closed detail 404 | Đúng với non-owner; owner vẫn 200 |
| FE tab Quản lý không hiện | Chỉ hiện khi `account_kind=organization` **và** đang xem **profile của chính owner** |
| `company_id` lệch sheet | Luôn tin `GET /users/me`, không hard-code 4 nếu DB đã đổi |

---

## 5. Cleanup (optional)

Owner:

1. Close các JD test: `POST …/close`.
2. Không bắt buộc xóa cứng (Sprint3 không có delete endpoint).

---

## 6. Prove tự động (không thay manual FE)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_jobmarket_sprint3.py
```

Expect cuối: `ALL_SMOKE_PASS`.
