# Week 2 Reflection

## Did your implementation pass verification on the first try?
Yes! The logic aligned perfectly with the test suite, allowing the min-heap to handle edge relaxation and accurately record our path trajectories to get a clean green passing validation on execution.

## What was the hardest part to implement?
The hardest part was path reconstruction. Writing the core traversal engine is relatively straightforward, but tracking a pointer backward from the destination using a dictionary of previous nodes, managing edge conditions, and flipping the list to output `[Source -> ... -> Target]` format required extra care.

## In your own words: why does Dijkstra need a min-heap?
Without a min-heap, finding the next unvisited node with the absolute lowest tentative distance requires looping through every node in the graph, resulting in an expensive $O(V^2)$ scan time. A min-heap natively retains the minimum value right at the top of the queue structure, cutting this extraction down to $O(\log V)$ and allowing the algorithm to execute effectively across huge real-world datasets.

## Why would Dijkstra give wrong answers on a graph with negative edge weights?
Dijkstra operates on a greedy assumption: once a node is popped out of the heap and marked as finalized, its shortest possible distance path has been determined permanently. If a negative edge exists down the line, it could theoretically present a much shorter alternative route to an already marked node, which Dijkstra will completely miss because it refuses to re-examine finalized vertices.

## How does this connect to ride-hailing?
In our Week 1 architecture design, the Map/Routing service is tasked with calculating the optimal driving route and generating accurate ETAs. Algorithms based on Dijkstra process structural road graphs (where intersections act as nodes and street intervals act as edges weighted by travel duration) to find the absolute fastest path for matching a driver to a rider.

## Time spent this week
3 hours

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| Adjacency list vs matrix — know when to use each | 5 |
| BFS and DFS — could implement from memory | 5 |
| Dijkstra — could implement from memory | 5 |
| Min-heap / heapq — understand how it works | 5 |
| Time complexity O((V+E) log V) — understand the derivation | 5 |
