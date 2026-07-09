"""
starter/driver_simulator.py
============================
Simulates a driver emitting GPS location updates over a WebSocket.

Emits every 3 seconds (throttled) — not every GPS tick.
Randomly walks the driver position around a starting point.

Usage:
    pip install websockets
    python driver_simulator.py
    python driver_simulator.py --server ws://localhost:8001 --trip xyz789

Arguments:
    --server   WebSocket server URL (default: ws://localhost:8000)
    --trip     Trip ID to join (default: abc123)
    --driver   Driver ID (default: driver_001)
"""

import asyncio
import json
import random
import argparse
import time

try:
    import websockets
except ImportError:
    print("Please install websockets: pip install websockets")
    exit(1)


# Starting position — Hyderabad city centre
START_LAT = 17.3850
START_LNG = 78.4867
EMIT_INTERVAL_SECONDS = 3   # throttle: emit once every 3 seconds
GPS_DRIFT = 0.0005           # random walk step size per interval


async def simulate_driver(server_url: str, trip_id: str, driver_id: str):
    ws_url = f"{server_url}/ws/driver/{trip_id}"

    print(f"Driver {driver_id} connecting to {ws_url}")
    print(f"Emitting location every {EMIT_INTERVAL_SECONDS}s...\n")

    lat = START_LAT
    lng = START_LNG

    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"Connected ✅\n")

            while True:
                # Simulate GPS random walk
                lat += random.uniform(-GPS_DRIFT, GPS_DRIFT)
                lng += random.uniform(-GPS_DRIFT, GPS_DRIFT)

                payload = {
                    "type": "location_update",
                    "driver_id": driver_id,
                    "lat": round(lat, 6),
                    "lng": round(lng, 6),
                    "timestamp": time.time(),
                }

                await websocket.send(json.dumps(payload))
                print(f"[{driver_id}] Emitted → lat={payload['lat']}, lng={payload['lng']}")

                # Wait for ack (optional) with a short timeout
                try:
                    ack = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"[{driver_id}] Server ack: {ack}")
                except asyncio.TimeoutError:
                    pass  # no ack required

                await asyncio.sleep(EMIT_INTERVAL_SECONDS)

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"\nConnection closed: {e}")
    except ConnectionRefusedError:
        print(f"\nCould not connect to {ws_url}. Is the server running?")


def main():
    parser = argparse.ArgumentParser(description="Driver GPS simulator")
    parser.add_argument("--server", default="ws://localhost:8000", help="WebSocket server URL")
    parser.add_argument("--trip", default="abc123", help="Trip ID")
    parser.add_argument("--driver", default="driver_001", help="Driver ID")
    args = parser.parse_args()

    asyncio.run(simulate_driver(args.server, args.trip, args.driver))


if __name__ == "__main__":
    main()
