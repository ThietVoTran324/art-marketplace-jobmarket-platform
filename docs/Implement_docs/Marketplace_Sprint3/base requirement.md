# Base requirement — Marketplace_Sprint3 (Phase 2.3 Payment methods)

> Input gốc cho **Plan #1**.  
> SSOT hệ thống: [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md) §3.C · D2.  
> Prerequisite: [`../Marketplace_Sprint2/`](../Marketplace_Sprint2/) **CLOSED** (`e1f2a3b4c5d6`) — manual test OK.  
> Sprint2 đã có **minimal** `seller_payment_methods` (create/list/delete) phục vụ gate P.

## Bối cảnh

- Gate eligibility vẫn đòi ≥1 method active.  
- Platform **không** ví nội bộ; tiền về STK/ví seller (payout sau order ở Sprint4).  
- Hoa hồng platform: **% config** (có thể 0).

## Mục tiêu shippable

1. Mở rộng CRUD payment method (field rõ hơn, set **default/primary**, soft-deactivate).  
2. Không xóa hết method nếu đang seller+listed mà không cảnh báo / rule chốt Plan #1.  
3. Config **commission %** đọc được (API settings hoặc `/marketplace/me/payout-preview` stub).  
4. FE: trang/settings (hoặc panel seller) quản lý payout methods — không chỉ nhét trong PinView.  
5. Smoke: primary method, không ví nội bộ, commission config.

## Ngoài phạm vi

- SePay / order / chuyển tiền thật → Sprint4  
- KYC ngân hàng nhà nước đầy đủ  
- Refund · ví nội bộ  

---

*Mở Plan #1 2026-08-08 (sau Sprint2 manual done).*
