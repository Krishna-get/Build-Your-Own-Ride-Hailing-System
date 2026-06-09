# Week 3 — A*, Heuristics & Real Road Networks

> **Engineering Behind Ride-Hailing & Mapping Systems** · 9-Week Roadmap

---

## 🎯 Goals

By the end of this week you should be able to:

- Explain why A* outperforms Dijkstra in practice (informed vs uninformed search)
- Define admissible and consistent heuristics and give examples of each
- Implement the Haversine formula from scratch to compute distance between two lat/lng points
- Implement A* on a real city road network loaded with OSMnx
- Given two lat/lng points, return and visualise the shortest route on a map
- Compare nodes explored by Dijkstra vs A* on the same query and explain the difference

---

## 📚 Topics

| # | Topic |
|---|-------|
| 1 | Why A* beats Dijkstra in practice — informed vs uninformed search |
| 2 | Admissible vs consistent heuristics — Euclidean, Haversine, Manhattan |
| 3 | The Haversine formula — distance between two lat/lng points on a sphere |
| 4 | OpenStreetMap data model: nodes, ways, relations, tags |
| 5 | Loading a real city road network as a graph using OSMnx |
| 6 | Bidirectional A* and contraction hierarchies (conceptual — used in Google Maps) |

---

## 🔗 Resources

All links verified.

| Resource | Link |
|----------|------|
| Red Blob Games — Introduction to A* (best explainer on the internet) | https://www.redblobgames.com/pathfinding/a-star/introduction.html |
| OSMnx documentation | https://osmnx.readthedocs.io |
| Amit's Game Programming — pathfinding theory (Stanford) | https://theory.stanford.edu/~amitp/GameProgramming/ |
| Haversine formula — movable-type | https://www.movable-type.co.uk/scripts/latlong.html |

### Suggested study order
1. **Red Blob Games first** — interactive diagrams make A* click immediately. Spend 45–60 min here.
2. **Amit's pathfinding pages** — deeper theory on heuristics after you understand the basics.
3. **Haversine article** — read the formula, then implement it yourself before looking at the starter code.
4. **OSMnx docs (Getting Started + Examples Gallery)** — skim enough to download a city graph and plot it.

---

## ⭐ Deliverable

> **Do not skip this. It is proof you learned the week.**

**Requirements:**

- [ ] Implement the Haversine formula from scratch (no library) — used as the A* heuristic
- [ ] Implement A* on a real city road network loaded with OSMnx
- [ ] Given two lat/lng points (provided in `starter/points.py`), return the shortest route
- [ ] Visualise the route as a polyline on a map (matplotlib or folium)
- [ ] Run **both Dijkstra (from Week 2) and A*** on the same query and print how many nodes each explored
- [ ] Your solution goes in `deliverable/astar.py`

**Expected output:**
```
Query: (17.3850, 78.4867) → (17.4239, 78.4738)   [Hyderabad example]
-------------------------------------------------------
A*       explored:   843 nodes   distance: 6.2 km
Dijkstra explored: 4,217 nodes   distance: 6.2 km

A* explored 80% fewer nodes for the same result.
Route saved to: output/route_map.html
```

---

## 🛠️ Setup

Install dependencies before starting:

```bash
pip install osmnx matplotlib folium
```

> OSMnx downloads road data from OpenStreetMap on first run. It caches the result locally — subsequent runs are instant.

---

## 📝 Reflection

Fill in `deliverable/REFLECTION.md` after completing the deliverable.

---

## 🗂️ Folder Structure

```
week3-astar-real-roads/
├── README.md
├── resources/
│   ├── astar-vs-dijkstra.md        ← How A* differs from Dijkstra + heuristic guide
│   └── haversine-explainer.md      ← The formula, derivation, and when to use it
├── starter/
│   ├── points.py                   ← Lat/lng pairs to route between (your city + others)
│   └── osmnx_quickstart.py         ← Minimal OSMnx example to get you started
└── deliverable/
    ├── astar.py                    ← Your implementation goes here
    └── REFLECTION.md
```

---

## 💡 Study Tips

- **Play with Red Blob Games interactively** — click "show search" and watch A* vs Dijkstra explore different numbers of nodes. That visual is worth 100 pages of notes.
- **The heuristic must never overestimate.** If it does, A* may miss the optimal path. Haversine (straight-line distance on a sphere) never overestimates road distance — roads can only be longer than a straight line.
- **OSMnx returns a NetworkX graph.** Each node has `x` (longitude) and `y` (latitude) attributes. Each edge has a `length` attribute in metres.
- **Don't fight OSMnx's built-in router.** The deliverable asks you to implement A* yourself on the graph OSMnx downloads — don't use `ox.shortest_path()`.

---

## ⏭️ What's Next

**Week 4 — Geospatial Indexing: Geohashing, Quadtrees & H3**  
You'll learn how Uber finds the 5 closest drivers in milliseconds out of millions — one of the most interview-relevant topics in the entire roadmap.

---

*Engineering Behind Ride-Hailing & Mapping Systems · Week 3 of 9*
