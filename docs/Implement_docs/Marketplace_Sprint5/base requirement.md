# Base requirement — Marketplace_Sprint5 (Phase 2.5 Copyright)

> Input gốc cho **Plan #1**.  
> SSOT hệ thống: [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md) §3.E · C09.  
> Prerequisite: Sprint2 + Sprint4 **CLOSED** (`a3b4c5d6e7f8`) — listing + paid → grant.

## Bối cảnh

- Seller đã list license 1-shot personal use.  
- Buyer paid → `pin_license_access` + original.  
- Chưa có attestation, file hash bền, copyright report, hay certificate.

## Mục tiêu shippable

1. Attestation khi create/relist listing.  
2. File hash (SHA-256) của original.  
3. `copyright_reports` + admin API list/resolve.  
4. License certificate tối thiểu sau `paid`.  
5. FE: report trên PinView; buyer xem certificate khi owned.  
6. Smoke C09 + certificate.

## Ngoài phạm vi

- Admin UI product-grade · court / auto-takedown · DRM  

---

*Plan #1 input 2026-08-08 (sau Sprint4 CLOSED).*
