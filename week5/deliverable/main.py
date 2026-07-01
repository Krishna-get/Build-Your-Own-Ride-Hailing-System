"""
Week 5 Deliverable — REST API Backend
========================================
A FastAPI backend implementing the core ride-hailing API contract.

Endpoints to implement this week:
    POST /v1/auth/login
    POST /v1/rides/request
    GET  /v1/rides/{id}
    POST /v1/drivers/location
    GET  /v1/drivers/nearby

Rules:
  - Use real JWT auth (see auth.py) — no fake/hardcoded tokens
  - All protected routes must return 401 if the token is missing/invalid
  - Connect to PostgreSQL using the schema in starter/schema.sql
  - Run `fastapi dev main.py` and check /docs — your OpenAPI spec should
    be generated automatically from your type hints and route definitions

This is a STUB week — return realistic mock/placeholder data where the
real business logic (dispatch, pricing) doesn't exist yet. Full logic for
nearby drivers comes from Week 4. Dispatch and pricing land in Weeks 7-8.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

from auth import create_access_token, get_current_user, require_role

app = FastAPI(
    title="Mini Ride-Hailing API",
    version="1.0.0",
    description="Week 5 deliverable — REST API foundation",
)


# ── Pydantic models (request/response shapes) ─────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RideRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    idempotency_key: Optional[str] = None


class RideResponse(BaseModel):
    id: str
    status: str
    driver_eta_minutes: Optional[float] = None


class DriverLocationUpdate(BaseModel):
    latitude: float
    longitude: float


class NearbyDriver(BaseModel):
    driver_id: str
    latitude: float
    longitude: float
    distance_km: float


# ── POST /v1/auth/login ────────────────────────────────────────────────────────

@app.post("/v1/auth/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """
    Verify username/password against the database, then issue a JWT.

    TODO:
      1. Look up the user in the `users` table by username
      2. Verify the password using passlib (bcrypt) — never compare plaintext
      3. If valid, call create_access_token(user_id, role)
      4. If invalid, raise HTTPException(401, "Invalid credentials")
    """
    # --- your code here ---
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ── POST /v1/rides/request ─────────────────────────────────────────────────────

@app.post("/v1/rides/request", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
def request_ride(
    ride: RideRequest,
    current_user: dict = Depends(require_role("rider")),
):
    """
    Create a new ride request.

    TODO:
      1. Check idempotency_key against existing trips — if it already exists,
         return the EXISTING trip instead of creating a new one (see
         resources/rest-design-cheatsheet.md "Idempotency in Practice")
      2. Insert a new row into `trips` with status='REQUESTED'
      3. Return the trip id and status
      4. (Real dispatch logic comes in Week 7 — for now just create the record)
    """
    # --- your code here ---
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ── GET /v1/rides/{id} ─────────────────────────────────────────────────────────

@app.get("/v1/rides/{ride_id}", response_model=RideResponse)
def get_ride(
    ride_id: str,
    current_user: dict = Depends(get_current_user),  # any authenticated user
):
    """
    Get the current status of a trip.

    TODO:
      1. Query the `trips` table by id
      2. If not found, raise HTTPException(404, "Ride not found")
      3. Return id, status, and driver_eta_minutes (can be None/null for now)
    """
    # --- your code here ---
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ── POST /v1/drivers/location ──────────────────────────────────────────────────

@app.post("/v1/drivers/location", status_code=status.HTTP_204_NO_CONTENT)
def update_driver_location(
    location: DriverLocationUpdate,
    current_user: dict = Depends(require_role("driver")),
):
    """
    Update the authenticated driver's current location.

    TODO:
      1. Upsert into `driver_locations` (insert if not exists, else update)
      2. Use current_user['sub'] as the driver_id
      3. Return 204 No Content on success
    """
    # --- your code here ---
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ── GET /v1/drivers/nearby ──────────────────────────────────────────────────────

@app.get("/v1/drivers/nearby", response_model=list[NearbyDriver])
def get_nearby_drivers(
    lat: float,
    lng: float,
    current_user: dict = Depends(require_role("rider")),
):
    """
    Return the 5 nearest online drivers to (lat, lng).

    TODO:
      Reuse your Week 4 nearby-drivers implementation here!
      1. Query driver_locations joined with drivers WHERE status='ONLINE'
      2. Rank by distance (Haversine, or PostGIS ST_Distance if you set it up)
      3. Return top 5
    """
    # --- your code here ---
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ── Health check (already implemented — useful for testing your setup works) ──

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
