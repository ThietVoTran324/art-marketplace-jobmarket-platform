# Business Requirements — JobMarket_Sprint1: Artist foundation (Phase 1.1)

**Mục đích:** SSOT nghiệp vụ cho sprint đầu Job Market — profile tabs artist (work-exp, education/licensing, CV owner) + FE roles hygiene.  
**Cách dùng:** Plan #1 đã hoàn thiện「Nội dung」dưới đây. Spec kỹ thuật + step + prove-done → Plan #2 (`plan_mode_decisions.md` / `devplan_checklist.md`).  
**Không** nhồn spec kỹ thuật vào BR.

**Nguồn hệ thống:** [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (§3.A, SAC-01..04, D3–D11).  
**Sprint map:** [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint1.  
**Base input:** [base requirement.md](base%20requirement.md).  
**Index bộ 3:** [PLANNING_TRIO.md](PLANNING_TRIO.md).  
**Deferred:** [`../../Planing_docs/deferred_and_out_of_scope_backlog.md`](../../Planing_docs/deferred_and_out_of_scope_backlog.md).

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

> Plan #1 đã chốt 2026-07-26. Nguồn base gốc: [base requirement.md](base%20requirement.md).  
> Gap #1–#6 trong base đã đóng theo bảng quyết định Plan #1 (xem §7).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Phase 0-core đã CLOSED: multi-role (`artist` mặc định; catalog `admin` / `employer` / `seller`), ownership, CSRF, audit append-only.
- Job Market Phase 1 bắt đầu bằng **nền artist trên profile user hiện có** — chưa company KYC, chưa JD/Explore, chưa apply.

*Mục tiêu nghiệp vụ*

- Thêm tab Work experience / Education-licensing / CV (owner) bên cạnh profile cơ bản; **giữ** tab pins hiện có (không coi pins là deliverable JM mới).
- Cho artist quản lý timeline work-exp, **credentials (education/licensing/awards)**, và tối đa 3 CV; visitor đọc work-exp + credentials; admin có thể override credentials.
- Hygiene FE: đọc roles từ kênh `/me/roles` trên shell auth liên quan JM; neo stub “yêu cầu quyền tuyển dụng” trên Settings (chưa form KYC).

*Người dùng / actor*

| Actor | Vai trò nghiệp vụ trong sprint này |
|-------|--------------------------------------|
| Owner (user / artist) | CRUD work-exp + credentials của mình; upload/xóa CV của mình (max 3) |
| Visitor (user khác hoặc khách theo rule profile hiện có) | Đọc work-exp (kèm status) + education/licensing/awards công khai; **không** xem/quản lý tab CV của người khác |
| Admin | Có thể CRUD credentials hộ (override); không thay artist tự quản work-exp/CV |
| Hệ thống | Auto-sort work-exp; enforce quota CV; chặn upload CV khi chưa có email; xóa file khi xóa CV khỏi list |

### 2. Đối tượng nghiệp vụ

#### 2.1 Profile tabs (cùng profile user hiện có)

| Tab | Ai xem / làm gì | Ghi chú |
|-----|-----------------|---------|
| Profile cơ bản | Giữ hành vi hiện có | Không thêm field profile gốc trong sprint này (JM-06 defer) |
| Work experience | Công khai đọc (dòng + status); owner CRUD | Timeline LinkedIn-like |
| Education / licensing / awards | Công khai đọc; **owner CRUD** | Ba loại; **không** university verify; admin override optional |
| CV | **Chỉ owner** quản lý list | Max 3; employer đọc-on-apply → Sprint4 |
| Pins | Giữ nguyên | Không deliverable JM (JM-07) |

#### 2.2 Work experience

*Field nghiệp vụ (mỗi dòng)*

- Tên công ty: **free-text** (Sprint1 không có suggest từ danh sách company — chưa có pháp nhân trên hệ thống).
- Hình thức làm việc: một trong `full-time`, `part-time`, `hybrid`, `outsourcing`, `collaborator`.
- Vị trí / chức vụ.
- Location: free-text.
- Thời gian: ngày bắt đầu bắt buộc; ngày kết thúc tùy chọn (trống = đang làm / present).
- Status phê duyệt: `Pending approval` hoặc `Approved` — **hiển thị rõ cho mọi visitor** (không ẩn status).

*Quy tắc*

- Owner được tạo / sửa / xóa dòng của mình.
- **Auto sort** theo ngày bắt đầu tăng dần (quá khứ → hiện tại); user không sắp xếp tay.
- Validation thời gian (nghiệp vụ): ngày kết thúc nếu có phải ≥ ngày bắt đầu; không cho khoảng thời gian vô lý (ví dụ kết thúc trước bắt đầu). Chi tiết ràng buộc kỹ thuật → Plan #2.
- Mọi dòng mới = **Pending approval**. Công ty ngoài hệ thống (free-text) **luôn** Pending trong Phase 1 cho đến khi có luồng approve (Sprint5) và company tồn tại trên hệ thống.
- Sprint1 **không** gửi notify / không có nút approve cho company (→ Sprint5; phần còn lại của SAC-02).
- Không backfill khi sau này có tài khoản company (JM-03).

#### 2.3 Education / licensing / awards

- Ba loại nội dung nghiệp vụ: **education**, **licensing**, **awards**.
- **Owner CRUD** trên profile mình; visitor chỉ đọc.
- Không mở role `university` và không có luồng “trường duyệt / verify credential” (JM-01 / NO-01). Credential **không** cần verify bên thứ ba.
- Admin có thể CRUD hộ qua API (override); Admin UI product-grade = ADM-03 backlog.

#### 2.4 CV (owner)

- Chỉ hai hành động nghiệp vụ chính trên tab: **upload** và **xóa**.
- Tối đa **3** CV / user. Upload vượt quota → từ chối kèm thông báo đủ nghĩa.
- Xóa khỏi list ⇒ **xóa luôn file đã lưu** (không để orphan nghiệp vụ).
- Tab / list CV: **hard block** — non-owner không xem list, không tải, không xóa.
- **Allowlist tối thiểu file:** PDF và DOC/DOCX; có **giới hạn dung lượng** nghiệp vụ (số cụ thể → Plan #2). Harden sâu (malware, MIME spoof…) → Sprint6.
- **Email bắt buộc** trước khi upload CV (D9): nếu chưa có email → chặn hành động + thông báo; UI cho hai lựa chọn: đi gắn email trên profile / tạm bỏ qua (không hoàn tất upload).
- Apply one-shot CV từ máy / employer đọc CV đã nộp → Sprint4 (không thuộc sprint này).

#### 2.5 Settings stub & FE roles

- Settings: mục / nút **“Yêu cầu quyền tuyển dụng”** ở trạng thái **stub** — disabled hoặc tương đương + copy kiểu “coming next” (trỏ Sprint2). **Không** mở route skeleton / form giả KYC.
- Hydrate roles (HY-06) trên shell auth liên quan JM: **Aside**, **UserView**, **Settings**. Không bắt buộc mọi view đã login trong Sprint1.
- Không dùng hardcode username làm nguồn quyền trên FE liên quan role.

### 3. Luồng & quy tắc nghiệp vụ

**Owner — work-exp**

1. Mở tab Work experience trên profile mình → thấy timeline đã sort.
2. Thêm / sửa / xóa dòng với đủ field bắt buộc; company nhập free-text.
3. Sau lưu: status = Pending approval; thứ tự list do hệ thống sắp theo ngày bắt đầu.

**Visitor — work-exp / education**

1. Mở profile người khác (theo rule profile hiện có) → đọc được work-exp kèm nhãn status rõ; đọc education/licensing/awards.
2. Không thấy tab quản lý CV của người đó; **không** mutate credentials / work-exp của người khác.

**Owner — credentials**

1. Thêm / sửa / xóa education, licensing, hoặc award trên profile mình.
2. Không có bước “chờ trường duyệt”.

**Owner — CV**

1. Có email → upload (trong quota + allowlist) hoặc xóa CV của mình.
2. Chưa email → bị chặn + CTA gắn email / bỏ qua.
3. Đủ 3 CV → upload tiếp bị từ chối.

**Admin — credentials (override)**

1. Admin có thể tạo / sửa / xóa credential trên profile user mục tiêu (API tối thiểu).
2. User không có quyền admin → không dùng được kênh admin.

**Hiring-rights (chỉ neo UI)**

- User thấy stub trên Settings; không submit được yêu cầu trong Sprint1.

### 4. Phạm vi

*In scope*

- Profile tabs: basic (giữ) / work-exp / education-licensing (**owner CRUD**) / CV (owner); pins giữ nguyên.
- Work-exp CRUD + auto-sort + free-text company + status public Pending/Approved (chưa approve flow).
- Education / licensing / awards: owner CRUD; visitor đọc; admin override API optional; **không** university verify.
- CV: max 3; upload/xóa + xóa file; allowlist PDF/DOC/DOCX + size cap; hard block non-owner; email gate trước upload.
- FE: hydrate roles trên Aside / UserView / Settings; Settings stub hiring-rights.

*Out of scope*

- Company registry, hiring-rights KYC, company profile → Sprint2.
- Explore JD / JD manage / đóng JD → Sprint3.
- Apply, application statuses, view-CV route, notify apply → Sprint4.
- Work-exp approve in-app + notify + employee tab → Sprint5 (phần còn lại SAC-02).
- Report JD / flag company / harden file sâu → Sprint6.
- Admin UI product (ADM-01, ADM-03, …).
- JM-01 university, JM-03 backfill, JM-05 badge verified tổng, JM-07 pins-as-JM, JM-08 chat–application, Marketplace (MP-*).
- Suggest company từ hệ thống; route skeleton KYC.
- HY-02 SSE / mark-read (ưu tiên Sprint4); HY-04 OR roles (khi moderation cần).

### 5. Acceptance criteria (business)

| ID | Tiêu chí | Map |
|----|----------|-----|
| AC-01 | Profile user có tab Work experience / Education-licensing / CV (owner) bên cạnh profile cơ bản; pins vẫn hoạt động như trước. | SAC-01 |
| AC-02 | Owner tạo / sửa / xóa được dòng work-exp; list tự sắp theo ngày bắt đầu tăng dần. | SAC-02 (partial) |
| AC-03 | Visitor đọc được timeline work-exp kèm status rõ (`Pending approval` / `Approved`); không mutate dòng của người khác. | SAC-01 / SAC-02 partial |
| AC-04 | Dòng work-exp mới luôn Pending; company free-text (không có suggest hệ thống trong sprint này). | D4 partial |
| AC-05 | Owner tạo / sửa / xóa được education hoặc licensing hoặc awards của mình; non-owner bị từ chối mutate. | SAC-03 |
| AC-06 | Visitor đọc được danh sách education-licensing-awards công khai. | SAC-03 |
| AC-05b | Admin vẫn tạo/sửa/xóa credential hộ qua API admin (override). | SAC-03 |
| AC-07 | Owner upload được CV trong quota 3 và allowlist PDF/DOC/DOCX (+ size cap); upload thứ 4 bị từ chối. | SAC-04 |
| AC-08 | Owner xóa CV khỏi list ⇒ file đã lưu không còn dùng được / bị gỡ theo nghĩa nghiệp vụ. | SAC-04 |
| AC-09 | Non-owner không list / không xóa / không tải CV của người khác. | SAC-04 |
| AC-10 | User chưa có email bị chặn upload CV kèm lựa chọn đi gắn email hoặc bỏ qua (không hoàn tất). | D9 |
| AC-11 | Settings có stub “Yêu cầu quyền tuyển dụng” (disabled / coming next); không mở form KYC. | Sprint map / gap #5 |
| AC-12 | Aside, UserView, Settings đọc được roles từ kênh `/me/roles` (không phụ thuộc hardcode username cho quyền). | HY-06 |

### 6. Traceability

| Nguồn | Liên quan sprint này |
|-------|----------------------|
| System BR §3.A | Profile tabs, work-exp, credentials owner CRUD, CV owner, email gate |
| SAC-01, SAC-03, SAC-04 | Đủ trong Sprint1 |
| SAC-02 | Chỉ CRUD + sort + free-text + status hiển thị; **approve/notify = Sprint5** |
| D3, D7, D9, D10, D11 | D10 = owner CRUD credentials (không university verify) |
| Deferred JM-01 university approve; ADM-03 UI | Out — không kéo vào Sprint1 |

### 7. Quyết định đóng gap Plan #1

| # | Gap | Chốt |
|---|-----|------|
| 1 | Work-exp public + status | Visitor thấy timeline + status rõ (`Pending approval` / `Approved`). Không ẩn status. |
| 2 | Education model | Ba loại (education / licensing / awards); **owner CRUD**; schema 1 bảng → Plan #2 đã chốt. **Corr 2026-07-27:** không còn admin-only. |
| 3 | CV file rules | Allowlist tối thiểu PDF + DOC/DOCX + size cap; harden sâu → Sprint6. |
| 4 | Company trên work-exp | Free-text only; suggest → Sprint2. |
| 5 | Settings hiring-rights | Stub UI disabled + “coming next”; không route skeleton. |
| 6 | Hydrate roles | Aside + UserView + Settings; không bắt buộc mọi view auth. |

---

> **Trạng thái:** BR sprint **hoàn thiện** — Plan #1 xong (2026-07-26).  
> **Corr 2026-07-27:** credentials = **owner CRUD** (không university verify).  
> **Plan #2 / Implement:** đã ship; corr credentials đã áp dụng codebase cùng ngày.
