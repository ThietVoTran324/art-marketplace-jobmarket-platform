# Business Requirements — Marketplace_Sprint5 (Phase 2.5 Copyright)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**SSOT hệ thống:** [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Prerequisite:** Marketplace_Sprint2 + Sprint4 **CLOSED** (`a3b4c5d6e7f8`)

> **Plan #1 CHỐT 2026-08-08** — cắt §3.E + C09; S1–S8 all suggest.

---

## 1. Mục tiêu

Ship lớp **bảo vệ / minh bạch bản quyền tối thiểu** quanh bán license:

| # | Năng lực |
|---|----------|
| 1 | Seller **attestation** khi list / relist |
| 2 | Lưu **file hash** original |
| 3 | User login tạo **copyright report**; admin API xử lý |
| 4 | Sau `paid`: **license certificate** tối thiểu (API + FE buyer) |
| 5 | Không auto-unlist / DRM / court workflow |

---

## 2. Actors

| Actor | Sprint5 |
|-------|---------|
| Seller | Attest khi bán; có thể bị report |
| Buyer | Xem certificate khi đã owned |
| Reporter | Login user gửi report |
| Admin | API list / resolve / dismiss |
| Hệ thống | Hash original; phát certificate sau paid |

---

## 3. Quy tắc nghiệp vụ

### 3.1 System

| ID | Quy tắc |
|----|---------|
| §3.E | Attestation; file hash; copyright_reports + admin API; certificate tối thiểu sau paid |
| C09 | Copyright report tạo được + admin API |

### 3.2 Quyết định sprint (S1–S8 CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **S1** | Attestation | Bắt buộc khi **create/relist listing** (checkbox + timestamp + text version); không chặn upload pin thường |
| **S2** | Hash | SHA-256 của **original file**; lưu gắn pin/media |
| **S3** | Reporter | User **login** (có thể chưa verified); không anonymous |
| **S4** | Report → listing | Chỉ ghi report + status; **không** auto-unlist |
| **S5** | Admin resolve | `open` → `resolved` \| `dismissed` + optional note |
| **S6** | Certificate | Payload tối thiểu: order, pin, buyer, seller, license_type, paid_at, hash snapshot; FE buyer khi owned |
| **S7** | FE report | Nút Report copyright trên PinView (reason ngắn) |
| **S8** | Admin FE | **Không** — chỉ API/Swagger |

---

## 4. Acceptance criteria

| AC | Mô tả | Case |
|----|-------|------|
| AC-01 | List/relist yêu cầu attestation | — |
| AC-02 | Pin có original → có hash | — |
| AC-03 | User login tạo copyright report | C09 |
| AC-04 | Admin list + resolve/dismiss | C09 |
| AC-05 | Paid → certificate đọc được qua API | — |
| AC-06 | Buyer owned thấy certificate trên PinView | — |
| AC-07 | Không DRM / không court / không auto-unlist | — |

---

## 5. Ngoài phạm vi

- Admin UI product-grade  
- Court / legal takedown automation  
- DRM · dynamic watermark nâng cao  

---

## 6. Trace → Plan #2

AC → `plan_mode_decisions.md` + `devplan_checklist.md`.

**Plan #2 quiz gợi ý:**

1. Attestation lưu: A) cột trên `pin_listings` **(suggest)** · B) bảng `seller_attestations` riêng  
2. Hash lưu: A) cột `pins.content_sha256` **(suggest)** · B) bảng `pin_media_hashes`  
3. Hash khi nào: A) Celery khi có original (cùng pipeline preview) **(suggest)** · B) sync trong upload request  
4. Certificate: A) bảng `license_certificates` 1:1 order **(suggest)** · B) compute on-the-fly từ order+pin (không bảng)  
5. Report duplicate: A) cho phép nhiều report / pin **(suggest)** · B) 1 open report / (user, pin)  
6. Admin routes: A) `/admin/copyright-reports` **(suggest)** · B) `/marketplace/admin/...`  

Trả lời `q1…` hoặc **all suggest**.
