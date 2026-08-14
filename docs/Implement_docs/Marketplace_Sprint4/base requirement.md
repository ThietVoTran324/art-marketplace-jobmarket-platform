# Base requirement — Marketplace_Sprint4 (Phase 2.4 Order + SePay)

> Input gốc cho **Plan #1**.  
> SSOT hệ thống: [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md) §3.D · D6–D9 · C04 C05 C12 C13.  
> Prerequisite: Sprint1–3 **CLOSED** (`f2a3b4c5d6e7`) — media ACL + listing + payout methods + commission %.

## Bối cảnh

- Preview public; original chỉ owner hoặc buyer đã grant (`pin_license_access`).  
- Listing `listed` có `price_minor` + `currency` (USD|VND).  
- Seller có ≥1 payout method active; commission % config sẵn (Sprint3).  
- **Chưa** có order / SePay / grant qua thanh toán.

## Mục tiêu shippable

1. Order state machine: `pending` → `paid` | `failed` | `cancelled` (không refund state).  
2. SePay-first (sandbox/prod qua config) + webhook idempotent.  
3. Currency theo listing; USD mặc định khi seller chọn USD.  
4. Paid → grant original access + email buyer.  
5. Block: chưa email verified; tự mua pin mình; đã có access.  
6. Snapshot hoa hồng trên order; không auto chuyển khoản seller.  
7. FE PinView: mua / pending / đã mua.  
8. C13: không hỗ trợ refund in-app.

## Ngoài phạm vi

- VNPay song song · chargeback automation · DRM  
- Certificate đầy đủ (Sprint5) · cart nhiều pin · auto payout bank API  

---

*Plan #1 input 2026-08-08 (sau Sprint3 CLOSED).*
