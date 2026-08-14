# Base requirement — JobMarket_Sprint2 (Phase 1.2 Company + hiring-rights KYC)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (§3.D, SAC-10, D15).  
> Cắt sprint: [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint2.  
> Sau Plan #1, SSOT nghiệp vụ sprint là `business_requirement.md` trong folder này — file base **không** supersede BR.

## Bối cảnh

Sprint1 đã ship nền artist (tabs, work-exp, credentials owner, CV, Settings stub hiring-rights).  
Sprint2 bật **pháp nhân + KYC hiring rights** — điều kiện để sau này đăng JD (Sprint3) và nhận work-exp approve (Sprint5).

## Mục tiêu sprint (shippable)

1. **`companies` + `company_verification_requests`** tách record; một pháp nhân = một company; nhiều request theo thời gian.
2. **Legal-entity unique** (hard): `country + authority + type + normalized_registration_number`; raw + normalized; tách `tax_id` / `vat_number`; không unique name/domain (chỉ cảnh báo).
3. **Settings → Yêu cầu quyền tuyển dụng:** precondition; form + docs private; review English; translation khi tài liệu không English; cam kết + e-sign metadata; company email confirm.
4. **Conflict flows** theo trạng thái company (active / pending / rejected / suspended / soft-deleted) — BR §3.D.
5. **Admin API** approve / need_more_info / reject (UI = ADM-02 backlog).
6. **Sau approve:** gán role `employer` + ownership một pháp nhân; **Company profile tab** (tên, chi nhánh, ngành, mô tả, size min–max) — mutate chỉ owner có hiring rights.

## Quyết định hệ thống đã chốt (không mở lại trừ conflict)

| ID | Chốt |
|----|------|
| SAC-10 | Hiring-rights KYC + tách companies/requests + unique pháp nhân + English review |
| D15 | Unique pháp nhân; không unique name/domain; conflict theo trạng thái |
| D1 (phần) | Hiring rights sau admin duyệt KYC — không self-claim |
| JM-09 | Multi-member self-serve = out |
| ADM-02 / ADM-05 | Admin KYC UI product / tranh chấp UI = backlog |

## SAC liên quan sprint này

| SAC | Phạm vi Sprint2 |
|-----|-----------------|
| SAC-10 | Đủ (KYC + unique + conflict + English + tách record) |
| SAC-09 (phần) | Company profile tab (chưa JD manage / đang tuyển / employees) |

## Ngoài phạm vi sprint này

- Explore JD / JD CRUD / đóng JD → Sprint3  
- Apply / view-CV / notify apply → Sprint4  
- Work-exp approve + employee tab → Sprint5  
- Report JD / flag company → Sprint6  
- Multi-member (JM-09); Admin UI KYC đầy đủ (ADM-02); tranh chấp UI (ADM-05)  
- Marketplace  

## Prove-done gợi ý (Plan #1 chốt AC)

- Submit thiếu precondition → báo thiếu gì  
- Hai request cùng normalized key khi pending → chặn, không lộ requester  
- Active verified → không tạo company mới  
- Reject rồi submit lại → liên kết candidate cũ, không spawn company mới  
- User chưa hiring rights → 403 mutate company profile  
- Non-owner / non-admin không đọc file KYC private  

## Gap Plan #1 — đã đóng (xem BR §7)

| # | Chốt |
|---|------|
| 1 | Hiring rights = role `employer` + company ownership |
| 2 | Sau approve: **org account** — profile chính **thay** artist bằng company profile |
| 3 | Authority VN có thể default `NATIONAL` |
| 4 | Company email confirm in-scope |
| 5 | Audit KYC trust actions (allowlist → Plan #2) |
| 6 | Admin review = API-only |
| 6b | **Pending trùng key: nhiều request OK; admin chọn** (quiz Q6=B) |

---

*Tạo 2026-07-27 — input Plan #1 JobMarket_Sprint2. Plan #1 BR chốt cùng ngày.*
