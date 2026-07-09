# WebSockets — Explainer

---

## The Problem with HTTP for Real-Time

HTTP is a request-response protocol — the client always initiates. To get updates, you have two naive options:

**Polling:** Ask the server every N seconds.  
```
Client → "Any new location?" → Server → "No"  (×100)
Client → "Any new location?" → Server → "Yes, here it is"
```
Wasteful. Adds latency equal to your polling interval.

**Long polling:** Ask, and the server holds the connection open until it has something to say.
```
Client → "Any new location?" → Server holds...
(driver moves)
Server → "Yes, here it is" → Client immediately asks again
```
Better, but each update still requires a new HTTP request with full headers.

**WebSockets** flip the model: establish one persistent connection, then both sides can send data at any time with near-zero overhead.

---

## The WebSocket Handshake

WebSockets start as an HTTP request and "upgrade" the protocol:

**1. Client sends HTTP Upgrade request:**
```http
GET /ws/trip/abc123 HTTP/1.1
Host: localhost:8000
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

**2. Server responds with 101 Switching Protocols:**
```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

After this, the TCP connection stays open and both sides communicate using the WebSocket frame format — no more HTTP headers on every message.

---

## WebSocket Frame Model

Every message is sent as one or more **frames**:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - -+
```

Key opcodes:
- `0x1` — Text frame (JSON messages)
- `0x2` — Binary frame
- `0x8` — Connection close
- `0x9` — Ping
- `0xA` — Pong

**Masking:** Clients MUST mask frames sent to the server (security requirement of RFC 6455). Servers send unmasked frames to clients.

---

## Ping / Pong — Keepalive

WebSocket connections over the public internet can be silently killed by proxies, load balancers, and NAT devices after a period of inactivity.

**Solution: heartbeat.**

The server periodically sends a `ping` frame. The client must respond with a `pong`. If no pong is received within a timeout window, the server closes the connection and the client knows to reconnect.

```python
# FastAPI handles ping/pong automatically via websocket.receive_bytes()
# but for explicit keepalive in asyncio:
async def heartbeat(websocket):
    while True:
        await asyncio.sleep(30)
        await websocket.send_json({"type": "ping"})
```

---

## Rooms / Channels

In a ride-hailing app, you need location updates to go to the RIGHT rider — not broadcast to everyone.

**Solution: channel namespacing**

Name your WebSocket endpoint with the trip ID:
```
ws://localhost:8000/ws/trip/{trip_id}
```

All clients (driver + rider) connected to `/ws/trip/abc123` are in the same "room". Updates published to `trip:abc123` in Redis go only to subscribers of that channel.

---

## Throttling Location Updates

A phone GPS fires every 500ms or faster. Broadcasting every update wastes bandwidth and CPU.

**The fix: buffer + emit on interval**

```python
# Driver side (simplified)
latest_position = None

async def gps_loop():
    """Receives GPS updates at full frequency"""
    global latest_position
    while True:
        latest_position = await get_gps()  # fires every 500ms
        await asyncio.sleep(0.1)

async def emit_loop(websocket):
    """Emits to server at throttled frequency"""
    while True:
        if latest_position:
            await websocket.send_json(latest_position)
        await asyncio.sleep(3)  # emit every 3 seconds
```

The server receives a new position every 3 seconds, not every 500ms — a 6× reduction in WebSocket messages.

---

## Python WebSocket in FastAPI

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws/trip/{trip_id}")
async def websocket_endpoint(websocket: WebSocket, trip_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # process data...
            await websocket.send_json({"ack": True})
    except WebSocketDisconnect:
        # clean up on disconnect
        pass
```
