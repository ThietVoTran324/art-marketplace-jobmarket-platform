# Business Requirements — Admin_Sprint4 (Phase 3.4 work-exp queue)

**Mức chi tiết:** ~3/10 (business).  
**SSOT hệ thống:** [`../../Planing_docs/admin/business_requirement.md`](../../Planing_docs/admin/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
**Prerequisite:** Admin_Sprint2+ CLOSED; system Q4 CHỐT

> **Plan #1 CHỐT 2026-08-11** — S1–S7 **A** (`all suggest`).

---

## 1. Mục tiêu

| # | Năng lực |
|---|----------|
| 1 | Admin list work-exp (mặc định pending) |
| 2 | UI approve / reject (API sẵn; không note — API không hỗ trợ) |
| 3 | Overview count + deep-link |
| 4 | Nav “Work exp” |

---

## 2. Quyết định (S1–S7 CHỐT)

| ID | **CHỐT** |
|----|----------|
| **S1** | `/admin/work-experiences` |
| **S2** | Default `pending` + filter status |
| **S3** | Không note (API decide không có note) |
| **S4** | `open_work_exp_pending` trên overview + card |
| **S5** | Nav Work exp |
| **S6** | Hygiene nhẹ |
| **S7** | `smoke_admin_sprint4.py` |

---

## 3. Acceptance

| AC | Mô tả |
|----|--------|
| AC-01 | Admin GET list pending |
| AC-02 | UI approve/reject |
| AC-03 | Overview count + link |
| AC-04 | Non-admin 403 |
| AC-05 | Owner flow không regress |

---

## 4. Ngoài phạm vi

ADM-05 · payment · note reject schema mới · analytics
