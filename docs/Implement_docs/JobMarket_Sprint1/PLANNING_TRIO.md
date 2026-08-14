# Bộ 3 planning — JobMarket_Sprint1 (Phase 1.1 Artist foundation)

> Initiative: **JobMarket_Sprint1 — Artist tabs + work-exp + CV owner + credentials owner CRUD**
> Phase map: [`../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md`](../../Planing_docs/marketplace_jobmarket_feasibility_phase_plan.md)  
> System BR: [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md)  
> Sprint map: [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md)  
> Deferred: [`../../Planing_docs/deferred_and_out_of_scope_backlog.md`](../../Planing_docs/deferred_and_out_of_scope_backlog.md)  
> Rule chung: [`../lessonlearn.md`](../lessonlearn.md) · Sự cố: [`../issues_history.md`](../issues_history.md)

| File | Vai trò | Thời điểm |
|------|---------|-----------|
| [business_requirement.md](business_requirement.md) | SSOT nghiệp vụ sprint (~3/10) | **Plan #1 DONE** (2026-07-26) |
| [plan_mode_decisions.md](plan_mode_decisions.md) | SSOT kỹ thuật | **Plan #2 DONE** (2026-07-26) |
| [devplan_checklist.md](devplan_checklist.md) | Thực thi + tick + prove-done | **CLOSED** 2026-07-26 |
| [base requirement.md](base%20requirement.md) | Spec gốc ngắn (input Plan #1) | Đã dùng; không supersede BR |

## Gate vào sprint này

- Phase 0-core **CLOSED** (roles, ownership/CSRF, audit).
- System BR Job Market D1–D16 đã chốt; sprint map **1.1–1.6** synced.
- Deferred backlog đã có (ADM-*, JM-*, HY-*).
- Sprint BR Plan #1 **hoàn thiện**; Plan #2 tech **chốt**.
- Implement domain: **DONE** (smoke pass).

## Gate đóng sprint

- [x] Prove-done theo `devplan_checklist.md`.
- [x] SAC-01, SAC-03, SAC-04 (owner CV), phần SAC-02 (CRUD/sort, **chưa** approve notify).
- [x] Hygiene: HY-06 (`/me/roles` FE); HY-01 avatar/banner ownership.
- Sẵn sàng mở `JobMarket_Sprint2` (company + hiring-rights KYC).

## Trạng thái Plan

| Plan | Trạng thái |
|------|------------|
| Plan #1 BR | **DONE** — [`business_requirement.md`](business_requirement.md) |
| Plan #2 tech | **DONE** — [`plan_mode_decisions.md`](plan_mode_decisions.md) + [`devplan_checklist.md`](devplan_checklist.md) |
| Implement | **CLOSED** — Alembic `c3d4e5f6a7b8`; smoke `ALL_SMOKE_PASS` |
