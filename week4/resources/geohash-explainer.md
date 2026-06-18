# Geohash — Explainer

---

## The Problem

You have 1 million drivers. A rider wants the 5 nearest ones.

**Naive approach:**
```sql
SELECT * FROM drivers
ORDER BY ST_Distance(location, rider_location)
LIMIT 5;
```

This computes the distance from the rider to **every single driver**, then sorts. That's an O(N log N) operation on every single request. At scale, this collapses.

**The fix:** pre-bucket drivers into spatial cells, then only search cells near the rider.

---

## What Is a Geohash?

A geohash encodes a lat/lng point into a short string by **recursively bisecting** the world into halves — alternating between longitude and latitude.

```
Step 1: Is the point in the East or West half of the world?  → 1 bit
Step 2: Is the point in the North or South half?              → 1 bit
Step 3: Subdivide again within that quadrant...                → repeat
```

Every 5 bits get mapped to one character from this alphabet:
```
0123456789bcdefghjkmnpqrstuvwxyz
```

**Example:** Hyderabad city centre (17.3850, 78.4867) → geohash `tedb3...`

Each additional character **shrinks the cell by roughly a factor of 8** (more precision).

| Geohash Length | Approx. Cell Size |
|----------------|--------------------|
| 1 | ~5,000 km |
| 3 | ~150 km |
| 5 | ~5 km |
| 7 | ~150 m |
| 9 | ~5 m |

---

## Why It's Useful: Prefix Matching

Geohashes have a beautiful property: **nearby points usually share a common prefix**.

```
Point A: tedb3xyz...
Point B: tedb3abc...
         └─┬─┘
     same prefix → same ~5km cell
```

To find drivers "near" a rider:
1. Compute the rider's geohash at some precision (e.g. 5 characters ≈ 5km cells)
2. Query: `SELECT * FROM drivers WHERE geohash LIKE 'tedb3%'`
3. This is an indexed prefix lookup — fast, even with millions of rows

---

## The Edge Case You Must Know

**Nearby points can have completely different geohashes if they straddle a cell boundary.**

```
Point A: u000  (just west of a major cell boundary)
Point B: ezzz  (just east of that boundary)
```

These two points might be only 30km apart — but share **zero** common prefix characters, because they fall on opposite sides of a high-level bisection.

### The Fix
Always search the rider's cell **plus its 8 neighbouring cells**, not just the exact prefix match:

```sql
SELECT * FROM drivers
WHERE geohash IN ('tedb3', 'tedb1', 'tedb9', 'tedb2', ...) -- center + 8 neighbours
```

This requires a `neighbours()` function (most geohash libraries provide one).

---

## Python Example

```python
import geohash2 as geohash  # pip install python-geohash or geohash2

# Encode
code = geohash.encode(17.3850, 78.4867, precision=7)
print(code)  # → e.g. 'tedb3xy'

# Decode
lat, lon = geohash.decode('tedb3xy')
print(lat, lon)

# Neighbours (needed to handle the boundary edge case)
neighbours = geohash.neighbors('tedb3xy')
print(neighbours)  # 8 surrounding cells
```

---

## Why H3 (Week 4's other topic) Improves on This

Geohash cells are **rectangles**. Rectangles have a problem: a cell's neighbours are not all equidistant — diagonal neighbours are farther away than edge neighbours, and the boundary-straddling edge case above is a direct consequence of this.

**Hexagons solve this:** every hexagon has exactly 6 neighbours, all equidistant from the center. This is why Uber built H3. See `h3-vs-geohash-vs-quadtree.md` for the full comparison.

---

## Summary

| Concept | Key Idea |
|---------|----------|
| Geohash | Recursively bisect lat/lng into a string; prefix = proximity |
| Strength | Simple, works in any database with string indexing |
| Weakness | Boundary-straddling edge case; rectangular cells aren't uniform distance to neighbours |
| Fix | Always search center cell + 8 neighbours, never just exact prefix match |
