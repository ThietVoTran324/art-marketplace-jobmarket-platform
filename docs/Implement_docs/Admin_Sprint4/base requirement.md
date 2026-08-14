# Base requirement — Admin_Sprint4 (Phase 3.4 work-exp queue)

> Input gốc cho **Plan #1**.  
> SSOT hệ thống: [`../../Planing_docs/admin/business_requirement.md`](../../Planing_docs/admin/business_requirement.md) §3.B · **Q4 CHỐT** (GET pending list + UI).  
> Prerequisite: Admin_Sprint2 **CLOSED** (JM admin UI pattern).  
> Survey gap: admin approve/reject **by id** đã có; **thiếu** admin pending list.

## Bối cảnh

- Artist tạo work-exp gắn company → status `pending` (company owner đã có queue `/me/company/work-experiences/pending`).  
- Admin API sẵn:  
  `POST /job-market/admin/work-experiences/{id}/approve`  
  `POST /job-market/admin/work-experiences/{id}/reject`  
- **Gap:** không có `GET` admin list pending toàn hệ thống → operator phải biết id hoặc dùng Swagger/SQL.  
- System Q4: thêm GET pending list + UI.

## Mục tiêu shippable

1. **API** admin list work-exp pending (filter tối thiểu).  
2. **UI** `/admin/work-experiences` (hoặc tương đương): list pending → approve / reject.  
3. Nav Admin: link Work exp (bỏ Soon nếu còn).  
4. Overview (optional quiz): count pending WE — cần metric mới hoặc bỏ.  
5. Smoke: list + approve/reject qua admin.

## Ngoài phạm vi

- ADM-05 dispute · payment admin · analytics  
- Đổi rule owner self-approve (đã có)  
- Backfill / auto-link company (JM-03 out)

## Acceptance hướng

| ID | Hướng |
|----|--------|
| B01 | Admin list được pending work-exp |
| B02 | Approve / reject qua UI = cùng API hiện có |
| B03 | Non-admin 403 |
| B04 | Owner queue vẫn hoạt động độc lập |

---

*Plan #1 input 2026-08-11.*
