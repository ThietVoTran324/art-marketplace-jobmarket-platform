# Business Requirements — JobMarket_Sprint2: Company + hiring-rights KYC (Phase 1.2)

**Mục đích:** SSOT nghiệp vụ cho sprint Company + hiring-rights KYC + legal-entity uniqueness + đổi identity profile sang tổ chức.  
**Cách dùng:** Plan #1 đã hoàn thiện「Nội dung」dưới đây. Spec kỹ thuật + step + prove-done → Plan #2 (`plan_mode_decisions.md` / `devplan_checklist.md`).  
**Không** nhồn spec kỹ thuật vào BR.

**Nguồn hệ thống:** [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (§3.D, SAC-10, D15).  
**Sprint map:** [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint2.  
**Base input:** [base requirement.md](base%20requirement.md).  
**Index bộ 3:** [PLANNING_TRIO.md](PLANNING_TRIO.md).  
**Deferred:** [`../../Planing_docs/deferred_and_out_of_scope_backlog.md`](../../Planing_docs/deferred_and_out_of_scope_backlog.md).  
**Prerequisite:** JobMarket_Sprint1 CLOSED.

---

## Quy tắc (cho AI — đọc trước mọi thao tác trên file này)

- File này = *SSOT nghiệp vụ* (~3/10 sau Plan); spec kỹ thuật + step + prove-done → `devplan_checklist.md` (~10/10). *Không* nhồn API/JSON/schema DB/widget/lệnh test vào BR.
- *Hai lần Plan mode* (không gộp một phiên):
  - *Plan #1 (file này):* từ base → chốt spec *nghiệp vụ* →「Nội dung」hoàn thiện. *Chưa* implement; *chưa* chốt tech.
  - **Plan #2 (`devplan_checklist.md` / `plan_mode_decisions.md`):** sau BR hoàn thiện → chốt spec *tech* → mới được implement.
- Nếu「Nội dung」chưa hoàn thiện → chỉ được làm *Plan #1*; *cấm* implement / nhét spec tech vào BR.
- *Anti-pattern:* một Plan mode làm cả BR + devplan chi tiết; hoặc implement khi mới có BR base.

---

## Nội dung

> Plan #1 **đã chốt 2026-07-27** theo quiz user. Nguồn base: [base requirement.md](base%20requirement.md).  
> Quiz: Q1=B + Q2=thay profile tổ chức; Q3=B; Q4=A; Q5=A; **Q6=B**; Q7–20=A (theo suggest trừ Q6).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Sprint1: account mặc định là **cá nhân / artist–ứng viên** (tabs work-exp, credentials, CV, pins).
- Settings có stub “Yêu cầu quyền tuyển dụng”.

*Mục tiêu nghiệp vụ*

- KYC xin quyền tuyển dụng + chống chiếm pháp nhân.
- Sau **approve**: account **không còn là profile cá nhân** — trở thành **account tổ chức**; bề mặt profile chính **thay thế** profile artist trước đó bằng **company profile**.
- Grant: role `employer` + ownership đúng **một** pháp nhân verified.
- Chưa JD / apply.

*Người dùng / actor*

| Actor | Vai trò trong sprint này |
|-------|---------------------------|
| Requester (cá nhân) | User trước khi được approve; submit / theo dõi KYC; xác nhận email công ty |
| Organization account (sau approve) | Cùng user record đã đổi identity hiển thị → company profile; mutate profile DN mình sở hữu |
| Admin | Duyệt / need_more_info / reject; khi nhiều request pending cùng key → **chọn** một |
| Hệ thống | Normalize; conflict; private docs; mail confirm; audit; chuyển bề mặt profile sau approve |

### 2. Đối tượng nghiệp vụ

#### 2.1 Company (pháp nhân)

- Một `companies` / một pháp nhân.
- Trạng thái: active (verified), pending verification, rejected (candidate tái dùng), suspended, soft-deleted / không tái dùng key tùy lý do.
- Profile tổ chức Phase 1: tên hiển thị, địa chỉ / **chi nhánh** (multi), ngành, mô tả, **size min–max**.
- Website / domain / tên: **cảnh báo trùng**, không hard unique.

#### 2.2 Company verification request (KYC)

- Tách khỏi company; nhiều request theo thời gian gắn candidate/company.
- Không spawn company mới mỗi lần submit khi đã có candidate.
- Form + cam kết/e-sign metadata + status (`pending` / `need_more_info` / `approved` / `rejected`) + docs.

#### 2.3 Legal-entity key

Hard unique (company đang hoạt động):

- `registration_country`
- `registration_authority` (string; được default **`NATIONAL`**)
- `registration_type`
- `registration_number_normalized` (trim, uppercase, bỏ separator cho phép; **giữ leading zero**; không cast int)

+ `registration_number_raw`. Tách `tax_id` / `vat_number` (optional) — không thay khóa chính.

#### 2.4 KYC documents (private)

Nhóm theo system BR §3.D: business registration (bắt buộc); tax / authorization / identity theo điều kiện; `document_translation` khi tài liệu **không phải English**.

Đọc file: **owner request + admin** only.  
File Phase 1: PDF/JPG/JPEG/PNG; giới hạn theo system BR; cấm archive/exe/Drive-link/password-PDF/DOCX pháp lý làm hồ sơ chính.

#### 2.5 Hiring rights + đổi identity profile (chốt quiz Q1–Q2, Q14)

Sau admin **approve** thành công:

1. Gán role catalog **`employer`**.  
2. Gắn user làm **owner** của đúng **một** `companies` verified.  
3. **Đổi identity hiển thị của account:**  
   - Trước approve: profile = cá nhân / artist–ứng viên (Sprint1).  
   - Sau approve: account được coi là **tài khoản tổ chức**; bề mặt profile chính **thay thế** profile cá nhân bằng **company profile** (không chỉ “thêm tab Company bên cạnh” artist tabs).  
4. Public/visitor vào profile username đó → thấy **company profile**, không còn trình bày như hồ sơ ứng viên cá nhân (work-exp / credentials / CV tabs không còn là mặt profile chính của account này).  
5. Dữ liệu artist cũ (pins / work-exp / CV…) không bắt buộc xóa khỏi hệ thống trong Sprint2; nhưng **không** là UX profile chính sau khi đã là org account. Chi tiết ẩn/giữ dữ liệu → Plan #2 nếu cần.

Chưa approve / chưa hiring rights → không mutate company profile (403).

### 3. Luồng & quy tắc nghiệp vụ

**Preconditions** (thiếu → báo rõ): đã login; email tài khoản **verified**; chưa có hiring rights đang hoạt động; account không khóa/hạn chế.

**Requester — submit KYC**

1. Settings → Yêu cầu quyền tuyển dụng → form + docs + cam kết + ký tên (lưu họ tên, thời gian, IP, UA, phiên bản điều khoản).  
2. Company email **khớp** email tài khoản; gửi mail **Xác nhận**.  
3. Request chờ xử lý; chưa fully usable đến khi email confirmed (admin vẫn xem/xử lý pending được).  
4. Mục đích KYC: đại diện **chính** DN đó — không phải headhunter đăng thay bên thứ ba (ủy quyền chỉ chứng minh quyền đại diện DN đang xin, không mở agency đa DN).

**Conflict khi mã pháp nhân đã tồn tại**

| Trạng thái Company | Hành vi (chốt quiz) |
|--------------------|---------------------|
| Active + verified | Không tạo mới. Message: DN đã tồn tại — hỗ trợ / ticket (chưa multi-member). |
| Pending verification | **Cho phép nhiều request pending** cùng key; **admin chọn** một để duyệt. Các requester **không** thấy danh tính nhau. Request không được chọn → reject / đóng theo quyết định admin. **Không** spawn thêm `companies` mới — dùng cùng candidate/company. |
| Rejected trước đó | Request mới liên kết candidate/company cũ — không spawn company mới. |
| Suspended | Không cho chiếm. Message hạn chế — hỗ trợ. |
| Soft-deleted / fraud / dissolved / merged | Không giải phóng unique key chỉ vì soft delete. |

**Admin — quyết định**

- `approve` → verify + grant rights + **chuyển profile sang tổ chức** + audit. Nếu nhiều pending cùng key: chỉ approve **một**; xử lý các pending còn lại (reject/đóng).  
- `need_more_info` → bổ sung; audit.  
- `reject` → lý do; audit; cho submit lại theo rule Rejected.  
- Kênh: **API-only** (ADM-02 UI sau).

**Organization account — company profile**

1. Sau approve, profile chính = company profile (thay artist).  
2. Mutate: tên, mô tả, ngành, size min–max, địa chỉ/chi nhánh.  
3. Non-owner / chưa hiring rights → 403.

**Settings**

- Entry KYC thay stub Sprint1. Không skeleton JD.

### 4. Phạm vi

*In scope*

- Companies + verification requests; unique pháp nhân; conflict (kể cả **multi-pending + admin chọn**)  
- KYC form + private docs + English + translation  
- Company email confirm  
- Admin API approve / need_more_info / reject  
- Grant `employer` + ownership một DN  
- **Đổi bề mặt profile cá nhân → tổ chức** sau approve  
- Company profile fields; audit KYC thành công; cảnh báo trùng name/domain  

*Out of scope*

- JD / Explore / apply (Sprint3–4)  
- Work-exp approve + employees (Sprint5)  
- Multi-member self-serve (JM-09); Admin UI KYC (ADM-02); tranh chấp UI (ADM-05)  
- Soft-delete tự giải phóng key (JM-13)  
- Marketplace  
- Giữ song song public artist profile + company profile trên cùng account sau approve (**đã reject** theo quiz Q2)

### 5. Acceptance criteria (business)

| ID | Tiêu chí |
|----|----------|
| AC-01 | Thiếu precondition → không submit; báo thiếu gì. |
| AC-02 | Submit gắn request đúng; không spawn company mới khi đã có candidate. |
| AC-03 | Nhiều request pending cùng legal-entity key được phép; admin chọn một; requester không lộ danh tính nhau. |
| AC-04 | Active+verified cùng key → không tạo mới; message hỗ trợ. |
| AC-05 | Reject rồi submit lại → liên kết candidate cũ. |
| AC-06 | File KYC: chỉ owner request + admin. |
| AC-07 | Tài liệu không English → cần document_translation. |
| AC-08 | Approve → `employer` + ownership 1 company + **profile chính = company (thay artist)**. |
| AC-09 | Admin need_more_info / reject qua API; non-admin không duyệt. |
| AC-10 | Chưa hiring rights / không owner → 403 mutate company profile. |
| AC-11 | Trùng tên/domain chỉ cảnh báo. |
| AC-12 | Audit KYC thành công (submit/approve/reject/need_more_info). |
| AC-13 | Settings mở flow KYC thật. |
| AC-14 | Gửi mail xác nhận company email khớp account. |
| AC-15 | Visitor xem profile account đã approve → thấy company profile, không còn mặt artist/ứng viên như trước approve. |

### 6. Traceability

| Nguồn | Liên quan |
|-------|-----------|
| System BR §3.D | KYC + unique + conflict (pending rule **sửa** theo quiz Q6=B) |
| SAC-10 | Đủ Sprint2 |
| Quiz 2026-07-27 | Q1–Q2 identity org; Q6 multi-pending |

### 7. Quyết định Plan #1 (quiz)

| # | Chốt |
|---|------|
| 1 | Approve → `employer` + owner 1 company verified |
| 2 | Sau approve: account = **tổ chức**; **thay** profile cá nhân/artist bằng company profile (không chỉ thêm tab) |
| 3 | Authority default `NATIONAL` được phép |
| 4 | Email confirm in-scope; chưa fully usable đến khi confirmed |
| 5 | Admin = API-only |
| 6 | **Pending trùng key: cho nhiều request; admin chọn** (không chặn cứng request 2) |
| 7–9 | Active block / reject reuse candidate / soft-delete không giải phóng key |
| 10–13 | Docs private; English+translation; name/domain warning; company email = account email |
| 14 | Một pháp nhân / account org |
| 15–20 | Email verified; profile org sau approve; audit; need_more_info; cấm headhunter đa DN; không JD Sprint2 |

---

> **Trạng thái:** Sprint **CLOSED** 2026-07-28 (Plan #1 + Plan #2 + implement + smoke).  
> **Bước kế tiếp:** JobMarket_Sprint3 theo sprint map (không mở trong Sprint2).
