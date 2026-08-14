# Business Requirements — Marketplace_Sprint1 (Phase 2.1 Media)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**SSOT hệ thống:** [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Prerequisite:** Marketplace_Sprint0 **CLOSED** (`c9d0e1f2a3b4`)

> **Plan #1 CHỐT 2026-08-08** — cắt §3.A + D3 + D10 + C01–C04.

---

## 1. Mục tiêu

Ship **tách lớp media** trước mọi listing/payment:

| # | Năng lực |
|---|----------|
| 1 | Original private trên disk + ACL |
| 2 | Preview watermark static phục vụ feed/public |
| 3 | Signed URL TTL ngắn cho original khi được phép |
| 4 | Pin mới bắt buộc pipeline; pin cũ wipe/reprocess theo chốt |

**Không** ship checkout, eligibility UI, copyright admin đầy đủ.

---

## 2. Actors & hành vi

| Actor | Sprint1 |
|-------|---------|
| Visitor / login thường | Chỉ xem/tải **preview** |
| Owner pin | Preview + **original** |
| Buyer `paid` | Preview + original (Sprint1: **hook ACL** sẵn; chưa có order thật → không buyer production path) |
| Hệ thống | Celery/async tạo preview watermark; không DRM |

---

## 3. Acceptance criteria (nghiệp vụ)

| AC | Mô tả | Case |
|----|-------|------|
| AC-01 | Ảnh trên feed / PinView (non-owner) là preview watermarked | C01 |
| AC-02 | Non-owner không có quyền paid → không lấy được original (403) | C02 |
| AC-03 | Owner lấy original thành công | C03 |
| AC-04 | Có cơ chế signed URL (TTL config) cho original khi authorized | C03–C04 |
| AC-05 | Hook “buyer paid” sẵn (helper/table stub) — Sprint4 gắn grant | C04 |
| AC-06 | Pin tạo mới sau sprint: có original + preview; không chỉ 1 file public | — |
| AC-07 | Pin cũ: theo chốt wipe hoặc reprocess; không để original public | C10/D10 |
| AC-08 | Video: preview = frame/ảnh watermarked (hoặc rule Plan #2); file video gốc ACL như original | — |

---

## 4. Quy tắc nghiệp vụ

1. **Preview ≠ original** — mọi surface “xem ảnh pin” dùng preview.  
2. **Watermark static** (logo/asset site) — không watermark động theo user MVP.  
3. **Không DRM** — chỉ ACL + watermark + audit sau (Sprint5).  
4. **Buyer access** đầy đủ sau `paid` ở Sprint4; Sprint1 không fake paid trong prod path.  
5. **`GET /pins/upload/{id}`** không còn nghĩa “original cho mọi login”.

---

## 5. Ngoài phạm vi

- Seller gate / listing / giá license  
- SePay / order / email paid  
- Certificate / copyright report UI  
- Refund  

---

## 6. Trace → Plan #2

AC-01..08 → `plan_mode_decisions.md` + `devplan_checklist.md`.  
**Plan #2 CHỐT 2026-08-08** (all suggest Q1–Q6 A).
