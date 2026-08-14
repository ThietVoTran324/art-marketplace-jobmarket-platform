# Base requirement — JobMarket_Sprint4 (Phase 1.4 Apply pipeline)

> Input gốc cho **Plan #1** (BR sprint).  
> SSOT hệ thống: [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (§3.B Apply / view CV / status; §3.C list ứng viên trong quản lý JD).  
> Cắt sprint: [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint4.  
> Sau Plan #1, SSOT nghiệp vụ sprint là `business_requirement.md` trong folder này — file base **không** supersede BR.  
> Prerequisite: [`../JobMarket_Sprint3/`](../JobMarket_Sprint3/) **CLOSED** (Alembic `e5f6a7b8c9d0`).  
> Deferred: [`../../Planing_docs/deferred_and_out_of_scope_backlog.md`](../../Planing_docs/deferred_and_out_of_scope_backlog.md) (JM-02, JM-08, …).

## Bối cảnh

Sprint1: artist tabs + CV quota 3 (owner).  
Sprint2: company + hiring-rights; org profile.  
Sprint3: JD + Explore + detail; Apply CTA **disabled** + “Coming next”.  
Sprint4 bật **apply thật** + pipeline ứng viên + view-CV + notify.

## Mục tiêu sprint (shippable)

1. **Apply popup** trên JD detail (active): cover **file** optional + lời ngỏ **text** + CV — chọn 1 CV trên tab **hoặc** upload one-shot từ máy (không vào quota 3, không tự thêm tab CV).
2. **Email gate (D9)** trước apply: chưa email → chặn + UX đi gắn email / bỏ qua.
3. **Application statuses:** `submitted` → `viewed` (khi employer mở view CV lần đầu) → `rejected` | `passed`. **Không** interview (JM-02 out).
4. **Vue route view CV** + nút tải; ACL chỉ employer/owner của JD đã nhận application.
5. **Notify** email + in-app: company khi có apply mới (link profile + view CV); ứng viên khi viewed / rejected / passed (link JD detail).
6. **Quản lý JD detail (owner):** phần list ứng viên — mở profile / view CV / đổi status rejected|passed.
7. **JD closed** → không apply thêm.

## Spec nghiệp vụ đã gom (input Plan #1)

### Apply

| Nhóm | Rule (hệ thống đã chốt hướng) |
|------|-------------------------------|
| Ai apply | User login; chi tiết org vs personal → **quiz** |
| JD phải | `active` + company cho phép (quiz: company active) |
| Cover file | Optional; không tính quota CV |
| Cover note | Text free text (optional vs bắt buộc → quiz) |
| CV | Chọn từ tab (≤3) **hoặc** one-shot upload; one-shot **không** quota / không vào tab (D12) |
| Email | Bắt buộc trước apply (D9) |
| Duplicate / re-apply | Quiz |
| Withdraw | Quiz (suggest out) |

### Application status

| Status | Khi nào |
|--------|---------|
| submitted | Vừa apply thành công |
| viewed | Employer **mở view CV** lần đầu |
| rejected | Owner chọn từ chối |
| passed | Owner chọn thông qua |

Không có `interview`.

### View CV

- Vue route riêng (D14); nút tải về máy.
- Hard ACL: chỉ employer/owner của JD gắn application đó.
- Non-employer → chặn rõ.

### Notify (SAC-08)

- Company: apply mới → email + in-app; link profile applicant + link view CV.
- Applicant: viewed / rejected / passed → email + in-app; link JD detail.
- In-app có thể cần **HY-02** (SSE/auth updates) tối thiểu nếu ship notify in-app trong sprint — quiz.

### Owner — list ứng viên

- Trong màn quản lý JD detail (owner-only): list đã apply; mở profile; mở view CV; đổi rejected/passed.
- Visitor không thấy list / không đổi status.

### Out — không nhầm vào Sprint4

- Interview status / pipeline phỏng vấn → **JM-02**
- Chat gắn application bắt buộc → **JM-08**
- Work-exp approve + employee tab → **Sprint5**
- Report JD / flag company → **Sprint6**
- Ranking Explore → JM-10

## Quyết định hệ thống đã chốt (không mở lại trừ conflict)

| ID | Chốt |
|----|------|
| SAC-06 | JD detail + apply (cover file optional + lời ngỏ text + CV chọn/lưu hoặc one-shot); chặn nếu chưa email; view CV Vue route + tải |
| SAC-07 | Status submitted → viewed → rejected \| passed; không interview |
| SAC-08 | Notify company (profile + view CV); applicant viewed/rejected/passed + JD detail link |
| D9 | Email bắt buộc trước apply |
| D12 | One-shot CV apply không vào quota 3 |
| D14 | View CV / JD detail = Vue routes |
| JM-02 | Interview = out |
| JM-08 | Chat–application = out Phase 1 |

## Hygiene liên quan

| ID | Ghi chú |
|----|---------|
| HY-02 | Auth SSE updates / mark-read — có thể cần tối thiểu nếu Sprint4 ship in-app notify apply (quiz Q18) |

## SAC liên quan sprint này

| SAC | Phạm vi Sprint4 |
|-----|-----------------|
| SAC-06 | Đủ (apply + view CV) |
| SAC-07 | Đủ (status machine không interview) |
| SAC-08 | Đủ (notify company + applicant) |

## Ngoài phạm vi sprint này

- JM-02, JM-08  
- Sprint5 work-exp / employees  
- Sprint6 report / flag  
- Marketplace  

## Prove-done gợi ý (Plan #1 sẽ chốt AC trên BR)

- Apply one-shot không tăng số CV trên tab owner  
- Mở view CV lần đầu → status `viewed` + notify ứng viên  
- Non-employer không tải CV application  
- JD closed → không apply thêm  
- Chưa email → chặn apply  
- Owner thấy list ứng viên; visitor không  
- Org account / rule apply theo quiz  

---

> **Trạng thái:** Base **đủ input Plan #1**. Plan #1 BR **đã chốt 2026-08-01** (all suggest **Q1–Q63**).  
> **Bước kế tiếp:** Plan #2 tech quiz / `plan_mode_decisions.md` + `devplan_checklist.md`.
