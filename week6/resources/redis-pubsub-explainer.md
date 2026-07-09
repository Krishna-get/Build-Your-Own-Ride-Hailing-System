# Redis Pub/Sub — Explainer

---

## The Scaling Problem

Without Redis Pub/Sub, your WebSocket server has a fatal flaw:

```
Driver  →  [Server 1]     [Server 2]  ←  Rider
              ↑                ↑
        driver connected   rider connected
           (port 8000)       (port 8001)
```

The driver connects to Server 1. The rider connects to Server 2. Server 1 has no way to push the driver's location to Server 2's rider — they're separate processes with no shared memory.

**This means your system can only run on ONE server instance** — which can't scale to handle millions of concurrent trips.

---

## The Fix: Redis Pub/Sub as a Message Bus

```
Driver  →  [Server 1]  →  PUBLISH trip:abc123  →  [Redis]
                                                       ↓
                                             SUBSCRIBE trip:abc123
                                                       ↓
                          [Server 2]  ←  message  ←  [Redis]
                               ↓
                             Rider
```

Every server instance subscribes to Redis channels for the trips whose riders are connected to it. When a driver publishes a location update on Server 1, Redis fans it out to every server that has a subscriber for that trip — including Server 2, which forwards it to the rider.

---

## Redis Pub/Sub Commands

```python
import redis.asyncio as redis

r = redis.Redis(host="localhost", port=6379)

# Publisher (on the server receiving driver updates)
await r.publish("trip:abc123", json.dumps({
    "driver_id": "driver_001",
    "lat": 17.385,
    "lng": 78.487
}))

# Subscriber (on the server with the rider connected)
pubsub = r.pubsub()
await pubsub.subscribe("trip:abc123")

async for message in pubsub.listen():
    if message["type"] == "message":
        data = json.loads(message["data"])
        # forward to rider's WebSocket
```

---

## The Full Architecture (Week 6)

```
Driver App
    │  emit lat/lng every 3s
    │  WebSocket
    ▼
WebSocket Server 1
    │  receives location
    │  PUBLISH trip:{id} → Redis channel
    ▼
Redis Pub/Sub
    │  fans out to all subscribers of trip:{id}
    ▼
WebSocket Server 2
    │  SUBSCRIBE trip:{id}
    │  receives message from Redis
    │  forwards to Rider's WebSocket
    ▼
Rider App
    │  sees driver marker move on map
```

---

## Key Properties of Redis Pub/Sub

| Property | Detail |
|----------|--------|
| **Fire and forget** | If no one is subscribed when PUBLISH is called, the message is lost — not queued |
| **No persistence** | Messages are NOT stored in Redis — this is purely a messaging bus |
| **Fan-out** | One PUBLISH delivers to ALL current subscribers of that channel |
| **Pattern subscriptions** | `PSUBSCRIBE trip:*` matches all channels starting with `trip:` |

**Implication for this roadmap:** if a rider disconnects and reconnects, they may miss location updates that happened while disconnected. That's acceptable for live location — they'll get the next one in 3 seconds. For critical events (trip acceptance, completion), use the database (PostgreSQL) as the source of truth, not Pub/Sub.

---

## Python Implementation Pattern

```python
import asyncio
import json
import redis.asyncio as redis
from fastapi import WebSocket

class ConnectionManager:
    """Manages active WebSocket connections per trip."""

    def __init__(self):
        # trip_id → list of WebSocket connections (riders watching that trip)
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, trip_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(trip_id, []).append(websocket)

    def disconnect(self, trip_id: str, websocket: WebSocket):
        self.active_connections.get(trip_id, []).remove(websocket)

    async def broadcast_to_trip(self, trip_id: str, message: dict):
        for ws in self.active_connections.get(trip_id, []):
            await ws.send_json(message)


async def redis_subscriber(manager: ConnectionManager, trip_id: str):
    """
    Background task: subscribe to Redis channel for a trip and
    forward messages to all connected riders.
    """
    r = redis.Redis(host="localhost", port=6379)
    pubsub = r.pubsub()
    await pubsub.subscribe(f"trip:{trip_id}")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            await manager.broadcast_to_trip(trip_id, data)
```

---

## Horizontal Scaling Check

To verify your implementation works across multiple server instances:

```bash
# Terminal 1
uvicorn server:app --port 8000

# Terminal 2
uvicorn server:app --port 8001

# Terminal 3 — driver simulator connects to server 1
python starter/driver_simulator.py --server ws://localhost:8000 --trip abc123

# Terminal 4 — rider client connects to server 2
python -c "
import asyncio, websockets, json
async def rider():
    async with websockets.connect('ws://localhost:8001/ws/rider/abc123') as ws:
        async for msg in ws:
            print('Rider received:', json.loads(msg))
asyncio.run(rider())
"
```

If the rider on port 8001 receives updates from the driver on port 8000, your Redis Pub/Sub is working correctly.
