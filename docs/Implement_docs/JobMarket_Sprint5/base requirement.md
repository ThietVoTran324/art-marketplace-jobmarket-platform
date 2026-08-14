# Base requirement — JobMarket_Sprint5 (Phase 1.5 Work-exp approve + employees)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (§3.A approve work-exp; §3.C tab nhân viên).  
> Cắt sprint: [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint5.  
> Sau Plan #1, SSOT nghiệp vụ sprint là `business_requirement.md` trong folder này — file base **không** supersede BR.  
> Prerequisite: [`../JobMarket_Sprint4/`](../JobMarket_Sprint4/) **CLOSED** (Alembic `f6a7b8c9d0e1`).  
> Deferred: JM-03 backfill, JM-04 email-token ngoài hệ thống, JM-05 badge tổng.

## Bối cảnh

Sprint1: work-exp CRUD + status `pending`|`approved`; company **free-text** (chưa FK company).  
Sprint2: `companies` + org owner sau KYC.  
Sprint3–4: JD / apply (không đụng approve work-exp).  
Sprint5 bật **approve khi gắn company trong hệ thống** + **tab Employees** trên org profile.

## Mục tiêu sprint (shippable)

1. **Link work-exp → company trong hệ thống** (khi artist chọn / gắn DN có tài khoản): notify **email + in-app** tới owner company; deep-link tab work-exp artist; UI approve **đúng dòng**.
2. **Approve / reject** dòng work-exp bởi **owner** company đúng pháp nhân; cập nhật status; **audit** (hệ thống đã chốt audit cho approve work-exp).
3. **Free-text / off-system company:** luôn `pending` (chưa approve); **không** gửi approve notify; **không** email-token ngoài (JM-04 out).
4. **Không backfill** khi company xuất hiện sau (JM-03 out) — user tự sửa dòng nếu muốn gắn.
5. **Employee tab (org):**  
   - List **tự động** artist có work-exp gắn company này với khoảng **past → present** (đang làm: `end_date` null hoặc ≥ today — chi tiết quiz).  
   - Sort mặc định theo thời điểm gia nhập (timeline).  
   - **Head people:** free CRUD block đầu — chỉ user hệ thống **đang làm** tại company.  
   - **Public / private** setting; private → hard block non-owner.

## Spec đã gom (input Plan #1)

### Work-exp approve

| Nhóm | Rule (hướng hệ thống) |
|------|------------------------|
| Off-system | Luôn chưa approve; không notify approve |
| On-system | Pending đến khi owner approve; có reject (quiz chi tiết) |
| Ai approve | Owner company của pháp nhân được gắn |
| Notify | Email + in-app; link tab work-exp + đúng dòng |
| Audit | Có (append-only) khi approve/reject thành công |
| Artist sửa dòng sau approve | Quiz (reset pending? giữ approved?) |

### Employees

| Nhóm | Rule (hướng hệ thống) |
|------|------------------------|
| Auto list | Derived từ work-exp gắn company + đang làm |
| Sort | Theo gia nhập (start / approved — quiz) |
| Head | CRUD owner; chỉ user hệ thống đang present |
| Visibility | Public \| private; private = owner-only API |

### Out

- JM-03 backfill · JM-04 email-token ngoài · JM-05 badge tổng  
- University approve · Sprint6 report/flag  

## Quyết định hệ thống đã chốt

| ID | Chốt |
|----|------|
| SAC-02 | Phần còn lại: approve + notify đúng dòng |
| SAC-09 (phần) | Employee tab |
| D4 | Off-system luôn unapproved; không email-token; không backfill |
| D11 | Badge tổng = out (JM-05) |
| Audit | Approve work-exp ghi audit khi thành công |

## Prove-done gợi ý

- Free-text company → không notify approve  
- Chỉ owner approve đúng dòng / đúng company  
- Private employees → non-owner 403  
- Head chỉ chấp nhận user đang present tại company  
- On-system create/link → owner nhận notify  

---

> **Trạng thái:** Base đủ. Plan #1 BR **CHỐT** 2026-08-01 (all suggest Q1–Q39).  
> **Bước kế tiếp:** Plan #2 tech.
