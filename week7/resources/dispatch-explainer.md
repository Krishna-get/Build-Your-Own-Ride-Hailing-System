# Dispatch & Matching — Explainer

---

## What is the Dispatch Problem?

Given N riders with ride requests and M online drivers, find the optimal assignment of drivers to riders — fast enough that the system responds in under a second.

At Uber's peak, this decision is made millions of times per second globally. Getting it right is the core of the product.

---

## Strategy 1: Greedy Nearest-Driver

The simplest approach: for each incoming request, immediately assign the nearest available driver.

```python
def match_greedy(rider_lat, rider_lng, available_drivers):
    return min(available_drivers, key=lambda d: haversine(rider_lat, rider_lng, d.lat, d.lng))
```

**Pros:** Simple, fast, low latency per request.

**Cons — the "wild goose chase" problem:**

```
Rider A ────────── 0.5km ──────────► Driver 1
Rider B ─────────────────── 2.0km ──────────────► Driver 2

With greedy:
  → Rider A gets Driver 1 (0.5km away) ✅
  → Rider B gets Driver 2 (2.0km away) ✅
  Total distance: 2.5km

But what if Driver 2 is actually 0.3km from Rider A's direction?
  → Optimal: Rider A → Driver 2 (0.3km), Rider B → Driver 1 (1.0km) = 1.3km total
  → Greedy gave: 2.5km total — nearly 2× worse!
```

Greedy is locally optimal (best for each individual request) but globally suboptimal (total system efficiency suffers).

---

## Strategy 2: Batched / Optimised Matching

Instead of matching immediately on each request, batch requests over a short window (e.g. 500ms) and solve the global assignment problem across all riders and drivers simultaneously.

This is the approach Uber moved to — framed as a **stable matching** / **linear assignment** problem.

The formal version: given a bipartite graph (riders ↔ drivers) with edge weights (e.g. ETA), find the matching that minimises total ETA across all pairs.

**Algorithm:** Hungarian algorithm (O(n³)) or auction-based algorithms for large scale.

**In practice:** Uber uses a constrained optimiser that considers ETA, driver earnings fairness, rider experience, surge zone membership, and more.

For this roadmap, implement greedy nearest-driver — it's correct and teaches all the important distributed systems concepts. Just understand conceptually why batching is better at scale.

---

## Driver State Machine

```
    [OFFLINE]
        │ go online (driver opens app)
        ▼
    [ONLINE]  ◄─────── re-match (decline/timeout)
        │ dispatch selects this driver
        ▼
 [PENDING_ACCEPT]
        │ driver accepts within 15s
        ▼
    [ACCEPTED]
        │ driver departs
        ▼
   [EN_ROUTE]
        │ driver confirms pickup
        ▼
    [IN_TRIP]
        │ driver calls complete
        ▼
   [COMPLETED]
        │ back online
        ▼
    [ONLINE]
```

**Important:** A driver can only be in ONE state at a time. Your Redlock prevents two trips from simultaneously transitioning the same driver into PENDING_ACCEPT.

---

## The Timeout System

Each state has a timeout. If the transition doesn't happen within the window, the system acts:

| Timeout | Action |
|---------|--------|
| No drivers found after 30s | Trip → CANCELLED, rider notified |
| Driver in PENDING_ACCEPT > 15s | Driver → ONLINE, trip re-matches to next driver |
| Driver in ACCEPTED > 10min | Flag for ops review (driver may have cancelled silently) |

**Implementation:** use `asyncio.wait_for()` with a timeout, or store a `match_expires_at` timestamp in the database and run a background scheduler that checks for stale states.

---

## Why Greedy Alone Isn't Enough at Scale

Three additional problems greedy doesn't handle:

### 1. Hotspot Exhaustion
All nearby drivers get grabbed by a burst of requests, leaving riders who arrive 2 seconds later with no options within 3km, even though drivers 4km away are idle.

**Fix:** batched matching considers future requests before committing drivers.

### 2. Driver Earnings Fairness
Greedy always picks the nearest driver — the same drivers near popular areas get the most rides, creating income inequality.

**Fix:** optimised matching includes a fairness term that distributes rides more equitably.

### 3. Direction Alignment
A driver heading north at 60km/h is "nearby" on a map but effectively far in ETA terms from a rider to the south.

**Fix:** ETA-optimised matching uses predicted travel time, not Haversine distance, as the edge weight.
