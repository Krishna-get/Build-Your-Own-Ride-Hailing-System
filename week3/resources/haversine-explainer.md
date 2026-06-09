# The Haversine Formula — Explainer

---

## The Problem

On a flat plane, the distance between two points is simply:  
`d = √((x2-x1)² + (y2-y1)²)`

But the Earth is a sphere. Latitude and longitude are angles, not distances.  
1° of longitude near the equator ≈ 111 km. 1° of longitude near the poles ≈ 0 km.

You cannot use Euclidean distance on lat/lng coordinates.

---

## The Formula

The Haversine formula calculates the **great-circle distance** — the shortest path between two points on the surface of a sphere.

```
a = sin²(Δlat/2) + cos(lat1) · cos(lat2) · sin²(Δlon/2)
c = 2 · atan2(√a, √(1−a))
d = R · c
```

Where:
- `lat1, lon1` = coordinates of point 1 in **radians**
- `lat2, lon2` = coordinates of point 2 in **radians**
- `Δlat = lat2 − lat1`
- `Δlon = lon2 − lon1`
- `R = 6,371,000` metres (Earth's mean radius)
- `d` = distance in metres

---

## Python Implementation

```python
import math

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance in metres between two points
    on Earth given their latitude and longitude in decimal degrees.

    Example:
        Hyderabad (17.3850, 78.4867) to Secunderabad (17.4416, 78.4983)
        → approximately 6,400 metres
    """
    R = 6_371_000  # Earth's mean radius in metres

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # distance in metres
```

---

## Quick Sanity Checks

```python
# Mumbai to Delhi (should be ~1,150 km)
print(haversine(19.0760, 72.8777, 28.6139, 77.2090) / 1000)
# → ~1,149 km ✅

# Same point (should be 0)
print(haversine(17.3850, 78.4867, 17.3850, 78.4867))
# → 0.0 ✅
```

---

## Why It's Admissible as an A* Heuristic

The Haversine distance is the **straight-line distance on the Earth's surface**.

Roads can only be longer than a straight line (they curve, detour, follow terrain).  
Therefore: `haversine(node, goal) ≤ true road distance(node, goal)` always.

This satisfies the admissibility condition — Haversine never overestimates.

---

## Accuracy

Haversine assumes a perfectly spherical Earth. The Earth is actually slightly oblate (wider at the equator).

Error: up to ~0.5% for long distances. For city-scale routing (< 100 km), this is negligible.

For higher accuracy: the **Vincenty formula** accounts for the ellipsoid. Production routing engines use this, but Haversine is fine for our purposes.

---

## In OSMnx

OSMnx stores node coordinates as:
- `G.nodes[node_id]['y']` → latitude
- `G.nodes[node_id]['x']` → longitude

Edge lengths are stored as `G.edges[u, v, 0]['length']` in metres (already computed by OSMnx using Haversine internally).
