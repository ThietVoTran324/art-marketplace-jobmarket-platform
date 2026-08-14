# Base requirement — Admin_Sprint2 (Phase 3.2 JM ops)

> Input gốc cho **Plan #1** sprint.  
> SSOT hệ thống: [`../../Planing_docs/admin/business_requirement.md`](../../Planing_docs/admin/business_requirement.md) §3.B · ADM-02, ADM-03, ADM-04, ADM-06.  
> Prerequisite: **Admin_Sprint1 CLOSED** (shell `/admin`, guard, overview counts).  
> Survey: [`../../Planing_docs/admin/system_survey.md`](../../Planing_docs/admin/system_survey.md).

## Bối cảnh

- Shell Admin đã có; nav JM đang **“Soon”**.  
- Backend JM admin API đã ship (Swagger-first):

| Area | API sẵn |
|------|---------|
| KYC | `GET /job-market/admin/hiring-rights-requests`; approve / need-more-info / reject; download doc file |
| Credentials | Admin create / patch / delete `.../admin/users/{id}/credentials` + public list `GET /job-market/users/{id}/credentials` |
| JD reports | `GET .../admin/job-reports`; dismiss / actioned |
| Company | suspend / unsuspend |

- **Gap biết trước:** không có `GET` admin **list documents** theo request (chỉ download theo `doc_id`) — Plan #1/#2 phải chốt cách admin biết `doc_id` (API list mới vs embed).

## Mục tiêu shippable (Sprint2)

1. Bật nav **Job Market** trong Admin shell (không còn Soon).  
2. **KYC queue UI:** list/filter status; detail; approve / need-more-info (note) / reject (reason); xem/tải documents.  
3. **Credentials override UI:** chọn user id → list → create / edit / delete (admin).  
4. **JD reports queue UI:** list (mặc định open); dismiss / actioned (+ note).  
5. **Suspend / unsuspend company** từ luồng report (hoặc màn company id).  
6. Overview Sprint1: counts KYC/JD vẫn đọc được; có thể deep-link từ card “Soon” → queue thật.

## Ngoài phạm vi Sprint2

- ADM-05 dispute / multi-claim product  
- ADM-08 notarize  
- Copyright queue / unlist (→ Sprint3)  
- Work-exp pending list (→ Sprint4)  
- Payment admin · analytics

## Acceptance hướng (để Plan #1 tinh)

| ID | Hướng |
|----|--------|
| B01 | Admin mở `/admin/...` JM queues |
| B02 | Duyệt KYC (approve / need-more / reject) qua UI = cùng hiệu ứng API |
| B03 | Xem/tải KYC docs trong UI |
| B04 | Override credentials user khác |
| B05 | Xử lý JD report + suspend/unsuspend company |
| B06 | Non-admin vẫn 403 / redirect (giữ Sprint1) |

---

*Plan #1 input 2026-08-11 (sau Admin_Sprint1 CLOSED).*
