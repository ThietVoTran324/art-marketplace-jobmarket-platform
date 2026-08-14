# Plan mode decisions — JobMarket_Sprint5 (Phase 1.5)

> Plan #2 **chốt 2026-08-01** (all suggest T1–T38). **Implement CLOSED** 2026-08-01.  
> Alembic: `f6a7b8c9d0e1` → `a7b8c9d0e1f2`

## P0
- `sprint5_routes` + sửa work-exp trong `routes.py`; smoke `smoke_jobmarket_sprint5.py`

## Schema
- `work_experiences.company_id` FK SET NULL; status + `rejected`; indexes
- `companies.employees_public` bool default true
- `company_employee_heads` (company_id, user_id unique, title, note, sort_order)
- audit actions `work_exp_approve` / `work_exp_reject`

## API
- work-exp create/patch: company_id XOR name; material reset; notify
- `GET /company-suggestions` (tránh conflict `/companies/{id}`)
- pending list; approve/reject owner+admin; audit+notify artist
- employees GET (ACL public); heads CRUD; `CompanyUpdate.employees_public`

## FE
- WorkExperienceTab company suggest; deep-link approve; Employees tab; pending on Company tab
