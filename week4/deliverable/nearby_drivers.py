"""
Week 4 Deliverable — Nearby Drivers Service
=============================================
Given a rider's lat/lng, return the 5 nearest drivers in under 50ms.

Use EITHER:
  (a) Geohash prefix matching (search center cell + 8 neighbours), or
  (b) H3 k-ring lookup

You may use Redis's built-in GEO commands (GEOSEARCH) OR implement your own
geohash/H3 bucketing — your choice. The goal is to understand WHY this is fast,
not to reinvent Redis's C implementation from scratch.

Rules:
  - You MUST seed and query at least 10,000 drivers (use starter/seed_drivers.py)
  - You MUST benchmark your query and report the time
  - You MUST explain (in REFLECTION.md) which approach you chose and why
"""

import time
import json
import math
import sys

sys.path.insert(0, "../starter")


# ── Haversine (reuse from Week 3 — needed to rank final candidates by distance) ──

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two lat/lng points."""
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Option A: Redis GEOSEARCH (recommended if you have Redis running) ─────────

def find_nearby_redis(rider_lat: float, rider_lng: float, count: int = 5) -> list:
    """
    Use Redis's built-in geospatial commands to find nearby drivers.

    Hint:
        import redis
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        results = r.geosearch(
            "drivers:geo",
            longitude=rider_lng, latitude=rider_lat,
            radius=10, unit="km",
            count=count, sort="ASC",
            withdist=True
        )
        # results: [(driver_id, distance_km), ...]
    """
    # --- your code here ---
    pass


# ── Option B: Your own H3 k-ring implementation ───────────────────────────────

def find_nearby_h3(rider_lat: float, rider_lng: float, drivers: dict, count: int = 5,
                    resolution: int = 7) -> list:
    """
    Use H3 k-ring lookup to find nearby drivers.

    Steps:
      1. Compute rider's H3 cell at `resolution`
      2. Get k-ring neighbours (try k=1, expand to k=2 if too few candidates found)
      3. Group all drivers by their H3 cell (precompute this once, not per-query!)
      4. Gather drivers whose cell is in the k-ring
      5. Compute exact Haversine distance for each candidate, sort, return top `count`

    Hint:
        import h3
        rider_cell = h3.latlng_to_cell(rider_lat, rider_lng, resolution)
        candidate_cells = h3.grid_disk(rider_cell, 1)  # k=1 ring
    """
    # --- your code here ---
    pass


# ── Option C: Your own geohash prefix implementation ──────────────────────────

def find_nearby_geohash(rider_lat: float, rider_lng: float, drivers: dict, count: int = 5,
                         precision: int = 5) -> list:
    """
    Use geohash prefix matching (center cell + 8 neighbours) to find nearby drivers.

    Steps:
      1. Compute rider's geohash at `precision`
      2. Get the 8 neighbouring geohash prefixes
      3. Group all drivers by their geohash prefix (precompute this once!)
      4. Gather drivers whose geohash starts with rider's prefix OR a neighbour's prefix
      5. Compute exact Haversine distance for each candidate, sort, return top `count`
    """
    # --- your code here ---
    pass


# ── Benchmark harness ──────────────────────────────────────────────────────────

def benchmark(fn, *args, runs: int = 100, **kwargs):
    """Run `fn` `runs` times and report average latency in ms."""
    times = []
    result = None
    for _ in range(runs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        times.append(elapsed_ms)

    avg_ms = sum(times) / len(times)
    return result, avg_ms


def main():
    rider_lat, rider_lng = 17.3850, 78.4867  # Hyderabad city centre

    print(f"Rider location: ({rider_lat}, {rider_lng})\n")
    print("Querying 5 nearest drivers...\n")

    # --- choose your implementation here ---
    # results, avg_ms = benchmark(find_nearby_redis, rider_lat, rider_lng)
    # OR
    # drivers = json.load(open("../starter/drivers_fallback.json"))
    # results, avg_ms = benchmark(find_nearby_h3, rider_lat, rider_lng, drivers)

    results, avg_ms = None, None  # placeholder until implemented

    if results:
        for i, (driver_id, dist) in enumerate(results, 1):
            print(f"{i}. {driver_id}  →  {dist:.2f} km")

        status = "✅" if avg_ms < 50 else "❌"
        print(f"\nQuery time: {avg_ms:.1f} ms  {status} (target: under 50ms)")
    else:
        print("Not implemented yet — fill in one of the find_nearby_* functions above.")


if __name__ == "__main__":
    main()
