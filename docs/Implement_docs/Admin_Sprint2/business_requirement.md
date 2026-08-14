# Business Requirements — Admin_Sprint2 (Phase 3.2 JM ops)

**Mức chi tiết:** ~3/10 (business). Schema/route → Plan #2.  
**SSOT hệ thống:** [`../../Planing_docs/admin/business_requirement.md`](../../Planing_docs/admin/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md) · Base: [base requirement.md](base%20requirement.md)  
**Prerequisite:** Admin_Sprint1 **CLOSED**

> **Plan #1 CHỐT 2026-08-11** — S1–S8 **A** (`all suggest`).

---

## 1. Mục tiêu

Ship **UI vận hành Job Market** trên shell Admin:

| # | Năng lực |
|---|----------|
| 1 | Nav JM thật: KYC · Credentials · Job reports |
| 2 | KYC queue + decide + docs (list admin + download) |
| 3 | Credentials admin override (CRUD theo user id) |
| 4 | JD reports queue + company suspend/unsuspend (không auto-suspend) |

---

## 2. Actors

| Actor | Sprint2 |
|-------|---------|
| Admin | Xử lý KYC, credentials, JD report, suspend company |
| Employer / requester | Chỉ thấy kết quả phía Settings (đã có) |
| Hệ thống | API `require_roles("admin")` giữ gate |

---

## 3. Quy tắc kế thừa

| ID | Quy tắc |
|----|---------|
| System §3.B | KYC / credentials / JD + suspend trong MVP |
| ADM-05 / 08 | **Out** |
| Sprint1 shell | Guard + layout giữ nguyên |

---

## 4. Quyết định sprint (S1–S8 CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **S1** | Route JM | **A** — `/admin/kyc`, `/admin/credentials`, `/admin/job-reports` |
| **S2** | KYC list mặc định | **A** — `pending` + `need_more_info` |
| **S3** | KYC docs | **A** — List docs admin (API mỏng) + download file sẵn |
| **S4** | Need-more-info | **A** — Note bắt buộc |
| **S5** | Credentials | **A** — User id → list + CRUD admin |
| **S6** | JD resolve | **A** — Dismiss / Actioned + optional note; **không** auto-suspend |
| **S7** | Suspend | **A** — Nút trên row report + confirm |
| **S8** | Overview | **A** — Deep-link card KYC / JD (bỏ Soon trên các card đó) |

---

## 5. Acceptance criteria

| AC | Mô tả |
|----|--------|
| AC-01 | Admin vào KYC / Credentials / Job reports từ nav |
| AC-02 | List + filter KYC; approve / need-more (note) / reject |
| AC-03 | List + mở/tải documents KYC |
| AC-04 | Credentials create/update/delete cho user khác |
| AC-05 | List JD reports; dismiss / actioned |
| AC-06 | Suspend / unsuspend company từ UI report |
| AC-07 | Overview deep-link KYC / JD |
| AC-08 | Không ship copyright / work-exp / dispute |

---

## 6. Ngoài phạm vi

ADM-05 · ADM-08 · copyright unlist · work-exp list · payment

---

## 7. Trace → Plan #2

List docs admin endpoint · FE pages · smoke. Quiz Plan #2 trên chat.
