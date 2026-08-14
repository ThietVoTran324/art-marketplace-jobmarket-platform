# Sprint2 — Swagger manual test sheet

**Mục đích:** test done JobMarket_Sprint2 qua Swagger (`http://localhost:8000/docs`).  
**Accounts seed:** suffix `132502` · password chung `SheetPass123!`  
**Script seed:** `scripts/seed_role_sheet_api.py`

---

## 0. Setup Swagger (mỗi lần đổi user)

Cookie session + CSRF (DEV_MODE):

1. Mở docs: `http://localhost:8000/api/docs` (hoặc `http://localhost:8000/docs` tùy proxy).
2. **Nếu login báo `CSRF validation failed`:** browser còn cookie `access_token` cũ trong khi path Swagger là `/api/users/login`.
   - Cách nhanh: DevTools → Application → Cookies → xóa cookies `localhost:8000` (hoặc ít nhất `access_token` + `csrf_token`), rồi login lại.
   - Hoặc: `GET /users/csrf` → Authorize CSRF → rồi mới `POST /users/login` kèm header.
3. **Authorize chưa cần** nếu cookies đã sạch.
4. `POST /users/login` — **không cần** field `email`:

```json
{
  "username": "sheet_admin_132502",
  "password": "SheetPass123!"
}
```

5. `GET /users/csrf` → copy `csrf_token`.
6. **Authorize** → scheme **CSRF token** → dán token → Authorize.
7. Mọi `POST/PATCH/DELETE` sau đó dùng cookie login + header `X-CSRF-Token`.

Đổi user: xóa cookies (hoặc logout) → login user khác → CSRF mới → Authorize lại.

Mailhog (xem mail confirm): `http://localhost:8025`

---

## 1. Account sheet (đã seed)

| Role | Username | Email | user_id | Ghi chú |
|------|----------|-------|---------|---------|
| admin | `sheet_admin_132502` | `sheet_admin_132502@example.com` | 93 | roles: admin, artist |
| artist | `sheet_artist_132502` | `sheet_artist_132502@example.com` | 94 | roles: artist |
| employer (org) | `sheet_employer_132502` | `sheet_employer_132502@example.com` | 95 | employer + org · **company_id=4** |
| seller | `sheet_seller_132502` | `sheet_seller_132502@example.com` | 96 | seller, artist |

Password tất cả: `SheetPass123!`

> Employer đã approve sẵn → dùng **Track A** để check org/profile; dùng **Track B** (requester mới + mã DN mới) để chạy lại full KYC trên Swagger.

---

## Track A — Verify account đã seed (nhanh)

### A1. Admin session

1. Login admin (body §0).
2. CSRF + Authorize.
3. `GET /users/me` → `verified=true`, `account_kind=personal`.
4. `GET /users/me/roles` → có `admin`.
5. `GET /job-market/admin/hiring-rights-requests` → 200, thấy request đã approve của employer.
6. Optional filter:

Query: `status=approved`

### A2. Employer org (AC-08 / AC-15 / AC-10)

1. Login `sheet_employer_132502` + CSRF.
2. `GET /users/me`

Expect:

```json
{
  "account_kind": "organization",
  "company_id": 4
}
```

3. `GET /users/me/roles` → có `employer`.
4. `GET /job-market/companies/4` → 200, `status=active`.
5. `PATCH /job-market/me/company`

```json
{
  "description": "Updated via Swagger Track A",
  "industry": "Design",
  "size_min": 2,
  "size_max": 25,
  "website": "https://sheet.example",
  "domain": "sheet.example"
}
```

Expect: 200; có thể có `warnings` nếu trùng name/domain (không 409).

6. `POST /job-market/me/company/branches`

```json
{
  "label": "HQ",
  "address_line": "2 Swagger St",
  "city": "HN",
  "country": "VN",
  "is_primary": false
}
```

7. `GET /job-market/companies/4/branches` → thấy branch mới.
8. `GET /job-market/users/95/work-experiences` (login artist hoặc admin) → **`[]`** (org ẩn artist list).

### A3. Non-owner / non-admin gates

1. Login `sheet_artist_132502` + CSRF.
2. `PATCH /job-market/me/company` (body bất kỳ) → **403** `hiring_rights_required` hoặc `not company owner`.
3. `POST /job-market/admin/hiring-rights-requests/{any_id}/approve` → **403**.

### A4. Seller sanity

1. Login seller + CSRF.
2. `GET /users/me/roles` → có `seller` (Sprint2 không thêm domain seller).

---

## Track B — Full KYC happy path (Swagger done Sprint2)

Dùng **admin seed** duyệt. Tạo **requester mới** (đừng dùng employer đã org).

### B0. Đăng ký requester mới

Chọn suffix tự do, ví dụ `swag01`:

`POST /users/register` (CSRF không bắt buộc — exempt)

```json
{
  "username": "kyc_swag_01",
  "password": "SheetPass123!",
  "email": "kyc_swag_01@example.com"
}
```

Ghi `user_id` từ response.

### B1. Verify email tài khoản (precondition AC-01)

Cách 1 — Mailhog: mở mail Verify → copy path `/users/verify/{token}` → `GET` path đó trên API.

Cách 2 — trong container (token cùng serializer app):

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app \
  python -c "from app.api.rest.utils import create_url_safe_token; print(create_url_safe_token({'username':'kyc_swag_01'}))"
```

Rồi Swagger: `GET /users/verify/{token}` → verified.

### B2. Login requester + CSRF

```json
{
  "username": "kyc_swag_01",
  "password": "SheetPass123!"
}
```

`GET /users/csrf` → Authorize.

`GET /users/me` → `verified=true`, `account_kind=personal`.

### B3. Precondition fail (AC-01) — optional

Tạm dùng user chưa verify / sai email → expect 400:

| detail | Khi |
|--------|-----|
| `email_not_verified` | chưa verify |
| `email_required` | không có email |
| `company_email_must_match_account_email` | company_email ≠ account email |
| `already_has_hiring_rights` | dùng `sheet_employer_132502` submit KYC |

### B4. Submit KYC (AC-02 / AC-11 / AC-12)

`POST /job-market/me/hiring-rights-requests`

**Body chuẩn** (đổi `registration_number_raw` cho unique — **không** dùng mã company đã active `SHEET-132502`):

```json
{
  "display_name": "Swagger Test Co",
  "description": "KYC via Swagger Track B",
  "industry": "Software",
  "size_min": 1,
  "size_max": 50,
  "website": "https://swagger-test.example",
  "domain": "swagger-test.example",
  "registration_country": "VN",
  "registration_authority": "NATIONAL",
  "registration_type": "LLC",
  "registration_number_raw": "SWAG-01-001",
  "tax_id": null,
  "vat_number": null,
  "signer_full_name": "Kyc Swagger",
  "terms_version": "hiring-rights-kyc-v1",
  "primary_document_language": "en",
  "company_email": "kyc_swag_01@example.com",
  "address_line": "10 Test Street",
  "city": "HN",
  "branch_country": "VN"
}
```

Expect: **201**

Ghi lại:

- `id` → `{REQUEST_ID}`
- `company_id` → `{COMPANY_ID}`
- `status` = `pending`
- `company_email_confirmed_at` = `null`
- `warnings` (nếu có) chỉ cảnh báo name/domain

### B5. List my requests (không lộ requester khác — AC-03)

`GET /job-market/me/hiring-rights-requests` → chỉ request của mình.

### B6. Confirm company email (AC-14)

Cách 1 — Mailhog: mail “Confirm company email” → `GET /job-market/kyc/confirm-email/{token}`

Cách 2 — container:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app \
  python -c "from app.api.rest.utils import create_url_safe_token; print(create_url_safe_token({'request_id': REQUEST_ID, 'user_id': USER_ID}, expiration=86400))"
```

Thay `REQUEST_ID` / `USER_ID` → `GET /job-market/kyc/confirm-email/{token}`

Expect: 200 JSON hoặc 302 redirect.

`GET /job-market/me/hiring-rights-requests/{REQUEST_ID}` → `company_email_confirmed_at` **không null**.

Optional: `POST /job-market/me/hiring-rights-requests/{REQUEST_ID}/resend-confirm` trước khi confirm.

### B7. Upload docs (AC-06 / AC-07)

`POST /job-market/me/hiring-rights-requests/{REQUEST_ID}/documents`

Swagger form-data:

| field | value |
|-------|--------|
| `doc_type` | `business_registration_document` |
| `file` | file PDF/JPG/PNG (≤15 MiB) |

Expect: **201**, ghi `doc_id`.

Nếu `primary_document_language` không phải `en` / `eng` / `english` → bắt buộc thêm:

`doc_type` = `document_translation`

`GET .../documents` → list.

`GET .../documents/{doc_id}/file` (owner) → file.

Login **artist** khác → cùng download URL → **404** (không lộ).

### B8. Admin: approve bị chặn nếu chưa confirm (AC-14)

Trước B6 (hoặc request khác chưa confirm):

Login admin + CSRF.

`POST /job-market/admin/hiring-rights-requests/{REQUEST_ID}/approve`

Expect: **400** `company_email_not_confirmed`

### B9. Admin list + need_more_info + reject (AC-09) — optional nhánh

`GET /job-market/admin/hiring-rights-requests?status=pending`

`POST /job-market/admin/hiring-rights-requests/{REQUEST_ID}/need-more-info`

```json
{ "note": "Please upload clearer registration scan" }
```

Expect: status `need_more_info`.

Hoặc reject (dùng request phụ nếu không muốn phá happy path):

```json
{ "reason": "incomplete package" }
```

### B10. Admin approve (AC-08 / AC-12)

Sau B6+B7 xong:

Login admin + CSRF.

`POST /job-market/admin/hiring-rights-requests/{REQUEST_ID}/approve`  
(body trống)

Expect: **200**, `status=approved`.

### B11. Org identity sau approve (AC-08 / AC-15)

Login lại requester + CSRF.

`GET /users/me`

```json
{
  "account_kind": "organization",
  "company_id": "{COMPANY_ID}"
}
```

`GET /users/me/roles` → có `employer`.

`GET /job-market/companies/{COMPANY_ID}` → `status=active`, `owner_user_id` = requester.

### B12. Company mutate (AC-10 / AC-11)

Requester (owner):

`PATCH /job-market/me/company`

```json
{
  "display_name": "Swagger Test Co Updated",
  "description": "Post-approve profile",
  "size_min": 5,
  "size_max": 100
}
```

Artist login → cùng PATCH → **403**.

### B13. Active key block (AC-04)

Register/verify user khác → submit KYC **cùng** `registration_number_raw: "SWAG-01-001"` (+ cùng country/authority/type).

Expect: **409** `company_already_verified_contact_support`

### B14. Multi-pending (AC-03) — optional

Trước khi approve (giữa B4 và B10): user thứ 2 submit **cùng** legal key → **201**, **cùng** `company_id`, admin approve một → sibling `rejected` / `superseded_by_other_approval`.

### B15. Audit (AC-12)

Login admin:

`GET /users/me/audit` (nếu có quyền) hoặc check DB/audit list admin — expect actions:

- `kyc_submit`
- `kyc_approve`
- (+ `kyc_reject` / `kyc_need_more_info` nếu đã chạy B9)
- `role_assign` (employer)

---

## Body / endpoint cheat sheet

| # | Method | Path | Actor |
|---|--------|------|--------|
| 1 | POST | `/users/login` | any |
| 2 | GET | `/users/csrf` | any logged-in |
| 3 | GET | `/users/me` | any |
| 4 | GET | `/users/me/roles` | any |
| 5 | POST | `/job-market/me/hiring-rights-requests` | requester |
| 6 | GET | `/job-market/me/hiring-rights-requests` | requester |
| 7 | GET | `/job-market/kyc/confirm-email/{token}` | (link) |
| 8 | POST | `/job-market/me/hiring-rights-requests/{id}/documents` | requester |
| 9 | GET | `/job-market/admin/hiring-rights-requests` | admin |
| 10 | POST | `/job-market/admin/hiring-rights-requests/{id}/approve` | admin |
| 11 | POST | `/job-market/admin/hiring-rights-requests/{id}/need-more-info` | admin |
| 12 | POST | `/job-market/admin/hiring-rights-requests/{id}/reject` | admin |
| 13 | PATCH | `/job-market/me/company` | employer owner |
| 14 | POST | `/job-market/me/company/branches` | employer owner |
| 15 | GET | `/job-market/companies/{id}` | auth user |

### Admin reject body

```json
{ "reason": "Documents unreadable" }
```

### Admin need_more_info body

```json
{ "note": "Add translation PDF" }
```

### Doc types hợp lệ

- `business_registration_document` (**bắt buộc** trước approve)
- `tax_registration_document`
- `authorization_evidence`
- `identity_document`
- `document_translation` (bắt buộc nếu language ≠ English)

---

## Checklist tick khi test Swagger

- [ ] A2 org employer `account_kind=organization` + PATCH company OK
- [ ] A3 artist 403 company + 403 admin approve
- [ ] B4 submit 201 + pending
- [ ] B6 email confirmed
- [ ] B7 upload biz doc + non-owner 404 file
- [ ] B8 approve trước confirm → 400
- [ ] B10 approve → employer + org
- [ ] B13 active key → 409
- [ ] (optional) B14 multi-pending + sibling reject

**FE bổ sung (không Swagger):** Settings KYC form + UserView tab Company khi org (AC-13 / AC-15 UI).
