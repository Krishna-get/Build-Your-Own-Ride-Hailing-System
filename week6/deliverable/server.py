"""
Week 6 Deliverable — Real-Time Location Streaming Server
==========================================================
A FastAPI WebSocket server that:
  1. Accepts driver connections on /ws/driver/{trip_id}
  2. Receives location updates from drivers and publishes to Redis Pub/Sub
  3. Accepts rider connections on /ws/rider/{trip_id}
  4. Subscribes to Redis Pub/Sub and forwards updates to connected riders

Key requirement: the system must work across TWO server instances.
- Driver connects to Server 1 (port 8000)
- Rider connects to Server 2 (port 8001)
- Rider on Server 2 still receives driver's location via Redis Pub/Sub

Run with:
    pip install "fastapi[standard]" redis websockets
    uvicorn server:app --port 8000   (terminal 1)
    uvicorn server:app --port 8001   (terminal 2)
    python ../starter/driver_simulator.py --server ws://localhost:8000 --trip abc123
    # In another terminal, connect a rider to port 8001 and verify updates arrive
"""

"""
Week 6 Deliverable — Real-Time Location Streaming Server
==========================================================
A FastAPI WebSocket server that:
  1. Accepts driver connections on /ws/driver/{trip_id}
  2. Receives location updates from drivers and publishes to Redis Pub/Sub
  3. Accepts rider connections on /ws/rider/{trip_id}
  4. Subscribes to Redis Pub/Sub and forwards updates to connected riders

Key requirement: the system must work across TWO server instances.
- Driver connects to Server 1 (port 8000)
- Rider connects to Server 2 (port 8001)
- Rider on Server 2 still receives driver's location via Redis Pub/Sub
"""

import asyncio
import json
import os

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Week 6 — Real-Time Location Streaming")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


# ── Connection Manager ────────────────────────────────────────────────────────

class ConnectionManager:
    """
    Tracks active rider WebSocket connections per trip.
    """

    def __init__(self):
        # Maps trip_id -> list of active rider WebSockets
        self.active_riders: dict[str, list[WebSocket]] = {}

    async def connect_rider(self, trip_id: str, websocket: WebSocket):
        """Accept the WebSocket and register the rider under trip_id."""
        await websocket.accept()
        if trip_id not in self.active_riders:
            self.active_riders[trip_id] = []
        self.active_riders[trip_id].append(websocket)

    def disconnect_rider(self, trip_id: str, websocket: WebSocket):
        """Remove the rider's WebSocket from the trip's connection list."""
        if trip_id in self.active_riders:
            if websocket in self.active_riders[trip_id]:
                self.active_riders[trip_id].remove(websocket)
            if not self.active_riders[trip_id]:
                del self.active_riders[trip_id]

    async def broadcast_to_riders(self, trip_id: str, message: dict):
        """
        Send a message to all riders watching trip_id.
        Handle WebSocketDisconnect gracefully — remove dead connections.
        """
        if trip_id not in self.active_riders:
            return

        dead_connections = []
        for websocket in self.active_riders[trip_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                dead_connections.append(websocket)

        # Clean up any broken connections caught during iteration
        for ws in dead_connections:
            self.disconnect_rider(trip_id, ws)


manager = ConnectionManager()


# ── Redis helpers ─────────────────────────────────────────────────────────────

async def get_redis():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)


async def publish_location(trip_id: str, payload: dict):
    """
    Publish a driver location update to the Redis Pub/Sub channel for this trip.
    """
    r = await get_redis()
    try:
        channel_name = f"trip:{trip_id}"
        await r.publish(channel_name, json.dumps(payload))
    finally:
        await r.aclose()


async def subscribe_to_trip(trip_id: str):
    """
    Background task: subscribe to Redis channel trip:{trip_id}
    and forward messages to all connected riders on THIS server instance.
    """
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(f"trip:{trip_id}")
    
    try:
        async for message in pubsub.listen():
            # Check if there are still riders on this instance; if not, break early to free resources
            if trip_id not in manager.active_riders:
                break
                
            if message["type"] == "message":
                data = json.loads(message["data"])
                await manager.broadcast_to_riders(trip_id, data)
    except Exception as e:
        print(f"Error in Pub/Sub listener for trip {trip_id}: {e}")
    finally:
        await pubsub.unsubscribe(f"trip:{trip_id}")
        await pubsub.close()
        await r.aclose()


# ── WebSocket endpoints ───────────────────────────────────────────────────────

@app.websocket("/ws/driver/{trip_id}")
async def driver_websocket(websocket: WebSocket, trip_id: str):
    """
    Drivers connect here to stream their location.
    """
    await websocket.accept()
    print(f"Driver connected to trip {trip_id}")

    try:
        while True:
            # Receive location JSON telemetry data packet from driver simulator
            data = await websocket.receive_json()

            # Publish the parsed driver updates directly out onto our Pub/Sub cluster layer
            await publish_location(trip_id, data)

            # Send ack response frame back to confirm safe delivery
            await websocket.send_json({"type": "ack", "status": "received"})

    except WebSocketDisconnect:
        print(f"Driver disconnected from trip {trip_id}")


@app.websocket("/ws/rider/{trip_id}")
async def rider_websocket(websocket: WebSocket, trip_id: str):
    """
    Riders connect here to receive live driver location.
    """
    await manager.connect_rider(trip_id, websocket)
    print(f"Rider connected to trip {trip_id}")

    # Spin up background subscription channel tasks to handle multi-node broadcast maps
    asyncio.create_task(subscribe_to_trip(trip_id))

    try:
        while True:
            # Persistent framing buffer blocking call - monitors connection status
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_rider(trip_id, websocket)
        print(f"Rider disconnected from trip {trip_id}")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "active_trips": list(manager.active_riders.keys())}