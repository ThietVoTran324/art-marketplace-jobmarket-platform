# Marketplace — system survey (codebase readiness)

> **Ngày:** 2026-08-06  
> **Phạm vi:** Backend + Vue readiness trước Phase 0-market + 2.1–2.5.  
> **Không** thay BR — chỉ inventory.

---

## 1. Verdict

| Layer | Ready? | Ghi chú |
|-------|--------|---------|
| Auth / CSRF / roles catalog (`seller`) | Yes | Behavior seller **chưa** gắn route |
| Pin create / media save | Yes | Serve original **chưa** ACL |
| Persistent pin `created_at` | **No** | MP-01 |
| Persistent view/engagement stats | **No** | View bị purge sau recommend |
| Unique likes / follows | **No** | MP-03 |
| Watermark / preview pipeline | Partial | Pillow/OpenCV có; chưa tách thư mục + task chuẩn |
| Order / payment / webhook | **No** | Zero remnant |
| License / seller_profiles | **No** | |
| Vue CreatePin / PinView | Yes shell | Chưa UI “Bán quyền” |
| System BR / sprint map | **CHỐT** | Plan #1; Implement Sprint0 Plan #2 CHỐT |

---

## 2. Backend — gap quyết định

### Pins & media

- `PinsOrm`: có `image` path; **không** `created_at` (survey feasibility §2.1).
- `GET /pins/upload/{id}`: FileResponse full — **không** check owner/license (§2.4).
- Media root: `settings.MEDIA_PATH` — cần convention `pins/original/` vs `pins/preview/`.

### Engagement

- `users_view_pins`: quan hệ user–pin; Celery recommend **xoá** view sau job → không dùng làm M bền.
- `LikesOrm` / `SubsrciptionsOrm`: thiếu unique pair → spam được.

### Roles

- `seller` trong `VALID_ROLES` từ Phase 0 — cần quyết định: auto-assign khi pass eligibility hay flag trên `seller_profiles` / capability riêng.

### Payment

- Không có `orders`, `payment_methods`, webhook handlers, idempotency keys.

---

## 3. Frontend — có sẵn

| Thành phần | Dùng cho |
|------------|----------|
| `CreatePinView` / pin upload FormData | Hook “enable license sale” |
| `PinView` | CTA mua / giá / tải original |
| Toast / updates store | Notify paid / eligibility |
| Axios CSRF interceptor | Checkout POST |

Chưa có: checkout UI, seller settings payment method, license badge trên pin card.

---

## 4. Rủi ro mở sprint sai thứ tự

1. Làm 2.4 payment trước 2.1 → bán file đang public.  
2. Làm 2.2 gate trước 0-market → rule N/M/K sai số.  
3. Nhét Admin UI JM vào MP → lệch scope.

---

## 5. Kết luận survey

**Ready để Plan #1 BR.**  
**Chưa ready code listing/payment** cho đến khi chốt D* + có sprint 0-market/2.1 trên map.
