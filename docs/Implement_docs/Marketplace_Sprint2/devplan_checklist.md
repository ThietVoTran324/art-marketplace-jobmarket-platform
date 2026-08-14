# Dev plan checklist — Marketplace_Sprint2 (Phase 2.2 Listing + gate)

**Initiative:** Marketplace_Sprint2 — eligibility + seller + listings  
**SSOT:** [business_requirement.md](business_requirement.md) · [plan_mode_decisions.md](plan_mode_decisions.md)  
**Trạng thái:** **CLOSED** 2026-08-08 — smoke `scripts/smoke_marketplace_sprint2.py` → `ALL_SMOKE_PASS`. Alembic head `e1f2a3b4c5d6`.

---

## Quyết định (T1–T14) — đã implement

Baseline `d0e1f2a3b4c5` → head **`e1f2a3b4c5d6`**.

---

## P0–P7

- [x] P0 baseline  
- [x] P1 schema + settings `MP_ELIGIBILITY_MIN_*`  
- [x] P2 `/marketplace` router  
- [x] P3 eligibility + enable-selling → `seller`  
- [x] P4 payment methods minimal  
- [x] P5 listings API + block below threshold  
- [x] P6 PinView + CreatePinView  
- [x] P7 smoke `ALL_SMOKE_PASS`  

### Prove command

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T -w /fastapi -e PYTHONPATH=/fastapi fastapi-app python scripts/smoke_marketplace_sprint2.py
```

---

## Đóng sprint

1. [x] Trio CLOSED  
2. [x] README marketplace  
3. Tiếp: mở Plan #1 `Marketplace_Sprint3` khi user yêu cầu  
