# Business Requirements — Admin_Sprint3 (Phase 3.3 MP copyright)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**SSOT hệ thống:** [`../../Planing_docs/admin/business_requirement.md`](../../Planing_docs/admin/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md) · Base: [base requirement.md](base%20requirement.md)  
**Prerequisite:** Admin_Sprint1 **CLOSED**; system Q3 unlist **CHỐT**

> **Plan #1 CHỐT 2026-08-11** — S1–S8 **A** (`all suggest`).

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | Queue UI `/admin/copyright` |
| 2 | Resolve / dismiss (+ optional note) |
| 3 | `resolved` → unlist listing(s) của pin |
| 4 | Overview deep-link + nav (bỏ Marketplace Soon) |
| 5 | Rate-limit tạo report (nhẹ) |

---

## 2. Actors

| Actor | Sprint3 |
|-------|---------|
| Admin | Queue; resolve → unlist |
| Reporter | User login; bị rate-limit |
| Seller | Listing có thể unlist |
| Buyer đã paid | Giữ license access |

---

## 3. Quyết định sprint (S1–S8 CHỐT)

| ID | **CHỐT** |
|----|----------|
| **S1** | `/admin/copyright` + nav |
| **S2** | Default filter `open` |
| **S3** | Chỉ `resolved` → unlist; dismiss không đụng listing |
| **S4** | Unlist mọi listing `listed` của pin (1:1 pin↔listing) |
| **S5** | Không listing / đã unlisted → resolve vẫn OK |
| **S6** | Rate-limit tạo report **in** sprint |
| **S7** | Overview card → `/admin/copyright` |
| **S8** | Admin note optional |

---

## 4. Acceptance criteria

| AC | Mô tả |
|----|--------|
| AC-01 | Admin vào `/admin/copyright` |
| AC-02 | List open; resolve / dismiss |
| AC-03 | Resolve → listing `unlisted` |
| AC-04 | Dismiss → listing không đổi |
| AC-05 | Resolve không listing → 200 |
| AC-06 | Overview deep-link |
| AC-07 | Rate-limit khi vượt ngưỡng |
| AC-08 | Không revoke license |

---

## 5. Ngoài phạm vi

Revoke license · payment admin · work-exp · DRM/court
