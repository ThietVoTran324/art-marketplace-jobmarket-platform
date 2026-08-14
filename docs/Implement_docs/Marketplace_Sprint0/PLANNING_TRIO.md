# Bộ 3 planning — Marketplace_Sprint0 (Phase 0-market data)

> Initiative: **Marketplace_Sprint0 — 0-market data foundation** (`created_at`, `pin_stats`, unique likes/follows)  
> System BR: [`../../Planing_docs/marketplace/business_requirement.md`](../../Planing_docs/marketplace/business_requirement.md)  
> Sprint map: [`../../Planing_docs/marketplace/sprint_map.md`](../../Planing_docs/marketplace/sprint_map.md)  
> Blocks: [`../../Planing_docs/marketplace/phase0_market_and_block_classification.md`](../../Planing_docs/marketplace/phase0_market_and_block_classification.md)  
> Survey: [`../../Planing_docs/marketplace/system_survey.md`](../../Planing_docs/marketplace/system_survey.md)  
> Deferred: [`../../Planing_docs/deferred_and_out_of_scope_backlog.md`](../../Planing_docs/deferred_and_out_of_scope_backlog.md) (MP-01..03 → sprint này)  
> Rule chung: [`../lessonlearn.md`](../lessonlearn.md) · Sự cố: [`../issues_history.md`](../issues_history.md)  
> Prerequisite: Job Market Phase 1 **CLOSED** (Alembic `b8c9d0e1f2a3`)

| File | Vai trò | Thời điểm |
|------|---------|-----------|
| [business_requirement.md](business_requirement.md) | SSOT nghiệp vụ sprint (~3/10) | **Plan #1 CHỐT** 2026-08-08 |
| [plan_mode_decisions.md](plan_mode_decisions.md) | SSOT kỹ thuật | **Plan #2 CHỐT** 2026-08-08 |
| [devplan_checklist.md](devplan_checklist.md) | Thực thi + tick + prove-done | **CLOSED** 2026-08-08 |
| [base requirement.md](base%20requirement.md) | Spec gốc ngắn (input Plan #1) | Đã dùng; không supersede BR |

## Gate vào sprint này

- System BR Marketplace D1–D10 **CHỐT**; sprint map **Synced**.
- JM Sprint6 **CLOSED**; không mở lại ADM-* / refund / media 2.1 trong sprint này.
- Plan #1 + Plan #2 sprint **chốt**.

## Gate đóng sprint

- [x] Prove-done theo `devplan_checklist.md` (smoke C08/C10).
- [x] Alembic head `c9d0e1f2a3b4`.
- [x] `pins.created_at` có; `pin_stats` bền; unique likes(pin)/follows.
- [x] Sẵn mở `Marketplace_Sprint1` (media 2.1) — **không** payment trước Sprint0+1.

## Trạng thái Plan

| Plan | Trạng thái |
|------|------------|
| Plan #1 BR | **DONE / CHỐT** |
| Plan #2 tech | **DONE / CHỐT** |
| Implement | **CLOSED** 2026-08-08 — Alembic `c9d0e1f2a3b4`; smoke `ALL_SMOKE_PASS` |
