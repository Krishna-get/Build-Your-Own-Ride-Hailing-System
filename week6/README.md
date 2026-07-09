# Week 6 — Real-Time Location Streaming with WebSockets

> **Engineering Behind Ride-Hailing & Mapping Systems** · 9-Week Roadmap

---

## 🎯 Goals

By the end of this week you should be able to:

- Explain the trade-offs between HTTP polling, long polling, SSE, and WebSockets
- Describe the WebSocket handshake (HTTP Upgrade → 101 Switching Protocols)
- Build a WebSocket server in Python using FastAPI
- Group connections by trip ID using rooms (namespaces)
- Use Redis Pub/Sub to fan-out location updates across multiple server instances
- Implement throttling — batch location updates to every 3 seconds instead of every GPS tick
- Handle graceful reconnection and heartbeat (ping/pong)

---

## 📚 Topics

| # | Topic |
|---|-------|
| 1 | HTTP polling vs long polling vs Server-Sent Events vs WebSockets — trade-offs |
| 2 | The WebSocket handshake: HTTP Upgrade header, 101 Switching Protocols |
| 3 | WebSocket frame model: opcodes, masking, fragmentation |
| 4 | Rooms and namespaces — grouping connections by trip ID |
| 5 | Redis Pub/Sub for horizontal scaling — fan-out across multiple server instances |
| 6 | Throttling — do not broadcast every GPS update; batch to every 3 seconds |
| 7 | Graceful reconnection and heartbeat (ping/pong) handling |

---

## 📊 Strategy Comparison

| Strategy | Latency | Server Load | Best For |
|----------|---------|-------------|----------|
| HTTP Polling | High (interval-bound) | Very high | Simple dashboards |
| Long Polling | Medium | High | Chat (legacy) |
| Server-Sent Events | Low | Medium | News feeds, notifications |
| **WebSockets ★** | **Very low (<100ms)** | **Low** | **Live maps, multiplayer games** |

---

## 🔗 Resources

All links verified.

| Resource | Link |
|----------|------|
| MDN — WebSocket API | https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API |
| Socket.IO official docs v4 | https://socket.io/docs/v4/ |
| Ably — WebSockets vs SSE vs Long Polling comparison | https://ably.com/blog/websockets-vs-sse |
| Redis Pub/Sub docs | https://redis.io/docs/latest/develop/pubsub/ |

> **Note:** The original roadmap listed the Redis Pub/Sub URL as `redis.io/docs/manual/pubsub/`. This URL has changed — the correct current link is above.

### Suggested study order
1. **Ably comparison article** — understand the trade-offs before writing a single line
2. **MDN WebSocket API** — read the "Writing WebSocket client applications" page, then "Writing WebSocket servers"
3. **Redis Pub/Sub docs** — focus on the PUBLISH/SUBSCRIBE/PSUBSCRIBE commands
4. **FastAPI WebSocket tutorial** — https://fastapi.tiangolo.com/advanced/websockets/

---

## ⭐ Deliverable

> **Do not skip this. It is proof you learned the week.**

**Requirements:**

- [ ] Driver simulator scripts emit their lat/lng over a WebSocket **every 3 seconds** (throttled — not every GPS tick)
- [ ] Riders connected to the same trip channel see those positions update in real time
- [ ] Use Redis Pub/Sub so the system works across multiple server instances
- [ ] **Verify horizontal scaling works:** run two server processes simultaneously, connect a driver to one and a rider to the other — the rider must still receive updates
- [ ] Include output in your README showing the two-process test passing

**Expected terminal output:**
```
[Server 1 - port 8000] Driver driver_001 connected to trip:abc123
[Server 1 - port 8000] Publishing location to Redis: {"lat": 17.385, "lng": 78.487}

[Server 2 - port 8001] Rider rider_42 connected to trip:abc123
[Server 2 - port 8001] Received from Redis Pub/Sub → forwarding to rider
[Server 2 - port 8001] Sent to rider: {"driver_id": "driver_001", "lat": 17.385, "lng": 78.487}
```

---

## 🛠️ Setup

```bash
pip install "fastapi[standard]" websockets redis asyncio
```

> Redis must be running. If not already set up:
> ```bash
> docker run -d -p 6379:6379 redis
> ```

---

## 🗂️ Folder Structure

```
week6-websockets-realtime/
├── README.md
├── resources/
│   ├── websocket-explainer.md      ← Handshake, frame model, ping/pong
│   └── redis-pubsub-explainer.md   ← How Pub/Sub enables horizontal scaling
├── starter/
│   └── driver_simulator.py         ← Simulates a driver emitting GPS every 3 seconds
└── deliverable/
    ├── server.py                   ← FastAPI WebSocket server skeleton
    └── REFLECTION.md
```

---

## 💡 Study Tips

- **This is the week your system starts feeling alive.** Take time to actually watch the location updates appear in real time before moving on.
- **The Redis Pub/Sub step is critical.** Without it, a rider connected to Server 2 would never receive updates from a driver connected to Server 1. This is the most important distributed systems concept in Week 6.
- **Throttle at the source (driver), not at the server.** If the driver's GPS fires every 500ms but you only broadcast every 3 seconds, buffer the latest position and only emit the last known one. Don't queue every update.
- **Test the two-server scenario explicitly.** Run `uvicorn server:app --port 8000` and `uvicorn server:app --port 8001` in two terminals. If both are connected through Redis Pub/Sub, the rider on port 8001 sees the driver on port 8000.

---

## ⏭️ What's Next

**Week 7 — The Matching / Dispatch Service**  
The most complex week — tie together geospatial indexing, real-time WebSockets, and business rules to build the core matching engine with distributed locks and a full trip state machine.

---

*Engineering Behind Ride-Hailing & Mapping Systems · Week 6 of 9*
