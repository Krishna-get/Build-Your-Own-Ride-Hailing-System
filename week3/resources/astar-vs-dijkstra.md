# A* vs Dijkstra — How They Differ & Heuristic Guide

---

## The Core Difference

**Dijkstra** explores outward in all directions equally — like a wave spreading from the source.  
**A*** is guided toward the goal — it prioritises nodes that look closer to the destination.

Both guarantee the shortest path. A* just gets there by exploring far fewer nodes.

---

## The Algorithm

A* uses a priority queue exactly like Dijkstra, but the priority is different:

| Algorithm | Priority of a node | Meaning |
|-----------|--------------------|---------|
| Dijkstra | `g(n)` | Cost from start to n |
| A* | `f(n) = g(n) + h(n)` | Cost from start to n **+ estimated cost from n to goal** |

- `g(n)` = actual cost from start to node n (same as Dijkstra's distance)
- `h(n)` = **heuristic** — your estimate of the remaining cost to reach the goal
- `f(n)` = total estimated cost of the cheapest path through n

---

## What Makes a Good Heuristic?

### Admissible
The heuristic must **never overestimate** the true remaining cost.

> If the true distance from n to the goal is 5 km, h(n) must be ≤ 5 km.

If this is violated, A* may skip the optimal path because it thinks a longer route looks cheaper.

### Consistent (Monotone)
For every node n and its neighbour n':  
`h(n) ≤ cost(n, n') + h(n')`

Consistency implies admissibility and ensures A* never needs to re-open a visited node.

---

## Common Heuristics for Road Networks

### Euclidean Distance (straight line)
```python
import math
def euclidean(node, goal):
    dx = node.x - goal.x
    dy = node.y - goal.y
    return math.sqrt(dx**2 + dy**2)
```
✅ Admissible for flat grids  
❌ Not accurate for lat/lng (Earth is a sphere, degrees aren't uniform distances)

---

### Haversine Distance (great-circle)
```python
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```
✅ Admissible — straight-line distance on a sphere never exceeds road distance  
✅ Accurate for lat/lng coordinates  
✅ **The right heuristic for real road networks** — this is what you'll implement

---

### Manhattan Distance
```python
def manhattan(node, goal):
    return abs(node.x - goal.x) + abs(node.y - goal.y)
```
✅ Admissible for grid maps where you can only move horizontally/vertically  
❌ Not suitable for road networks (roads aren't axis-aligned grids)

---

## Nodes Explored: Why A* Wins

On a road network, Dijkstra expands in all directions — including roads going away from the destination. A* uses the heuristic to avoid expanding nodes that are clearly in the wrong direction.

```
Dijkstra: explores a full circle of radius = distance to goal
A*:       explores a narrow corridor roughly pointed at the goal
```

Typical savings on a city road network query:
- Dijkstra: explores 40–60% of the graph
- A* with Haversine: explores 5–15% of the graph

---

## Bidirectional A* (Conceptual)

Run A* simultaneously from both the source *and* the goal. Stop when the two frontiers meet.

Roughly halves the search space again. Used in Google Maps and Apple Maps for long-distance routing.

---

## Contraction Hierarchies (Conceptual)

A preprocessing technique used by production routing engines (OSRM, Valhalla, GraphHopper):

1. **Preprocessing:** Rank nodes by "importance". Remove less important nodes and add shortcut edges that preserve distances.
2. **Query:** Run a bidirectional search only on the upper layers of the hierarchy.

Result: millisecond routing on continent-scale graphs. The preprocessing takes hours but only happens once.

This is how Uber's routing actually works at scale — you won't implement this, but knowing it exists is important.
