# Base requirement — Marketplace_Sprint0 (Phase 0-market)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md) (D1–D10).  
> Cắt sprint: [`../../Planing_docs/marketplace/sprint_map.md`](../../Planing_docs/marketplace/sprint_map.md) § Marketplace_Sprint0.  
> Sau Plan #1, SSOT nghiệp vụ sprint là `business_requirement.md` trong folder này — file base **không** supersede BR.

## Bối cảnh

Job Market Phase 1 CLOSED. Marketplace chưa bán được đúng vì thiếu nền dữ liệu:

- `pins` **không** có `created_at` (MP-01).
- View engagement gắn `users_view_pins` rồi bị Celery recommend **xóa** → không dùng làm M bền (MP-02).
- `likes` (pin) / `subscriptions` **không** unique pair → spam follower/like (MP-03).

Lượng pin DB hiện ít — Plan #1 D10: **được xóa pin cũ** nếu conflict với migration/constraint/pipeline.

## Mục tiêu sprint (shippable)

1. **`pins.created_at`** timestamptz — mọi pin mới có timestamp; pin còn lại sau wipe/backfill có giá trị hợp lệ.
2. **`pin_stats`** (hoặc tương đương) lưu **view count bền** theo pin — không phụ thuộc hàng `users_view_pins` còn sống.
3. **Unique** like `(user_id, pin_id)` khi like pin; **unique** follow `(follower_id, following_id)`.
4. API like/follow: trùng → reject rõ (409) hoặc idempotent; **không** tạo bản ghi trùng.
5. Smoke prove C08 (unique) + C10 (wipe/created_at path).
6. Optional: script wipe pins (+ cascade) cho môi trường local/dev khi cần sạch trước Sprint1.

## Quyết định hệ thống đã chốt (không mở lại)

| ID | Chốt liên quan Sprint0 |
|----|------------------------|
| D4 | Gate N/M/K cần stats + unique follow — nền ở đây |
| D10 | Wipe pin cũ OK nếu conflict |
| MP-01..03 | In-scope sprint này |

## Case liên quan

| Case | Kỳ vọng Sprint0 |
|------|-----------------|
| C08 | Follow/like trùng → DB/API reject |
| C10 | Pin cũ conflict → được wipe; pin mới có `created_at` |

## Ngoài phạm vi sprint này

- Watermark / original ACL / signed URL → Sprint1  
- Seller gate / listing / role assign behavior → Sprint2  
- Payment methods → Sprint3  
- Orders / SePay → Sprint4  
- Copyright → Sprint5  
- Refund (D7 never) · DRM (NO-02)

## Prove-done gợi ý

- Migration upgrade sạch từ `b8c9d0e1f2a3`.
- Insert like/follow trùng fail.
- Ghi view → `pin_stats.view_count` tăng; xóa `users_view_pins` (simulate recommend) **không** làm mất count.
- (Optional) wipe pins script chạy được trên local.

---

*Tạo 2026-08-08 — input Plan #1 sprint.*
