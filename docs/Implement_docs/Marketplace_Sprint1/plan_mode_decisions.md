# Plan mode decisions — Marketplace_Sprint1 (Phase 2.1 Media)

> **Initiative:** Marketplace_Sprint1 — preview/original + static watermark + ACL + signed URL  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) (Plan #1 CHỐT)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-08** — all suggest (Q1–Q6 A) — được implement theo checklist.

---

## 0. Meta

| | |
|---|---|
| Initiative | Marketplace_Sprint1 — Media tách lớp |
| Stack | FastAPI + SQLAlchemy + Alembic + Celery + Pillow + Vue (URL tối thiểu) |
| Baseline Alembic head | `c9d0e1f2a3b4` (Sprint0 CLOSED) |
| Target head (placeholder) | `d0e1f2a3b4c5` — `marketplace sprint1 media split` |
| Quiz lock | Q1A layout · Q2A HMAC · Q3A wipe · Q4A endpoints · Q5A logo file · Q6A video frame |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Gate AC-01..08; smoke C01–C04 |
| P0-2 | **Wipe pins** (script Sprint0 + `CONFIRM_WIPE_PINS=YES`) **trước** hoặc ngay đầu prove-done local — không migrate in-place path cũ (Q3A / D10) |
| P0-3 | Migration: cột path original + bảng stub access; **không** payment |
| P0-4 | Watermark **Celery** (async); upload API có thể trả pin khi original đã lưu, preview path cập nhật khi task xong (hoặc sync fallback nếu file nhỏ — ưu tiên Celery) |
| P0-5 | FE: giữ `GET /pins/upload/{id}` làm ảnh card/PinView → giờ = **preview**; không đổi hàng loạt URL nếu endpoint cũ đổi nghĩa sang preview |
| P0-6 | Không SePay / listing / seller gate |

---

## D* — Core technical

### Layout & columns (Q1A, Q5A, Q6A)

| ID | Quyết định |
|----|------------|
| D1 | Disk: `{MEDIA_PATH}/pins/original/{uuid}.ext` và `{MEDIA_PATH}/pins/preview/{uuid}.ext` (preview watermarked). |
| D2 | DB: `pins.image` = **preview** relative path (`pins/preview/...`) — giữ tên field cho FE. Thêm `pins.original_image` = `pins/original/...` (nullable tới khi file sẵn). |
| D3 | Video: original = video file dưới `pins/original/`; `videoPreview` + `image` trỏ preview **frame đầu đã watermark** dưới `pins/preview/`. |
| D4 | Watermark asset: `assets/watermark.png` (repo; overlay Pillow — góc/center mờ config). Nếu thiếu file lúc dev → generate placeholder PNG tối giản trong assets khi implement. |
| D5 | Upload flow: (1) lưu original; (2) enqueue Celery `generate_pin_preview`; (3) task ghi preview + update `pins.image` / `videoPreview`; (4) seed `pin_stats` giữ như Sprint0. |

### Endpoints & ACL (Q4A)

| ID | Quyết định |
|----|------------|
| D6 | `GET /pins/upload/{id}` → phục vụ **preview** only (login như hiện tại). Không bao giờ stream original. |
| D7 | `GET /pins/original/{id}` → ACL: owner **hoặc** row trong `pin_license_access`; sau đó redirect/stream qua **signed URL** hoặc trả FileResponse chỉ khi request kèm sig hợp lệ. Prefer: endpoint này kiểm ACL rồi trả **JSON `{url: signed}`** hoặc 302 tới `GET /pins/original/{id}/file?exp=&sig=` (file handler chỉ verify sig, không tin client user_id không khớp payload). |
| D8 | Signed file handler: verify HMAC; `exp` chưa hết; `pin_id` khớp; optional bind `user_id` trong payload. TTL mặc định **300s** (settings `PIN_ORIGINAL_URL_TTL_SECONDS`). |
| D9 | Helper `assert_can_access_pin_original(db, user_id, pin)` → 403 nếu không owner và không access row. |

### Signed URL (Q2A)

| ID | Quyết định |
|----|------------|
| D10 | HMAC-SHA256 over canonical string `pin_id:user_id:exp` (hoặc `pin_id:exp` nếu không bind user — **bind user_id**). Secret: `settings.JWT_SECRET_KEY` (reuse) trừ khi thêm `PIN_MEDIA_SIGNING_SECRET` optional override. |
| D11 | Query params: `exp` (unix), `uid`, `sig` (hex/base64url). Không JWT. |

### Access stub (AC-05 / C04 hook)

| ID | Quyết định |
|----|------------|
| D12 | Bảng `pin_license_access`: `id`, `user_id` FK, `pin_id` FK CASCADE, `order_id` nullable (Sprint4), `granted_at` timestamptz; **UNIQUE (user_id, pin_id)**. Sprint1: không public API grant; smoke có thể INSERT trực tiếp để chứng C04. |
| D13 | Không bảng order Sprint1. |

### Wipe (Q3A)

| ID | Quyết định |
|----|------------|
| D14 | Dùng `scripts/wipe_pins_for_marketplace.py` (cập nhật xóa cả `pins/original` + `pins/preview` best-effort). Không auto trong Alembic upgrade. |
| D15 | Sau wipe, mọi pin mới phải qua pipeline D5. |

### FE

| ID | Quyết định |
|----|------------|
| D16 | Card/PinView tiếp tục gọi `/pins/upload/{id}` (preview). Owner UI: nút/link “Tải bản gốc” → gọi original endpoint (signed) — tối thiểu trên `PinView.vue`. |
| D17 | Không UI bán license Sprint1. |

### Smoke

| ID | Quyết định |
|----|------------|
| D18 | `scripts/smoke_marketplace_sprint1.py`: create pin image → original + preview trên disk; non-owner GET upload = preview bytes ≠ original; non-owner original → 403; owner original → 200/signed OK; insert `pin_license_access` → buyer original OK; print `ALL_SMOKE_PASS`. |

---

## Out of scope (tech)

- SePay / orders / email paid  
- Eligibility N/M/K / role `seller` assign  
- Copyright hash/report  
- DRM / per-user dynamic watermark  
- VNPay  

---

## Trace → checklist

P0* / D* → `devplan_checklist.md` P0–P7. Implement khi user yêu cầu code.
