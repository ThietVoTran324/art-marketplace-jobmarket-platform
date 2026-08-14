# Business Requirements — JobMarket_Sprint4: Apply pipeline (Phase 1.4)

**Mục đích:** SSOT nghiệp vụ cho sprint Apply + application status + view-CV + notify + list ứng viên trong quản lý JD.  
**Cách dùng:** Plan #1 đã hoàn thiện「Nội dung」dưới đây từ [base requirement.md](base%20requirement.md). Spec kỹ thuật + step + prove-done → Plan #2 (`plan_mode_decisions.md` / `devplan_checklist.md`).  
**Không** nhồn spec kỹ thuật vào BR.

**Nguồn hệ thống:** [`../../Planing_docs/job_market/business_requirement.md`](../../Planing_docs/job_market/business_requirement.md) (§3.B, §3.C phần ứng viên; SAC-06, 07, 08; D9, D12, D14).  
**Sprint map:** [`../../Planing_docs/job_market/sprint_map.md`](../../Planing_docs/job_market/sprint_map.md) § JobMarket_Sprint4.  
**Base input:** [base requirement.md](base%20requirement.md).  
**Index bộ 3:** [PLANNING_TRIO.md](PLANNING_TRIO.md).  
**Deferred:** [`../../Planing_docs/deferred_and_out_of_scope_backlog.md`](../../Planing_docs/deferred_and_out_of_scope_backlog.md) (JM-02, JM-08, …).  
**Prerequisite:** JobMarket_Sprint3 CLOSED.

---

## Quy tắc (cho AI — đọc trước mọi thao tác trên file này)

- File này = *SSOT nghiệp vụ* (~3/10 sau Plan); spec kỹ thuật + step + prove-done → `devplan_checklist.md` (~10/10). *Không* nhồn API/JSON/schema DB/widget/lệnh test vào BR.
- *Hai lần Plan mode* (không gộp một phiên):
  - *Plan #1 (file này):* từ base → chốt spec *nghiệp vụ* →「Nội dung」hoàn thiện. *Chưa* implement; *chưa* chốt tech.
  - **Plan #2 (`devplan_checklist.md` / `plan_mode_decisions.md`):** sau BR hoàn thiện → chốt spec *tech* → mới được implement.
- Nếu「Nội dung」chưa hoàn thiện → chỉ được làm *Plan #1*; *cấm* implement / nhét spec tech vào BR.
- *Anti-pattern:* một Plan mode làm cả BR + devplan chi tiết; hoặc implement khi mới có BR base.

---

## Nội dung

> Plan #1 **đã chốt 2026-08-01** theo base + quiz nghiệp vụ mở rộng (**all suggest** Q1–Q63).

### 1. Bối cảnh & mục tiêu

*Bối cảnh*

- Sprint3: JD trên Explore/detail; Apply disabled + “Coming next”.
- Sprint1: CV tab owner max 3.

*Mục tiêu nghiệp vụ*

- Personal apply vào JD đủ điều kiện (cover + CV).
- Owner: list ứng viên, view/tải CV + cover, rejected/passed; xử lý đơn cũ cả khi JD đã đóng.
- Notify email + in-app (best-effort); HY-02 tối thiểu nếu cần in-app.
- Bật Apply thật trên **JD detail** (Explore chỉ dẫn vào detail).

*Người dùng / actor*

| Actor | Vai trò |
|-------|---------|
| Applicant (personal) | Apply; badge status trên JD detail (đơn mới nhất); nhận notify viewed/rejected/passed |
| Organization owner | List/CV/status; nhận notify apply mới |
| Org account | **Không** apply bất kỳ JD nào (kể cả JD DN mình / DN khác) |
| Hệ thống | Gates; snapshot CV đã nộp; status; ACL; notify best-effort |

### 2. Đối tượng nghiệp vụ

#### 2.1 Application

| Nhóm | Rule |
|------|------|
| Ai tạo | Chỉ **personal**. Org không apply; không exception “self-hire”. |
| JD + company | JD `active` **và** company `active`. Closed / company không active → chặn. |
| Race đóng JD | Popup mở rồi JD bị đóng trước submit → fail rõ; không tạo đơn. |
| Reopen JD | Đơn cũ giữ status; apply mới chỉ theo duplicate / re-apply. |
| Cover file | Optional; không quota CV; loại **tài liệu** (pdf/doc/docx) — không ảnh/video; MIME cụ thể → Plan #2. |
| Cover note | Optional free text; **có max length** (số cụ thể → Plan #2; không unlimited). |
| CV | Bắt buộc đúng **một** nguồn: CV tab **XOR** one-shot (không gửi cả hai). |
| One-shot | Không quota 3; không tự vào tab; **không** auto-promote vào tab sau apply. |
| Snapshot CV | Xóa CV tab sau apply **không** làm mất bản đã nộp; owner vẫn xem/tải bản nộp. |
| Email | Bắt buộc; **chưa có hoặc chưa verified** → chặn + UX gắn email / bỏ qua. |
| Duplicate | Chặn nếu còn đơn cùng user+JD **chưa terminal** (`submitted` \| `viewed`). |
| Terminal | `rejected` \| `passed`. |
| Re-apply | Sau `rejected` → application **mới** được. Sau `passed` → **không**. |
| Withdraw / xóa đơn | **Out** — không rút; owner không soft-delete đơn Phase 1. |
| Spam cap | Không soft-cap số apply toàn site; chỉ rule theo JD. |
| Status set | `submitted` / `viewed` / `rejected` / `passed` only; **không** interview. |

#### 2.2 Status transitions

| Status | Khi nào |
|--------|---------|
| submitted | Apply OK |
| viewed | Lần đầu owner **truy cập thành công ACL** xem hoặc tải CV của đơn (view-CV route / download từ đó). Mở **profile** alone **không** → viewed. |
| rejected / passed | Owner chọn; **được** từ `submitted` **không** bắt buộc qua viewed |
| Terminal khóa | Sau rejected/passed **không** đổi status lại; không admin override Sprint4 |

#### 2.3 View CV (+ cover)

- Vue route riêng + nút tải CV đã nộp; cover file cùng ACL (cùng trang / đính kèm).
- Chỉ **owner** company của JD.
- Applicant **không** vào route employer; visitor đoán URL → hard block.
- Non-owner → chặn rõ.

#### 2.4 Notify

| Sự kiện | Ai | Kênh | Link |
|---------|-----|------|------|
| Apply mới | Owner company | Email + in-app | Profile applicant + view CV |
| viewed / rejected / passed | Applicant | Email + in-app | JD detail |

- Một notify / một sự kiện (không digest Phase 1).
- **Không** bắt buộc mail “bạn đã submitted” cho applicant.
- Owner đổi status → **không** self-notify company.
- Notify **best-effort**: mail/in-app lỗi **không** rollback apply/status.
- HY-02: tối thiểu trong Sprint4 nếu ship in-app.

#### 2.5 Owner — list ứng viên

- Trong **quản lý JD detail** (owner-only).
- Hiện **mọi** application của JD (lịch sử rejected + đơn mới); sort **mới nhất trước**; có thể highlight đơn mới nhất.
- Từ list: mở profile; view CV; rejected/passed.
- **Không** filter/search phức tạp Phase 1.
- JD **closed**: không apply mới; owner **vẫn** xem list/CV và **vẫn** rejected/passed đơn đã có.
- Company suspend sau khi có đơn: không apply mới; owner còn quyền org thì vẫn xử lý đơn cũ; mất quyền hoàn toàn → admin sau (**out** Sprint4).

#### 2.6 Applicant — tiến độ

- Badge/status trên **JD detail** (đơn **mới nhất** nếu có lịch sử).
- **Không** trang “tất cả đơn của tôi” Sprint4.
- **Không** lý do rejected text Phase 1 — chỉ status.
- Personal→org sau khi có đơn mở: đơn cũ giữ; không apply thêm; owner vẫn xử lý đơn cũ.

#### 2.7 Entry Apply

- CTA Apply trên **JD detail** (bỏ Coming next).
- Explore chỉ dẫn vào detail — **không** apply thẳng từ list.
- UI ngôn ngữ theo app hiện tại (EN như tab JM đã ship); không i18n sprint này.
- User banned/khóa: theo auth chung site — không rule JM riêng.

### 3. Luồng tóm tắt

**Applicant:** JD detail → gates (personal, email+verified, JD+company active, duplicate/re-apply) → popup (cover optional + CV XOR) → submitted → notify owner.

**Owner:** List → view/tải CV (viewed lần đầu + notify) hoặc reject/pass (kể cả skip viewed) → notify applicant; terminal khóa.

### 4. Phạm vi

*In*

Apply + snapshot CV + status machine + view-CV/cover ACL + notify + list lịch sử trong JD manage + badge trên detail + HY-02 tối thiểu nếu cần + xử lý đơn khi JD closed.

*Out*

Interview; chat–application; withdraw; soft-delete đơn; audit status; reason rejected; trang all-my-applications; filter list phức tạp; admin override; auto-promote one-shot→tab; digest notify; Sprint5+; report/flag.

### 5. Acceptance criteria (business)

| ID | Tiêu chí |
|----|----------|
| AC-01 | Org / owner không apply bất kỳ JD nào. |
| AC-02 | Personal apply OK khi JD active + company active. |
| AC-03 | JD closed hoặc đóng giữa chừng → không tạo đơn. |
| AC-04 | Company không active → không apply. |
| AC-05 | Email thiếu hoặc chưa verified → chặn + UX gắn email / bỏ qua. |
| AC-06 | Cover file optional; tài liệu; không quota CV. |
| AC-07 | Cover note optional; có max length. |
| AC-08 | CV bắt buộc XOR tab \| one-shot; không cả hai. |
| AC-09 | One-shot không quota / không tab / không auto-promote. |
| AC-10 | Xóa CV tab sau apply → owner vẫn xem bản đã nộp. |
| AC-11 | Duplicate chặn khi còn submitted\|viewed. |
| AC-12 | Re-apply sau rejected; không sau passed. |
| AC-13 | Không withdraw / không xóa đơn Phase 1. |
| AC-14 | Viewed = lần đầu ACL xem/tải CV đơn; mở profile alone không. |
| AC-15 | Reject/pass từ submitted không bắt buộc qua viewed. |
| AC-16 | Terminal khóa; không đổi status lại; không admin override. |
| AC-17 | View CV (+cover): route + tải; chỉ owner; applicant/visitor block. |
| AC-18 | Notify company apply: email+in-app, profile+view CV; 1/event. |
| AC-19 | Notify applicant viewed/rejected/passed + JD detail; không bắt buộc mail submitted. |
| AC-20 | Notify best-effort; không rollback đơn/status. |
| AC-21 | List mọi đơn JD (lịch sử), sort mới nhất; owner-only. |
| AC-22 | JD closed: vẫn list/CV/status đơn cũ; không apply mới. |
| AC-23 | Badge status trên JD detail (đơn mới nhất); không trang all-apps; không reject reason. |
| AC-24 | Apply chỉ từ JD detail; Explore không apply thẳng. |
| AC-25 | Không interview; không audit status Sprint4. |
| AC-26 | Personal→org sau apply: đơn cũ giữ; không apply thêm. |

### 6. Traceability

| Nguồn | Liên quan |
|-------|-----------|
| System BR §3.B / §3.C | Apply + list ứng viên |
| SAC-06, 07, 08 · D9, D12, D14 | Apply / status / notify / email / one-shot / routes |
| Quiz 2026-08-01 | **Q1–Q63 all suggest** |

### 7. Quyết định Plan #1 (quiz Q1–Q63 — all suggest)

| Nhóm | Chốt chính |
|------|------------|
| A Q1–7 | Personal-only; no self-hire; JD+company active; closed block + race fail; reopen giữ đơn cũ |
| B Q8–14 | Non-terminal duplicate; terminal=rejected\|passed; re-apply after rejected only; list full history; no withdraw/delete |
| C Q15–25 | Cover file/note optional; doc types; note max; CV XOR; one-shot D12; snapshot; email+verified gate |
| D Q26–34 | Status set; viewed=ACL CV access; skip-to reject/pass OK; terminal lock; owner only; no admin |
| E Q35–39 | View-CV route+download; owner ACL; no applicant on employer route; cover cùng ACL |
| F Q40–46 | Notify maps; no digest; no submitted mail; no owner self-notify; best-effort; HY-02 min |
| G Q47–51 | List in JD manage; no complex filter; closed JD vẫn xử lý đơn |
| H Q52–54 | Badge on JD detail; no all-apps page; no reject reason |
| I Q55–60 | No audit/interview/chat; Apply on detail; no spam cap; UI EN hiện tại |
| J Q61–63 | Auth chung; personal→org giữ đơn; suspend: no new apply, xử lý đơn cũ nếu còn quyền |

---

> **Plan #1 CHỐT 2026-08-01** (all suggest Q1–Q63). Bước kế tiếp: **Plan #2** tech — chưa implement.
