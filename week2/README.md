# Week 2 — Graphs & Dijkstra's Algorithm

> **Engineering Behind Ride-Hailing & Mapping Systems** · 9-Week Roadmap

---

## 🎯 Goals

By the end of this week you should be able to:

- Represent a graph as an adjacency list and explain when to prefer it over an adjacency matrix
- Explain BFS and DFS and what problems each solves
- Walk through Dijkstra's algorithm step-by-step from memory — relaxation, visited set, distance array
- Explain why a min-heap is essential to Dijkstra's efficiency
- Implement Dijkstra from scratch in Python using `heapq`
- State the time complexity O((V + E) log V) and explain where it comes from
- Explain why Dijkstra fails with negative edges and name the alternative

---

## 📚 Topics

| # | Topic |
|---|-------|
| 1 | Graph representations: adjacency list vs adjacency matrix — when to use each |
| 2 | BFS and DFS recap — unweighted shortest path, connected components |
| 3 | Dijkstra's algorithm step-by-step — relaxation, visited set, distance array |
| 4 | Priority queues and min-heaps — the data structure that makes Dijkstra fast |
| 5 | Why Dijkstra fails with negative edges (Bellman-Ford as the alternative) |
| 6 | Time complexity: O((V + E) log V) with a binary heap |

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| William Fiset — Graph Theory Playlist (YouTube) | https://youtube.com/playlist?list=PLDV1Zeh2NRsDGO4--qE8yH72HFL1Km93P |
| MIT OCW 6.006 — Lecture 13: Dijkstra (Spring 2020) | https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/ |
| CP-Algorithms — Dijkstra's algorithm | https://cp-algorithms.com/graph/dijkstra.html |
| VisuAlgo — interactive SSSP visualiser | https://visualgo.net/en/sssp |

### Suggested study order
1. Watch William Fiset's BFS, DFS, and Dijkstra videos first — they are short and clear
2. Play with VisuAlgo interactively — run Dijkstra step by step on a sample graph
3. Read the CP-Algorithms article — it has the cleanest written explanation
4. MIT OCW Lecture 13 for the formal proof and complexity analysis

---

## ⭐ Deliverable

> **Do not skip this. It is proof you learned the week.**

Implement Dijkstra's algorithm **from scratch** in Python using a min-heap (`heapq`).

**Requirements:**

- [ ] Use an adjacency list to represent the graph (not a matrix)
- [ ] Use Python's `heapq` module — no importing a pre-built Dijkstra
- [ ] Run it on the provided 10-node weighted graph in `starter/graph.py`
- [ ] For every node, print: the shortest distance from the source, and the path taken to get there
- [ ] Your solution goes in `deliverable/dijkstra.py`

**Expected output format:**
```
Source: Node 0
Node 0 → distance: 0    path: [0]
Node 1 → distance: 4    path: [0, 1]
Node 2 → distance: 7    path: [0, 2]
Node 3 → distance: 9    path: [0, 1, 3]
...
```

---

## 📝 Reflection

Fill in `deliverable/REFLECTION.md` after completing the deliverable.

---

## 🗂️ Folder Structure

```
week2-graphs-dijkstra/
├── README.md
├── resources/
│   ├── graph-representations.md    ← Adjacency list vs matrix cheat sheet
│   └── dijkstra-walkthrough.md     ← Step-by-step worked example
├── starter/
│   └── graph.py                    ← The 10-node graph to run your solution on
└── deliverable/
    ├── dijkstra.py                 ← Your implementation goes here
    └── REFLECTION.md               ← Fill in after completing
```

---

## 💡 Study Tips

- **Use VisuAlgo before coding.** Run Dijkstra on the interactive visualiser until you can predict the next step. Only then open your editor.
- **Write the algorithm in plain English first.** Comment every line of your code before writing it.
- **The min-heap is the key insight.** If you don't understand why `heapq` replaces the naïve O(V²) approach, re-read the CP-Algorithms article.
- **Trace through your own code by hand** on a 4-node graph before running it on the full 10-node graph.

---

## ⏭️ What's Next

**Week 3 — A\*, Heuristics & Real Road Networks**  
You'll move from textbook graphs to actual city streets, implement A* on a real OpenStreetMap road network, and compare how many nodes it explores vs Dijkstra.

---

*Engineering Behind Ride-Hailing & Mapping Systems · Week 2 of 9*
