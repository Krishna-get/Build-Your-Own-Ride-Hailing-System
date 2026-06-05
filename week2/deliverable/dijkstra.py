"""
Week 2 Deliverable — Dijkstra's Algorithm
==========================================
Implement Dijkstra from scratch using Python's heapq (min-heap).

Rules:
  - Do NOT import any graph library (networkx, igraph, etc.)
  - Do NOT use a pre-built shortest-path function
  - You MAY use: heapq, collections, sys, math — and nothing else

Your implementation must:
  1. Find the shortest distance from SOURCE to every other node
  2. Track the actual path taken (not just the distance)
  3. Print results in the format shown below
  4. Verify results against EXPECTED_DISTANCES and print PASS/FAIL

Expected output format:
  Source: Node 0
  ----------------------------------------
  Node 0 → distance:  0    path: [0]
  Node 1 → distance:  4    path: [0, 1]
  Node 2 → distance: 12    path: [0, 1, 2]
  ...
  ----------------------------------------
  Verification: PASS ✅
"""

import heapq
import sys

# Import the graph defined for you
sys.path.insert(0, "../starter")
from graph import GRAPH, SOURCE, EXPECTED_DISTANCES


def dijkstra(graph: dict, source: int) -> tuple[dict, dict]:
    """
    Run Dijkstra's algorithm on `graph` from `source`.

    Args:
        graph:  adjacency list — {node: [(neighbour, weight), ...]}
        source: the starting node

    Returns:
        distances: {node: shortest_distance_from_source}
        previous:  {node: previous_node_on_shortest_path}
                   (use this to reconstruct paths)
    """
    # TODO: implement Dijkstra here
    # Hint: structure your solution around these steps:
    #   1. Initialise distances to infinity for all nodes except source (= 0)
    #   2. Initialise a min-heap with (0, source)
    #   3. Keep a visited set
    #   4. While heap is not empty:
    #        a. Pop (current_dist, current_node)
    #        b. If already visited, skip
    #        c. Mark visited
    #        d. For each (neighbour, weight):
    #             if current_dist + weight < distances[neighbour]:
    #                 update distances[neighbour]
    #                 update previous[neighbour] = current_node
    #                 push (new_dist, neighbour) to heap

    distances = {}
    previous = {}

    # --- your code here ---

    return distances, previous


def reconstruct_path(previous: dict, source: int, target: int) -> list:
    """
    Walk backwards through `previous` to reconstruct the path
    from `source` to `target`.

    Returns a list of nodes from source to target, or [] if unreachable.
    """
    path = []

    # --- your code here ---

    return path


def main():
    distances, previous = dijkstra(GRAPH, SOURCE)

    print(f"Source: Node {SOURCE}")
    print("-" * 40)

    all_nodes = sorted(GRAPH.keys())
    for node in all_nodes:
        dist = distances.get(node, float("inf"))
        path = reconstruct_path(previous, SOURCE, node)
        print(f"Node {node} → distance: {dist:>3}    path: {path}")

    print("-" * 40)

    # Verification
    correct = all(distances.get(n) == d for n, d in EXPECTED_DISTANCES.items())
    if correct:
        print("Verification: PASS ✅")
    else:
        print("Verification: FAIL ❌")
        for node, expected in EXPECTED_DISTANCES.items():
            got = distances.get(node, "missing")
            if got != expected:
                print(f"  Node {node}: expected {expected}, got {got}")


if __name__ == "__main__":
    main()
