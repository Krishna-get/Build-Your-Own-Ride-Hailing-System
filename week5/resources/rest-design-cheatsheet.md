# REST API Design — Cheat Sheet

---

## HTTP Verbs and What They Mean

| Verb | Use | Idempotent? | Body? |
|------|-----|-------------|-------|
| GET | Read a resource | ✅ Yes | No |
| POST | Create a new resource | ❌ No | Yes |
| PUT | Replace a resource entirely | ✅ Yes | Yes |
| PATCH | Partially update a resource | ❌ No (usually) | Yes |
| DELETE | Remove a resource | ✅ Yes | Usually no |

**Idempotent** means: calling it once or 100 times has the same effect. `DELETE /rides/123` twice still results in the ride being deleted — no error on the second call in most designs (or a clear "already deleted" response). `POST /rides/request` twice creates **two trips** — not idempotent, which is why request-deduplication matters (see below).

---

## Status Codes You'll Actually Use

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST that created a resource |
| 204 | No Content | Successful DELETE, nothing to return |
| 400 | Bad Request | Malformed request body / invalid input |
| 401 | Unauthorized | Missing or invalid JWT |
| 403 | Forbidden | Valid JWT, but wrong role/permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | E.g. driver already accepted by another rider |
| 422 | Unprocessable Entity | Validation failed (FastAPI uses this for Pydantic errors) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unhandled server-side bug |

---

## Idempotency in Practice: POST /rides/request

A naive `POST /rides/request` is NOT idempotent — if the rider's phone has a flaky connection and the app retries, you could create two ride requests.

**Fix: Idempotency keys.**

```
POST /rides/request
Idempotency-Key: client-generated-uuid-abc123
```

The server stores `(idempotency_key → response)` for a short window (e.g. 5 minutes). If the same key arrives again, return the cached response instead of creating a new trip.

This pattern is used by Stripe, Uber, and most production payment/transaction APIs.

---

## API Versioning Strategies

### 1. URL Path Versioning (most common, what this roadmap uses)
```
GET /v1/rides/{id}
GET /v2/rides/{id}
```
✅ Simple, visible, easy to route  
❌ "Breaks" REST purity slightly (the URL changes for the same resource)

### 2. Header-Based Versioning
```
GET /rides/{id}
Accept: application/vnd.ridehailing.v2+json
```
✅ Cleaner URLs  
❌ Harder to test in a browser, less discoverable

**Recommendation for this roadmap:** use `/v1/` prefix. It's simple and what most public APIs do (Stripe, GitHub, Twitter all use path versioning).

---

## Pagination: Cursor vs Offset

### Offset-based (simpler, but has issues at scale)
```
GET /trips?offset=20&limit=10
```
❌ If a row is inserted/deleted between requests, results can shift or duplicate  
❌ Slow on large tables (`OFFSET 100000` still scans 100,000 rows)

### Cursor-based (preferred for production)
```
GET /trips?after=trip_8821&limit=10
```
✅ Stable even as data changes  
✅ Fast — uses an indexed `WHERE id > cursor` instead of scanning  
✅ What Stripe, GitHub, Slack APIs use

**For this roadmap:** offset pagination is fine for `GET /drivers/nearby` (small, bounded result sets). Use cursor-based if you add a `GET /trips/history` endpoint later — trip history can grow unbounded.

---

## Error Contract — Be Consistent

Pick ONE error response shape and use it everywhere:

```json
{
  "error": {
    "code": "RIDE_NOT_FOUND",
    "message": "No ride found with id abc123",
    "status": 404
  }
}
```

Don't mix shapes (`{"detail": "..."}` in one endpoint, `{"error": "..."}` in another). FastAPI defaults to `{"detail": "..."}` for HTTPException — fine to standardise around that if you don't want to write custom exception handlers.

---

## Rate Limiting (Conceptual)

Why it matters: without it, a buggy client (or malicious actor) can hammer your API and degrade service for everyone.

**Common algorithm: Token Bucket**
- Each client gets a "bucket" of N tokens (e.g. 100 requests/minute)
- Each request consumes 1 token
- Tokens refill at a fixed rate
- Bucket empty → reject with `429 Too Many Requests`

```python
# Conceptual sketch (use a library like slowapi in production)
from collections import defaultdict
import time

buckets = defaultdict(lambda: {"tokens": 100, "last_refill": time.time()})

def check_rate_limit(client_id: str, max_tokens=100, refill_rate=100/60):
    bucket = buckets[client_id]
    now = time.time()
    elapsed = now - bucket["last_refill"]
    bucket["tokens"] = min(max_tokens, bucket["tokens"] + elapsed * refill_rate)
    bucket["last_refill"] = now

    if bucket["tokens"] < 1:
        return False  # rate limited
    bucket["tokens"] -= 1
    return True
```

You don't need to implement this for Week 5's deliverable — just understand the concept. You'll see it again if you deploy your app in Week 9.

---

## Resource Naming Conventions

✅ `GET /rides/{id}` — nouns, not verbs  
❌ `GET /getRide?id=123` — avoid verb-based URLs  
✅ Plural for collections: `/drivers`, `/rides`  
✅ Nested resources for ownership: `/rides/{id}/receipt`  
✅ lowercase, hyphen-separated for multi-word: `/driver-locations` (not `/driverLocations` or `/Driver_Locations`)
