# Dijkstra's Algorithm — Step-by-Step Walkthrough

---

## The Problem

Given a weighted graph and a source node, find the **shortest path from the source to every other node**.

---

## The Graph We'll Use

```
        4
   0 ———————— 1
   |           |
 1 |           | 1
   |           |
   2 ———————— 3
        5
```

Edges: 0→1 (weight 4), 0→2 (weight 1), 1→3 (weight 1), 2→3 (weight 5)

---

## The Algorithm — Plain English

1. Set distance to source = 0, distance to everything else = ∞
2. Add the source to a min-heap (priority queue) with priority 0
3. While the heap is not empty:
   - Pop the node with the **smallest known distance**
   - If already visited, skip it
   - Mark it visited
   - For each unvisited neighbour: if `current_dist + edge_weight < neighbour's known distance`, update it and push to heap

---

## Step-by-Step Trace (source = node 0)

**Initial state:**

| Node | Distance | Visited |
|------|----------|---------|
| 0    | **0**    | No      |
| 1    | ∞        | No      |
| 2    | ∞        | No      |
| 3    | ∞        | No      |

Heap: `[(0, node_0)]`

---

**Iteration 1 — pop node 0 (dist=0)**

Check neighbours:
- Node 1: 0 + 4 = 4 < ∞ → update to 4, push (4, node_1)
- Node 2: 0 + 1 = 1 < ∞ → update to 1, push (1, node_2)

| Node | Distance | Visited |
|------|----------|---------|
| 0    | 0        | ✅ Yes  |
| 1    | **4**    | No      |
| 2    | **1**    | No      |
| 3    | ∞        | No      |

Heap: `[(1, node_2), (4, node_1)]`

---

**Iteration 2 — pop node 2 (dist=1)**

Check neighbours:
- Node 0: already visited, skip
- Node 3: 1 + 5 = 6 < ∞ → update to 6, push (6, node_3)

| Node | Distance | Visited |
|------|----------|---------|
| 0    | 0        | ✅ Yes  |
| 1    | 4        | No      |
| 2    | **1**    | ✅ Yes  |
| 3    | **6**    | No      |

Heap: `[(4, node_1), (6, node_3)]`

---

**Iteration 3 — pop node 1 (dist=4)**

Check neighbours:
- Node 0: already visited, skip
- Node 3: 4 + 1 = 5 < 6 → **update to 5**, push (5, node_3)

| Node | Distance | Visited |
|------|----------|---------|
| 0    | 0        | ✅ Yes  |
| 1    | 4        | ✅ Yes  |
| 2    | 1        | ✅ Yes  |
| 3    | **5**    | No      |

Heap: `[(5, node_3), (6, node_3)]`  ← note: stale (6, node_3) still in heap

---

**Iteration 4 — pop node 3 (dist=5)**

Mark visited. No unvisited neighbours.

Heap: `[(6, node_3)]`

---

**Iteration 5 — pop (6, node_3)**

Node 3 already visited → **skip**.

Heap empty. Done.

---

## Final Result

| Node | Shortest Distance from Node 0 | Path |
|------|-------------------------------|------|
| 0    | 0                             | [0] |
| 1    | 4                             | [0, 1] |
| 2    | 1                             | [0, 2] |
| 3    | 5                             | [0, 1, 3] ← not [0, 2, 3] which would be 6 |

---

## Key Insight: Why the Min-Heap?

Without a heap, finding the unvisited node with minimum distance requires scanning all nodes: **O(V)** per iteration → **O(V²)** total.

With a min-heap, the minimum is always at the top: **O(log V)** per pop → **O((V + E) log V)** total.

For a road network with 200,000 nodes and 500,000 edges:
- Naïve: 200,000² = **40 billion operations**
- With heap: (200,000 + 500,000) × log(200,000) ≈ **12 million operations**

---

## Why Dijkstra Fails with Negative Edges

Dijkstra assumes: *once a node is popped from the heap as visited, its distance is final.*

This assumption breaks if a negative edge could later provide a shorter path to an already-visited node.

**Alternative:** Bellman-Ford — relaxes all edges V-1 times. Works with negative weights. Time: O(V × E) — much slower, but correct.

For road networks: edge weights are distances, so always positive. Dijkstra is safe.
