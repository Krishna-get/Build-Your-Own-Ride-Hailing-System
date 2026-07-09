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

import asyncio
import json
import sys
import uuid
import os

import redis.asyncio as aioredis

sys.path.insert(0, "../starter")
from state_machine import (
    TripStatus, DriverStatus, WSMessageType,
    validate_trip_transition
)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
LOCK_TTL_MS = 20_000        # 20 seconds — 15s accept window + 5s buffer
ACCEPT_TIMEOUT_S = 15       # seconds driver has to accept
MAX_REMATCH_ATTEMPTS = 3    # try up to 3 drivers before cancelling


# ── Redis lock helpers ─────────────────────────────────────────────────────────

async def acquire_driver_lock(r: aioredis.Redis, driver_id: str) -> str | None:
    """
    Try to acquire an exclusive lock on driver_id.

    Returns a unique token string if the lock was acquired, None if not.

    TODO:
      token = str(uuid.uuid4())
      key = f"driver:lock:{driver_id}"
      result = await r.set(key, token, nx=True, px=LOCK_TTL_MS)
      return token if result else None
    """
    # --- your code here ---
    pass


async def release_driver_lock(r: aioredis.Redis, driver_id: str, token: str) -> bool:
    """
    Release the lock ONLY if we still own it (our token matches).
    Uses a Lua script to make the check-and-delete atomic.

    TODO:
      lua_script = '''
      if redis.call('get', KEYS[1]) == ARGV[1] then
          return redis.call('del', KEYS[1])
      else
          return 0
      end
      '''
      key = f"driver:lock:{driver_id}"
      result = await r.eval(lua_script, 1, key, token)
      return bool(result)
    """
    # --- your code here ---
    pass


# ── WebSocket notification ─────────────────────────────────────────────────────

async def notify_driver(r: aioredis.Redis, driver_id: str, trip_id: str, payload: dict):
    """
    Publish a ride request notification to the driver via Redis Pub/Sub.
    The WebSocket server (Week 6) is subscribed to driver:{driver_id} and will
    forward this to the driver's connected WebSocket.

    TODO:
      message = json.dumps({
          "type": WSMessageType.RIDE_REQUEST,
          "trip_id": trip_id,
          **payload
      })
      await r.publish(f"driver:{driver_id}", message)
    """
    # --- your code here ---
    pass


async def notify_rider(r: aioredis.Redis, trip_id: str, message: dict):
    """
    Publish a notification to the rider via Redis Pub/Sub.
    The WebSocket server is subscribed to trip:{trip_id}.

    TODO:
      await r.publish(f"trip:{trip_id}", json.dumps(message))
    """
    # --- your code here ---
    pass


# ── Accept signal (set by the PUT /rides/{id}/accept endpoint) ────────────────

async def wait_for_driver_accept(r: aioredis.Redis, trip_id: str, driver_id: str) -> bool:
    """
    Wait for the driver to accept by polling a Redis key that the
    PUT /rides/{id}/accept endpoint sets.

    The accept endpoint should do:
      await r.set(f"accept:{trip_id}:{driver_id}", "1", px=30000)

    TODO:
      Poll every 0.5 seconds for up to ACCEPT_TIMEOUT_S:
        key = f"accept:{trip_id}:{driver_id}"
        result = await r.get(key)
        if result:
            await r.delete(key)
            return True
        await asyncio.sleep(0.5)
      return False
    """
    # --- your code here ---
    pass


# ── Database helpers (stub — wire to your Week 5 PostgreSQL setup) ────────────

async def get_nearby_online_drivers(pickup_lat: float, pickup_lng: float, limit: int = 5) -> list[dict]:
    """
    Return a list of nearby online drivers sorted by distance.
    Reuse your Week 4 implementation here.

    Each dict: {"driver_id": str, "lat": float, "lng": float, "distance_km": float}

    TODO: call your Week 4 nearby-drivers service
    """
    # --- your code here (or import from Week 4) ---
    return []


async def update_trip_status(trip_id: str, new_status: str, driver_id: str | None = None):
    """
    Persist the trip's new status (and optionally driver_id) to PostgreSQL.

    TODO:
      Use your Week 5 database connection to run:
        UPDATE trips SET status=$1, driver_id=$2 WHERE id=$3
    """
    print(f"[DB] Trip {trip_id} → {new_status}" + (f" (driver: {driver_id})" if driver_id else ""))
    # --- your code here ---


async def update_driver_status(driver_id: str, new_status: str):
    """
    Persist the driver's new status to PostgreSQL.

    TODO:
      UPDATE drivers SET status=$1 WHERE user_id=$2
    """
    print(f"[DB] Driver {driver_id} → {new_status}")
    # --- your code here ---


# ── Main dispatch function ─────────────────────────────────────────────────────

async def dispatch_trip(trip_id: str, pickup_lat: float, pickup_lng: float) -> dict:
    """
    The core dispatch loop. Called when a rider creates a new trip.

    Returns:
        {"success": True,  "driver_id": ..., "status": "ACCEPTED"}  on success
        {"success": False, "reason": "no_driver_found", "status": "CANCELLED"}  on failure

    Algorithm:
      1. Update trip status: REQUESTED → MATCHING
      2. Query nearby online drivers (sorted by distance)
      3. For each driver (up to MAX_REMATCH_ATTEMPTS):
          a. Try to acquire Redis lock on driver
          b. If locked by someone else → skip to next driver
          c. Update driver status → PENDING_ACCEPT
          d. Update trip status → PENDING_ACCEPT
          e. Notify driver via WebSocket (through Redis Pub/Sub)
          f. Wait up to 15 seconds for accept signal
          g. If accepted:
               - Update trip → ACCEPTED, set driver_id
               - Update driver → EN_ROUTE
               - Notify rider → DRIVER_ASSIGNED
               - Release lock
               - Return success
          h. If declined/timeout:
               - Release lock
               - Update driver → ONLINE (available again)
               - Update trip → MATCHING (re-matching)
               - Try next driver
      4. If all drivers exhausted:
          - Update trip → CANCELLED
          - Notify rider → NO_DRIVER_FOUND
          - Return failure
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

        # --- your dispatch loop here ---
        # Follow the algorithm described in the docstring above

        pass  # remove this once implemented

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


# ── Quick test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Quick smoke test — run this to check your dispatch logic works end-to-end.
    Make sure Redis is running and your Week 4 nearby-drivers service returns data.
    """
    result = asyncio.run(dispatch_trip(
        trip_id=str(uuid.uuid4()),
        pickup_lat=17.3850,
        pickup_lng=78.4867
    ))
    print(f"\nDispatch result: {result}")
