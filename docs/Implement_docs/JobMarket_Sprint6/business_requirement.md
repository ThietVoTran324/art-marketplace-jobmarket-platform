# Business Requirements — JobMarket_Sprint6: Trust & moderation (Phase 1.6)

**Mục đích:** SSOT nghiệp vụ cho sprint report JD + suspend company + harden file.  
**Cách dùng:** Plan #1 đã hoàn thiện「Nội dung」từ [base requirement.md](base%20requirement.md). Spec kỹ thuật → Plan #2 / `devplan_checklist.md`.  
**Không** nhồn API/JSON/schema/widget vào BR.

**Nguồn hệ thống:** [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) §3.E, §3.F; SAC-12; D6.  
**Sprint map:** [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint6.  
**Base:** [base requirement.md](base%20requirement.md).  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md).  
**Deferred:** ADM-04 (Admin UI moderation đầy đủ); JM-13 soft-delete unique.  
**Prerequisite:** JobMarket_Sprint5 CLOSED.

---

## Quy tắc (cho AI)

- File này = SSOT nghiệp vụ (~3/10). Tech → `plan_mode_decisions.md` / `devplan_checklist.md`.
- Hai lần Plan: #1 nghiệp vụ (file này) → #2 tech → mới implement.

---

## Nội dung

> Plan #1 **đã chốt 2026-08-03** theo quiz (**all suggest** Q1–Q26).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Sprint1–5: artist tabs, KYC/company (`suspended` đã có trong status enum), Explore/JD, Apply, work-exp approve + employees.
- Chưa có report JD; chưa có luồng admin suspend/unsuspend + chặn hiring/JD.
- CV/KYC allowlist+size đã có; sprint này harden nhẹ + regression.

*Mục tiêu*

- User login report JD; admin xử lý qua API.
- Admin suspend / unsuspend company; chặn post/edit JD, Explore, apply theo rule dưới.
- Audit trust actions; FE nút Report tối thiểu; smoke + regression.

*Actor*

| Actor | Vai trò |
|-------|---------|
| User (login) | Report JD (không report JD của chính company mình) |
| Organization owner | Chịu chặn khi company suspended; đọc profile/config của mình; đọc application cũ |
| Admin | List/resolve report; suspend/unsuspend company; audit |
| Hệ thống | Gate hiring/JD/apply; audit; notify suspend/unsuspend |

### 2. Report JD

| Rule | Chốt |
|------|------|
| Ai report | Mọi user đã login |
| Self-report | **Chặn** nếu reporter là owner company của JD |
| Target | Một `job_post` (kể cả JD đã `closed` nếu còn đọc được detail) |
| Lý do | Enum: `spam` \| `scam` \| `inappropriate` \| `other` + text optional khi `other` (bắt buộc text nếu other) |
| Trùng | **Một** report `open` / (user, JD); tạo lại khi đang open → 409 |
| Status | `open` → `dismissed` \| `actioned` |
| Admin | API: list (filter open), dismiss, actioned (+ note optional) |
| Side-effect | **Không** auto đóng JD / auto suspend khi actioned — admin làm action riêng |
| Notify | **Không** notify owner khi bị report / khi resolve (tránh tip-off / spam) |
| FE | Nút Report tối thiểu trên Job detail |
| Public | Không hiện số report / badge cho visitor |

### 3. Suspend / flag company

| Rule | Chốt |
|------|------|
| Model | Dùng status `suspended` đã có — **không** thêm trạng thái “flagged” riêng |
| Ai | Admin API |
| Unsuspend | Có — admin đặt lại `active` |
| Lý do suspend | Text bắt buộc (admin) |
| Khi suspended | Không tạo / sửa / reopen JD; JD của DN **ẩn** khỏi Explore; **không** apply mới vào JD của DN; GET detail JD (non-owner) → 404 hoặc không apply được (cùng hướng ẩn); owner vẫn đọc company profile + list JD/manage ứng viên **read** (quiz: manage status ứng viên cũ vẫn được) |
| Hiring rights | Role `employer` giữ; gate theo `company.status == active` trên mutate |
| Soft-delete | **Out** sprint này (JM-13) |
| Notify | Email + in-app tới owner khi **suspend** và khi **unsuspend** |

### 4. Harden CV/KYC + hygiene

| Rule | Chốt |
|------|------|
| File rules | Giữ allowlist MIME+ext + size/count hiện có; đảm bảo mọi đường upload CV/KYC/oneshot dùng cùng helper |
| Magic-byte / double-ext sâu | **Không** Phase 1.6 (trừ bug rõ khi implement) |
| HY-04 `require_roles` OR | **Không cần** sprint này — moderation = **admin-only** |
| Create-user-entity / gaps khác | Không mở rộng ngoài moderation trừ khi chặn ship |

### 5. Audit

Ghi audit khi thành công:

- `company_suspend` / `company_unsuspend`
- `job_report_dismiss` / `job_report_actioned`
- `job_report_create` (user report — trail chống abuse)

### 6. Phạm vi

*In:* report JD + admin resolve · suspend/unsuspend · gates Explore/JD/apply · audit · notify suspend · FE Report · smoke/regression · file-rule consistency.

*Out:* ADM-04 Admin UI · SIEM · Marketplace · JM-13 · magic-byte sâu · auto-action từ report.

### 7. Acceptance criteria

| ID | Tiêu chí |
|----|----------|
| AC-01 | Login user report JD với enum lý do; other cần text. |
| AC-02 | Owner không self-report JD company mình. |
| AC-03 | Một open report / user+JD; trùng → 409. |
| AC-04 | Admin dismiss / actioned (+ note); không auto suspend/đóng JD. |
| AC-05 | Không notify owner về report/resolve. |
| AC-06 | FE có nút Report trên Job detail. |
| AC-07 | Admin suspend → company `suspended`; lý do bắt buộc; audit + notify owner. |
| AC-08 | Suspended: không post/edit JD; Explore ẩn JD; không apply mới. |
| AC-09 | Admin unsuspend → `active`; audit + notify; hiring/JD trở lại theo rule active. |
| AC-10 | Owner suspended vẫn đọc profile/JD/applications (không mutate JD). |
| AC-11 | Audit report create + dismiss/actioned + suspend/unsuspend. |
| AC-12 | Không ADM-04 UI; moderation qua API (+ Report FE). |
| AC-13 | Smoke Sprint6 pass; regression smoke Sprint3–5 (hoặc gói tương đương) không vỡ. |

### 8. Traceability

| Nguồn | Liên quan |
|-------|-----------|
| SAC-12 / D6 / §3.E | Trust + audit |
| ADM-04 | UI đầy đủ = out |
| HY-04 | Không cần OR sprint này |
| Quiz 2026-08-03 | Q1–Q26 all suggest |

### 9. Quyết định Plan #1 (tóm tắt)

Q1–9 Report A · Q10–19 Suspend A (unsuspend có; ẩn Explore; chặn apply; notify; no flagged) · Q20–26 Harden/audit/FE/out A.

---

> **Plan #1 CHỐT 2026-08-03** (all suggest). Plan #2 tech **CHỐT** cùng ngày (all suggest) → xem `plan_mode_decisions.md` / `devplan_checklist.md`.
