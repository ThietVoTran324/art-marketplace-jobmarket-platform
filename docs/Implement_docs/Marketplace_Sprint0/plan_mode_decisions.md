# Plan mode decisions — Marketplace_Sprint0 (Phase 0-market)

> **Initiative:** Marketplace_Sprint0 — 0-market data foundation  
> **Index:** [PLANNING_TRIO.md](PLANNING_TRIO.md)  
> **BR:** [business_requirement.md](business_requirement.md) (Plan #1 CHỐT)  
> **Devplan:** [devplan_checklist.md](devplan_checklist.md)  
> **Trạng thái:** Plan #2 **CHỐT 2026-08-08** — được implement theo checklist.

---

## 0. Meta

| | |
|---|---|
| Initiative | Marketplace_Sprint0 — created_at + pin_stats + unique likes/follows |
| Stack | FastAPI + SQLAlchemy + Alembic + Postgres (+ Celery touch view path) |
| Baseline Alembic head | `b8c9d0e1f2a3` (JM Sprint6 CLOSED) |
| Target head (placeholder) | `c9d0e1f2a3b4` — `marketplace sprint0 0-market data` |
| FE | **Không** bắt buộc UI mới Sprint0 |
| Hygiene | Dedup trước unique; like/follow API không crash IntegrityError |

---

## P0 — Chiến lược

| ID | Quyết định |
|----|------------|
| P0-1 | Gate: AC-01..07 bắt buộc; AC-08 wipe optional nhưng script phải có sẵn |
| P0-2 | Migration revise `b8c9d0e1f2a3`; một revision gói: created_at + pin_stats + dedup + unique indexes |
| P0-3 | **Wipe pins:** không auto-wipe trong migration production. Script `scripts/wipe_pins_for_marketplace.py` (TRUNCATE/DELETE cascade-safe) — local/dev khi D10. Prove-done có thể wipe trước unique nếu duplicate bẩn. |
| P0-4 | `users_view_pins` **giữ** cho recommend; **không** dùng làm nguồn M. Increment `pin_stats.view_count` tại chỗ ghi view hiện có (Celery/API). |
| P0-5 | Không router domain marketplace mới ở Sprint0 (trừ endpoint debug/stats optional). Sửa likes/subscription routes + model + migration. |
| P0-6 | Không đụng watermark / ACL original / seller role behavior. |

---

## D* — Core technical

### Schema

| ID | Quyết định |
|----|------------|
| D1 | `pins.created_at`: `TIMESTAMP(timezone=True)` NOT NULL; `server_default=now()`; ORM `default=lambda: datetime.now(timezone.utc)`. Pin cũ: backfill = `now()` tại migration (hoặc wipe trước rồi không còn row). |
| D2 | Bảng `pin_stats`: `pin_id` PK FK → `pins.id` ON DELETE CASCADE; `view_count` BIGINT NOT NULL DEFAULT 0; `updated_at` timestamptz. **Không** bắt buộc mirror `like_count` Sprint0 (đếm từ `likes` khi cần). |
| D3 | Tạo `pin_stats` row: (a) migration backfill `INSERT … SELECT id, 0 FROM pins`; (b) khi create pin → insert stats 0; (c) khi increment view → upsert (`INSERT … ON CONFLICT DO UPDATE` hoặc get-or-create). |
| D4 | Unique likes **pin**: partial unique index `UNIQUE (user_id, pin_id) WHERE pin_id IS NOT NULL`. |
| D5 | Unique likes **comment** (cùng migration, rẻ): `UNIQUE (user_id, comment_id) WHERE comment_id IS NOT NULL`. |
| D6 | Unique follows: `UNIQUE (follower_id, following_id)` trên `subscriptions`. Dedup: giữ `MIN(id)` per pair trước khi tạo index. |
| D7 | Optional CHECK `follower_id <> following_id` nếu chưa có — thêm nếu không phá data (self-follow: xóa trước). |

### Data hygiene (migration steps order)

| ID | Quyết định |
|----|------------|
| D8 | Order migration: (1) optional note wipe script ngoài; (2) dedup likes pin/comment; (3) dedup subscriptions; (4) delete self-follows; (5) add `created_at` + backfill; (6) create `pin_stats` + backfill; (7) create unique indexes / constraints. |
| D9 | Dedup likes: với mỗi `(user_id, pin_id)` where pin_id not null → giữ 1 row (min id), xóa còn lại. Tương tự comment. |

### View increment

| ID | Quyết định |
|----|------------|
| D10 | Tại điểm hiện insert `users_view_pins` (Celery task / route tương đương): **đồng thời** `UPDATE pin_stats SET view_count = view_count + 1` (hoặc +1 chỉ lần đầu per user-pin trong session bảng tạm — **MVP Sprint0: +1 mỗi lần ghi view mới vào users_view_pins** để không đổi semantics recommend). Nếu insert view bị skip vì đã tồn tại PK → **không** +1 lại. |
| D11 | Recommend job `DELETE users_view_pins` **không** đụng `pin_stats`. |

### API

| ID | Quyết định |
|----|------------|
| D12 | `POST` like pin / follow: bắt `IntegrityError` → **409** với body rõ (`already_liked` / `already_following`). Không 500. |
| D13 | Không đổi URL public likes/subscriptions. |
| D14 | (Optional) `GET /pins/{id}/stats` hoặc field `view_count` trên pin detail nếu đã có serializer — chỉ nếu đụng file sẵn; không bắt buộc FE. |

### Wipe script

| ID | Quyết định |
|----|------------|
| D15 | `scripts/wipe_pins_for_marketplace.py`: xóa pins (+ cascade FKs ON DELETE CASCADE); log count; require confirm env `CONFIRM_WIPE_PINS=YES`. Không gọi từ migration. |
| D16 | Media files trên disk: script **cố gắng** xóa file pin dưới `MEDIA_PATH` nếu path resolve được; best-effort (Sprint1 sẽ chuẩn hóa layout). |

### Smoke

| ID | Quyết định |
|----|------------|
| D17 | `scripts/smoke_marketplace_sprint0.py`: created_at not null; duplicate like → 409; duplicate follow → 409; increment view → stats tăng; simulate delete users_view_pins → stats giữ; print `ALL_SMOKE_PASS`. |

---

## Out of scope (tech)

- `pins/original` vs `preview` dirs  
- Watermark Celery task  
- `seller` assign / eligibility  
- Orders / SePay / payment_methods  
- FE CreatePin “Bán quyền”  
- Refund  

---

## Trace → checklist

Mọi P0* / D* map step trong `devplan_checklist.md` (P0–P6). Implement **chỉ** sau khi user yêu cầu code.
