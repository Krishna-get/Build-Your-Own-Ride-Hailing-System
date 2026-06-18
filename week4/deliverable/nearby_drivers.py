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
import os

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
    # Import locally to keep dependencies optional if someone doesn't have redis-py
    import redis
    
    # Establish connection with the local running Redis database instance
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    
    # Run an optimized spatial range search directly inside Redis's sorted set memory
    results = r.geosearch(
        "drivers:geo",                # The geospatial key name used in seed_drivers.py
        longitude=rider_lng,
        latitude=rider_lat,
        radius=15,                    # Radius limit to capture drivers in scattered radius
        unit="km",
        count=count,                  # Slices exactly the top matches
        sort="ASC",                   # Sorts by closest distance automatically
        withdist=True                 # Returns a tuple of (driver_id, distance)
    )
    return results


# ── Option B: Your own H3 k-ring implementation ───────────────────────────────

# Global dictionary to act as our precomputed cell index so we don't rebuild it on every query
_h3_precomputed_index = {}

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
    import h3
    global _h3_precomputed_index

    # Step 3: Group all drivers by their H3 cell (precompute this once across the benchmark!)
    if not _h3_precomputed_index:
        for driver_id, loc in drivers.items():
            cell = h3.latlng_to_cell(loc["lat"], loc["lng"], resolution)
            if cell not in _h3_precomputed_index:
                _h3_precomputed_index[cell] = []
            # Index structural layout: { cell_index: [(driver_id, loc_dict), ...] }
            _h3_precomputed_index[cell].append((driver_id, loc))

    # Step 1: Compute rider's corresponding H3 cell coordinate index
    rider_cell = h3.latlng_to_cell(rider_lat, rider_lng, resolution)
    
    # Step 2: Extract the center cell + its 1st concentric ring of neighbors (7 cells total)
    k = 1
    candidate_cells = h3.grid_disk(rider_cell, k)
    
    # Step 4: Gather candidate drivers sitting directly inside these ring cells
    candidates = []
    for cell in candidate_cells:
        if cell in _h3_precomputed_index:
            candidates.extend(_h3_precomputed_index[cell])
            
    # Dynamic expansion: if k=1 yields too few records, expand boundary scanning to a k=2 ring
    if len(candidates) < count:
        candidate_cells = h3.grid_disk(rider_cell, 2)
        candidates = []
        for cell in candidate_cells:
            if cell in _h3_precomputed_index:
                candidates.extend(_h3_precomputed_index[cell])

    # Step 5: Compute exact Haversine distance for each bucketed candidate to filter precisely
    final_results = []
    for driver_id, loc in candidates:
        dist = haversine(rider_lat, rider_lng, loc["lat"], loc["lng"])
        final_results.append((driver_id, dist))
        
    # Sort strictly by closest distance criteria and slice down to the requested count
    final_results.sort(key=lambda x: x[1])
    return final_results[:count]


# ── Option C: Your own geohash prefix implementation ──────────────────────────

# Global dictionary to store the precomputed geohash prefix map across iterations
_geohash_precomputed_index = {}

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
    # Support both 'geohash2' and standard 'geohash' library brand namings
    try:
        import geohash2 as geohash
    except ImportError:
        import geohash
        
    global _geohash_precomputed_index

    # Step 3: Group all drivers by their unique geohash prefix (precompute this once!)
    if not _geohash_precomputed_index:
        for driver_id, loc in drivers.items():
            gh = geohash.encode(loc["lat"], loc["lng"], precision)
            if gh not in _geohash_precomputed_index:
                _geohash_precomputed_index[gh] = []
            _geohash_precomputed_index[gh].append((driver_id, loc))

    # Step 1: Compute rider's primary target geohash string
    rider_gh = geohash.encode(rider_lat, rider_lng, precision)
    
    # Step 2: Extract the 8 adjacent cell prefixes to safely clear boundary edge cases
    if hasattr(geohash, 'neighbors'):
        neighbor_cells = geohash.neighbors(rider_gh)
    else:
        neighbor_cells = geohash.neighbours(rider_gh)
        
    # Assemble complete target zone: center cell string prefix + 8 neighboring prefixes
    search_cells = [rider_gh] + neighbor_cells

    # Step 4: Harvest driver rows associated with these specific prefix indexes
    candidates = []
    for gh in search_cells:
        if gh in _geohash_precomputed_index:
            candidates.extend(_geohash_precomputed_index[gh])

    # Step 5: Compute exact Haversine distance for the isolated candidates
    final_results = []
    for driver_id, loc in candidates:
        dist = haversine(rider_lat, rider_lng, loc["lat"], loc["lng"])
        final_results.append((driver_id, dist))
        
    # Sort strictly ascending and slice the top nearest elements
    final_results.sort(key=lambda x: x[1])
    return final_results[:count]


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

    results, avg_ms = None, None

    # Step A: Attempt strategy evaluation against Redis if a live running server exists
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        if r.exists("drivers:geo"):
            results, avg_ms = benchmark(find_nearby_redis, rider_lat, rider_lng)
            print("Strategy: Redis GEOSEARCH (Option A)")
    except Exception:
        results, avg_ms = None, None

    # Step B: If Redis is unavailable, fall back onto regional In-Memory Index Strategies
    if not results:
        fallback_filepath = "../drivers_fallback.json"
        if os.path.exists(fallback_filepath):
            drivers = json.load(open(fallback_filepath))
            
            # Prioritize Uber H3 over Geohash due to superior distance equality mapping
            try:
                import h3
                results, avg_ms = benchmark(find_nearby_h3, rider_lat, rider_lng, drivers)
                print("Strategy: In-Memory Uber H3 Grid (Option B)")
            except ImportError:
                results, avg_ms = benchmark(find_nearby_geohash, rider_lat, rider_lng, drivers)
                print("Strategy: In-Memory Geohash Prefix Matching (Option C)")

    # Render benchmarking summaries cleanly
    if results:
        for i, (driver_id, dist) in enumerate(results, 1):
            print(f"{i}. {driver_id}  →  {dist:.2f} km")

        status = "✅" if avg_ms < 50 else "❌"
        print(f"\nQuery time: {avg_ms:.2f} ms  {status} (target: under 50ms)")
    else:
        print("Not implemented yet — fill in one of the find_nearby_* functions above.")


if __name__ == "__main__":
    main()