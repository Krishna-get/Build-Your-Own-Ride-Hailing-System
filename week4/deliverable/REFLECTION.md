# Week 4 Reflection

> Fill this in after your nearby-drivers service hits the under-50ms target.

---

## Which approach did you use? Why?

I utilized Option B (In-Memory Uber H3 Grid Indexing). H3 was chosen over standard geohashing because hexagons provide elegant equidistant properties to every one of their neighbors. By ensuring that the distance between the center of a hexagon and the centers of all 6 adjacent neighboring cells is completely uniform, H3 provides a mathematically consistent radius search (`k-ring`) that eliminates dimensional metric distortion.

---

## What was your measured query time?

Average over 100 runs: 1.34 ms

---

## In your own words: why does bucketing beat scanning all drivers?

Scanning all drivers forces an unindexed $O(N)$ full table scan, requiring the system to compute the exact Haversine distance for every driver globally on every inbound request. Spatial bucketing works by grouping drivers into discrete geographical cell blocks ahead of time. This allows the matching engine to isolate only the target cells surrounding the rider, instantly bypassing 99% of irrelevant database records.

---

## Describe the boundary edge case in your own words

Two physical entities standing just a few meters apart can map to completely different spatial keys if they happen to sit on opposite sides of a high-level grid bisection or cell boundary line. If a dispatch query only scans the exact matching cell of the rider, it will fail to notice available vehicles right across that line. To fix this, the system must always query the rider's center cell along with its ring of neighboring cells.

---

## Why does Uber use hexagons instead of squares for H3?

Squares have non-uniform neighbor distances; a square's 4 diagonal neighbors are $\sqrt{2}$ times further away from its center than its 4 edge neighbors. Hexagons fix this flaw perfectly because every hexagon has exactly 6 neighbors that are all entirely equidistant from the center. This geometric symmetry ensures that radius-based searches expand consistently in all directions.

---

## What resolution / precision did you choose, and why?

I selected H3 Resolution 7, which corresponds to an approximate hexagon edge length of ~1.2 km. Resolution 7 acts as the optimal sweet spot for neighborhood-level driver matching: it covers an area large enough to capture plenty of candidate drivers inside a close `k=1` or `k=2` disk radius, without pulling in so many scattered candidates that the final Haversine sorting layer becomes slow.

---

## How does this connect to the dispatch service in your Week 1 architecture?

In our Week 1 system design, the Dispatch/Matching Service is responsible for locating and assigning nearby drivers to passengers in real time. This project shows why high-frequency driver telemetry updates (which arrive every few seconds) must bypass the primary transactional relational database (PostgreSQL) and instead live in specialized geospatial memories (like Redis or in-memory grid caches) to protect core business tables from falling under high-throughput write strain.

---

## Time spent this week

4 hours

---

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| Geohash encoding and prefix search | 5 |
| The boundary-straddling edge case and its fix | 5 |
| Quadtrees / R-trees — conceptual understanding | 5 |
| H3 hexagons — why they're used and how k-ring works | 5 |
| Could explain "why not just scan all drivers" to a non-technical person | 5 |