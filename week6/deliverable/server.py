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

    TODO:
      - Store connections in a dict: {trip_id: [WebSocket, ...]}
      - Implement connect(), disconnect(), broadcast_to_trip()
    """

    def __init__(self):
        self.active_riders: dict[str, list[WebSocket]] = {}

    async def connect_rider(self, trip_id: str, websocket: WebSocket):
        """Accept the WebSocket and register the rider under trip_id."""
        await websocket.accept()
        # --- your code here ---

    def disconnect_rider(self, trip_id: str, websocket: WebSocket):
        """Remove the rider's WebSocket from the trip's connection list."""
        # --- your code here ---

    async def broadcast_to_riders(self, trip_id: str, message: dict):
        """
        Send a message to all riders watching trip_id.
        Handle WebSocketDisconnect gracefully — remove dead connections.
        """
        # --- your code here ---


manager = ConnectionManager()


# ── Redis helpers ─────────────────────────────────────────────────────────────

async def get_redis():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)


async def publish_location(trip_id: str, payload: dict):
    """
    Publish a driver location update to the Redis Pub/Sub channel for this trip.

    Channel name convention: trip:{trip_id}
    Payload: JSON string of {"driver_id": ..., "lat": ..., "lng": ..., "timestamp": ...}

    TODO:
      r = await get_redis()
      await r.publish(f"trip:{trip_id}", json.dumps(payload))
    """
    # --- your code here ---
    pass


async def subscribe_to_trip(trip_id: str):
    """
    Background task: subscribe to Redis channel trip:{trip_id}
    and forward messages to all connected riders on THIS server instance.

    This is the key to horizontal scaling — each server subscribes to Redis
    for every trip that has at least one rider connected to it.

    TODO:
      r = await get_redis()
      pubsub = r.pubsub()
      await pubsub.subscribe(f"trip:{trip_id}")
      async for message in pubsub.listen():
          if message["type"] == "message":
              data = json.loads(message["data"])
              await manager.broadcast_to_riders(trip_id, data)
    """
    # --- your code here ---
    pass


# ── WebSocket endpoints ───────────────────────────────────────────────────────

@app.websocket("/ws/driver/{trip_id}")
async def driver_websocket(websocket: WebSocket, trip_id: str):
    """
    Drivers connect here to stream their location.

    Flow:
      1. Accept the connection
      2. Loop: receive location JSON from driver
      3. Publish to Redis Pub/Sub channel for this trip
      4. Send ack back to driver
      5. Handle WebSocketDisconnect gracefully

    TODO: implement the receive-publish-ack loop
    """
    await websocket.accept()
    print(f"Driver connected to trip {trip_id}")

    try:
        while True:
            data = await websocket.receive_json()

            # --- your code here: publish data to Redis ---

            # Send ack
            await websocket.send_json({"type": "ack", "status": "received"})

    except WebSocketDisconnect:
        print(f"Driver disconnected from trip {trip_id}")


@app.websocket("/ws/rider/{trip_id}")
async def rider_websocket(websocket: WebSocket, trip_id: str):
    """
    Riders connect here to receive live driver location.

    Flow:
      1. Register rider in ConnectionManager
      2. Start a background task to subscribe to Redis for this trip
      3. Keep the connection alive (wait for disconnect)
      4. Clean up on disconnect

    TODO: implement the full flow
    Hint:
      asyncio.create_task(subscribe_to_trip(trip_id))
      try:
          while True:
              await websocket.receive_text()  # keep alive, wait for disconnect
      except WebSocketDisconnect:
          manager.disconnect_rider(trip_id, websocket)
    """
    await manager.connect_rider(trip_id, websocket)
    print(f"Rider connected to trip {trip_id}")

    # --- your code here ---

    try:
        while True:
            await websocket.receive_text()  # placeholder — keeps connection alive
    except WebSocketDisconnect:
        manager.disconnect_rider(trip_id, websocket)
        print(f"Rider disconnected from trip {trip_id}")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "active_trips": list(manager.active_riders.keys())}
