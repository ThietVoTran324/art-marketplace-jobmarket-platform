"""Quick check POST /api/pins/feed-meta + compare request count vs old N+1."""
import time
import uuid

import httpx

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


def main() -> None:
    user = f"feedmeta_{uuid.uuid4().hex[:8]}"
    c = httpx.Client(base_url=BASE, timeout=60.0)
    c.post("/api/users/register", json={"username": user, "password": PASSWORD})
    assert c.post("/api/users/login", json={"username": user, "password": PASSWORD}).status_code == 200
    csrf = c.cookies.get("csrf_token")
    headers = {"X-CSRF-Token": csrf}

    pins = c.get("/api/pins/", params={"offset": 0, "limit": 15}).json()
    ids = [p["id"] for p in pins]
    print("pins", len(ids))

    t0 = time.perf_counter()
    r = c.post("/api/pins/feed-meta", json={"pin_ids": ids}, headers=headers)
    batch_ms = (time.perf_counter() - t0) * 1000
    print("feed-meta", r.status_code, f"{batch_ms:.1f}ms", "rows", len(r.json()) if r.status_code == 200 else r.text[:200])
    if r.status_code == 200 and r.json():
        print("sample", r.json()[0])

    # Old N+1 for comparison (first 5 only to keep short)
    sample = pins[:5]
    t0 = time.perf_counter()
    for p in sample:
        c.get(f"/api/users/user_id/{p['user_id']}")
        c.get(f"/api/likes/pin/likes/cnt/{p['id']}")
        c.get(f"/api/likes/pin/user_like/{p['id']}")
        c.get(f"/api/comments/cnt/comments/{p['id']}")
    old_ms = (time.perf_counter() - t0) * 1000
    print(f"old_meta_5pins_20reqs={old_ms:.1f}ms  vs batch_15pins_1req={batch_ms:.1f}ms")


if __name__ == "__main__":
    main()
