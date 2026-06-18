# H3 vs Geohash vs Quadtree — Comparison

---

## Quadtrees (Conceptual)

A quadtree recursively divides 2D space into 4 quadrants, only subdividing further where data density requires it.

```
┌─────┬─────┐
│ NW  │ NE  │
├─────┼─────┤
│ SW  │ SE  │     → SW quadrant has many points, subdivide further
└─────┴─────┘

┌─────┬─────┐
│ NW  │ NE  │
├──┬──┼─────┤
│NW│NE│     │
├──┼──┤ SE  │
│SW│SE│     │
└──┴──┴─────┘
```

**Strength:** adapts to data density — sparse areas stay coarse, dense areas get fine-grained cells.  
**Weakness:** irregular cell sizes make "is point A within X km of point B" harder to reason about uniformly. More complex to implement and query than a flat hash.

**Where it's used:** PostGIS uses a variant called **R-trees** internally for its spatial indexes (`GIST` index type) — bounding boxes organized hierarchically, similar spirit to a quadtree but built around minimum bounding rectangles of the actual data.

---

## R-Trees (Conceptual)

An R-tree groups nearby objects into bounding rectangles, and groups those rectangles into larger bounding rectangles, recursively — like a quadtree but built bottom-up from data rather than top-down by fixed subdivision.

```
Leaf level:    [Driver A] [Driver B] [Driver C] [Driver D]
                    └─────┬─────┘         └─────┬─────┘
Level 1:          [Bounding Box 1]      [Bounding Box 2]
                            └──────┬──────┘
Root:                  [Bounding Box covering all]
```

**Where it's used:** This is what powers `ST_DWithin`, `ST_Distance` and other PostGIS spatial queries under the hood. When you create a `GIST` index on a `geometry` column in PostgreSQL, you're building an R-tree.

---

## Geohash — Quick Recap

Recursive bisection of lat/lng into a string. Prefix matching = proximity (with the boundary edge case described in `geohash-explainer.md`).

**Cell shape:** rectangle. Cell size varies with latitude (shrinks toward poles).

---

## H3 — Why Hexagons?

Uber built H3 specifically to solve problems they hit with geohash-style square grids at massive scale (millions of driver location updates per second).

### Problem 1: Unequal neighbour distances (squares)
```
┌───┬───┬───┐
│ NW│ N │ NE│   ← diagonal neighbours (NW, NE, SW, SE)
├───┼───┼───┤      are √2 times farther than edge neighbours (N, S, E, W)
│ W │ X │ E │
├───┼───┼───┤
│ SW│ S │ SE│
└───┴───┴───┘
```
This makes "find all cells within radius R" inconsistent — some neighbours are closer than others.

### The Hexagon Fix
```
      ___
     /   \
 ___/  N  \___
/   \     /   \
| NW |  X  | NE |
\___/     \___/
    \  S  /
     \___/
```
Every hexagon has **exactly 6 neighbours, all equidistant from the center**. This makes radius-based searches (`k-ring`) mathematically consistent — no diagonal-distance distortion.

### Problem 2: Boundary-straddling (geohash)
As shown in `geohash-explainer.md`, two nearby points can have wildly different geohash prefixes if they straddle a cell boundary.

H3 doesn't eliminate this entirely (any tiling has boundaries), but the **k-ring** function makes handling it trivial: just always query the center cell + its ring of neighbours, and hexagonal symmetry means this ring is uniform in all directions.

---

## H3 Resolution Levels

H3 has 16 resolution levels (0 = coarsest, 15 = finest):

| Resolution | Approx. Hexagon Edge Length | Use Case |
|------------|------------------------------|----------|
| 0 | ~1,107 km | Continent-level analysis |
| 5 | ~8.5 km | City-level demand heatmaps |
| 7 | ~1.2 km | Neighbourhood-level driver search |
| 9 | ~0.17 km | Street-level matching |
| 15 | ~0.5 m | Building footprint |

For "find nearby drivers" — **resolution 7–8** is typically the sweet spot: small enough to be meaningful, large enough that you don't need to scan dozens of cells.

---

## K-Ring Lookup

`k_ring(cell, k)` returns all hexagons within `k` rings of the center cell.

```python
import h3

center = h3.latlng_to_cell(17.3850, 78.4867, 7)  # resolution 7
ring = h3.grid_disk(center, 1)  # center + 1 ring of neighbours (7 cells total)
```

To find nearby drivers: compute each driver's H3 cell at resolution 7, group drivers by cell, then look up `k_ring(rider_cell, k=1)` and gather all drivers across those cells.

---

## Summary Comparison

| | Geohash | Quadtree / R-tree | H3 |
|---|---------|---------------------|-----|
| Cell shape | Rectangle | Rectangle (variable size) | Hexagon |
| Neighbour distances | Unequal (diagonal vs edge) | N/A (irregular) | Equal (6 neighbours, same distance) |
| Adapts to data density | No (fixed grid) | Yes | No (fixed grid, but multi-resolution) |
| Used by | Redis GEO commands | PostGIS (GIST index) | Uber, Lyft, many ride-hailing/delivery platforms |
| Best for | Simple proximity search, easy DB indexing | General-purpose spatial queries | High-volume radius search with uniform symmetry |
