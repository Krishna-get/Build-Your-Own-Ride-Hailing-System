# Week 3 Reflection

---

## How many nodes did A* explore vs Dijkstra on your city query?

A* explored: 2,530  
Dijkstra explored: 28,556  
Saving: 91%

---

## In your own words: why did A* explore fewer nodes?

Dijkstra behaves as an uninformed search, expanding blindly in an evenly distributed circular wave pattern in all directions from the starting point. A* incorporates the Haversine formula as a heuristic to project the remaining straight-line distance to the target, prioritizing nodes that lead directly toward the goal. This limits the exploration scope to a highly focused corridor pointed toward the final destination, avoiding thousands of irrelevant roads heading away from it.

---

## What would happen if your heuristic overestimated the true distance?

If the heuristic overestimates the distance, it breaks the required property of admissibility. Because the estimated cost $h(n)$ can exceed the actual true path cost, A* may penalize a node along the absolute shortest route, assuming it is more expensive than it actually is. As a result, the algorithm could choose a suboptimal path and complete early, failing to guarantee the global shortest path.

---

## What is the Haversine formula actually calculating?

Geometrically, the Haversine formula determines the great-circle distance, which represents the absolute shortest line between two coordinate points across the surface of a three-dimensional sphere. It accounts for the earth's curvature from raw angles of latitude and longitude, computing straight-line spherical distance rather than simple flat 2D Euclidean length.

---

## What did you find surprising about the OSMnx road graph?

The sheer size and density of real city graphs was unexpected—even localized regions have thousands of intersecting nodes and directed edges. It was also fascinating to observe how perfectly it captures infrastructure attributes such as complex multi-lane junctions, street names, and strict one-way parameters (`MultiDiGraph`) which directly govern real-world path routing.

---

## How does this connect to the ride-hailing system from Week 1?

This connects directly to the **Map / Routing Service** defined in our initial system design. Whenever a passenger requests a ride, this engine must calculate optimal road paths to determine baseline distances and precise ETAs, allowing the **Pricing** and **Dispatch** systems to safely generate accurate fare calculations and assign drivers.

---

## Time spent this week

1 hours

---

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| A* algorithm — could implement from memory | 5 |
| Admissible heuristic — understand the requirement | 5 |
| Haversine formula — understand what it computes | 5 |
| OSMnx — comfortable loading a graph and querying it | 5 |
| Bidirectional A* / contraction hierarchies — conceptual understanding | 4 |
