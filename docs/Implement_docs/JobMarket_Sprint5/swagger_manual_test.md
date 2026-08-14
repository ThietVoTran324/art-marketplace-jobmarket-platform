# Sprint5 — Manual / API testing guide

**Trạng thái:** **Manual + API test DONE** (2026-08-01).  
**Mục đích:** checklist tham chiếu JobMarket_Sprint5 (work-exp approve + employees).  
**Docs:** `http://localhost:8000/api/docs`  
**FE:** `http://localhost:3000`  
**Smoke:** `scripts/smoke_jobmarket_sprint5.py` → `ALL_SMOKE_PASS`  
**Alembic head:** `a7b8c9d0e1f2`

Setup Swagger (CSRF + login): xem [`../JobMarket_Sprint3/swagger_manual_test.md`](../JobMarket_Sprint3/swagger_manual_test.md) §0.

---

## API chính

| Method | Path | Ghi chú |
|--------|------|---------|
| GET | `/job-market/company-suggestions?q=` | Suggest DN active |
| POST | `/job-market/me/work-experiences` | `company_id` **XOR** `company_name` |
| PATCH | `/job-market/me/work-experiences/{id}` | material → pending; `clear_company_id` |
| GET | `/job-market/me/company/work-experiences/pending` | Owner pending list |
| POST | `/job-market/me/company/work-experiences/{id}/approve` | Owner |
| POST | `/job-market/me/company/work-experiences/{id}/reject` | Owner |
| POST | `/job-market/admin/work-experiences/{id}/approve` | Admin override |
| POST | `/job-market/admin/work-experiences/{id}/reject` | Admin override |
| GET | `/job-market/companies/{id}/employees` | Public hoặc owner; private → 403 |
| POST/PATCH/DELETE | `/job-market/me/company/employee-heads` | Head CRUD |
| PATCH | `/job-market/me/company` | `employees_public` |

---

## FE smoke (đã test)

- Artist: Experience tab — suggest company / free-text; status Pending / Approved / Rejected
- Owner: Company tab — pending list + Approve/Reject; deep-link `?tab=experience&workExpId=`
- Org: Employees tab — list + head; toggle public/private
- Non-owner: private employees → blocked

---

## Prove-done đã xác nhận

- [x] Off-system → pending, không notify approve
- [x] On-system → notify owner; approve/reject + audit
- [x] Material edit khi approved → pending + notify
- [x] Private employees → non-owner 403
- [x] Head chỉ user present; delete work-exp → khỏi list
- [x] Smoke `ALL_SMOKE_PASS`
