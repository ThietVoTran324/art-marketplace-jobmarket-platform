# Business Requirements — Admin_Sprint1 (Phase 3.1 Core shell)

**Mức chi tiết:** ~3/10 (business). Schema/route/widget → Plan #2.  
**SSOT hệ thống:** [`../../Planing_docs/admin/business_requirement.md`](../../Planing_docs/admin/business_requirement.md)  
**Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md) · Base: [base requirement.md](base%20requirement.md)  
**Prerequisite:** System Admin Plan #1 **CHỐT**; 3 phase trước **CLOSED**

> **Plan #1 CHỐT 2026-08-08** — S3 **B**; S1/S2/S4–S8 **A** (suggest).

---

## 1. Mục tiêu

Ship **lớp vận hành Core** đầu tiên:

| # | Năng lực |
|---|----------|
| 1 | Shell `/admin/*` + guard role `admin` |
| 2 | Nav Overview · Roles · Audit · Content (+ placeholder JM/MP) |
| 3 | Overview **có số liệu** (counts) — không chỉ hub tĩnh |
| 4 | Roles assign/revoke UI (không self-modify) |
| 5 | Audit viewer + filter theo API sẵn |
| 6 | Xóa pin / comment từ Admin Content + giữ xóa comment trên Pin |

---

## 2. Actors

| Actor | Sprint1 |
|-------|---------|
| Admin | Vào shell; xem overview counts; quản role; xem audit; xóa pin/comment |
| User thường | Không thấy entry / bị redirect khỏi `/admin` |
| Hệ thống | API `require_roles("admin")` vẫn là gate thật |

---

## 3. Quy tắc kế thừa (system)

| ID | Quy tắc |
|----|---------|
| Q1 | Shell trong Vue app hiện tại (`/admin/*`) |
| Q2 | Core → JM → MP lần lượt (Sprint1 = Core only) |
| A06 | Không tự sửa role mình |
| A07 | Non-admin API → 403 |

---

## 4. Quyết định sprint (S1–S8 CHỐT)

| ID | Chủ đề | **CHỐT** |
|----|--------|----------|
| **S1** | Entry vào Admin | **A** — Link “Admin” trong nav/aside chỉ khi `hasRole('admin')` |
| **S2** | Non-admin mở `/admin` | **A** — Redirect về Home |
| **S3** | Overview | **B** — Overview **có số liệu** (counts); không chỉ hub tĩnh |
| **S4** | Chọn user khi gán role | **A** — Nhập **user id** (+ kết quả API) |
| **S5** | Role trên UI | **A** — Đủ `admin` / `artist` / `employer` / `seller` (cấm self) |
| **S6** | Xóa pin | **A** — Form pin id + confirm trên Admin → Content |
| **S7** | Xóa comment | **A** — Giữ CommentSection **và** form id trên Admin Content |
| **S8** | Nav JM / MP | **A** — Link disabled / “Soon” |

---

## 5. Acceptance criteria

| AC | Mô tả |
|----|--------|
| AC-01 | Admin thấy entry + vào `/admin` |
| AC-02 | Non-admin redirect Home |
| AC-03 | Overview hiển thị counts (ít nhất các metric đã chốt Plan #2) |
| AC-04 | Assign + revoke role user khác; self bị chặn |
| AC-05 | Audit list + filter action / actor / khoảng thời gian |
| AC-06 | Admin xóa pin qua Content UI |
| AC-07 | Admin xóa comment (Pin + Content) |
| AC-08 | Không ship queue KYC / JD / copyright (chỉ placeholder + optional count nếu Plan #2 cho phép đọc API sẵn) |

---

## 6. Ngoài phạm vi

- Queue UI Sprint2–4 · unlist · payment admin · dispute · notarize · analytics nặng

---

## 7. Trace → Plan #2

AC + S3B counts → quyết định endpoint/stats vs compose list APIs.  
Plan #2 quiz trên chat / `plan_mode_decisions.md` sau CHỐT tech.
