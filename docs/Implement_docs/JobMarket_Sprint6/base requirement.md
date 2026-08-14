# Base requirement — JobMarket_Sprint6 (Phase 1.6 Trust & moderation)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) §3.E, §3.F; SAC-12; D6.  
> Cắt sprint: [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint6.  
> Sau Plan #1, SSOT nghiệp vụ sprint là `business_requirement.md` trong folder này — file base **không** supersede BR.  
> Prerequisite: [`../JobMarket_Sprint5/`](../JobMarket_Sprint5/) **CLOSED** (Alembic `a7b8c9d0e1f2`).  
> Deferred UI: ADM-04 (Admin UI moderation đầy đủ). Hygiene: HY-04 `require_roles` OR nếu cần.

## Bối cảnh

Sprint1–5 đã ship: artist tabs, KYC/company, Explore/JD, Apply, work-exp approve + employees.  
Company đã có status `suspended` trong schema nhưng **chưa** có luồng admin flag/suspend + chặn hiring/JD.  
Chưa có report JD. CV/KYC allowlist+size đã có cơ bản — sprint này chỉ **siết gap** nếu còn.

## Mục tiêu sprint (shippable)

1. **Report JD** — user login báo cáo JD; admin đọc/xử lý qua **API** (không Admin UI product).
2. **Flag / suspend company** — admin suspend (và bỏ suspend nếu quiz cho phép); chặn hiring/JD/apply theo rule đã chốt.
3. **Audit** mọi trust action moderation thành công (SAC-12 / D6).
4. **Harden file rules** CV/KYC nếu còn gap (magic-byte / double-ext / path — quiz).
5. **HY-04** nếu route moderation cần `admin|employer` OR semantics.
6. **Regression** smoke Sprint1–5 (hoặc smoke Sprint6 + smoke key paths).

## Spec đã gom (input Plan #1)

### Report JD

| Nhóm | Rule (hướng hệ thống) |
|------|------------------------|
| Ai report | User đã login (quiz: mọi user / chỉ personal / không tự report JD mình?) |
| Target | Một JD (job_post) |
| Lý do | Quiz: enum lý do ± free-text |
| Dup | Quiz: 1 open report / user+JD hay nhiều |
| Admin | List + resolve (dismiss / action) qua API |
| Notify | Quiz: có notify owner khi bị report / resolve không |
| FE | Quiz: nút Report trên JD detail tối thiểu vs API-only |

### Suspend / flag company

| Nhóm | Rule (hướng hệ thống) |
|------|------------------------|
| Ai | Admin (API) |
| Status | Dùng `suspended` đã có trên `companies` |
| Hiệu lực | Chặn post/edit JD, apply vào JD của DN?, Explore ẩn JD?, owner đọc profile? — **quiz** |
| Unsuspend | Quiz: có / không Phase 1 |
| Soft-delete | **Out** policy giải phóng unique (JM-13) |
| Notify | Quiz: email/in-app tới owner khi suspend |

### Harden CV/KYC

| Nhóm | Hướng |
|------|--------|
| Hiện có | Allowlist MIME+ext; size CV 5MiB; KYC 15MiB; count limits |
| Gap có thể | sniff content; reject double extension; path traversal — quiz mức độ |

### Out

- ADM-04 Admin UI moderation đầy đủ  
- Marketplace / SIEM  
- JM-08 chat–application  
- Soft-delete giải phóng unique (JM-13)

## Quyết định hệ thống đã chốt

| ID | Chốt |
|----|------|
| SAC-12 | Audit tối thiểu cho trust actions đã chốt sprint |
| D6 | Audit có; action code theo sprint |
| §3.E | Report JD + flag/suspend company + harden CV; UI đầy đủ = ADM-04 |
| §3.D | Status `suspended` đã định nghĩa (không cho chiếm legal key) |

## Prove-done gợi ý

- Report tạo được; admin list/resolve qua API  
- Company suspended → không post/apply theo rule sprint  
- Audit ghi suspend / resolve report  
- Regression Sprint1–5 smoke (hoặc tương đương)

---

> **Trạng thái:** Base đủ. Plan #1+#2 **CHỐT** · Implement **CLOSED** 2026-08-04 (`b8c9d0e1f2a3`).
