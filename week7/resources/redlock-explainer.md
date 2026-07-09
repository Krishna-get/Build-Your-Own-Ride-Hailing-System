# Redis Distributed Locks (Redlock) — Explainer

---

## The Race Condition

Two riders request a ride at the same millisecond. Both get matched to the same driver (the nearest). Without a lock:

```
Server 1 (Rider A's request):            Server 2 (Rider B's request):
  1. Find nearest driver → driver_042       1. Find nearest driver → driver_042
  2. Notify driver_042 via WS               2. Notify driver_042 via WS
  3. Wait for accept...                     3. Wait for accept...
  4. Driver accepts → assign to Rider A    4. Driver accepts → assign to Rider B ← DOUBLE BOOKING
```

The driver receives two accept notifications and only responds to one. The other rider is now in MATCHING state with a driver who's already been assigned elsewhere. The trip record for one rider will never progress.

**This is one of the hardest problems in dispatch systems.** It's the same problem banks face with double-spending.

---

## The Solution: Distributed Lock

Before notifying the driver, acquire an exclusive lock. Only one server can hold the lock for a given driver at any time.

```
Server 1 (Rider A's request):            Server 2 (Rider B's request):
  1. Find nearest → driver_042              1. Find nearest → driver_042
  2. SET driver:lock:042 token1 NX PX 20000 2. SET driver:lock:042 token2 NX PX 20000
     → OK (lock acquired ✅)                   → nil (lock NOT acquired ❌)
  3. Notify driver_042                      3. Skip driver_042, try next driver
  4. Wait for accept...                     4. Find next nearest → driver_019
  5. Accept received                        5. SET driver:lock:019 token2 NX PX 20000...
  6. DEL driver:lock:042 (if token matches)
```

---

## The Redis Lock Pattern (Single Instance)

```python
import redis
import uuid
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def acquire_lock(driver_id: str, ttl_ms: int = 20000) -> str | None:
    """
    Try to acquire an exclusive lock on driver_id.
    Returns a unique token if successful, None if lock already held.

    Uses SET NX PX:
      NX = Only set if key does Not eXist
      PX = Set expiry in milliseconds
    """
    token = str(uuid.uuid4())
    key = f"driver:lock:{driver_id}"
    result = r.set(key, token, nx=True, px=ttl_ms)
    return token if result else None


def release_lock(driver_id: str, token: str) -> bool:
    """
    Release the lock ONLY if we still own it (our token matches).
    Uses a Lua script to make check-and-delete atomic.

    Why atomic? Without atomicity:
      1. We check: key value == our token ✅
      2. Lock expires (TTL hits)
      3. Another server acquires the lock
      4. We delete the key ← we just deleted someone else's lock!
    """
    lua_script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    key = f"driver:lock:{driver_id}"
    result = r.eval(lua_script, 1, key, token)
    return bool(result)
```

---

## Using the Lock in Dispatch

```python
async def dispatch_to_driver(driver_id: str, trip_id: str, rider_ws_channel: str):
    token = acquire_lock(driver_id, ttl_ms=20000)

    if token is None:
        return False  # driver already being processed — try next driver

    try:
        # Notify driver via WebSocket (Week 6)
        await notify_driver(driver_id, trip_id)

        # Wait for accept with 15-second timeout
        try:
            accepted = await asyncio.wait_for(
                wait_for_driver_response(driver_id, trip_id),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            accepted = False

        if accepted:
            await update_trip_status(trip_id, "ACCEPTED", driver_id)
            return True
        else:
            return False

    finally:
        release_lock(driver_id, token)  # always release, even on exception
```

---

## TTL — Why It's Critical

The lock has a TTL (time to live) set via `PX 20000` (20 seconds).

**What if the server holding the lock crashes?**

Without TTL: the lock key lives in Redis forever. No driver is ever matched again. The system deadlocks.

With TTL: Redis automatically deletes the key after 20 seconds. The next dispatch attempt can acquire the lock.

**Choose TTL carefully:**
- Too short → lock expires while driver is still considering the request → another rider grabs the driver → double booking
- Too long → a server crash blocks that driver for the full TTL window

For a 15-second accept timeout: TTL = 20 seconds (15s window + 5s buffer for network latency) is a reasonable choice.

---

## Important Limitation of Single-Instance Redlock

The pattern above uses a single Redis instance. If that instance crashes after granting the lock but before the client confirms, another client could acquire the lock on a replica that hasn't received the key yet (Redis replication is asynchronous).

**The full Redlock algorithm** acquires the lock on N (≥3) independent Redis instances and requires a majority (≥N/2+1) to succeed.

For this roadmap: single-instance Redlock is fine. In production at Uber scale, you'd use the full multi-instance algorithm or a dedicated coordination service (etcd, ZooKeeper).

---

## Martin Kleppmann's Critique

Even the full Redlock algorithm has edge cases around process pauses (e.g. GC stop-the-world). Kleppmann argues that for true safety, you need **fencing tokens** — a monotonically increasing number issued with each lock, passed to the resource being protected, which rejects requests with stale tokens.

Read his analysis linked from the Redis Redlock docs — it's one of the best distributed systems articles on the internet.

For ride-hailing: the window for these edge cases is small and the consequence (a double-booked driver who declines one request) is recoverable. Production systems accept this risk and add retry logic to handle the rare case.
