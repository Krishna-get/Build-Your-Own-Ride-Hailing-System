# Week 5 — REST API Design & Backend Foundation

> **Engineering Behind Ride-Hailing & Mapping Systems** · 9-Week Roadmap

---

## 🎯 Goals

By the end of this week you should be able to:

- Apply REST principles correctly: resources, HTTP verbs, status codes, idempotency
- Choose and justify an API versioning strategy
- Explain JWT structure (header, payload, signature) and implement JWT auth in your backend
- Design a normalized database schema for users, drivers, trips, driver_locations, and payments
- Write an OpenAPI spec **before** implementing the handler code
- Explain rate limiting conceptually and why production APIs need it

---

## 📚 Topics

| # | Topic |
|---|-------|
| 1 | REST principles: resources, HTTP verbs (GET/POST/PUT/PATCH/DELETE), status codes, idempotency |
| 2 | API versioning strategies (/v1/, header-based), pagination (cursor vs offset), error contracts |
| 3 | JWT-based authentication — header structure, signing, expiry, refresh tokens |
| 4 | Database schema design for: users, drivers, trips, driver_locations, payments |
| 5 | OpenAPI / Swagger — writing the API spec before writing the implementation |
| 6 | Rate limiting and request throttling (conceptual) |

---

## 📋 The API Contract

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/login` | None | Issue JWT for rider or driver |
| POST | `/rides/request` | Rider JWT | Create a ride request, trigger dispatch |
| GET | `/rides/{id}` | Any JWT | Get trip status, driver ETA |
| POST | `/drivers/location` | Driver JWT | Update driver's lat/lng |
| GET | `/drivers/nearby` | Rider JWT | Return 5 nearest online drivers |
| GET | `/pricing/quote` | Rider JWT | Return fare + surge for a route |
| PUT | `/rides/{id}/accept` | Driver JWT | Driver accepts the ride request |
| PUT | `/rides/{id}/complete` | Driver JWT | Mark trip as completed |

---

## 🔗 Resources

All links verified.

| Resource | Link |
|----------|------|
| Microsoft REST API Design Guidelines (GitHub) | https://github.com/microsoft/api-guidelines |
| REST API Tutorial | https://restfulapi.net |
| JWT introduction | https://jwt.io/introduction |
| FastAPI tutorial (Python) | https://fastapi.tiangolo.com/tutorial/ |

### Suggested study order
1. **restfulapi.net** — read the HTTP Methods and Status Codes pages first
2. **jwt.io/introduction** — understand header/payload/signature before writing any auth code
3. **FastAPI tutorial** — work through "First Steps", "Path Parameters", "Request Body", and "Security - First Steps"
4. **Microsoft REST API Guidelines** — skim for versioning and error-contract conventions; don't read the whole thing, it's written for Azure internally

---

## ⭐ Deliverable

> **Do not skip this. It is proof you learned the week.**

**Requirements:**

- [ ] All 5 endpoints below implemented and **stubbed** (return realistic mock data — full business logic comes in later weeks)
- [ ] JWT auth working on all protected routes — requests without a valid token get `401 Unauthorized`
- [ ] PostgreSQL schema created with migrations (see `starter/schema.sql`)
- [ ] Full OpenAPI documentation auto-generated (FastAPI gives you this for free at `/docs`)

**Endpoints to implement this week:**
- `POST /auth/login`
- `POST /rides/request`
- `GET /rides/{id}`
- `POST /drivers/location`
- `GET /drivers/nearby`

> The remaining 3 endpoints (`/pricing/quote`, `/rides/{id}/accept`, `/rides/{id}/complete`) will be wired up with real logic in Weeks 7–8 once dispatch and pricing services exist. Stub them too if you want to get ahead.

**Expected behaviour:**
```
POST /auth/login    {"username": "rider1", "password": "test123"}
→ 200 {"access_token": "eyJ...", "token_type": "bearer"}

GET /rides/abc123    (no Authorization header)
→ 401 {"detail": "Not authenticated"}

GET /rides/abc123    (Authorization: Bearer eyJ...)
→ 200 {"id": "abc123", "status": "MATCHING", "driver_eta_minutes": null}
```

---

## 🛠️ Setup

```bash
pip install "fastapi[standard]" sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt]
```

> Need PostgreSQL? Quick Docker setup:
> ```bash
> docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
> ```

---

## 📝 Reflection

Fill in `deliverable/REFLECTION.md` after completing the deliverable.

---

## 🗂️ Folder Structure

```
week5-rest-api-backend/
├── README.md
├── resources/
│   ├── jwt-explainer.md           ← JWT structure + auth flow diagram
│   └── rest-design-cheatsheet.md  ← Status codes, idempotency, versioning, pagination
├── starter/
│   └── schema.sql                 ← PostgreSQL schema for users, drivers, trips, etc.
└── deliverable/
    ├── main.py                    ← FastAPI app skeleton with TODOs
    ├── auth.py                    ← JWT creation/verification skeleton
    └── REFLECTION.md
```

---

## 💡 Study Tips

- **Build the OpenAPI spec mentally before writing code.** FastAPI generates `/docs` automatically from your type hints — but you should be able to describe each endpoint's request/response shape on paper first.
- **JWT ≠ session.** There's no server-side session store — the token itself carries all the claims. This is why JWTs need an expiry and why "logout" is tricky (you can't easily revoke a JWT before expiry without a blocklist).
- **Idempotency matters for `POST /rides/request`.** What happens if the rider's app retries the request due to a flaky network? Think about how you'd prevent creating two trips.
- **Don't over-engineer the schema yet.** Get the 5 core tables right (users, drivers, trips, driver_locations, payments) — you'll evolve it in later weeks as dispatch and pricing logic land.

---

## ⏭️ What's Next

**Week 6 — Real-Time Location Streaming with WebSockets**  
You'll move driver locations live onto a map using WebSockets and Redis Pub/Sub — this is the week your system starts feeling alive.

---

*Engineering Behind Ride-Hailing & Mapping Systems · Week 5 of 9*
