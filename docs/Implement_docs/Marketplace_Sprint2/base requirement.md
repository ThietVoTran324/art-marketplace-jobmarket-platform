# Base requirement — Marketplace_Sprint2 (Phase 2.2 Listing + gate)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md) §3.B · D1 D4 D5 · C06 C07 C11.  
> Prerequisite: Sprint0 + Sprint1 **CLOSED** (`d0e1f2a3b4c5`).  
> Sau Plan #1, SSOT nghiệp vụ = `business_requirement.md`. Plan #2 tech = `plan_mode_decisions.md` + checklist.

## Bối cảnh

Sprint0–1 CLOSED. Role `seller` catalog sẵn, chưa behavior. Gate hệ thống cần N/M/K + payment method; Sprint3 mới “đầy đủ” method UX → Sprint2 ship **minimal** method.

## Mục tiêu shippable

1. Eligibility N≥5 / M≥100 / K≥10 / ≥1 payment method (config).  
2. Enable selling → gán `seller`; dưới ngưỡng → **không** listing mới (giữ role + listing cũ).  
3. Bảng `pin_listings` — personal-use one-shot; giá minor units; USD mặc định.  
4. API prefix `/marketplace/...`.  
5. FE CreatePin + PinView “Bán quyền”; owner không CTA mua.  
6. Smoke C06 / C07 / C11.

## Plan #2 lock (all suggest)

| Q | CHỐT |
|---|------|
| Q1 | Bảng `pin_listings` |
| Q2 | Giữ `seller`; block listing mới nếu dưới ngưỡng |
| Q3 | `/marketplace/...` |
| Q4 | Giá integer minor units (cents) |
| Q5 | FE CreatePin + PinView |

## Ngoài phạm vi

SePay/order · commission payout đầy đủ · copyright · refund · DRM  

---

*Plan #1+#2 2026-08-08.*
