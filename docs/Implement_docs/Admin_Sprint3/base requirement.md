# Base requirement — Admin_Sprint3 (Phase 3.3 MP copyright)

> Input gốc cho **Plan #1** sprint.  
> SSOT hệ thống: [`../../Planing_docs/admin/business_requirement.md`](../../Planing_docs/admin/business_requirement.md) §3.C · **Q3 CHỐT** resolve → unlist · A05 · SEC-T2-01/02/08.  
> Prerequisite: **Admin_Sprint1 CLOSED** (shell `/admin`). Sprint2 CLOSED (nav pattern).  
> Survey: [`../../Planing_docs/admin/system_survey.md`](../../Planing_docs/admin/system_survey.md).

## Bối cảnh

- Marketplace Sprint5 đã ship: user tạo `copyright_reports`; admin API  
  `GET/PATCH /admin/copyright-reports` (status `open` → `resolved` \| `dismissed` + note).  
- **Hiện resolve/dismiss chỉ đổi status report** — **không** đổi `pin_listings` (SEC-T2-01).  
- System Admin BR **đã CHỐT:** resolve → **unlist listing**; **không** revoke `pin_license_access` trong MVP.  
- FE: Overview card copyright vẫn “Soon”; nav “Marketplace · Soon”.  
- Rate-limit tạo report (SEC-T2-02) gắn sprint này hoặc hardening — Plan #1 chốt.

## Mục tiêu shippable (Sprint3)

1. Bật nav / route **Copyright** trong Admin (bỏ Soon MP cho queue này).  
2. **Copyright queue UI:** list/filter (mặc định open); resolve / dismiss (+ note).  
3. **Khi resolve:** đồng thời **unlist** listing của pin (nếu đang listed).  
4. Dismiss: **không** unlist (đề xuất — confirm Plan #1).  
5. Overview: deep-link card copyright → queue.  
6. (Optional quiz) Rate-limit tạo copyright report.  
7. Smoke: resolve → listing `unlisted`; dismiss không đụng listing; UI/API AC.

## Ngoài phạm vi Sprint3

- Revoke / thu hồi `pin_license_access`  
- Order / payout / SePay admin  
- Work-exp queue (→ Sprint4)  
- DRM / court / auto-takedown ngoài unlist  
- ADM-05 / ADM-08  

## Acceptance hướng (để Plan #1 tinh)

| ID | Hướng |
|----|--------|
| B01 | Admin mở queue copyright từ nav / Overview |
| B02 | List + filter reports; resolve / dismiss |
| B03 | Resolve → listing pin chuyển `unlisted` (nếu có) |
| B04 | Buyer đã owned vẫn giữ access (không revoke) |
| B05 | Dismiss không unlist (nếu CHỐT vậy) |
| B06 | Non-admin 403 / redirect (giữ shell) |

---

*Plan #1 input 2026-08-11 (sau Admin_Sprint2 CLOSED).*
