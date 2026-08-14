"""Benchmark home feed caching / scroll cost (local)."""
import statistics
import time
import uuid

import httpx

BASE = "http://127.0.0.1:8000"
PASSWORD = "TestPass123!"


def ms(t0: float) -> float:
    return (time.perf_counter() - t0) * 1000


def main() -> None:
    user = f"feedbench_{uuid.uuid4().hex[:8]}"
    client = httpx.Client(base_url=BASE, timeout=60.0, follow_redirects=True)
    client.post("/api/users/register", json={"username": user, "password": PASSWORD})
    r = client.post("/api/users/login", json={"username": user, "password": PASSWORD})
    print("login", r.status_code, "cookies", list(client.cookies.keys()))
    assert r.status_code == 200

    pages = [(0, 15), (15, 5), (20, 5), (25, 5)]

    def bench_list(path: str, rounds: int = 2):
        results = []
        for rnd in range(rounds):
            for offset, limit in pages:
                t0 = time.perf_counter()
                resp = client.get(path, params={"offset": offset, "limit": limit})
                elapsed = ms(t0)
                try:
                    n = len(resp.json()) if resp.status_code == 200 else 0
                except Exception:
                    n = 0
                results.append(
                    {
                        "round": rnd,
                        "offset": offset,
                        "limit": limit,
                        "status": resp.status_code,
                        "ms": elapsed,
                        "bytes": len(resp.content),
                        "count": n,
                        "x_cache": resp.headers.get("x-fastapi-cache")
                        or resp.headers.get("X-FastAPI-Cache")
                        or "-",
                    }
                )
        return results

    list_main = bench_list("/api/pins/")
    list_cache = bench_list("/api/pins/cache/")

    print("\n=== LIST /api/pins/ (HomeView uses this) ===")
    for row in list_main:
        print(
            f"  r{row['round']} off={row['offset']:2d} lim={row['limit']:2d} "
            f"status={row['status']} pins={row['count']:2d} "
            f"{row['ms']:7.1f}ms  {row['bytes']:6d}B  cache={row['x_cache']}"
        )

    print("\n=== LIST /api/pins/cache/ (Redis FastAPICache, NOT wired to Home) ===")
    for row in list_cache:
        print(
            f"  r{row['round']} off={row['offset']:2d} lim={row['limit']:2d} "
            f"status={row['status']} pins={row['count']:2d} "
            f"{row['ms']:7.1f}ms  {row['bytes']:6d}B  cache={row['x_cache']}"
        )

    pins = client.get("/api/pins/", params={"offset": 0, "limit": 15}).json()
    print(f"\n=== PER-CARD waterfall (PinFeedCard) for first {len(pins)} pins ===")

    def card_requests(pin_id: int, user_id: int):
        times = {}
        t0 = time.perf_counter()
        media = client.get(f"/api/pins/upload/{pin_id}")
        times["media_ms"] = ms(t0)
        times["media_bytes"] = len(media.content)

        t0 = time.perf_counter()
        client.get(f"/api/users/user_id/{user_id}")
        times["user_ms"] = ms(t0)

        t0 = time.perf_counter()
        client.get(f"/api/likes/pin/likes/cnt/{pin_id}")
        times["likes_ms"] = ms(t0)

        t0 = time.perf_counter()
        client.get(f"/api/likes/pin/user_like/{pin_id}")
        times["liked_ms"] = ms(t0)

        t0 = time.perf_counter()
        client.get(f"/api/comments/cnt/comments/{pin_id}")
        times["comments_ms"] = ms(t0)

        meta_parallel = max(times["likes_ms"], times["liked_ms"], times["comments_ms"])
        # FE: loadMedia || loadMeta; loadMeta = user then Promise.all(3)
        times["approx_fe_wall_ms"] = max(times["media_ms"], times["user_ms"] + meta_parallel)
        return times

    card_rows = []
    t_batch0 = time.perf_counter()
    for p in pins:
        card_rows.append(card_requests(p["id"], p["user_id"]))
    batch_wall = ms(t_batch0)

    media_ms = [r["media_ms"] for r in card_rows]
    fe_wall = [r["approx_fe_wall_ms"] for r in card_rows]
    media_bytes = [r["media_bytes"] for r in card_rows]
    print(f"pins={len(pins)}  HTTP_reqs={len(pins) * 5}  (+1 list) = {len(pins) * 5 + 1}")
    print(
        f"media_ms  avg={statistics.mean(media_ms):.1f}  p50={statistics.median(media_ms):.1f}  "
        f"min={min(media_ms):.1f}  max={max(media_ms):.1f}"
    )
    print(
        f"media_KB  avg={statistics.mean(media_bytes) / 1024:.1f}  "
        f"sum={sum(media_bytes) / 1024:.1f}  max={max(media_bytes) / 1024:.1f}"
    )
    print(
        f"approx_FE_card_wall_ms avg={statistics.mean(fe_wall):.1f}  "
        f"p50={statistics.median(fe_wall):.1f}  max={max(fe_wall):.1f}"
    )
    print(f"sequential_all_cards_wall_ms={batch_wall:.1f}")
    print(f"if_browser_unlimited_parallel_batch≈{max(fe_wall):.1f}ms (slowest card)")

    print("\n=== MEDIA re-fetch warm (same 15 pins again) ===")
    warm = []
    t0 = time.perf_counter()
    for p in pins:
        tw = time.perf_counter()
        client.get(f"/api/pins/upload/{p['id']}")
        warm.append(ms(tw))
    print(
        f"media_warm_ms avg={statistics.mean(warm):.1f} p50={statistics.median(warm):.1f} "
        f"min={min(warm):.1f} max={max(warm):.1f}  batch={ms(t0):.1f}"
    )

    def avg_ms(rows, rnd):
        xs = [r["ms"] for r in rows if r["round"] == rnd and r["status"] == 200]
        return statistics.mean(xs) if xs else float("nan")

    print("\n=== SUMMARY ===")
    print("Home list endpoint: /api/pins/  (NO Redis list cache wired)")
    print(
        f"  round0 avg page ms={avg_ms(list_main, 0):.1f}  "
        f"round1 avg page ms={avg_ms(list_main, 1):.1f}"
    )
    print("Cache list endpoint: /api/pins/cache/")
    print(
        f"  round0 avg page ms={avg_ms(list_cache, 0):.1f}  "
        f"round1 avg page ms={avg_ms(list_cache, 1):.1f}"
    )
    print(
        f"Scroll page1 (15 pins): ~{15 * 5 + 1} HTTP calls; "
        f"each next page (5 pins): ~{5 * 5 + 1} HTTP"
    )
    print(
        "FE media: URL.createObjectURL per mount only — "
        "no shared media Map, no HTTP Cache-Control reuse strategy, no virtualization"
    )


if __name__ == "__main__":
    main()
