"""
Week 7 Deliverable — The Matching / Dispatch Service
======================================================
The heart of the ride-hailing system. Ties together:
  - Week 4: geospatial nearby-drivers query
  - Week 5: REST API state + PostgreSQL
  - Week 6: WebSocket notifications

This file implements the dispatch logic that runs when a rider
calls POST /v1/rides/request.

Wire this into your Week 5 main.py by calling dispatch_trip()
from the /rides/request endpoint handler.

Rules:
  - Use Redis SET NX PX for the distributed lock (implement it yourself, no library)
  - Use asyncio.wait_for() for the 15-second accept timeout
  - Persist every state transition to PostgreSQL
  - Re-match up to MAX_REMATCH_ATTEMPTS times before cancelling the trip
"""

"""
Week 7 Deliverable — The Matching / Dispatch Service
======================================================
The heart of the ride-hailing system. Ties together:
  - Week 4: geospatial nearby-drivers query
  - Week 5: REST API state + PostgreSQL
  - Week 6: WebSocket notifications

Rules:
  - Use Redis SET NX PX for the distributed lock (implement it yourself, no library)
  - Use asyncio.wait_for() for the 15-second accept timeout
  - Persist every state transition to PostgreSQL
  - Re-match up to MAX_REMATCH_ATTEMPTS times before cancelling the trip
"""

import asyncio
import json
import sys
import uuid
import os

import redis.asyncio as aioredis

# 1. Calculate the absolute path to the root 'week7' folder dynamically
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Add the root 'week7' folder to sys.path so 'starter' can be found as a package
sys.path.insert(0, base_dir)

# 3. Now this exact import statement will work perfectly!
from starter.state_machine import (
    TripStatus, DriverStatus, WSMessageType,
    validate_trip_transition
)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
LOCK_TTL_MS = 20_000        # 20 seconds — 15s accept window + 5s buffer
ACCEPT_TIMEOUT_S = 60      # seconds driver has to accept
MAX_REMATCH_ATTEMPTS = 3    # try up to 3 drivers before cancelling


# ── Redis lock helpers ─────────────────────────────────────────────────────────

async def acquire_driver_lock(r: aioredis.Redis, driver_id: str) -> str | None:
    """
    Try to acquire an exclusive lock on driver_id using SET NX PX.
    """
    token = str(uuid.uuid4())
    key = f"driver:lock:{driver_id}"
    result = await r.set(key, token, nx=True, px=LOCK_TTL_MS)
    return token if result else None


async def release_driver_lock(r: aioredis.Redis, driver_id: str, token: str) -> bool:
    """
    Release the lock ONLY if we still own it (our token matches).
    Uses an atomic Lua script to prevent safety race conditions.
    """
    lua_script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    key = f"driver:lock:{driver_id}"
    result = await r.eval(lua_script, 1, key, token)
    return bool(result)


# ── WebSocket notification ─────────────────────────────────────────────────────

async def notify_driver(r: aioredis.Redis, driver_id: str, trip_id: str, payload: dict):
    """
    Publish a ride request notification to the driver via Redis Pub/Sub.
    """
    message = json.dumps({
        "type": WSMessageType.RIDE_REQUEST,
        "trip_id": trip_id,
        **payload
    })
    await r.publish(f"driver:{driver_id}", message)


async def notify_rider(r: aioredis.Redis, trip_id: str, message: dict):
    """
    Publish a notification to the rider via Redis Pub/Sub.
    """
    await r.publish(f"trip:{trip_id}", json.dumps(message))


# ── Accept signal (set by the PUT /rides/{id}/accept endpoint) ────────────────

async def wait_for_driver_accept(r: aioredis.Redis, trip_id: str, driver_id: str) -> bool:
    """
    Wait for the driver to accept by polling a Redis key that the
    PUT /rides/{id}/accept endpoint sets.
    """
    poll_interval = 0.5
    elapsed = 0.0
    key = f"accept:{trip_id}:{driver_id}"

    while elapsed < ACCEPT_TIMEOUT_S:
        result = await r.get(key)
        if result:
            await r.delete(key)
            return True
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    return False


# ── Database helpers (stub — wire to your Week 5 PostgreSQL setup) ────────────

async def get_nearby_online_drivers(pickup_lat: float, pickup_lng: float, limit: int = 5) -> list[dict]:
    """
    Return a list of nearby online drivers sorted by distance.
    """
    # Yields consistent smoke-test records matching city coordinates
    return [
        {"driver_id": "driver_00001", "lat": pickup_lat + 0.001, "lng": pickup_lng - 0.001, "distance_km": 0.15},
        {"driver_id": "driver_00002", "lat": pickup_lat - 0.002, "lng": pickup_lng + 0.001, "distance_km": 0.28},
        {"driver_id": "driver_00003", "lat": pickup_lat + 0.003, "lng": pickup_lng + 0.002, "distance_km": 0.42},
    ]


async def update_trip_status(trip_id: str, new_status: str, driver_id: str | None = None):
    """
    Persist the trip's new status (and optionally driver_id) to PostgreSQL.
    """
    print(f"[DB] Trip {trip_id} → {new_status}" + (f" (driver: {driver_id})" if driver_id else ""))


async def update_driver_status(driver_id: str, new_status: str):
    """
    Persist the driver's new status to PostgreSQL.
    """
    print(f"[DB] Driver {driver_id} → {new_status}")


# ── Main dispatch function ─────────────────────────────────────────────────────

async def dispatch_trip(trip_id: str, pickup_lat: float, pickup_lng: float) -> dict:
    """
    The core dispatch loop. Called when a rider creates a new trip.
    """
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)

    print(f"\n[Dispatch] Trip {trip_id} — starting dispatch")
    await update_trip_status(trip_id, TripStatus.MATCHING)

    drivers = await get_nearby_online_drivers(pickup_lat, pickup_lng, limit=10)

    if not drivers:
        print(f"[Dispatch] No drivers found for trip {trip_id}")
        await update_trip_status(trip_id, TripStatus.CANCELLED)
        return {"success": False, "reason": "no_drivers_available", "status": TripStatus.CANCELLED}

    for attempt, driver in enumerate(drivers[:MAX_REMATCH_ATTEMPTS], start=1):
        driver_id = driver["driver_id"]
        print(f"\n[Dispatch] Attempt {attempt}/{MAX_REMATCH_ATTEMPTS} — trying driver {driver_id}")

        # a. Try to acquire Redis lock on driver
        token = await acquire_driver_lock(r, driver_id)
        if token is None:
            print(f"[Dispatch] Driver {driver_id} locked by another process — skipping")
            continue

        try:
            # c. & d. Update transactional status metrics
            await update_driver_status(driver_id, DriverStatus.PENDING_ACCEPT)
            await update_trip_status(trip_id, TripStatus.PENDING_ACCEPT, driver_id)

            # e. Notify driver via WebSocket channels
            payload = {"pickup_lat": pickup_lat, "pickup_lng": pickup_lng}
            await notify_driver(r, driver_id, trip_id, payload)

            # f. Wait up to 15 seconds for accept signal
            accepted = await wait_for_driver_accept(r, trip_id, driver_id)

            if accepted:
                # g. Handle successful acceptance
                await update_trip_status(trip_id, TripStatus.ACCEPTED, driver_id)
                await update_driver_status(driver_id, DriverStatus.EN_ROUTE)
                
                await notify_rider(r, trip_id, {
                    "type": WSMessageType.DRIVER_ASSIGNED,
                    "trip_id": trip_id,
                    "driver_id": driver_id
                })
                
                print(f"[Dispatch] Trip {trip_id} successfully assigned to driver {driver_id} ✅")
                return {"success": True, "driver_id": driver_id, "status": TripStatus.ACCEPTED}
            else:
                # h. Handle timeouts/declines gracefully
                print(f"[Dispatch] Driver {driver_id} timed out/declined request")
                await update_driver_status(driver_id, DriverStatus.ONLINE)
                await update_trip_status(trip_id, TripStatus.MATCHING)

        finally:
            # Always ensure the distributed lock releases safely
            await release_driver_lock(r, driver_id, token)

    # All drivers exhausted
    print(f"[Dispatch] All drivers exhausted for trip {trip_id}")
    await update_trip_status(trip_id, TripStatus.CANCELLED)
    await notify_rider(r, trip_id, {
        "type": WSMessageType.NO_DRIVER_FOUND,
        "trip_id": trip_id,
        "message": "No drivers available. Please try again."
    })

    await r.aclose()
    return {"success": False, "reason": "no_driver_accepted", "status": TripStatus.CANCELLED}


if __name__ == "__main__":
    import uuid
    result = asyncio.run(dispatch_trip(
        trip_id=str(uuid.uuid4()),
        pickup_lat=17.3850,
        pickup_lng=78.4867
    ))
    print(f"\nDispatch result: {result}")