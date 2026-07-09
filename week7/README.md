# Week 7 — The Matching / Dispatch Service

> **Engineering Behind Ride-Hailing & Mapping Systems** · 9-Week Roadmap

---

## 🎯 Goals

By the end of this week you should be able to:

- Implement a greedy nearest-driver matching strategy
- Model the driver state machine (offline → online → en route → on trip → complete)
- Explain the race condition where two riders request the same driver simultaneously and how to prevent it
- Use Redis Redlock to acquire a distributed lock on a driver before notifying them
- Implement the full trip state machine with correct state transitions and timeouts
- Handle a 15-second accept/decline timeout and re-match to the next available driver
- Explain why Uber moved from greedy matching to batched optimised matching

---

## 📚 Topics

| # | Topic |
|---|-------|
| 1 | Matching strategies: nearest-driver (greedy), batched matching, ETA-optimised matching |
| 2 | Driver state machine: offline → online → en route to pickup → on trip → complete |
| 3 | Handling race conditions — two riders requesting the same driver simultaneously |
| 4 | Distributed locks with Redis (Redlock algorithm) to prevent double-booking |
| 5 | Trip lifecycle: request → matching → accepted → pickup → in-trip → complete → rated |
| 6 | Timeouts: driver must accept within 15 seconds, else re-match to next nearest driver |
| 7 | Why Uber moved away from greedy nearest-driver to batched optimised matching |

---

## 🗺️ Trip State Machine

| State | Trigger | Next State | Timeout |
|-------|---------|------------|---------|
| **REQUESTED** | Rider calls `POST /rides/request` | MATCHING | 30s |
| **MATCHING** | Dispatch finds nearest driver | PENDING_ACCEPT | 15s |
| **PENDING_ACCEPT** | Driver receives WS notification | ACCEPTED / re-match | 15s |
| **ACCEPTED** | Driver calls `PUT /rides/{id}/accept` | EN_ROUTE | None |
| **EN_ROUTE** | Driver departs toward pickup | IN_TRIP | None |
| **IN_TRIP** | Driver confirms pickup | COMPLETED | None |
| **COMPLETED** | Driver calls `PUT /rides/{id}/complete` | RATED | None |

---

## 🔗 Resources

All links verified. Note: some URLs have changed from the original roadmap — corrected below.

| Resource | Link |
|----------|------|
| Uber blog — Engineering the New Driver App Architecture | https://www.uber.com/blog/driver-app-ribs-architecture |
| Lyft blog — Quantifying Efficiency in Ridesharing Marketplaces | https://eng.lyft.com/quantifying-efficiency-in-ridesharing-marketplaces-affd53043db2 |
| Redis — Distributed Locks with Redlock | https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/ |
| Paper: Ride-sharing — a stable matching problem (Google Scholar) | https://scholar.google.com |

> **Corrections from original roadmap:**
> - The Redlock URL has moved to `redis.io/docs/latest/develop/clients/patterns/distributed-locks/`
> - The Lyft resource has been updated to their most relevant marketplace matching article

### Suggested study order
1. **Redis Redlock docs** — understand the algorithm and its limitations before implementing
2. **Lyft marketplace article** — see how a real team thinks about matching efficiency
3. **Uber driver app blog** — skim for context on driver state management at scale
4. **Martin Kleppmann's critique of Redlock** (linked from the Redis page) — important for understanding the limits of distributed locking

---

## ⭐ Deliverable

> **This is the most complex week — take your time.**

Build a **matching service** that, on `POST /rides/request`:

- [ ] Finds nearby online drivers using your Week 4 geospatial service
- [ ] Acquires a **distributed lock** on the chosen driver using Redis (`SET NX PX`)
- [ ] Notifies the driver over **WebSocket** (from Week 6) with the ride request details
- [ ] Waits up to **15 seconds** for the driver to accept via `PUT /rides/{id}/accept`
- [ ] If the driver **declines or times out** → releases the lock → re-matches to the next nearest driver
- [ ] If the driver **accepts** → updates trip status to `ACCEPTED` → persists to PostgreSQL
- [ ] All state transitions are persisted to the database

**Expected flow:**
```
POST /rides/request
  → finds driver_042 (nearest, 0.3km)
  → acquires lock: driver:lock:driver_042  (TTL 20s)
  → WebSocket → driver_042: {"type": "ride_request", "trip_id": "abc123", ...}
  → waiting for accept (15s timeout)...

PUT /rides/abc123/accept  (driver_042 responds within 8s)
  → trip status: PENDING_ACCEPT → ACCEPTED
  → lock released
  → rider notified: {"type": "driver_assigned", "driver_id": "driver_042", "eta_minutes": 4}

200 OK: {"trip_id": "abc123", "status": "ACCEPTED", "driver_id": "driver_042"}
```

**Timeout scenario:**
```
  → waiting for accept (15s timeout)...
  → [15 seconds pass, no response]
  → lock released on driver_042
  → re-matching to driver_019 (next nearest)...
  → acquires lock: driver:lock:driver_019
  → WebSocket → driver_019: ride request
```

---

## 🛠️ Setup

```bash
pip install "fastapi[standard]" redis asyncio
```

Redis must be running:
```bash
docker run -d -p 6379:6379 redis
```

---

## 🗂️ Folder Structure

```
week7-dispatch-service/
├── README.md
├── resources/
│   ├── dispatch-explainer.md        ← Matching strategies + why greedy isn't enough
│   └── redlock-explainer.md         ← The race condition + distributed lock solution
├── starter/
│   └── state_machine.py             ← Trip and driver state machine constants + helpers
└── deliverable/
    ├── dispatch.py                  ← Your matching service implementation
    └── REFLECTION.md
```

---

## 💡 Study Tips

- **Whiteboard the race condition first.** Draw two riders, one driver, and two server instances — trace what happens without a lock. Only then implement Redlock.
- **Use `SET key value NX PX ttl` directly** rather than a Redlock library — implementing it yourself teaches the actual pattern. The NX flag means "only set if Not eXists" — that's your lock.
- **TTL on your lock is critical.** If the driver's app crashes mid-accept, the lock must auto-expire so other riders can eventually be matched. Set TTL to ~20 seconds (15s accept window + 5s buffer).
- **This week ties together Weeks 4, 5, and 6.** You're calling your geospatial service (Week 4), updating your REST API state (Week 5), and sending WebSocket notifications (Week 6). If something breaks, check those earlier pieces first.

---

## ⏭️ What's Next

**Week 8 — Surge Pricing & Dynamic Pricing Logic**  
Implement the fare formula with a dynamic surge multiplier based on real-time supply/demand ratios per H3 cell — and wire it into your `GET /pricing/quote` endpoint.

---

*Engineering Behind Ride-Hailing & Mapping Systems · Week 7 of 9*
