# Base requirement — Marketplace_Sprint1 (Phase 2.1 Media)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md) §3.A · D3 · D10 · C01–C04.  
> Prerequisite: [`../Marketplace_Sprint0/`](../Marketplace_Sprint0/) **CLOSED** (`c9d0e1f2a3b4`).  
> Sau Plan #1, SSOT nghiệp vụ sprint = `business_requirement.md` — file base **không** supersede BR.

## Bối cảnh

Sprint0 đã có `created_at`, `pin_stats`, unique like/follow.  
Hiện `GET /pins/upload/{id}` phục vụ **file gốc** cho mọi user login → bán license vô nghĩa (H1).  
Storage hiện: `MEDIA_PATH/pins/{uuid}.ext` — một path, không tách preview/original.  
D10: pin DB ít → **được wipe** nếu conflict pipeline mới.

## Mục tiêu sprint (shippable)

1. Tách **original** (private) vs **preview** (static watermark logo/site).  
2. Feed / card / PinView ảnh công khai → **chỉ preview**.  
3. Original: **owner** luôn được; buyer `paid` → hook sẵn (grant table/API stub nếu chưa có order Sprint4).  
4. Tải original qua **signed URL TTL ngắn** (không lộ path tĩnh dài hạn).  
5. Pin mới bắt buộc qua pipeline; pin cũ: wipe hoặc reprocess (chốt Plan #1/Q).  
6. Smoke C01–C04.

## Quyết định hệ thống đã chốt

| ID | Chốt |
|----|------|
| D3 | Watermark **static** trên preview |
| D7 | Không refund (không liên quan media) |
| D10 | Wipe pin cũ OK nếu conflict |
| H1 | Không public original |
| H4 / NO-02 | Không DRM tuyệt đối |

## Case liên quan

| Case | Kỳ vọng |
|------|---------|
| C01 | Chưa mua → preview only |
| C02 | Non-owner non-buyer → original 403 |
| C03 | Owner → original 200 |
| C04 | Buyer paid → original 200 (Sprint1: stub/hook; full grant Sprint4) |

## Ngoài phạm vi

- Eligibility / listing / seller role behavior → Sprint2  
- Payment methods / SePay / orders → Sprint3–4  
- Copyright hash/report đầy đủ → Sprint5  
- DRM · dynamic per-user watermark · VNPay  

## Prove-done gợi ý

- Non-owner gọi original không signed / không quyền → 403  
- Feed URL không trả byte original  
- Owner tải original OK  
- Preview có watermark nhìn thấy  
- Pin tạo mới có cả original + preview trên disk  

---

*Cập nhật 2026-08-08 — mở Plan #1.*
