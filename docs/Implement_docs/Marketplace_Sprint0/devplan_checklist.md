# Dev plan checklist — Marketplace_Sprint0 (0-market data)

**Initiative:** Marketplace_Sprint0 — Phase 0-market  
**SSOT nghiệp vụ:** [business_requirement.md](business_requirement.md) (Plan #1 CHỐT 2026-08-08)  
**SSOT kỹ thuật:** [plan_mode_decisions.md](plan_mode_decisions.md) + bảng T dưới đây  
**Phase / sprint map:** [`../../Planing_docs/marketplace/`](../../Planing_docs/marketplace/)  
**Gate vào:** JM CLOSED ✅ · System BR D1–D10 CHỐT ✅ · Plan #2 CHỐT ✅  
**Trạng thái:** **CLOSED** 2026-08-08 — smoke `scripts/smoke_marketplace_sprint0.py` → `ALL_SMOKE_PASS`. Alembic head `c9d0e1f2a3b4`.

---

## Quy ước

- Chỉ tick `[x]` khi có prove-done runtime (hoặc verify ghi rõ).
- Hard stop: step hiện tại chưa pass → không sang step sau.
- Không mở scope Sprint1+ (media / listing / payment).

---

## Quyết định kỹ thuật đã chốt (T1–T12)

| ID | Quyết định | Map |
|----|------------|-----|
| T1 | `pins.created_at` timestamptz NOT NULL + server_default/backfill | D1 |
| T2 | Bảng `pin_stats` (`pin_id` PK, `view_count`, `updated_at`) + backfill | D2–D3 |
| T3 | Partial unique likes `(user_id, pin_id)` và `(user_id, comment_id)` | D4–D5 |
| T4 | Unique `subscriptions (follower_id, following_id)` + dedup + no self-follow | D6–D7 |
| T5 | Migration order: dedup → columns/tables → uniques | D8–D9 |
| T6 | Increment `pin_stats` khi insert view mới; recommend không xóa stats | D10–D11 |
| T7 | Like/follow trùng → **409** (không 500) | D12 |
| T8 | Không router marketplace domain mới bắt buộc | P0-5 |
| T9 | Wipe script + `CONFIRM_WIPE_PINS=YES` (không auto trong migration) | D15–D16, P0-3 |
| T10 | Smoke `scripts/smoke_marketplace_sprint0.py` | D17 |
| T11 | Alembic `b8c9d0e1f2a3` → `c9d0e1f2a3b4` | P0-2 |
| T12 | Không FE bắt buộc Sprint0 | Meta |

**Baseline migration head:** `b8c9d0e1f2a3` → **head:** `c9d0e1f2a3b4`.

---

## P0 — Runtime baseline

- [x] Docker stack healthy
- [x] `alembic current` was `b8c9d0e1f2a3` trước upgrade
- [x] JM smoke Sprint6 vẫn `ALL_SMOKE_PASS` (regression spot-check)

---

## P1 — Models + migration (T1–T5, T11)

- [x] `PinsOrm.created_at`
- [x] `PinStatsOrm`
- [x] Alembic `c9d0e1f2a3b4_marketplace_sprint0_0_market_data.py`
- [x] `alembic upgrade head` sạch → `c9d0e1f2a3b4`

---

## P2 — Pin create → seed `pin_stats` (T2)

- [x] `POST /pins/` và `create-pin-entity` insert `pin_stats` view_count=0

---

## P3 — View increment bền (T6)

- [x] `user_view_pin` Celery: insert view mới → `pin_stats.view_count += 1`
- [x] Recommend chỉ `DELETE users_view_pins` (không đụng stats) — verified smoke purge

---

## P4 — Like / follow API 409 (T7)

- [x] Like pin trùng → 409 `already_liked`
- [x] Follow trùng → 409 `already_following`
- [x] Like comment trùng → 409 `already_liked`

---

## P5 — Wipe script optional (T9, AC-08)

- [x] `scripts/wipe_pins_for_marketplace.py`
- [x] Require `CONFIRM_WIPE_PINS=YES` (refuse without)
- [x] Best-effort media unlink
- [x] Dùng trước Sprint1 nếu pin cũ conflict pipeline media

---

## P6 — Smoke + prove-done (T10)

- [x] `scripts/smoke_marketplace_sprint0.py` → `ALL_SMOKE_PASS`
- [x] Cover: created_at; unique like; unique follow; stats survive view purge
- [x] Alembic head ghi vào trio

### Prove command

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_marketplace_sprint0.py
```

---

## Đóng sprint

1. [x] `PLANNING_TRIO.md` → Implement **CLOSED** + head `c9d0e1f2a3b4`
2. [x] Cập nhật Planing marketplace README
3. Tiếp: mở Plan #1 `Marketplace_Sprint1` (media 2.1) khi user yêu cầu
