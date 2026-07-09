"""
Week 9 Deliverable — The Production API Gateway
================================================
Bridges REST API endpoints with the Week 7 asynchronous dispatch engine,
running seamlessly inside containerized Docker multi-node networks.
"""

import asyncio
import json
import os
import sys
from typing import Optional, List
from uuid import uuid4

import redis.asyncio as aioredis
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

# Inject relative paths to cleanly import Week 5 auth modules and Week 7 matching routines
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(CURRENT_DIR, "../../week5/deliverable")))
sys.path.insert(0, os.path.abspath(os.path.join(CURRENT_DIR, "../../week7/deliverable")))

from auth import create_access_token, get_current_user, require_role
from dispatch import dispatch_trip

app = FastAPI(
    title="Production Ride-Hailing Gateway",
    version="1.0.0",
    description="Unified API gateway layer running inside multi-container networks.",
)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


# ── Validation Schemas ────────────────────────────────────────────────────────

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
    driver_id: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/v1/auth/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Verify user credentials and issue cryptographically signed JWT strings."""
    if form_data.username in ["rider1", "driver1"] and form_data.password == "test123":
        role = "rider" if form_data.username == "rider1" else "driver"
        assigned_id = "00000000-0000-0000-0000-000000000001" if role == "rider" else "00000000-0000-0000-0000-000000000002"
        token = create_access_token(user_id=assigned_id, role=role)
        return {"access_token": token, "token_type": "bearer"}
        
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/v1/rides/request", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def request_ride(
    ride: RideRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role("rider")),
):
    """
    Creates a new ride transaction record inside Redis and hands over execution
    to the concurrent background dispatch matching engine worker seamlessly.
    """
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    
    try:
        if ride.idempotency_key:
            existing_trip = await r.get(f"idempotency:{ride.idempotency_key}")
            if existing_trip:
                return json.loads(existing_trip)

        new_trip_id = str(uuid4())
        initial_payload = {
            "id": new_trip_id,
            "status": "REQUESTED",
            "driver_id": None
        }

        # Cache transaction snapshots so subsequent API hits stay lightning fast
        if ride.idempotency_key:
            await r.set(f"idempotency:{ride.idempotency_key}", json.dumps(initial_payload), ex=300)
        await r.set(f"trip_state:{new_trip_id}", json.dumps(initial_payload), ex=3600)

        # Offload the heavy blocking 15-second matching service loop directly to background threads
        background_tasks.add_task(
            dispatch_trip, 
            trip_id=new_trip_id, 
            pickup_lat=ride.pickup_lat, 
            pickup_lng=ride.pickup_lng
        )

        return initial_payload
    finally:
        await r.aclose()


@app.get("/v1/rides/{ride_id}", response_model=RideResponse)
async def get_ride(ride_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch live transaction data directly out of high-performance caches."""
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        trip_data = await r.get(f"trip_state:{ride_id}")
        if not trip_data:
            raise HTTPException(status_code=404, detail="Ride transaction not found")
        return json.loads(trip_data)
    finally:
        await r.aclose()


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": "production_containerized"}