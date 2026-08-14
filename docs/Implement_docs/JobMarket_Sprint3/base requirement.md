# Base requirement — JobMarket_Sprint3 (Phase 1.3 Explore JD + quản lý JD)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (§3.B Explore/JD detail; §3.C site công ty — tab đang tuyển / quản lý JD).  
> Cắt sprint: [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint3.  
> Sau Plan #1, SSOT nghiệp vụ sprint là `business_requirement.md` trong folder này — file base **không** supersede BR.  
> Prerequisite: [`../JobMarket_Sprint2/`](../JobMarket_Sprint2/) **CLOSED**.

## Bối cảnh

Sprint1: artist tabs + work-exp + credentials + CV.  
Sprint2: company + hiring-rights KYC; sau approve → org account + company profile (chi nhánh, size, …).  
Sprint3 bật **đăng / khám phá / xem JD** — điều kiện để Sprint4 làm apply + pipeline ứng viên.

## Mục tiêu sprint (shippable)

1. **Job post (JD)** gắn một `companies` verified/owner: title + years experience **bắt buộc**; mô tả / yêu cầu / quyền lợi free text; salary mode (**you'll love it** XOR min/max); currency **VND | USD** (mặc định VND); địa điểm làm việc chọn từ chi nhánh company (**≥1**, multi) và **snapshot** lúc chọn.
2. **Company surfaces (org / owner hiring rights):**
   - Tab **Đang tuyển**: visitor + owner thấy JD `active` của DN.
   - Tab **Quản lý JD**: **chỉ owner**; CRUD + đóng + reopen; hard block non-owner.
3. **Explore JD**: entry nav lớn (Aside); list JD `active`; search title + tên công ty; filter years / salary range / location text; **chỉ user đã login**.
4. **Vue route JD detail**: nội dung JD đầy đủ; CTA Apply **disabled** + “Coming next” (wire Sprint4) — chưa apply thật.

## Spec nghiệp vụ đã gom (input Plan #1)

### Job post — fields & rules

| Nhóm | Rule |
|------|------|
| Title | Bắt buộc |
| Years experience | Bắt buộc; **số nguyên ≥ 0** |
| Mô tả / yêu cầu / quyền lợi | Free text |
| Salary mode | Bắt buộc chọn **đúng một**: (1) *you'll love it* (không nhập min/max) **hoặc** (2) rõ ràng — min và/hoặc max có validation |
| Currency | **VND** (default) hoặc **USD**; dropdown nhỏ khi cần; không currency khác Phase 1 |
| Locations | Bắt buộc **≥1** chi nhánh từ company profile; được chọn nhiều; lưu **snapshot** địa chỉ tại thời điểm chọn (Explore/filter không gãy nếu chi nhánh sau đó đổi/xóa) |
| Status | Chỉ `active` \| `closed`. Tạo mới → `active` ngay. **Không** `draft` |
| Đóng / reopen | Owner đóng chủ động bất kỳ lúc nào → không còn trên Explore. Owner **reopen** → `active` lại trên Explore |
| Sửa khi active | Owner được PATCH hầu hết field (title, years, texts, salary mode/currency/amounts, locations) khi còn `active` |
| Quota | Không soft-cap số JD active / company Phase 1 |
| Quyền tạo/sửa/đóng | Chỉ owner company đã có hiring rights (`employer` + owned active company). Chưa hiring rights / non-owner → chặn rõ (403) |

### Explore JD

- Nav lớn ngang profile/settings (Aside) + route list riêng.
- List mặc định: mọi JD **`active`** (không ranking phức tạp — JM-10 out).
- Search text: **title JD** + **tên công ty**.
- Filter popup: số năm kinh nghiệm yêu cầu; mức/range lương; vị trí làm việc (search text trên địa chỉ đã gắn/snapshot vào JD).
- Filter lương theo range: JD *you'll love it* **không** nằm trong kết quả đã filter; không bật filter lương → love-it vẫn hiện trong list.
- Click item → **Vue route JD detail** (không chỉ panel tạm).
- **Chỉ user đã login** được xem Explore + detail (chuẩn bị sau này đếm view / analytics không lệch guest).

### JD detail (Sprint3)

- Nội dung JD đầy đủ (field trên + company context cần thiết).
- Cuối trang: nút **Apply** hiện nhưng **disabled** + copy “Coming next” (wire Sprint4). Không ẩn nút; không bắt buộc 501 page.

### Company — Đang tuyển vs Quản lý JD

| Surface | Ai thấy | Nội dung Sprint3 |
|---------|---------|------------------|
| Tab Đang tuyển | Visitor + owner | List JD `active` của DN |
| Tab Quản lý JD | **Chỉ owner** (visitor không thấy tab) | List/manage JD của DN; tạo/sửa/đóng/reopen; **không** list ứng viên (Sprint4) |

### Out — không nhầm vào Sprint3

- Apply popup / cover file / cover note / CV one-shot / status machine / notify apply / view-CV ACL → **Sprint4**
- List ứng viên trong màn quản lý JD detail → **Sprint4**
- Work-exp approve + employee tab → **Sprint5**
- Report JD / flag company / audit trust JD → **Sprint6** (hoặc hygiene sau)
- Notify khi đăng/đóng JD → **out** Sprint3
- Audit tạo/đóng/sửa JD → **out** Sprint3
- Ranking / recommendation phức tạp → **JM-10**
- Marketplace

## Quyết định hệ thống đã chốt (không mở lại trừ conflict)

| ID | Chốt |
|----|------|
| SAC-05 | Explore list active + search/filter; JD bắt buộc title + years experience |
| SAC-09 (phần) | Tab đang tuyển + quản lý JD owner (chưa ứng viên / employees) |
| D1 (phần) | Chỉ account có hiring rights / owner DN mới quản lý JD |
| JM-10 | Ranking phức tạp = out Sprint3 |

## Quyết định quiz đã chốt (2026-08-01)

| # | Chốt |
|---|------|
| Q1 | Explore + JD detail: **chỉ user đã login** (A) — để sau đếm view/analytics không lệch guest |
| Q2 | CTA Apply Sprint3: nút **disabled** + “Coming next” (A) |
| Q3 | Status: chỉ `active` \| `closed`; tạo = active ngay; **không draft** (A) |
| Q4 | Owner **được reopen** JD closed → active lại trên Explore (A) |
| Q5 | Locations: **bắt buộc ≥1** chi nhánh từ company profile (A) |
| Q6 | JD **snapshot** địa chỉ lúc chọn; không phụ thuộc xóa/sửa chi nhánh sau (A) |
| Q7 | Filter lương: JD *you'll love it* **bị loại** khi user đang filter theo range; không filter → love-it vẫn hiện (B) |
| Q8 | Currency: **VND \| USD**; **mặc định VND**; dropdown nhỏ chọn USD (**không** multi-currency khác) |
| Q9 | Tab Đang tuyển: **visitor + owner** thấy JD active của DN (A) |
| Q10 | Tab Quản lý JD: **chỉ owner**; visitor không thấy tab (A) |
| Q11 | Owner **PATCH** được field JD khi còn active (A) |
| Q12 | Không soft-cap số JD active Phase 1 (A) |
| Q13 | Audit tạo/đóng/sửa JD: **out** Sprint3 (A) |
| Q14 | Notify đăng/đóng JD: **out** Sprint3 (A) |
| Q15 | Nav Explore lớn trên Aside + route riêng (A) |
| Q16 | List ứng viên trong quản lý JD: **out** → Sprint4 (A) |
| Q17 | Years experience: **số nguyên ≥ 0** (A) |

## SAC liên quan sprint này

| SAC | Phạm vi Sprint3 |
|-----|-----------------|
| SAC-05 | Đủ (Explore + bắt buộc title/years) |
| SAC-09 (phần) | Đang tuyển + quản lý JD owner; **chưa** ứng viên / nhân viên |

## Ngoài phạm vi sprint này

- Apply đầy đủ / notify / view-CV / list ứng viên → **Sprint4**  
- Work-exp approve + employee tab → **Sprint5**  
- Report JD / flag company / audit JD → **Sprint6** (hoặc sau)  
- Ranking phức tạp (JM-10)  
- Marketplace  

## Prove-done gợi ý (Plan #1 sẽ chốt AC trên BR)

- Non-owner quản lý JD → 403; visitor không thấy tab Quản lý JD  
- Chưa hiring rights / không owner → không tạo/sửa/đóng/reopen JD  
- Tạo JD thiếu title hoặc years → lỗi rõ (400/422)  
- Tạo thiếu location / thiếu salary mode → lỗi rõ  
- Explore: chỉ user login; chỉ JD `active`; search title+company; filter years/salary/location khớp  
- Filter lương range → không trả JD *you'll love it*  
- Đóng JD → biến mất Explore; reopen → xuất hiện lại  
- JD detail: Apply disabled + “Coming next”  
- Tab Đang tuyển (visitor): thấy JD active của DN  
- Currency default VND; chọn USD được khi mode có số liệu lương  

---

> **Trạng thái:** Base **đủ input Plan #1** (quiz nghiệp vụ chốt 2026-08-01).  
> **Bước kế tiếp:** Plan #1 BR **đã chốt** → Plan #2 tech quiz / `plan_mode_decisions.md` + `devplan_checklist.md`.
