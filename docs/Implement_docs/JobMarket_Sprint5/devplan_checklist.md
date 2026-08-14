# Dev plan checklist — JobMarket_Sprint5 (Work-exp approve + employees)

**Initiative:** JobMarket_Sprint5 — Phase 1.5 Work-exp approve + employees  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 Q1–Q39)  
**SSOT kỹ thuật:** [plan_mode_decisions.md](plan_mode_decisions.md)  
**Gate vào:** Sprint4 CLOSED ✅ · Plan #1 CHỐT ✅ · Plan #2 CHỐT ✅  
**Trạng thái:** **CLOSED** 2026-08-01 — smoke `ALL_SMOKE_PASS` · **manual + API test DONE**. Alembic head `a7b8c9d0e1f2`.

---

## P0 — Baseline

- [x] Docker healthy; upgrade from `f6a7b8c9d0e1`

## P1 — Schema

- [x] `work_experiences.company_id` + status `rejected` + indexes
- [x] `companies.employees_public`
- [x] `company_employee_heads`
- [x] audit actions `work_exp_approve` / `work_exp_reject`
- [x] `alembic upgrade head` → `a7b8c9d0e1f2`

## P2 — Work-exp API + notify

- [x] create/patch: company_id XOR name; material reset; notify owner
- [x] mail templates + in-app update types

## P3 — Approve / pending / suggest

- [x] suggest (`/company-suggestions`); pending list; owner + admin approve/reject + audit

## P4 — Employees + heads

- [x] GET employees ACL; heads CRUD; `CompanyUpdate.employees_public`

## P5 — FE

- [x] WorkExperienceTab suggest + status + approve deep-link
- [x] Company pending + visibility; Employees tab; `?tab=` deep-link

## P6 — Smoke + đóng

- [x] `smoke_jobmarket_sprint5.py` → `ALL_SMOKE_PASS`
- [x] Manual + API test DONE (Swagger + FE)
- [x] PLANNING_TRIO / README / sprint_map CLOSED

---

> **CLOSED 2026-08-01.** Smoke: `docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_jobmarket_sprint5.py`  
> Manual guide: [swagger_manual_test.md](swagger_manual_test.md)
