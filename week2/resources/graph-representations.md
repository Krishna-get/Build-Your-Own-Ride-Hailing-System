# Graph Representations — Cheat Sheet

---

## The Two Main Representations

### 1. Adjacency List

Each node stores a list of its neighbours (and edge weights).

```python
# Undirected weighted graph with 4 nodes
graph = {
    0: [(1, 4), (2, 1)],   # node 0 connects to node 1 (weight 4) and node 2 (weight 1)
    1: [(0, 4), (3, 1)],
    2: [(0, 1), (3, 5)],
    3: [(1, 1), (2, 5)],
}
```

**Space:** O(V + E)  
**Check if edge (u, v) exists:** O(degree(u))  
**Iterate over neighbours of u:** O(degree(u))

✅ Use when: the graph is **sparse** (few edges relative to nodes²) — road networks, social graphs  
✅ Default choice for almost all graph algorithms

---

### 2. Adjacency Matrix

A V×V grid where `matrix[u][v]` is the weight of the edge from u to v (or 0/∞ if no edge).

```python
INF = float('inf')

# Same 4-node graph as above
matrix = [
    #  0    1    2    3
    [  0,   4,   1, INF],  # node 0
    [  4,   0, INF,   1],  # node 1
    [  1, INF,   0,   5],  # node 2
    [INF,   1,   5,   0],  # node 3
]
```

**Space:** O(V²)  
**Check if edge (u, v) exists:** O(1)  
**Iterate over neighbours of u:** O(V) — must scan the full row

✅ Use when: the graph is **dense** (edges close to V²), or you need O(1) edge lookups  
✅ Also useful for Floyd-Warshall all-pairs shortest paths

---

## Quick Comparison

| Operation | Adjacency List | Adjacency Matrix |
|-----------|---------------|------------------|
| Space | O(V + E) | O(V²) |
| Add edge | O(1) | O(1) |
| Remove edge | O(degree) | O(1) |
| Check edge exists | O(degree) | O(1) |
| Get all neighbours | O(degree) | O(V) |
| Best for | Sparse graphs | Dense graphs |

---

## For This Roadmap

Road networks are **extremely sparse** — a city intersection typically has 3–4 connections, not thousands. An adjacency list is always the right choice for routing.

Mumbai's road graph (OpenStreetMap) has ~200,000 nodes and ~500,000 edges.  
- Adjacency list: ~700,000 entries  
- Adjacency matrix: 200,000² = **40 billion entries** — completely unusable

---

## BFS vs DFS — Quick Recap

| | BFS | DFS |
|---|-----|-----|
| Data structure | Queue | Stack (or recursion) |
| Finds shortest path? | ✅ Yes (unweighted) | ❌ No |
| Memory usage | High (stores whole frontier) | Low |
| Good for | Shortest path, level-order | Cycle detection, topological sort, connected components |
| Time complexity | O(V + E) | O(V + E) |

**Key insight:** BFS gives the shortest path in terms of *number of edges* (unweighted). For weighted graphs, you need Dijkstra.
