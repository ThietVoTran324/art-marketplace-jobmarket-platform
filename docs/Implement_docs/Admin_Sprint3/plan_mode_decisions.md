# Plan mode decisions — Admin_Sprint3 (Phase 3.3 MP copyright)

> **BR:** [business_requirement.md](business_requirement.md) — Plan #1 CHỐT  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-11** — self-research + all suggest.

---

## 0. Meta

| | |
|---|---|
| Baseline Alembic | `b4c5d6e7f8a9` |
| Migration | **Không** |
| Plan #2 | Q1–Q7 **A** (chốt nội bộ) |

---

## Plan #2 (CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **Q1** | Unlist khi nào | Trong `PATCH /admin/copyright-reports/{id}` khi `status=resolved` |
| **Q2** | Unlist how | `UPDATE pin_listings SET status='unlisted' WHERE pin_id=? AND status='listed'` |
| **Q3** | Audit meta | Thêm `unlisted_count` vào metadata audit resolve |
| **Q4** | Rate-limit | DB count reports của user trong window; config `MP_COPYRIGHT_REPORT_MAX` + `MP_COPYRIGHT_REPORT_WINDOW_SECONDS` |
| **Q5** | FE | `AdminCopyrightView` + nav + Overview |
| **Q6** | Dismiss | Chỉ đổi report status (giữ hành vi cũ) |
| **Q7** | Smoke | `scripts/smoke_admin_sprint3.py` |

**Defaults suggest:** max **5** reports / user / **3600s**.

---

## D*

| ID | Quyết định |
|----|------------|
| D1 | Không revoke `pin_license_access` |
| D2 | Unique listing/pin → tối đa 1 row unlist |
| D3 | 429 `copyright_report_rate_limited` khi vượt |
| D4 | Routes FE `/admin/copyright` |

---

## Out of scope

Revoke · payment admin · fastapi_limiter IP-only · migration
