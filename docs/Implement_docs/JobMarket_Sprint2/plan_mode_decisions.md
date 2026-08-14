# Plan mode decisions — JobMarket_Sprint2 (Phase 1.2)

> **Initiative:** JobMarket_Sprint2 — Company + hiring-rights KYC  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) (Plan #1 CHỐT 2026-07-27)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **chốt 2026-07-27** — implement **CLOSED** 2026-07-28 theo checklist + smoke.

---

## 0. Meta

| | |
|---|---|
| Initiative | JobMarket_Sprint2 — companies + KYC + legal-entity unique + org profile switch |
| Profile Core | Schema + KYC API + email confirm + admin approve API + company profile + FE Settings/UserView |
| Stack | FastAPI + SQLAlchemy + Alembic + Postgres + Vue 3 + Pinia + Celery mail |
| Baseline Alembic head | `c3d4e5f6a7b8` |
| Hygiene in-sprint | **HY-05** (audit KYC actions); ownership helpers KYC/company |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Gate: AC-01..15 chứng minh được (API smoke + FE thủ công Settings KYC + UserView org). |
| P0-2 | Migration mới `down_revision = c3d4e5f6a7b8` → head mới (ví dụ `d4e5f6a7b8c9`). Docker `alembic upgrade head` trước prove-done. |
| P0-3 | Mở rộng module sẵn có `app/api/rest/job_market/` (không router package mới); không nhồi KYC vào `users/routes.py` trừ hydrate `account_kind` trên `/users/me`. |
| P0-4 | **HY-05 in-sprint:** mở rộng `ck_audit_logs_action` + `VALID_ACTIONS` cho 4 action KYC. |
| P0-5 | Admin KYC = **API-only** (không Admin UI Vue; ADM-02 backlog). |
| P0-6 | Prove-done: `scripts/smoke_jobmarket_sprint2.py` → `ALL_SMOKE_PASS` + FE thủ công. |

---

## D* — Core technical

### Identity org (AC-08 / AC-15)

| ID | Quyết định |
|----|------------|
| D1 | **Không** cột `account_kind` trên `users` (tránh dual source). Org = user có role `employer` **và** sở hữu đúng 1 `companies` với `status=active`. |
| D2 | Hydrate computed: mở rộng `GET /users/me` (và profile public cần thiết) trả `account_kind: "personal" \| "organization"` + `company_id` (nullable). Pinia `authUserStore` lưu các field này. |
| D3 | Sau approve: `assign_role(db, user_id, "employer")` + set `companies.owner_user_id` + `status=active` + `verified_at=now()`. Audit `kyc_approve` + `role_assign` (action role đã có). |
| D4 | Artist data (work-exp / credentials / CV) **giữ DB**; không xóa trong Sprint2. |
| D5 | FE: khi `account_kind===organization` → ẩn tabs Experience / Credentials / CV; default tab **Company**. Giữ tabs pins Created (và Saved/Liked/Boards khi owner). |
| D6 | Public list artist JM (`work-experiences`, `credentials`) khi target user là org → **200 + `[]`** (không lộ dữ liệu cũ như mặt profile chính). |

### Schema

| ID | Quyết định |
|----|------------|
| D7 | Bảng `companies`: `id` (UUID hoặc BigInt theo convention repo), `owner_user_id` FK `users.id` NULLABLE (NULL khi pending/rejected), `display_name` String(200), `description` Text nullable, `industry` String(100) nullable, `size_min` / `size_max` Integer nullable, `website` String(255) nullable, `domain` String(255) nullable, legal key fields (D8), `status` String(30), `verified_at` timestamptz nullable, `deleted_at` timestamptz nullable, `delete_reason` String(100) nullable, `created_at` / `updated_at`. |
| D8 | Legal key: `registration_country` String(2 hoặc 10), `registration_authority` String(100) default app **`NATIONAL`**, `registration_type` String(50), `registration_number_raw` String(100), `registration_number_normalized` String(100). Optional: `tax_id`, `vat_number` String nullable — **không** thay khóa chính. |
| D9 | UNIQUE DB `(registration_country, registration_authority, registration_type, registration_number_normalized)` — **không** drop khi soft-delete / rejected. |
| D10 | `status` CHECK IN (`pending_verification`, `active`, `rejected`, `suspended`, `soft_deleted`). |
| D11 | Partial unique: một user chỉ `owner_user_id` của tối đa một company nơi `owner_user_id IS NOT NULL` (1 DN / org account). |
| D12 | Bảng `company_branches`: `id`, `company_id` FK CASCADE, `label` String(100) nullable, `address_line` String(300), `city` String(100) nullable, `country` String(10) nullable, `is_primary` Boolean default false, `created_at` / `updated_at`. Index `(company_id)`. |
| D13 | Bảng `company_verification_requests`: `id`, `company_id` FK, `requester_user_id` FK, `status` CHECK IN (`pending`, `need_more_info`, `approved`, `rejected`), e-sign (`signer_full_name`, `signed_at`, `signer_ip`, `signer_user_agent`, `terms_version`), `company_email`, `company_email_confirmed_at` nullable, `admin_note` / `rejection_reason` Text nullable, `primary_document_language` String(20), `created_at` / `updated_at`. Index `(company_id, status)`, `(requester_user_id)`. |
| D14 | Cho phép **nhiều** request `pending` / `need_more_info` cùng `company_id` (AC-03 / Q6=B). |
| D15 | Bảng `company_verification_documents`: `id`, `request_id` FK CASCADE, `doc_type` CHECK IN (`business_registration_document`, `tax_registration_document`, `authorization_evidence`, `identity_document`, `document_translation`), `original_filename` String(255), `stored_name` String(255) (relative `kyc/{request_id}/{uuid}.ext`), `content_type` String(100), `size_bytes` Integer, `created_at`. Index `(request_id, doc_type)`. |
| D16 | KYC storage: `{MEDIA_PATH}/kyc/{request_id}/` + `save_file_bytes`; xóa row **và** file khi delete doc. Download **không** qua static public mount. |
| D17 | File allowlist: `.pdf`, `.jpg`, `.jpeg`, `.png`; MIME tương ứng. **15 MiB**/file; max **5**/`doc_type` nhóm; max **15**/request. Cấm archive/exe/DOCX pháp lý làm hồ sơ chính (reject upload). PDF page-count ≤30 khi có thể đọc được; password-PDF → reject. |
| D18 | Helper `normalize_registration_number(raw)`: trim, uppercase, bỏ separator cho phép (`-`, space, `.`); **giữ leading zero**; không cast int. |

### Conflict / multi-pending

| ID | Quyết định |
|----|------------|
| D19 | Lookup company by legal key normalized. `active` → 409/400 message hỗ trợ (không tạo). `suspended` / `soft_deleted` → block message hạn chế. |
| D20 | Không có company / `rejected` → tạo mới (`pending_verification`) hoặc **reuse** candidate cũ; request mới `pending`. |
| D21 | `pending_verification` → **không** spawn company; gắn request mới cùng `company_id`. |
| D22 | List “my requests” chỉ của requester; admin list thấy đủ. Không lộ danh tính requester khác cho nhau. |
| D23 | **Approve atomic:** approve 1 request → company `active` + owner + employer; mọi request cùng `company_id` còn `pending`/`need_more_info` → auto-`rejected` với `rejection_reason=superseded_by_other_approval`; audit `kyc_approve` cho request được chọn + `kyc_reject` cho siblings (hoặc một audit approve kèm metadata sibling ids — **chọn:** audit riêng từng sibling reject để HY-05 rõ). |

### Email confirm

| ID | Quyết định |
|----|------------|
| D24 | Submit precondition: account có email + **verified**; chưa có hiring rights đang hoạt động (`employer` + owned active company). Thiếu → 400 `email_required` / `email_not_verified` / `already_has_hiring_rights`. |
| D25 | `company_email` phải khớp email account (case-insensitive). Gửi mail Celery `send_email.delay` + template `mail_company_email_confirm.html`. |
| D26 | Token: `create_url_safe_token({"request_id": ..., "user_id": ...})`. Link: `{API_DOMAIN}/job-market/kyc/confirm-email/{token}` (GET). Confirm set `company_email_confirmed_at`. |
| D27 | **Approve bị chặn** nếu `company_email_confirmed_at` IS NULL (400/409). Admin vẫn `GET` list / `need_more_info` / `reject` được khi chưa confirm. |

### API

| ID | Quyết định |
|----|------------|
| D28 | KYC me: `GET/POST /job-market/me/hiring-rights-requests`; `GET /job-market/me/hiring-rights-requests/{id}`; docs: list/upload/delete + `GET .../documents/{doc_id}/file` (owner). |
| D29 | Confirm: `GET /job-market/kyc/confirm-email/{token}`. |
| D30 | Company: `GET /job-market/companies/{id}` (public-to-auth như profile); `PATCH /job-market/me/company` — yêu cầu employer + owner; branches: `POST/PATCH/DELETE /job-market/me/company/branches[/{id}]`. |
| D31 | Submit/PATCH company trả `warnings: [{code: "duplicate_name"\|"duplicate_domain"}]` khi trùng display_name/domain với company `active` khác — **không** 409. |
| D32 | Admin: `GET /job-market/admin/hiring-rights-requests` (filter `status`, legal key); `POST .../{id}/approve`, `.../need-more-info`, `.../reject` + `require_roles("admin")`. Doc download admin bypass ownership. |
| D33 | Ownership helpers: `assert_kyc_request_owner`, `assert_company_owner` trong `ownership.py` (404 cross-user id theo pattern Sprint1 CV). |
| D34 | Submit bắt buộc ≥1 `business_registration_document`. Nếu `primary_document_language` không phải English → bắt buộc ≥1 `document_translation` (400 nếu thiếu). |

### Audit (HY-05)

| ID | Quyết định |
|----|------------|
| D35 | Thêm actions: `kyc_submit`, `kyc_approve`, `kyc_reject`, `kyc_need_more_info`. Migration widen `ck_audit_logs_action` + update `VALID_ACTIONS` / constants trong `audit.py`. |
| D36 | Targets mới: `TARGET_KYC_REQUEST`, `TARGET_COMPANY`. Sprint2 **không** bắt buộc `company_profile_update` audit. |
| D37 | Ghi audit khi thành công: submit, approve, reject (kể cả auto-sibling), need_more_info. Grant employer dùng `role_assign` sẵn có. |

### FE

| ID | Quyết định |
|----|------------|
| D38 | `SettingsView.vue`: thay stub → form KYC + upload docs + xem status request + CTA confirm/resend nếu chưa confirm. |
| D39 | `UserView.vue`: org → Company tab mặc định; ẩn Experience/Credentials/CV. |
| D40 | Component `vuejs/src/components/Auth/JobMarket/CompanyProfileTab.vue` (+ form KYC dưới Settings hoặc component con). |
| D41 | Hydrate `account_kind` / `company_id` từ `/users/me` vào `authUserStore`. |

---

## Out of scope (tech)

- JD / Explore / apply  
- Multi-member self-serve; Admin KYC UI; employees tab  
- Soft-delete giải phóng unique key  
- Xóa artist rows sau approve  
- Audit `company_profile_update`  
- OR-semantics `require_roles` (HY-04)  

---

## Trace → checklist

Mọi D* / P0* map step trong `devplan_checklist.md` (P0–P9). Implement **chỉ** sau khi checklist tồn tại (file này + checklist = Plan #2 DONE) và user bắt đầu implement.
