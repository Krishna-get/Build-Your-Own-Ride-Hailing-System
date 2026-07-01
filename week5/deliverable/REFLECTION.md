# Week 5 Reflection

> Fill this in after your 5 endpoints are working and JWT auth is enforced.

---

## Walk through your JWT auth flow in your own words

The authentication flow begins when a client submits their username and password via `POST /v1/auth/login` using the standard form URL-encoded body format. The server validates these credentials against known records and hashes. Upon successful verification, the server generates a JSON Web Token (JWT) containing standard claims: `sub` representing the user ID, `role` defining whether they are a rider or driver, and an `exp` expiration timestamp set to 60 minutes in the future. This payload is signed using a secure `SECRET_KEY` via the `HS256` algorithm and returned as a bearer access token.

For any subsequent protected requests, the client attaches this signed token to the `Authorization: Bearer <token>` header. FastAPI routes intercept the incoming header and pass it to our verification dependency layers. The token is decoded and verified cryptographically. If the signature has been tampered with or the expiration window has passed, the server immediately short-circuits the pipeline and rejects the request with an `HTTP 401 Unauthorized` response. If the token passes validation, the role claim is cross-checked against route-specific factories (e.g., verifying a driver role is calling the location telemetry endpoint). If the roles do not match, an `HTTP 403 Forbidden` error is returned; otherwise, the request is accepted and allowed to execute.

---

## How did you handle the idempotency problem on POST /rides/request?

To prevent duplicate trip creation caused by erratic client network connections or repeated app-side retries, the system utilizes a unique client-generated string parameter passed in the body schema named `idempotency_key`. 

When a rider initiates a `POST /v1/rides/request`, the application checks an in-memory tracking store (`MOCK_IDEMPOTENCY_LOGS`) to see if that specific key has already been processed. If the key matches an existing log entry, the backend instantly intercepts the query and bypasses the downstream resource creation mechanics, returning the original cached trip response to the caller. If it is a completely new token, a new trip record is created with a `REQUESTED` state and stored under that key, guaranteeing that no matter how many times a duplicate call hits the cluster, only a single unique transaction occurs.

---

## What did your /docs (auto-generated OpenAPI) page look like?

FastAPI automatically parses our Pydantic classes and endpoint security dependencies to compile a highly clean, structured, and completely interactive Swagger UI document right at `/docs`. It formats our five core routes neatly into expandable blocks categorized under a default section. 

The `/v1/auth/login` endpoint displays input text boxes for `username` and `password` inside an `application/x-www-form-urlencoded` form specification structure. At the top right of the screen sits a large "Authorize" padlock utility button. Once clicked, it safely gathers credentials, receives the JWT string, and manages session variables globally. Every other single protected route displays clear response definitions, mapping exact JSON schemas for status codes like `200 Successful Response`, `201 Created`, or `422 Validation Error`.

---

## Which status codes did you use, and why?

* **`200 OK`**: Used for standard successful fetches, such as pulling trip status history queries in `GET /v1/rides/{id}`.
* **`201 Created`**: Handled explicitly on `POST /v1/rides/request` because it signals to the caller that a new entity resource has successfully been initialized and written to the database.
* **`204 No Content`**: Applied to `POST /v1/drivers/location`. High-frequency telemetry coordinates change every couple of seconds; the server successfully updates our spatial index and returns a bodyless response to conserve bandwidth and reduce network latency.
* **`401 Unauthorized`**: Returned when an endpoint requires a valid session token but the client passes a corrupted key, expired signature, or no header at all.
* **`403 Forbidden`**: Handled when the identity token is perfectly valid, but the user's role lacks the authorization permissions required to execute that resource (e.g., a rider attempting to call the location update route).
* **`404 Not Found`**: Thrown if a lookup is made for a trip ID that does not exist in our trip tables.
* **`422 Unprocessable Entity`**: Automatically managed by FastAPI if a schema fails internal field formatting constraints (e.g., string parameters inserted into coordinate fields).

---

## What would happen if two riders requested the same driver at the same instant?

If two individual riders attempt to lock down and match with the same physical driver at the exact same fraction of a second, a severe multi-threaded concurrency race condition occurs. Without prevention layers, the matching logic could read the driver's status as `ONLINE` for both riders simultaneously. Both order flows would proceed to assign the trip, overriding the database state table records and double-booking the driver. 

To fix this down the line in Week 7, we must implement an atomic distributed locking mechanism, such as Redis `Redlock`, or enforce strong relational isolation criteria (like explicit `SELECT ... FOR UPDATE` rows inside our database transaction block). This ensures that the first worker engine instance that grabs the driver record locks it securely, forcing the competing request to fail gracefully and fall back into a standard re-matching dispatch loop.

---

## How does your schema connect to the architecture diagram from Week 1?

Our `schema.sql` translates the data model contracts of our high-level architectural blocks into concrete storage. 

The primary relational datastore (PostgreSQL) handles durable entities that represent financial and transactional consistency constraints: the `users` and `drivers` extensions map out permissions, `trips` stores lifecycle state progression handled by our Trip Service, and `payments` tracks billing data. Meanwhile, the ephemeral `driver_locations` table directly matches the spatial buffer concept from our diagram. It uses dedicated indexes to support fast spatial scan lookups without overwhelming historical logs.

---

## Time spent this week

1 hours

---

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| REST principles (verbs, status codes, idempotency) | 5 |
| JWT — could explain header/payload/signature to someone else | 5 |
| Database schema design — comfortable with the 5 core tables | 5 |
| OpenAPI — understand how FastAPI generates it automatically | 5 |
| Rate limiting — conceptual understanding | 5 |