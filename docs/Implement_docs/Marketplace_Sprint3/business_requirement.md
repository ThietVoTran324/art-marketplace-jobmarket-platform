# Business Requirements — Marketplace_Sprint3 (Phase 2.3 Payment methods)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**SSOT hệ thống:** [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Prerequisite:** Marketplace_Sprint2 **CLOSED** (`e1f2a3b4c5d6`)

> **Plan #1 CHỐT 2026-08-08** — cắt §3.C + D2; mở rộng từ minimal method Sprint2.

---

## 1. Mục tiêu

Ship **payout destination** đủ dùng trước order/SePay:

| # | Năng lực |
|---|----------|
| 1 | Seller quản lý payment methods (bank / e-wallet) đầy đủ hơn Sprint2 |
| 2 | Có **một method mặc định** (primary) để Sprint4 payout về đúng chỗ |
| 3 | Hoa hồng platform **% config** (default có thể 0) — hiển thị / đọc được |
| 4 | FE quản lý method riêng (Settings hoặc Seller payout panel) |
| 5 | Vẫn **không** ví nội bộ / số dư platform |

**Không** charge buyer / webhook (Sprint4).

---

## 2. Actors

| Actor | Sprint3 |
|-------|---------|
| Seller | CRUD methods; chọn primary; xem % hoa hồng (ước tính) |
| Hệ thống | Gate P vẫn đếm method active ≥1; lưu commission config |
| Buyer | Không đổi (chưa checkout) |

---

## 3. Payment method (nghiệp vụ)

| Quy tắc | Chốt |
|---------|------|
| Loại | `bank` · `e_wallet` (giữ; mở rộng field theo Plan #2) |
| Primary | Mỗi seller tối đa **1** method `is_primary=true` (active) |
| Active | Method inactive **không** tính vào gate P |
| Xóa / deactivate method cuối | Nếu seller còn listing `listed` → **chặn** hoặc bắt unlist trước (chốt Plan #2 suggest: **403** nếu sẽ làm P=0 trong khi còn listed) |
| Dữ liệu nhạy cảm | MVP lưu identifier text (STK/ví); không PCI card |
| Ví nội bộ | **Không** |

### Hoa hồng (D2)

- `MP_PLATFORM_COMMISSION_PERCENT` (config, decimal hoặc basis points — Plan #2).  
- Default MVP: **0**.  
- Sprint3: expose config + (optional) công thức ước tính seller net = price − commission; **chưa** trừ tiền thật.

---

## 4. Acceptance criteria

| AC | Mô tả |
|----|-------|
| AC-01 | Seller tạo/sửa/list/deactivate method với field mở rộng (ít nhất: type, display, identifier + primary) |
| AC-02 | Set primary: chỉ 1 primary active |
| AC-03 | Gate P chỉ đếm method `is_active` |
| AC-04 | Không thể để P=0 khi còn pin `listed` (block deactivate/delete last) |
| AC-05 | Đọc được commission % từ config/API |
| AC-06 | FE trang/panel quản lý payout (không chỉ PinView create tối thiểu) |
| AC-07 | Không có balance/wallet endpoint |

---

## 5. Ngoài phạm vi

- Order / SePay / chuyển khoản thật  
- VNPay · refund · KYC nhà nước  
- Copyright  

---

## 6. Trace → Plan #2

AC → `plan_mode_decisions.md` + checklist.

**Plan #2 quiz gợi ý:**

1. Mở rộng cột: A) thêm `bank_name` / `account_holder` · B) JSON `metadata`  
2. Primary: A) cột `is_primary` · B) bảng preference riêng  
3. Chặn xóa method cuối khi còn listed: A) 403 **(suggest)** · B) auto-unlist  
4. Commission: A) percent float settings · B) basis points int  
5. FE: A) `/settings` payout section **(suggest)** · B) trang `/seller/payout` mới  

Trả lời `q1…` hoặc **all suggest**.
