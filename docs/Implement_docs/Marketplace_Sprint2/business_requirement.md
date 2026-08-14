# Business Requirements — Marketplace_Sprint2 (Phase 2.2 Listing + gate)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2 (đã chốt).  
**SSOT hệ thống:** [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Prerequisite:** Sprint0 + Sprint1 **CLOSED** (`d0e1f2a3b4c5`)

> **Plan #1 CHỐT 2026-08-08** — §3.B + D1 D4 D5 D8 + C06 C07 C11.  
> **Plan #2 CHỐT 2026-08-08** — all suggest Q1–Q5 A → [`plan_mode_decisions.md`](plan_mode_decisions.md) + [`devplan_checklist.md`](devplan_checklist.md).

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | Eligibility N / M / K / payment method (config) |
| 2 | Pass + enable → role `seller` |
| 3 | Listing personal-use one-shot trên pin mình (`pin_listings`) |
| 4 | FE CreatePin + PinView bán; không CTA tự mua |
| 5 | Minimal payment method để thỏa điều kiện P |

**Không** SePay/checkout (Sprint4).

---

## 2. Actors

| Actor | Hành vi |
|-------|---------|
| User dưới ngưỡng | Xem eligibility; không enable seller; không listing mới |
| Seller | Listing/unlisted pin mình; method tối thiểu |
| Buyer tiềm năng | Thấy giá/badge; chưa checkout; owner không mua được pin mình |
| Hệ thống | Đếm N/M/K; gán `seller`; block list mới nếu tụt ngưỡng |

---

## 3. Eligibility

| Mã | Điều kiện | MVP (config) |
|----|-----------|--------------|
| N | Số pin user | ≥ 5 |
| M | Tổng `pin_stats.view_count` pin user | ≥ 100 |
| K | Followers unique | ≥ 10 |
| P | ≥ 1 payment method | Bắt buộc |

- Enable selling thành công → `assign_role(..., "seller")`.  
- **Tụt ngưỡng sau đó (Plan #2 Q2A):** giữ role `seller` + listing đang có; **từ chối tạo listing mới** / re-list cho đến khi đủ lại.

### Payment method (Sprint2 minimal)

CRUD tối thiểu (create/list/delete own): loại bank | e-wallet + định danh nhận tiền (text). Sprint3 mở rộng.

---

## 4. Listing

| Quy tắc | Chốt |
|---------|------|
| Storage | Bảng **`pin_listings`** (1 active / pin) |
| License | Personal use · one-shot · perpetual |
| Giá | Integer **minor units** (> 0); currency `USD` mặc định hoặc `VND` |
| Status | `listed` / `unlisted` |
| Media | Cần `original_image` + preview (`image`) |
| C11 | Owner không CTA/API mua listing của mình |

---

## 5. Acceptance criteria

| AC | Mô tả | Case |
|----|-------|------|
| AC-01 | Eligibility trả N/M/K/P (current + pass + thresholds) | C06 |
| AC-02 | Thiếu điều kiện → không enable seller | C06 |
| AC-03 | Đủ + enable → role `seller` | C07 |
| AC-04 | Seller tạo listing (giá minor, currency, personal) | C07 |
| AC-05 | Non-owner/non-seller → 403 listing mutate | C06 |
| AC-06 | Thiếu media / không owner → không list | — |
| AC-07 | Owner: bán OK; không CTA mua mình | C11 |
| AC-08 | Người khác thấy badge/giá listed (chưa checkout) | C07 |
| AC-09 | Minimal payment method thỏa P | C06–C07 |
| AC-10 | Thresholds từ settings/config | D4 |
| AC-11 | Dưới ngưỡng sau seller: block **listing mới** | Q2A |

---

## 6. Ngoài phạm vi

Order/SePay · commission payout · copyright · refund · DRM  

---

## 7. Trace

AC → Plan #2 `plan_mode_decisions.md` + `devplan_checklist.md` (P0–P7).  
**Sẵn implement** khi user yêu cầu code.
