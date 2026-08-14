# Base requirement — JobMarket_Sprint1 (Phase 1.1 Artist foundation)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (D1–D16).  
> Cắt sprint: [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint1.  
> Sau Plan #1, SSOT nghiệp vụ sprint là `business_requirement.md` trong folder này — file base **không** supersede BR.

## Bối cảnh

Phase 0 đã có: multi-role (`artist` mặc định, `admin`, catalog `employer`/`seller`), ownership helpers, CSRF, audit append-only.  
Job Market Phase 1 bắt đầu bằng **nền artist trên profile user hiện có**: tab work-exp / education-licensing / CV — chưa company KYC, chưa JD/apply.

## Mục tiêu sprint (shippable)

1. **Profile tabs** trên cùng profile user: Profile cơ bản (giữ) / Work experience / Education-licensing (đọc) / CV (owner). Pins tab **giữ nguyên** — không deliverable JM mới (JM-07).
2. **Work experience:** CRUD timeline; employment types; date validation; location free-text; **auto sort** theo `start_date`; company free-text (suggest đầy đủ khi có `companies` ở Sprint2); status dòng mặc định *chưa approve*; company ngoài hệ thống luôn chưa approve. **Chưa** ship notify/approve in-app (→ Sprint5).
3. **Education / licensing / awards:** đọc công khai; **owner CRUD**; không role `university` / verify (JM-01). Admin override API optional (ADM-03 UI sau).
4. **CV owner:** upload + xóa only; max **3**; xóa list ⇒ xóa file; hard block non-owner; email bắt buộc trước upload (D9) + UX: đi gắn email / bỏ qua.
5. **FE hygiene:** hydrate `/users/me/roles` (HY-06); Settings neo stub “Yêu cầu quyền tuyển dụng” → Sprint2; không hardcode username trên FE liên quan role.

## Quyết định hệ thống đã chốt (không mở lại trừ khi Plan #1 phát hiện conflict)

| ID | Chốt |
|----|------|
| D3 | Gộp tab vào profile user hiện có; pins không phải deliverable JM |
| D4 (phần) | Off-system company → luôn unapproved; **không** backfill (JM-03); approve/notify **không** in Sprint1 |
| D7 / D12 (phần) | Tab CV owner-manage max 3; apply one-shot CV → Sprint4 |
| D9 | Email bắt buộc trước **upload CV** (và apply — Sprint4) |
| D10 | Education = **owner CRUD**; không university role/approve |
| D11 | Badge verified tổng = defer (JM-05); status từng dòng vẫn có |

## SAC liên quan sprint này

| SAC | Phạm vi Sprint1 |
|-----|-----------------|
| SAC-01 | Tabs Work exp / Education / CV (owner) + profile cơ bản; pins giữ |
| SAC-02 | **Một phần:** CRUD + auto sort + free-text company; **chưa** approve/notify |
| SAC-03 | Education/licensing/awards **owner CRUD** |
| SAC-04 | CV max 3 owner; xóa ⇒ xóa file; hard block non-owner (employer read-on-apply → Sprint4) |

## Ngoài phạm vi sprint này

- Hiring-rights KYC, `companies`, company profile → Sprint2  
- Explore JD / JD manage / đóng JD → Sprint3  
- Apply, application statuses, view-CV route, notify apply → Sprint4  
- Work-exp approve in-app + employee tab → Sprint5  
- Report JD / flag company → Sprint6  
- Admin UI product (ADM-01, ADM-03, …)  
- JM-01 university, JM-05 badge tổng, JM-08 chat–application, Marketplace (MP-*)  
- HY-02 SSE / mark-read (ưu tiên Sprint4); HY-04 OR roles (khi moderation cần)

## Prove-done gợi ý (Plan #1 sẽ chốt AC chính thức)

- Owner CRUD work-exp + list auto-sort theo `start_date` đúng  
- Non-owner không list/xóa CV (403)  
- Upload CV thứ 4 bị từ chối; user chưa email → bị chặn kèm CTA gắn email / bỏ qua  
- Owner CRUD credentials; visitor chỉ đọc; non-owner 403  
- Admin override API vẫn được (optional)  
- FE đọc được roles từ `/me/roles` (không phụ thuộc hardcode)

## Gap Plan #1 — đã đóng

> SSOT: [`business_requirement.md`](business_requirement.md) §7. File base không supersede BR.

| # | Chốt |
|---|------|
| 1 | Status work-exp public rõ (`Pending approval` / `Approved`) |
| 2 | Ba loại education/licensing/awards; schema → Plan #2 |
| 3 | Allowlist PDF+DOC/DOCX + size cap; harden → Sprint6 |
| 4 | Company free-text only; suggest → Sprint2 |
| 5 | Settings stub disabled + coming next |
| 6 | Hydrate roles: Aside + UserView + Settings |

---

*Tạo 2026-07-26 — input Plan #1. Plan #1 BR chốt cùng ngày.*
