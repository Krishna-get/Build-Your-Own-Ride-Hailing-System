"""
Week 8 Deliverable — The Dynamic Surge Pricing Engine
======================================================
Calculates baseline fares combined with live hexagonal market multipliers.
"""

import asyncio
import json
import math
import os
import time
import h3
import redis.asyncio as aioredis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

# ── Pricing Baseline Constants ────────────────────────────────────────────────
BASE_FARE = 2.50         # Base cost to unlock a ride ($)
PER_KM_RATE = 1.20       # Cost per kilometer ($)
PER_MINUTE_RATE = 0.35   # Cost per minute of travel ($)

H3_RESOLUTION = 8        # Spatial grid density level for neighborhoods
COUNTER_TTL_S = 60       # Retain demand historical metrics for 1 minute max


# ── Redis Supply / Demand Aggregators ─────────────────────────────────────────

async def record_ride_demand(r: aioredis.Redis, lat: float, lng: float):
    """
    Atomically increment demand counter inside the local H3 cell.
    Uses an explicit short TTL window to keep historical state transient.
    """
    cell_id = h3.latlng_to_cell(lat, lng, H3_RESOLUTION)
    key = f"surge:demand:{cell_id}"
    
    # Increment counter atomically and ensure eviction intervals are refreshed
    await r.incr(key)
    await r.expire(key, COUNTER_TTL_S)


async def set_local_driver_supply(r: aioredis.Redis, lat: float, lng: float, count: int):
    """
    Explicitly set current active online driver supply numbers for an H3 zone.
    """
    cell_id = h3.latlng_to_cell(lat, lng, H3_RESOLUTION)
    key = f"surge:supply:{cell_id}"
    await r.set(key, str(count), ex=COUNTER_TTL_S)


async def calculate_surge_multiplier(r: aioredis.Redis, lat: float, lng: float) -> float:
    """
    Evaluate marketplace tension inside the target coordinate's hexagonal footprint.
    Formula rules:
      - Multiplier scales upward as Demand exceeds Supply.
      - Default is 1.0x if market state remains stable.
      - Maximum cap is limited to 3.0x to protect user conversions.
    """
    cell_id = h3.latlng_to_cell(lat, lng, H3_RESOLUTION)
    
    demand_count = await r.get(f"surge:demand:{cell_id}")
    supply_count = await r.get(f"surge:supply:{cell_id}")
    
    demand = int(demand_count) if demand_count else 0
    supply = int(supply_count) if supply_count else 0
    
    print(f"[Market Analysis] Cell {cell_id} -> Current Demand: {demand}, Active Supply: {supply}")
    
    if demand <= 1 or supply >= demand:
        return 1.0
        
    if supply == 0:
        return 2.0 if demand > 1 else 1.0

    # Continuous scaling algorithm based on lack of vehicle saturation
    ratio = demand / supply
    multiplier = 1.0 + (ratio * 0.25)
    
    return min(max(round(multiplier, 2), 1.0), 3.0)


# ── Core Quote Calculations ───────────────────────────────────────────────────

def estimate_travel_metrics(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> tuple[float, float]:
    """
    Calculate baseline route length using spherical straight-line Haversine math.
    Assumes an average urban traversal velocity of 30 km/h to estimate duration blocks.
    """
    R = 6371.0  # Earth radius (km)
    phi1, phi2 = math.radians(origin_lat), math.radians(dest_lat)
    dphi = math.radians(dest_lat - origin_lat)
    dlambda = math.radians(dest_lng - origin_lng)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance_km = R * c
    
    # Factor real road detours slightly by augmenting Euclidean gaps by 25%
    real_distance_km = distance_km * 1.25
    
    # Calculate duration (Hours = Distance / Speed; Minutes = Hours * 60)
    average_speed_kmh = 30.0
    duration_minutes = (real_distance_km / average_speed_kmh) * 60.0
    
    return round(real_distance_km, 2), round(duration_minutes, 1)


async def generate_pricing_quote(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> dict:
    """
    Executes structural fare mapping by processing distance coordinates and live surge criteria.
    """
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    
    try:
        # 1. Harvest baseline estimation travel profiles
        distance_km, duration_minutes = estimate_travel_metrics(origin_lat, origin_lng, dest_lat, dest_lng)
        
        # 2. Evaluate marketplace surge multipliers at point of pickup origin
        surge_multiplier = await calculate_surge_multiplier(r, origin_lat, origin_lng)
        
        # 3. Calculate absolute pricing using formula parameters
        base_subtotal = BASE_FARE + (PER_KM_RATE * distance_km) + (PER_MINUTE_RATE * duration_minutes)
        final_fare = round(base_subtotal * surge_multiplier, 2)
        
        return {
            "success": True,
            "base_fare": BASE_FARE,
            "distance_km": distance_km,
            "duration_minutes": duration_minutes,
            "surge_multiplier": surge_multiplier,
            "fare_total": final_fare,
            "currency": "USD"
        }
    finally:
        await r.aclose()


# ── Quick Verification Smoke Test Harness ──────────────────────────────────────

async def main():
    print("Initializing Dynamic Pricing Engine Test Execution Cluster...")
    r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    
    # Center Coordinates: Hyderabad City Centre
    lat, lng = 17.3850, 78.4867
    dest_lat, dest_lng = 17.4239, 78.4738
    
    # Test Scenario 1: Quiet Market Conditions (Balanced Supply/Demand)
    await r.delete(f"surge:demand:{h3.latlng_to_cell(lat, lng, H3_RESOLUTION)}")
    await set_local_driver_supply(r, lat, lng, count=10)
    await record_ride_demand(r, lat, lng)
    
    quote_normal = await generate_pricing_quote(lat, lng, dest_lat, dest_lng)
    print(f"\n[Test Result] Normal Conditions Quote:\n{json.dumps(quote_normal, indent=2)}")
    
    # Test Scenario 2: High Saturation Market Conditions (Demand Spikes, Low Vehicles)
    print("\nSimulating local demand surge events...")
    await set_local_driver_supply(r, lat, lng, count=2)
    for _ in range(12):  # Log 12 concurrent requests matching that spatial block
        await record_ride_demand(r, lat, lng)
        
    quote_surge = await generate_pricing_quote(lat, lng, dest_lat, dest_lng)
    print(f"\n[Test Result] Surged Conditions Quote:\n{json.dumps(quote_surge, indent=2)}")
    
    await r.aclose()

if __name__ == "__main__":
    asyncio.run(main())