# Plan mode decisions — Marketplace_Sprint5 (Phase 2.5 Copyright)

> **Initiative:** Marketplace_Sprint5 — copyright report + hash + certificate  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) — Plan #1 CHỐT  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-08** — all suggest Q1–Q6 A.

---

## 0. Meta

| | |
|---|---|
| Baseline Alembic | `a3b4c5d6e7f8` |
| Target head | `b4c5d6e7f8a9` — `marketplace sprint5 copyright` |
| Quiz | Q1A listings attest · Q2A pins.content_sha256 · Q3A Celery · Q4A license_certificates · Q5A many reports · Q6A /admin/copyright-reports |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Attestation trên `pin_listings` (không bảng riêng) |
| P0-2 | Hash SHA-256 trên `pins.content_sha256` trong `generate_pin_preview` |
| P0-3 | Certificate 1:1 order; tạo lúc paid |
| P0-4 | Reports nhiều / pin; không auto-unlist |
| P0-5 | Admin API only — không Admin UI |

---

## D* — Core

| ID | Quyết định |
|----|------------|
| D1 | `pin_listings`: `attestation_accepted` bool, `attestation_version` str, `attested_at` timestamptz — required khi status→listed |
| D2 | `ListingCreateIn.attestation_accepted: true` bắt buộc; version từ `MP_ATTESTATION_VERSION` |
| D3 | `pins.content_sha256` String(64) nullable; set trong Celery preview task |
| D4 | `copyright_reports`: reporter_user_id, pin_id, reason, status open\|resolved\|dismissed, admin_note, timestamps |
| D5 | `POST /marketplace/pins/{id}/copyright-reports` (login) |
| D6 | `GET/PATCH /admin/copyright-reports` (admin) |
| D7 | `license_certificates` UNIQUE order_id: buyer/seller/pin/license_type/paid_at/content_sha256/certificate_code |
| D8 | Paid → upsert certificate; `GET /marketplace/me/certificates/{order_id}` + by pin when owned |
| D9 | FE PinView: attest checkbox; report form; show certificate when owned |
| D10 | Smoke: attest required; hash set; report+admin; paid→cert |

---

## Config

- `MP_ATTESTATION_VERSION=seller-rights-v1`

---

## Out of scope

Admin UI · auto-unlist · DRM · court
