# Phase 0-market & block classification — Marketplace

> **Ngày:** 2026-08-06  
> **Mục đích:** Phân loại block **bắt buộc trước bán license**, block theo sprint 2.x, và điểm khó cố định.  
> **SSOT phase map:** [`../marketplace_jobmarket_feasibility_phase_plan.md`](../marketplace_jobmarket_feasibility_phase_plan.md)  
> **Prerequisite:** Job Market Phase 1 **CLOSED**; Phase 0-core **CLOSED**.

---

## 1. Đã có từ Phase 0-core + Job Market (tái dùng)

| Block | Sẵn | Ghi chú Marketplace |
|-------|-----|---------------------|
| Auth cookie / CSRF / CORS / TrustedHost | Yes | Giữ |
| `user_roles` + `require_roles` | Yes | Role **`seller`** đã có catalog — behavior chưa gắn |
| Ownership / audit helpers | Yes | Mở rộng action order/license/report |
| Celery + Pillow/OpenCV | Yes | Watermark / preview pipeline |
| Pin upload pipeline | Yes | Phải **đổi** serve path (hiện lộ original) |
| Updates / SSE / email | Yes | Notify paid / eligibility |
| Chat | Yes | Buyer–seller optional sau (không MVP cứng) |

**Không** mở lại Phase 0-core. Không kéo ADM-* Job Market vào đây.

---

## 2. Phase 0-market — block **phải có** trước eligibility / listing thật

| ID | Block | Vì sao bắt buộc | Risk nếu bỏ |
|----|-------|-----------------|-------------|
| **0.1** | `pins.created_at` + backfill **hoặc wipe pins** (D10: DB ít pin, được xóa nếu conflict) | Đếm tuổi / lịch sử đăng | Eligibility sai |
| **0.2** | `pin_stats` (view bền vững ± like aggregate) | View hiện bị xóa sau recommend | Không có M engagement thật |
| **0.3** | Unique `(follower, following)` / `(user, pin)` likes | Chống spam follow/like | Gian lận ngưỡng K followers |

> 0.1–0.3 = **Marketplace_Sprint0**. Pin cũ: **không bắt buộc** migrate phức tạp — được truncate nếu conflict code mới (Plan #1 D10).

---

## 3. Điểm khó cố định (không negotiable kiến trúc)

### H1 — File gốc đang lộ

`GET /pins/upload/{id}` phục vụ **original** cho mọi user login → bán license vô nghĩa nếu chưa:

1. Tách `original/` (private) vs `preview/` (watermark)  
2. Public/feed **chỉ** preview  
3. Original: owner **hoặc** buyer đã `paid` (+ signed URL)

### H2 — Eligibility phụ thuộc dữ liệu chưa có

Rule “N pins / M views / K followers + payment method” **không implement được đúng** trước 0-market + payment_methods.

### H3 — Webhook thanh toán

SePay/VNPay: idempotent webhook, state machine order, không cấp quyền 2 lần, không tin client “đã trả”.

### H4 — DRM tuyệt đối

**Không** làm (NO-02). Chỉ watermark + ACL + audit/report.

---

## 4. Block theo Phase 2.x (sau 0-market)

| Phase | In | Out / sau |
|-------|-----|-----------|
| **2.1** Media tách lớp | Watermark Celery; ACL original; signed download | DRM; dynamic watermark phức tạp nếu chưa chốt |
| **2.2** Listing + gate | `pin_licenses` / seller profile; UI bán; check eligibility | Ranking marketplace phức tạp |
| **2.3** Payment method | Payout destination seller | Full KYC ngân hàng nhà nước nếu chưa cần |
| **2.4** Order + pay | Orders + webhook + quyền sau paid | Refund/chargeback đầy đủ nếu defer |
| **2.5** Copyright | Report + hash + certificate tối thiểu | Court workflow; Admin UI product-grade |

---

## 5. Phân loại “làm ngay / song song / defer”

| Loại | Mục |
|------|-----|
| **Trước code domain bán** | 0.1–0.3 + 2.1 media rewrite |
| **Song song sprint** | Audit actions mới; FE CreatePin/PinView; env SePay/VNPay sandbox |
| **Defer** | DRM; ví nội bộ phức tạp (nếu chọn payout thẳng); Admin UI lớn; chat bắt buộc theo order |

---

## 6. Kết luận handoff

| Câu hỏi | Trả lời |
|---------|---------|
| Đủ để mở planning Marketplace? | **Có** — JM xong; feasibility đủ |
| Block platform bắt buộc trước listing? | **0-market + 2.1** |
| Admin UI JM có chặn Marketplace? | **Không** — backlog riêng |
| Việc đầu tiên sau file này? | Plan #1 chốt BR hệ thống → sync `sprint_map.md` → mới mở Implement |
