# Business Requirements — Marketplace (system level)

**Mục đích:** SSOT nghiệp vụ cấp **hệ thống** cho Marketplace (Phase 0-market + Phase 2.1–2.5).  
**Mức chi tiết:** ~3/10 (business). Schema/route → `Implement_docs/Marketplace_SprintN/` sau khi chốt.  
**Nguồn:** feasibility phase plan; survey 2026-08-06; Plan #1 quiz 2026-08-08.

> **Trạng thái:** Plan #1 **CHỐT 2026-08-08** (D1–D10).  
> Implement: [`../../Implement_docs/Marketplace_Sprint0/`](../../Implement_docs/Marketplace_Sprint0/) — Plan #2 **CHỐT**; Sprint1–5 template sẵn.

---

## 1. Bối cảnh & mục tiêu

### Bối cảnh

- Web gốc: pin social free; Phase 0-core + Job Market Phase 1 **CLOSED**.
- File gốc pin hiện ai login cũng tải được → phải tách preview/original trước khi bán.
- Lượng pin DB hiện **ít** — được phép **xóa sạch pin cũ** nếu conflict với pipeline mới (D10).

### Mục tiêu Phase 2 (+ 0-market)

1. Nền dữ liệu eligibility: `created_at`, stats bền, unique follow/like.  
2. Media: preview watermark static vs original ACL + signed URL.  
3. Seller đủ điều kiện (role `seller`) bật bán license **một lần / pin** (personal use).  
4. Buyer (email verified) thanh toán **SePay-first**, currency **USD mặc định** (có VND).  
5. Copyright report + certificate tối thiểu (API).  
6. **Không** luồng trả hàng / refund trong hệ thống.

### Ngoài phạm vi

- DRM tuyệt đối (NO-02)  
- Refund / return / chargeback workflow (D7)  
- Ví nội bộ + rút (D2 = payout thẳng qua method đã lưu)  
- VNPay song song MVP (sau SePay)  
- Admin UI product-grade; ADM-* Job Market  
- Ranking marketplace phức tạp  

---

## 2. Actors

| Actor | Vai trò |
|-------|---------|
| Seller | Pass gate → role `seller`; listing; nhận tiền qua payment method đã lưu |
| Buyer | Login + email verified; mua license pin **không phải của mình** |
| Visitor / login thường | Chỉ preview watermark |
| Owner pin | Luôn tải original của mình |
| Admin | Copyright report API |
| Hệ thống | Watermark; SePay webhook idempotent; cấp quyền; notify; **không** refund |

---

## 3. Năng lực theo mặt sản phẩm

### 3.0 — Phase 0-market

- `pins.created_at` (+ backfill **hoặc** wipe pin cũ theo D10 rồi tạo mới).  
- `pin_stats` view bền.  
- Unique likes `(user_id, pin_id)` + unique follows `(follower_id, following_id)`.

### 3.A — Media (2.1)

- Original private; preview **static watermark** (logo/site).  
- Feed/public → preview only.  
- Original: owner hoặc buyer đã `paid`; signed URL TTL ngắn.  
- Pin tồn tại sau Sprint1 phải đi pipeline mới; pin cũ conflict → **được xóa** (D10).

### 3.B — Eligibility & listing (2.2)

**Pass gate khi đủ tất cả:**

| Điều kiện | Giá trị MVP (config được) |
|-----------|---------------------------|
| Payment method nhận tiền | Bắt buộc (≥1) |
| Số pin | **N ≥ 5** |
| Views bền (tổng pin seller hoặc rule implement chi tiết sprint) | **M ≥ 100** |
| Followers unique | **K ≥ 10** |

Khi pass → gán role **`seller`** (D5).  
License MVP: **một lần / một pin**, perpetual **personal use** (D1).  
UI: CreatePin / PinView “Bán quyền sử dụng”.

### 3.C — Payment method (2.3)

- Seller lưu bank / e-wallet (định danh nhận tiền).  
- Platform **không** giữ số dư ví nội bộ.  
- Hoa hồng platform: **% config** (có thể 0 lúc đầu) — trừ khi payout (logic chi tiết Sprint3/4).

### 3.D — Order & thanh toán (2.4)

- Order: `pending` → `paid` | `failed` | `cancelled`.  
- Provider MVP: **SePay trước**; VNPay sau.  
- Currency: **USD mặc định**; hỗ trợ **VND** (D8).  
- Webhook idempotent; chỉ `paid` → cấp quyền tải + email.  
- **Không** state/machine refund/return trong hệ thống (D7). Tranh chấp tiền = ngoài hệ thống / vận hành tay.

### 3.E — Copyright (2.5)

- Attestation khi **create/relist listing** (không bắt buộc trên upload pin thường).  
- File hash; `copyright_reports`; admin API.  
- License certificate tối thiểu sau paid.

---

## 4. Case chính (acceptance hướng hệ thống)

| ID | Case | Kỳ vọng |
|----|------|---------|
| C01 | Xem pin chưa mua | Preview only |
| C02 | Original chưa mua | 403 |
| C03 | Owner original | 200 |
| C04 | Buyer paid → original | 200 / signed URL |
| C05 | Webhook trùng | Không cấp quyền 2 lần |
| C06 | Thiếu N/M/K hoặc thiếu payment method | Không bật bán / không `seller` |
| C07 | Đủ gate | Role `seller` + được listing |
| C08 | Follow/like trùng | DB reject |
| C09 | Copyright report | Tạo + admin API |
| C10 | Pin cũ conflict pipeline | Được wipe; pin mới bắt buộc pipeline 2.1 |
| C11 | Tự mua pin mình | Chặn |
| C12 | Buyer chưa email verified | Chặn checkout |
| C13 | User yêu cầu refund trong app | **Không hỗ trợ** — không có luồng |

---

## 5. Quyết định đã chốt (Plan #1)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **D1** | License | Một lần / pin · perpetual personal use |
| **D2** | Payout | Lưu STK/ví seller; không ví nội bộ; hoa hồng % config |
| **D3** | Watermark | Static trên preview |
| **D4** | Eligibility | Payment method + N=5 + M=100 views + K=10 followers (config) |
| **D5** | Seller | Pass gate → gán role `seller` |
| **D6** | Provider | SePay-first; VNPay sau |
| **D7** | Refund/return | **Không** trong hệ thống |
| **D8** | Currency | VND + USD; **USD mặc định** |
| **D9** | Buyer rules | Login + email verified; không tự mua pin mình |
| **D10** | Pin cũ | DB ít pin → **được xóa** nếu conflict code/pipeline mới; không bắt buộc giữ/migrate phức tạp |

---

## 6. Traceability sprint

Xem [`sprint_map.md`](sprint_map.md) (**Synced** sau Plan #1).

| Phase | Sprint | Gói |
|-------|--------|-----|
| 0-market | Marketplace_Sprint0 | created_at / stats / unique (± wipe pins) |
| 2.1 | Marketplace_Sprint1 | Media tách lớp |
| 2.2 | Marketplace_Sprint2 | Gate + listing |
| 2.3 | Marketplace_Sprint3 | Payment methods |
| 2.4 | Marketplace_Sprint4 | Order + SePay |
| 2.5 | Marketplace_Sprint5 | Copyright |

---

## 7. Quy tắc AI / implement

1. File này = SSOT nghiệp vụ hệ thống sau 2026-08-08.  
2. Không payment trước Sprint0+1 CLOSED.  
3. Không thêm refund flow trừ khi đổi BR.  
4. Tech → Plan #2 trong từng Implement sprint.

---

> **Plan #1 CHỐT 2026-08-08.** Sẵn mở Implement bắt đầu **Marketplace_Sprint0**.
