# Plan mode decisions — Admin_Sprint4 (Phase 3.4 work-exp)

> **BR:** [business_requirement.md](business_requirement.md) — Plan #1 CHỐT  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-11** — all suggest (self).

## Meta

| | |
|---|---|
| Baseline | `b4c5d6e7f8a9` |
| Migration | **Không** |

## Plan #2 CHỐT

| ID | **CHỐT** |
|----|----------|
| **Q1** | `GET /job-market/admin/work-experiences?status=` → `list[PendingWorkExperienceOut]` |
| **Q2** | Default status=`pending`; allow `approved` \| `rejected` \| omit=all |
| **Q3** | Join artist username như owner pending list |
| **Q4** | Overview: `open_work_exp_pending` count status=pending |
| **Q5** | FE `AdminWorkExperiencesView` + nav + overview card |
| **Q6** | Approve/reject gọi API sẵn (POST) |
| **Q7** | `scripts/smoke_admin_sprint4.py` |

## Out

Reject note body · revoke · payment · migration
