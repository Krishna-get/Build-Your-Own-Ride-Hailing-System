"""
starter/seed_drivers.py
========================
Generates 10,000 fake driver locations scattered around a city centre
and stores them either in Redis (if available) or an in-memory dict.

Run this before working on deliverable/nearby_drivers.py.

Usage:
    pip install redis  # optional, only if you want real Redis
    python seed_drivers.py
"""

import random
import json

# ── City centre to scatter drivers around ─────────────────────────────────────
CITY_CENTER_LAT = 17.3850   # Hyderabad
CITY_CENTER_LNG = 78.4867
SCATTER_RADIUS_DEG = 0.15   # roughly ±15km in each direction

NUM_DRIVERS = 10_000


def generate_fake_drivers(n: int = NUM_DRIVERS) -> dict:
    """
    Generate n fake drivers with random lat/lng near the city centre.

    Returns:
        {driver_id: {"lat": float, "lng": float}}
    """
    drivers = {}
    for i in range(n):
        driver_id = f"driver_{i:05d}"
        lat = CITY_CENTER_LAT + random.uniform(-SCATTER_RADIUS_DEG, SCATTER_RADIUS_DEG)
        lng = CITY_CENTER_LNG + random.uniform(-SCATTER_RADIUS_DEG, SCATTER_RADIUS_DEG)
        drivers[driver_id] = {"lat": lat, "lng": lng}
    return drivers


def seed_into_redis(drivers: dict):
    """
    Seed drivers into Redis using the GEOADD command.
    Requires a running Redis instance (localhost:6379 by default).
    """
    import redis

    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r.delete("drivers:geo")  # clear previous run

    pipe = r.pipeline()
    for driver_id, loc in drivers.items():
        # GEOADD key longitude latitude member
        pipe.geoadd("drivers:geo", (loc["lng"], loc["lat"], driver_id))
    pipe.execute()

    print(f"Seeded {len(drivers)} drivers into Redis key 'drivers:geo'")


def seed_into_memory(drivers: dict, filepath: str = "drivers_fallback.json"):
    """
    Fallback: save drivers to a local JSON file for in-memory use
    if Redis isn't available.
    """
    with open(filepath, "w") as f:
        json.dump(drivers, f, indent=2)
    print(f"Seeded {len(drivers)} drivers into {filepath} (in-memory fallback)")


def main():
    print(f"Generating {NUM_DRIVERS:,} fake drivers around ({CITY_CENTER_LAT}, {CITY_CENTER_LNG})...")
    drivers = generate_fake_drivers()

    try:
        seed_into_redis(drivers)
    except Exception as e:
        print(f"Redis not available ({e}). Falling back to in-memory JSON file.")
        seed_into_memory(drivers)


if __name__ == "__main__":
    main()
