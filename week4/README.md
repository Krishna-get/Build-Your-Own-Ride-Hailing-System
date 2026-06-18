# Week 4 — Geospatial Indexing: Geohashing, Quadtrees & H3

> **Engineering Behind Ride-Hailing & Mapping Systems** · 9-Week Roadmap

---

## 🎯 Goals

By the end of this week you should be able to:

- Explain why `SELECT * FROM drivers ORDER BY distance` doesn't scale
- Encode a lat/lng point as a geohash and explain prefix-based proximity search
- Explain the edge case where nearby points have completely different geohash prefixes
- Describe quadtrees and R-trees conceptually
- Explain why Uber built H3 with hexagons instead of squares
- Use H3 k-ring lookups to find nearby cells
- Build a working "nearby drivers" service that responds in under 50ms

---

## 📚 Topics

| # | Topic |
|---|-------|
| 1 | Why `SELECT * FROM drivers ORDER BY distance` does not scale — full table scans |
| 2 | Geohash encoding — turning lat/lng into a hierarchical alphanumeric string |
| 3 | Geohash prefix matching for proximity search — neighbours and edge cases |
| 4 | Quadtrees and R-trees — conceptual understanding, how PostGIS uses them |
| 5 | Uber's H3 hexagonal hierarchical index — why hexagons instead of squares |
| 6 | H3 resolution levels — from continent (res 0) to building footprint (res 15) |
| 7 | Proximity search via H3 k-ring (ring of neighbouring hex cells) |

---

## 🔗 Resources

All links verified.

| Resource | Link |
|----------|------|
| Geohash explainer — movable-type | https://www.movable-type.co.uk/scripts/geohash.html |
| Uber H3 — official intro blog post | https://www.uber.com/en-IN/blog/h3/ |
| H3 documentation and tutorials | https://h3geo.org |
| Geospatial Indexing at Scale — Lyft's 15M QPS Redis Architecture (Daniel Hochman) | https://www.slideshare.net/slideshow/geospatial-indexing-at-scale-the-15-million-qps-redis-architecture-powering-lyft/76662828 |

> **Correction note:** the original roadmap PDF listed the 4th resource as an "Uber blog" post. We checked — this talk is actually by **Lyft**, not Uber, and the real figure is **15 million QPS**, not 10M. We've corrected the citation above so you're learning from the right source.

### Suggested study order
1. **Geohash explainer first** — play with the interactive map, type in your own coordinates
2. **Uber's H3 blog post** — understand *why* hexagons beat squares before touching code
3. **H3 docs Quick Start** — install `h3-py` and run the basic indexing examples
4. **Lyft's slide deck** — see how a real company scaled this to production

---

## ⭐ Deliverable

> **Do not skip this. It is proof you learned the week.**

Build a **"nearby drivers" service**.

**Requirements:**

- [ ] Seed 10,000 fake driver locations into Redis (or an in-memory store if you don't have Redis set up)
- [ ] Given a rider's lat/lng, return the **5 nearest drivers**
- [ ] Use **either** geohash prefix matching **or** H3 k-ring lookup (your choice — try both if you have time)
- [ ] Response time must be **under 50ms**
- [ ] Benchmark it and include the response time in your `README.md` inside `deliverable/`

**Expected output:**
```
Seeding 10,000 fake drivers across Hyderabad...
Done in 1.8s

Rider location: (17.3850, 78.4867)

Querying 5 nearest drivers...
1. driver_4231  →  0.21 km
2. driver_8857  →  0.34 km
3. driver_1098  →  0.41 km
4. driver_6623  →  0.52 km
5. driver_3301  →  0.58 km

Query time: 12.4 ms  ✅ (under 50ms target)
```

---

## 🛠️ Setup

```bash
pip install redis h3
```

> If you don't have Redis running locally, install it via Docker:
> ```bash
> docker run -d -p 6379:6379 redis
> ```
> Or use the in-memory fallback in `starter/seed_drivers.py` (no Redis required).

---

## 📝 Reflection

Fill in `deliverable/REFLECTION.md` after completing the deliverable.

---

## 🗂️ Folder Structure

```
week4-geospatial-indexing/
├── README.md
├── resources/
│   ├── geohash-explainer.md       ← Encoding, prefix search, edge cases
│   └── h3-vs-geohash-vs-quadtree.md  ← Comparison + why Uber chose hexagons
├── starter/
│   └── seed_drivers.py            ← Generates 10,000 fake drivers around your city
└── deliverable/
    ├── nearby_drivers.py          ← Your implementation goes here
    └── REFLECTION.md
```

---

## 💡 Study Tips

- **Geohash prefix matching has a sharp edge case:** two points 30km apart can share zero prefix characters if they straddle a cell boundary. Always search neighbouring prefixes too, not just the exact match.
- **H3's k-ring is the cleaner solution to that edge case** — hexagons don't have the "boundary straddling" problem that geohash's rectangular cells do, since every hexagon has 6 equidistant neighbours.
- **Think about resolution choice.** H3 resolution 7 (~5km² hexagons) is often right for city-level driver search; resolution 9 (~0.1km²) is too fine and creates too many cells to scan.
- **Benchmark properly.** Run your query 100 times and report the *average*, not a single lucky run.

---

## ⏭️ What's Next

**Week 5 — REST API Design & Backend Foundation**  
You'll design the full HTTP surface for your ride-hailing system — authentication, versioning, and a documented OpenAPI contract — before writing handler code.

---

*Engineering Behind Ride-Hailing & Mapping Systems · Week 4 of 9*
