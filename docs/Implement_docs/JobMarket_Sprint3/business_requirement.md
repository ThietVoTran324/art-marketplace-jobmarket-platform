# Business Requirements — JobMarket_Sprint3: Explore JD + quản lý JD (Phase 1.3)

**Mục đích:** SSOT nghiệp vụ cho sprint Explore JD + JD detail + company quản lý JD + tab đang tuyển.  
**Cách dùng:** Plan #1 đã hoàn thiện「Nội dung」dưới đây từ [base requirement.md](base%20requirement.md). Spec kỹ thuật + step + prove-done → Plan #2 (`plan_mode_decisions.md` / `devplan_checklist.md`).  
**Không** nhồn spec kỹ thuật vào BR.

**Nguồn hệ thống:** [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (§3.B, §3.C; SAC-05; SAC-09 phần JD).  
**Sprint map:** [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint3.  
**Base input:** [base requirement.md](base%20requirement.md).  
**Index bộ 3:** [PLANNING_TRIO.md](PLANNING_TRIO.md).  
**Deferred:** [`../../Planing_docs/deferred_and_out_of_scope_backlog.md`](../../Planing_docs/deferred_and_out_of_scope_backlog.md).  
**Prerequisite:** JobMarket_Sprint2 CLOSED.

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

> Plan #1 **đã chốt 2026-08-01** theo base + quiz nghiệp vụ (Q1=A; Q8=VND/USD default VND; Q2–Q7, Q9–Q17 = suggest).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Sprint2: org account sau KYC; company profile + chi nhánh.
- Chưa có đăng JD / Explore / detail apply.

*Mục tiêu nghiệp vụ*

- Owner DN đăng và quản lý JD; đóng / reopen.
- User đã login khám phá JD active (Explore) và xem JD detail.
- CTA Apply chỉ **wire** Sprint4 (disabled + “Coming next”) — chưa apply thật.

*Người dùng / actor*

| Actor | Vai trò trong sprint này |
|-------|---------------------------|
| Organization owner (employer + owned company) | Tạo / sửa / đóng / reopen JD; tab Quản lý JD; thấy Đang tuyển |
| Visitor (user login, kể cả xem profile org người khác) | Tab Đang tuyển (JD active); Explore + JD detail |
| Artist / user login | Explore + JD detail; không quản lý JD DN người khác |
| Hệ thống | Enforce owner-only manage; Explore chỉ active; snapshot location; filter salary loại love-it |

### 2. Đối tượng nghiệp vụ

#### 2.1 Job post (JD)

Gắn đúng một company của owner.

| Nhóm | Rule |
|------|------|
| Title | Bắt buộc |
| Years experience | Bắt buộc; số nguyên ≥ 0 |
| Mô tả / yêu cầu / quyền lợi | Free text |
| Salary mode | Đúng một: *you'll love it* (không min/max) **XOR** rõ ràng (min và/hoặc max + validation) |
| Currency | VND (mặc định) hoặc USD |
| Locations | ≥1 chi nhánh từ company profile; multi; **snapshot** địa chỉ lúc chọn |
| Status | `active` \| `closed` only; tạo = `active`; không draft |
| Đóng / reopen | Owner đóng → khỏi Explore; reopen → `active` lại |
| Sửa khi active | Owner được sửa hầu hết field khi còn active |
| Quota | Không soft-cap số JD active / company |
| Quyền | Chỉ owner có hiring rights; khác → 403 |

#### 2.2 Explore JD

- Nav lớn (Aside) + list route.
- Chỉ **user đã login**.
- List mặc định: JD `active` (không ranking phức tạp).
- Search: title JD + tên công ty.
- Filter: years; salary range; location text trên snapshot địa chỉ.
- Khi đang filter lương theo range: JD *you'll love it* **không** vào kết quả; không filter lương → love-it vẫn hiện.
- Click → route JD detail.

#### 2.3 JD detail

- Nội dung JD đầy đủ + context company cần thiết.
- Nút Apply: **hiện, disabled**, copy “Coming next” (Sprint4).

#### 2.4 Company surfaces

| Surface | Ai thấy | Nội dung |
|---------|---------|----------|
| Đang tuyển | Visitor + owner | JD `active` của DN |
| Quản lý JD | Chỉ owner | CRUD / đóng / reopen; **không** list ứng viên |

### 3. Luồng & quy tắc nghiệp vụ

**Preconditions tạo/sửa/đóng/reopen JD:** login; account org với hiring rights; owner đúng company; company active.

**Owner**

1. Tab Quản lý JD → tạo JD (đủ field bắt buộc + ≥1 location + salary mode).
2. Sửa JD active khi cần.
3. Đóng → biến mất Explore / Đang tuyển (active list).
4. Reopen → xuất hiện lại.

**Visitor / artist (login)**

1. Aside → Explore → search/filter → mở detail.
2. Trên profile org: tab Đang tuyển thấy JD active.
3. Không thấy / không gọi được mutate quản lý JD của DN khác.

**Conflict / quyền**

- Non-owner manage → 403; visitor không thấy tab Quản lý JD.
- Chưa hiring rights → không tạo/sửa/đóng/reopen.
- Thiếu title / years / location / salary mode → báo lỗi rõ.

### 4. Phạm vi

*In scope*

- JD entity + owner CRUD/đóng/reopen  
- Explore (login) + search/filter  
- JD detail + Apply disabled wire  
- Tab Đang tuyển (public-to-login visitors) + tab Quản lý JD (owner)  
- Currency VND/USD; location snapshot; salary love-it vs range rules  

*Out of scope*

- Apply / cover / CV one-shot / status / notify / view-CV / list ứng viên → Sprint4  
- Work-exp approve + employees → Sprint5  
- Report JD / flag / audit JD / notify đăng-đóng → Sprint6 hoặc sau  
- Ranking phức tạp (JM-10); draft JD; soft-cap; Marketplace  

### 5. Acceptance criteria (business)

| ID | Tiêu chí |
|----|----------|
| AC-01 | Chưa hiring rights / non-owner → không tạo/sửa/đóng/reopen JD (403). |
| AC-02 | Visitor không thấy tab Quản lý JD. |
| AC-03 | Tạo thiếu title hoặc years → lỗi rõ. |
| AC-04 | Tạo thiếu location (≥1) hoặc thiếu salary mode → lỗi rõ. |
| AC-05 | Explore chỉ user login; chỉ JD `active`. |
| AC-06 | Search title + tên công ty khớp. |
| AC-07 | Filter years / location text khớp. |
| AC-08 | Filter lương range → không trả JD *you'll love it*; không filter → love-it vẫn có thể hiện. |
| AC-09 | Đóng JD → không còn Explore / Đang tuyển active; reopen → trở lại. |
| AC-10 | JD detail hiện Apply disabled + “Coming next”. |
| AC-11 | Tab Đang tuyển (visitor) thấy JD active của DN. |
| AC-12 | Currency mặc định VND; chọn USD được khi dùng mode có số lương (và khi love-it vẫn lưu currency default nếu cần hiển thị sau). |
| AC-13 | Snapshot location: đổi/xóa chi nhánh sau không làm mất địa chỉ đã gắn trên JD cho filter/search. |
| AC-14 | Owner PATCH được JD đang active. |
| AC-15 | Aside có entry Explore dẫn tới list. |

### 6. Traceability

| Nguồn | Liên quan |
|-------|-----------|
| System BR §3.B / §3.C | Explore + company JD tabs |
| SAC-05 / SAC-09 (phần) | Explore + đang tuyển / quản lý |
| Base + quiz 2026-08-01 | Q1–Q17 |

### 7. Quyết định Plan #1 (quiz nghiệp vụ)

| # | Chốt |
|---|------|
| 1 | Explore + detail: chỉ login |
| 2 | Apply CTA: disabled + Coming next |
| 3 | Status: active \| closed; không draft |
| 4 | Reopen được |
| 5 | Locations ≥1 bắt buộc |
| 6 | Snapshot địa chỉ |
| 7 | Filter lương loại love-it |
| 8 | Currency VND \| USD; default VND |
| 9–10 | Đang tuyển visitor+owner; Quản lý chỉ owner |
| 11–12 | PATCH khi active; không soft-cap |
| 13–14 | Audit/notify JD out Sprint3 |
| 15–17 | Aside Explore; không list ứng viên; years ≥0 integer |

---

> **Trạng thái:** BR sprint **CHỐT Plan #1** (2026-08-01).  
> **Bước kế tiếp:** Implement theo Plan #2 (`plan_mode_decisions.md` / `devplan_checklist.md`) — **chưa** bắt đầu domain code tại thời điểm chốt Plan #2.
