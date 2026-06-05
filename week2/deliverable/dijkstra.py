import heapq
import sys
import os

# Dynamically find the absolute path to your starter directory
current_dir = os.path.dirname(os.path.abspath(__file__))
week2_dir = os.path.dirname(current_dir)
starter_dir = os.path.join(week2_dir, "starter")
sys.path.insert(0, starter_dir)

from graph import GRAPH, SOURCE, EXPECTED_DISTANCES  # type: ignore


def dijkstra(graph: dict, source: int) -> tuple[dict, dict]:
    """
    Run Dijkstra's algorithm on `graph` from `source`.
    """
    # 1. Initialise distances to infinity for all nodes except source (= 0)
    distances = {node: float("inf") for node in graph}
    distances[source] = 0
    previous = {node: None for node in graph}
    
    # 2. Initialise a min-heap with (0, source)
    min_heap = [(0, source)]
    
    # 3. Keep a visited set
    visited = set()

    # 4. While heap is not empty:
    while min_heap:
        # a. Pop (current_dist, current_node)
        current_dist, current_node = heapq.heappop(min_heap)

        # b. If already visited, skip
        if current_node in visited:
            continue
            
        # c. Mark visited
        visited.add(current_node)

        # d. For each (neighbour, weight):
        for neighbour, weight in graph.get(current_node, []):
            if neighbour in visited:
                continue
                
            new_dist = current_dist + weight
            if new_dist < distances[neighbour]:
                # update distances and previous node on shortest path
                distances[neighbour] = new_dist
                previous[neighbour] = current_node
                # push (new_dist, neighbour) to heap
                heapq.heappush(min_heap, (new_dist, neighbour))

    return distances, previous


def reconstruct_path(previous: dict, source: int, target: int) -> list:
    """
    Walk backwards through `previous` to reconstruct the path
    from `source` to `target`.
    """
    if target not in previous and source != target:
        return []
        
    path = []
    current = target
    
    # Trace back until we hit the source node
    while current is not None:
        path.append(current)
        current = previous[current]
        
    path.reverse()
    
    if path[0] == source:
        return path
    return []


def main():
    distances, previous = dijkstra(GRAPH, SOURCE)

    print(f"Source: Node {SOURCE}")
    print("-" * 40)

    all_nodes = sorted(GRAPH.keys())
    for node in all_nodes:
        dist = distances.get(node, float("inf"))
        path = reconstruct_path(previous, SOURCE, node)
        # Using "->" instead of unicode arrow to stay fully safe on older consoles
        print(f"Node {node} -> distance: {dist:>3}    path: {path}")

    print("-" * 40)

    # Verification against EXPECTED_DISTANCES
    correct = all(distances.get(n) == d for n, d in EXPECTED_DISTANCES.items())
    if correct:
        print("Verification: PASS")
    else:
        print("Verification: FAIL")


if __name__ == "__main__":
    main()
