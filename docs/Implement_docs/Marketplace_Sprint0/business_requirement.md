# Business Requirements — Marketplace_Sprint0 (Phase 0-market)

**Mức chi tiết:** ~3/10 (business). Schema/route chi tiết → Plan #2.  
**SSOT hệ thống:** [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)

> **Plan #1 CHỐT 2026-08-08** — cắt từ system BR §3.0 + C08/C10 + D10.

---

## 1. Mục tiêu

Ship **nền dữ liệu** để eligibility Marketplace sau này đúng số:

| # | Năng lực |
|---|----------|
| 1 | Mọi pin có `created_at` (UTC) |
| 2 | View count **bền** theo pin (`pin_stats`) |
| 3 | Không spam like pin / follow (unique pair) |
| 4 | Cho phép wipe pin cũ (D10) khi conflict |

**Không** ship UI bán, watermark, payment trong sprint này.

---

## 2. Actors & hành vi

| Actor | Sprint0 |
|-------|---------|
| User login | Like pin / follow như cũ; trùng bị chặn |
| Hệ thống / Celery | Recommend vẫn có thể xóa `users_view_pins`; **không** xóa `pin_stats` |
| Dev/admin local | Có thể chạy wipe pins khi cần sạch DB |

---

## 3. Acceptance criteria (nghiệp vụ)

| AC | Mô tả | Case |
|----|-------|------|
| AC-01 | Cột `pins.created_at` tồn tại; pin mới luôn có timestamp | C10 |
| AC-02 | Pin còn lại sau migration/wipe có `created_at` không null | C10 |
| AC-03 | Mỗi pin có (hoặc tạo lazy) bản ghi stats; `view_count` tăng khi user xem pin theo luồng hiện có | — |
| AC-04 | Sau khi recommend purge `users_view_pins`, `view_count` **giữ nguyên** | — |
| AC-05 | Cùng user không like cùng pin 2 lần (DB enforce) | C08 |
| AC-06 | Cùng follower không follow cùng following 2 lần (DB enforce) | C08 |
| AC-07 | API like/follow trùng → không tạo row thứ 2 (409 hoặc idempotent 2xx rõ) | C08 |
| AC-08 | (Optional local) Wipe pins + quan hệ liên quan chạy được; DB sẵn sàng Sprint1 | C10 |

---

## 4. Quy tắc dữ liệu (business)

1. **Views bền** = tổng lượt xem đã ghi vào stats; không phải “đang còn trong bảng view tạm”.  
2. **M eligibility sau này** đọc từ `pin_stats` (tổng theo seller) — Sprint2; Sprint0 chỉ đảm bảo số đúng.  
3. **Like comment** giữ như cũ; unique sprint này tập trung **like pin** + **follow**. (Unique like comment = hygiene cùng migration nếu rẻ.)  
4. **Wipe** không bắt buộc production path — được phép và khuyến nghị local khi conflict (D10).

---

## 5. Ngoài phạm vi

- Media preview/original (Sprint1)  
- Eligibility N/M/K UI (Sprint2)  
- Mọi payment / order / refund  

---

## 6. Trace → Plan #2 / checklist

AC-01..08 → `plan_mode_decisions.md` + steps P0–P6 trong `devplan_checklist.md`.
