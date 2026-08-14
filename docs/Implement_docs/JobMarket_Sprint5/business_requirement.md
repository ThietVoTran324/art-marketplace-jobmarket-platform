# Business Requirements — JobMarket_Sprint5: Work-exp approve + employees (Phase 1.5)

**Mục đích:** SSOT nghiệp vụ cho sprint approve work-exp + employee tab.  
**Cách dùng:** Plan #1 đã hoàn thiện「Nội dung」từ [base requirement.md](base%20requirement.md). Spec kỹ thuật → Plan #2.  
**Không** nhồn API/JSON/schema/widget vào BR.

**Nguồn hệ thống:** [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) §3.A, §3.C; SAC-02, SAC-09 (phần).  
**Sprint map:** [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint5.  
**Base:** [base requirement.md](base%20requirement.md).  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md).  
**Deferred:** JM-03, JM-04, JM-05.  
**Prerequisite:** JobMarket_Sprint4 CLOSED.

---

## Quy tắc (cho AI)

- File này = SSOT nghiệp vụ (~3/10). Tech → `plan_mode_decisions.md` / `devplan_checklist.md`.
- Hai lần Plan: #1 nghiệp vụ (file này) → #2 tech → mới implement.

---

## Nội dung

> Plan #1 **đã chốt 2026-08-01** theo quiz (**all suggest** Q1–Q39).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Sprint1: work-exp CRUD; status `pending`|`approved`; company free-text; chưa approve/notify.
- Sprint2: company + owner org.
- Sprint5: gắn company on-system + approve/reject + Employees tab.

*Mục tiêu*

- Artist gắn DN trong hệ thống → owner nhận notify; duyệt đúng dòng.
- Off-system luôn chưa approve; không email-token; không backfill.
- Org: tab Employees (auto list + head + public/private).

*Actor*

| Actor | Vai trò |
|-------|---------|
| Artist (personal) | CRUD work-exp; gắn company_id; nhận notify khi approved/rejected |
| Organization owner | Approve/reject đúng company; list pending; Employees tab; head CRUD; visibility |
| Admin | Override approve/reject API |
| Visitor (login) | Đọc work-exp + status công khai; đọc Employees nếu public |
| Hệ thống | Notify; derive employees; audit approve/reject |

### 2. Work-exp — gắn company & status

| Rule | Chốt |
|------|------|
| On-system | Chọn company từ hệ thống → lưu `company_id` + snapshot tên |
| Off-system | Free-text; luôn `pending`; **không** notify approve |
| Backfill | **Không** (JM-03) |
| Đổi free-text → on-system | Cho; status → `pending`; gửi notify |
| Gỡ company_id → free-text | Cho; → `pending`; khỏi derive employees |
| Status | `pending` \| `approved` \| `rejected` |
| Reject reason | **Không** Phase 1 |
| Sau rejected | Sửa dòng → `pending` lại; notify nếu còn company_id |
| Sửa material khi approved | company_id/name, title, start/end, employment_type → reset `pending` + notify nếu còn company_id |
| Approve lại khi đã approved | Idempotent OK |
| Org profile | Không work-exp (như Sprint2) |

### 3. Notify & duyệt

| Sự kiện | Ai | Kênh | Deep-link |
|---------|-----|------|-----------|
| Gắn/đổi company_id (pending) | Owner company | Email + in-app | Profile artist + tab work-exp + đúng dòng |
| approved / rejected | Artist | Email + in-app | Profile / tab work-exp |

- Không spam mỗi PATCH field nhỏ — chỉ khi gắn/đổi company_id hoặc material reset.
- Notify best-effort; không rollback work-exp.
- Duyệt: **owner** company khớp `company_id`; **admin** override API.
- Surface owner: deep-link đúng dòng **và** list pending trên org.
- Visitor thấy label status công khai (Pending / Approved / Rejected).
- Non-owner approve → 403; sai company → 403/404.
- Company không active: **không** approve mới; owner vẫn đọc cấu hình employees.

### 4. Audit

- Ghi audit khi **approve** và **reject** thành công.

### 5. Employees tab

| Rule | Chốt |
|------|------|
| Membership | `company_id` = DN này + `approved` + **present** |
| Present | `end_date IS NULL` OR `end_date >= today` (UTC date) |
| Sort | `start_date` ASC |
| Dedupe | Một user một lần trong list (dòng present “chính” = `start_date` min) |
| Pending/rejected | Không vào list |
| Visibility | Owner toggle **public** (default) \| **private**; private → non-owner 403 + ẩn tab |
| Head | Owner CRUD; chỉ user hệ thống **đang trong** auto list present; vị trí + note free-text; hiện đầu list |
| Head khi mất present | **Auto drop** khỏi head |
| Ai thấy head | Theo visibility tab |
| Artist xóa dòng approved | Cho; khỏi employees |

### 6. Phạm vi

*In:* company_id link · notify · approve/reject (+admin) · status rejected · audit · pending list org · Employees + head + visibility.

*Out:* JM-03/04/05 · university · report/flag Sprint6 · i18n mới.

### 7. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC-01 | Off-system / free-text → luôn pending; không notify approve. |
| AC-02 | Gắn company_id lần đầu / đổi company → pending + notify owner (email+in-app) deep-link đúng dòng. |
| AC-03 | Không backfill khi company xuất hiện sau. |
| AC-04 | Chỉ owner (đúng company) hoặc admin approve/reject. |
| AC-05 | Reject → status `rejected`; không reason; sửa → pending (+notify nếu on-system). |
| AC-06 | Sửa material khi approved → pending + notify nếu còn company_id. |
| AC-07 | Approve idempotent khi đã approved. |
| AC-08 | Audit ghi approve và reject. |
| AC-09 | Artist nhận notify khi approved/rejected. |
| AC-10 | Owner có list pending trên org + deep-link đúng dòng. |
| AC-11 | Visitor thấy status work-exp công khai. |
| AC-12 | Employees chỉ approved+present; sort start ASC; dedupe user. |
| AC-13 | Private employees → non-owner 403. |
| AC-14 | Default visibility public. |
| AC-15 | Head chỉ user present; auto-drop khi hết present. |
| AC-16 | Non-owner / sai company approve → 403. |
| AC-17 | Company không active → không approve mới. |
| AC-18 | Xóa work-exp approved → khỏi employees. |
| AC-19 | Notify best-effort không rollback work-exp. |
| AC-20 | Org account không có work-exp tab/list. |

### 8. Traceability

| Nguồn | Liên quan |
|-------|-----------|
| SAC-02 / SAC-09 | Approve + employees |
| D4 / D11 | Off-system; no badge tổng |
| Quiz 2026-08-01 | Q1–Q39 all suggest |

### 9. Quyết định Plan #1 (tóm tắt)

Q1–5 gắn company A · Q6–10 notify A · Q11–20 approve/reject A (Q14=C no reason) · Q21=C dual surface · Q22=A · Q23–27 employees A · Q28–32 visibility/head A · Q33–36 gates A · Q37–39 out/notify artist/UI A.

---

> **Plan #1 CHỐT 2026-08-01** (all suggest). Plan #2 + Implement **CLOSED** 2026-08-01 (`a7b8c9d0e1f2`).
