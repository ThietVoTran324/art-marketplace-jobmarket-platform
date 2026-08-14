# Base requirement — Admin_Sprint1 (Phase 3.1 Core shell)

> Input gốc cho **Plan #1** sprint.  
> SSOT hệ thống: [`../../Planing_docs/admin/business_requirement.md`](../../Planing_docs/admin/business_requirement.md) §3.A · Q1–Q2 · A01/A02/A06/A07 · ADM-01/07.  
> Prerequisite: Phase 0 + JM + MP **CLOSED**; Admin system Plan #1 **CHỐT** (`all suggest`).  
> Survey: [`../../Planing_docs/admin/system_survey.md`](../../Planing_docs/admin/system_survey.md).

## Bối cảnh

- Backend đã có admin API Core: xóa pin/comment, gán/thu hồi role, `GET /admin/audit` (filter).  
- Rule giữ: không tự sửa role của chính mình; mọi mutate admin đã / sẽ gắn audit (Phase 0).  
- Vue: gần như **không** có Admin product — chỉ xóa comment inline khi `hasRole('admin')`; **không** route `/admin*`.  
- Ops hiện tại: Swagger + `scripts/grant_admin.py`.

## Mục tiêu shippable (Sprint1)

1. **Admin shell** trong app Vue hiện tại: prefix `/admin/*`, chỉ user có role `admin`.  
2. **Nav tối thiểu:** Overview · Users/Roles · Audit · Content (pin/comment).  
3. **Roles UI:** gán / thu hồi role cho user khác (khớp `VALID_ROLES`: admin, artist, employer, seller).  
4. **Audit viewer UI:** xem log + filter theo năng lực API đã có.  
5. **Content moderation UI:** admin xóa pin / comment qua shell (giữ hoặc bổ sung chỗ xóa comment hiện có trên Pin).  
6. Non-admin không vào được shell (redirect / trang từ chối).  
7. Placeholder nav JM / MP (chưa queue) — hướng Sprint2–3, không implement queue.

## Ngoài phạm vi Sprint1

- KYC / credentials / JD report / suspend (→ Sprint2)  
- Copyright queue / unlist (→ Sprint3)  
- Work-exp pending list (→ Sprint4)  
- Payment / order admin · ADM-05 dispute · ADM-08 notarize  
- SIEM / analytics dashboard · đổi theme app toàn cục  
- API mới lớn (Sprint1 ưu tiên UI trên API sẵn; lookup user nếu thiếu = quyết định Plan #1/#2)

## Acceptance hướng (để Plan #1 tinh)

| ID | Hướng |
|----|--------|
| B01 | `admin` vào `/admin` dùng được |
| B02 | Non-admin bị chặn |
| B03 | Gán/thu hồi role (không self) qua UI |
| B04 | Xem audit + filter cơ bản |
| B05 | Xóa pin / comment qua UI admin |
| B06 | Không lộ queue JM/MP thật trong Sprint1 |

---

*Plan #1 input 2026-08-08 (sau system BR CHỐT).*
