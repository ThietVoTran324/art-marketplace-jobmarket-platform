# Dev plan checklist — JobMarket_Sprint6 (Trust & moderation)

**Initiative:** JobMarket_Sprint6 — Phase 1.6 Trust & moderation  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 Q1–Q26)  
**SSOT kỹ thuật:** [plan_mode_decisions.md](plan_mode_decisions.md)  
**Gate vào:** Sprint5 CLOSED ✅ · Plan #1 CHỐT ✅ · Plan #2 CHỐT ✅  
**Trạng thái:** **CLOSED** 2026-08-04 — smoke `ALL_SMOKE_PASS` · regression Sprint3–5 pass. Alembic head `b8c9d0e1f2a3`.

---

## P0 — Baseline

- [x] Docker healthy; confirm head `a7b8c9d0e1f2`
- [x] Gate AC-01…13 mapped to smoke

## P1 — Schema / migration

- [x] Table `job_post_reports` + CHECKs + partial unique open
- [x] `companies.suspend_reason` + `suspended_at`
- [x] Audit CHECK: report + suspend actions
- [x] Models + `alembic upgrade head` → `b8c9d0e1f2a3`

## P2 — Skeleton

- [x] constants / schemas / `sprint6_routes` include
- [x] audit.py VALID_ACTIONS + TARGET types
- [x] notify helpers suspend/unsuspend (+ mail template)

## P3 — Report API

- [x] POST report (enum/other, self-owner 403, duplicate 409) + audit create
- [x] Admin list / dismiss / actioned + audit (no auto JD/company side-effect)

## P4 — Suspend + gates

- [x] Admin suspend / unsuspend + audit + notify
- [x] Gate JD mutate (active company only)
- [x] Explore + public GET job hide suspended company
- [x] Apply blocked when company suspended
- [x] Owner read paths still work

## P5 — Harden (light)

- [x] Existing CV/KYC allowlist retained (no magic-byte); helpers already shared

## P6 — FE

- [x] JobDetailView Report button + modal

## P7 — Smoke + đóng

- [x] `scripts/smoke_jobmarket_sprint6.py` → `ALL_SMOKE_PASS`
- [x] Regression: smoke Sprint3 + 4 + 5
- [x] PLANNING_TRIO / README / sprint_map → CLOSED

---

> **CLOSED 2026-08-04.** Prove: `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_jobmarket_sprint6.py`
