# Dev plan checklist — Marketplace_Sprint1 (Phase 2.1 Media)

**Initiative:** Marketplace_Sprint1 — preview/original + watermark + ACL  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md)  
**SSOT kỹ thuật:** [plan_mode_decisions.md](plan_mode_decisions.md)  
**Trạng thái:** **CLOSED** 2026-08-08 — smoke `scripts/smoke_marketplace_sprint1.py` → `ALL_SMOKE_PASS`. Alembic head `d0e1f2a3b4c5`.

---

## Quyết định (T1–T14) — đã implement

Baseline `c9d0e1f2a3b4` → head **`d0e1f2a3b4c5`**.

---

## P0 — Baseline + wipe

- [x] Stack healthy; upgraded from `c9d0e1f2a3b4`
- [x] Wipe script sẵn (`CONFIRM_WIPE_PINS=YES`) — dùng khi cần sạch path cũ
- [x] Migration + smoke prove-done

---

## P1 — Schema + migration

- [x] `PinsOrm.original_image`
- [x] `PinLicenseAccessOrm`
- [x] Alembic `d0e1f2a3b4c5`

---

## P2 — Watermark + Celery

- [x] `assets/watermark.png`
- [x] `app/api/rest/pins/watermark.py`
- [x] Task `generate_pin_preview`

---

## P3 — Upload rewrite

- [x] Original → `pins/original/`; preview → `pins/preview/`
- [x] `create-pin-entity` + `POST /upload/{id}`
- [x] Seed `pin_stats` giữ

---

## P4 — Serve + signed

- [x] `GET /pins/upload/{id}` = preview only
- [x] `GET /pins/original/{id}` + `/file` HMAC
- [x] TTL `PIN_ORIGINAL_URL_TTL_SECONDS` (default 300)

---

## P5 — License access stub

- [x] Table + helper `assert_can_access_pin_original`
- [x] Smoke INSERT access → buyer OK

---

## P6 — FE

- [x] `PinView.vue` — owner “Download original”

---

## P7 — Smoke

- [x] `scripts/smoke_marketplace_sprint1.py` → `ALL_SMOKE_PASS`
- [x] Wipe script cập nhật original/preview

### Prove command

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_marketplace_sprint1.py
```

---

## Đóng sprint

1. [x] Trio CLOSED + head `d0e1f2a3b4c5`
2. [x] Planing marketplace README
3. Tiếp: mở Plan #1 `Marketplace_Sprint2` khi user yêu cầu
