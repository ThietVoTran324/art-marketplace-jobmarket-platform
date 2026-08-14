# Dev plan checklist — JobMarket_Sprint4 (Apply pipeline)

**Initiative:** JobMarket_Sprint4 — Phase 1.4 Apply pipeline  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 Q1–Q63)  
**SSOT kỹ thuật:** [plan_mode_decisions.md](plan_mode_decisions.md)  
**Gate vào:** Sprint3 CLOSED ✅ · Plan #1 CHỐT ✅ · Plan #2 CHỐT ✅  
**Trạng thái:** **CLOSED** 2026-08-01 — smoke `scripts/smoke_jobmarket_sprint4.py` → `ALL_SMOKE_PASS`. Alembic head `f6a7b8c9d0e1`.

---

## P0 — Baseline

- [x] Docker healthy; upgrade from `e5f6a7b8c9d0`

## P1 — Schema

- [x] `JobApplicationsOrm` + CHECKs + partial unique
- [x] `updates.metadata` JSONB nullable
- [x] `alembic upgrade head` → `f6a7b8c9d0e1`

## P2 — Skeleton

- [x] constants / schemas / ownership / `sprint4_routes` include
- [x] HY-02: SSE auth; mark-read + get update ownership

## P3 — Apply API

- [x] POST apply multipart XOR; gates; snapshot CV; notify company

## P4 — Owner + view-CV + status

- [x] list applications; reject/pass; cv-view/file/cover; viewed side-effect; my_application on GET job

## P5 — FE

- [x] Apply modal; badge; `/applications/:id/cv`; ManageJobsTab applicants

## P6 — Smoke + đóng

- [x] `smoke_jobmarket_sprint4.py` → `ALL_SMOKE_PASS`
- [x] PLANNING_TRIO / README / sprint_map CLOSED

---

> **CLOSED 2026-08-01.** Prove: `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_jobmarket_sprint4.py`
