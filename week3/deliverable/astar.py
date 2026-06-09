"""
Week 3 Deliverable — A* on a Real City Road Network
=====================================================
Implement A* using Haversine as the heuristic on an OSMnx road graph.
Then compare it against Dijkstra to measure how many fewer nodes it explores.

Rules:
  - Implement haversine() yourself (no geopy, no haversine library)
  - Implement astar() yourself (no nx.astar_path, no ox.shortest_path)
  - You MAY use: osmnx, heapq, math, matplotlib or folium for visualisation
"""

import heapq
import math
import os
import sys

import osmnx as ox

# sys.path.insert(0, "../starter")
from starter.points import (
    ORIGIN_LAT,
    ORIGIN_LNG,
    DEST_LAT,
    DEST_LNG,
    LABEL,
)

os.makedirs("output", exist_ok=True)


# ── Haversine heuristic ───────────────────────────────────────────────────────

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Return the great-circle distance in metres between two lat/lng points.
    Implement this from scratch using the formula in resources/haversine-explainer.md
    Do NOT use any library for this.
    """
    R = 6371000.0  # Earth's mean radius in metres

    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Apply the Haversine formula
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c


# ── A* implementation ─────────────────────────────────────────────────────────

def astar(G, origin_node: int, dest_node: int) -> tuple[list, float, int]:
    """
    Run A* on the OSMnx graph G from origin_node to dest_node.
    Use haversine() as the heuristic (straight-line distance to destination).
    """
    dest_lat = G.nodes[dest_node]['y']
    dest_lon = G.nodes[dest_node]['x']

    # Open set tracking: (f_score, current_node)
    min_heap = [(haversine(G.nodes[origin_node]['y'], G.nodes[origin_node]['x'], dest_lat, dest_lon), origin_node)]
    
    # Cost records
    g_score = {node: float("inf") for node in G.nodes}
    g_score[origin_node] = 0.0

    previous = {}
    visited = set()
    nodes_explored = 0

    while min_heap:
        current_f, current_node = heapq.heappop(min_heap)

        if current_node in visited:
            continue

        visited.add(current_node)
        nodes_explored += 1

        # Target reached early
        if current_node == dest_node:
            break

        # Explore successors (OSMnx MultiDiGraph uses successors for directed edges)
        for neighbour in G.successors(current_node):
            if neighbour in visited:
                continue

            # MultiDiGraph could have parallel paths, grab the absolute minimum distance edge
            edge_weight = min(d['length'] for d in G[current_node][neighbour].values())
            tentative_g = g_score[current_node] + edge_weight

            if tentative_g < g_score[neighbour]:
                g_score[neighbour] = tentative_g
                previous[neighbour] = current_node
                
                # Compute total cost f(n) = g(n) + h(n)
                h_score = haversine(G.nodes[neighbour]['y'], G.nodes[neighbour]['x'], dest_lat, dest_lon)
                f_score = tentative_g + h_score
                
                heapq.heappush(min_heap, (f_score, neighbour))

    # Path reconstruction
    path = []
    if dest_node in previous or origin_node == dest_node:
        curr = dest_node
        while curr in previous:
            path.append(curr)
            curr = previous[curr]
        path.append(origin_node)
        path.reverse()

    distance = g_score[dest_node] if g_score[dest_node] != float("inf") else 0.0
    return path, distance, nodes_explored


# ── Dijkstra (for comparison) ─────────────────────────────────────────────────

def dijkstra(G, origin_node: int, dest_node: int) -> tuple[list, float, int]:
    """
    Run Dijkstra on the same OSMnx graph.
    Same interface as astar() — returns (path, distance, nodes_explored).
    """
    min_heap = [(0.0, origin_node)]
    
    distances = {node: float("inf") for node in G.nodes}
    distances[origin_node] = 0.0

    previous = {}
    visited = set()
    nodes_explored = 0

    while min_heap:
        current_dist, current_node = heapq.heappop(min_heap)

        if current_node in visited:
            continue

        visited.add(current_node)
        nodes_explored += 1

        # Early termination when target node is reached
        if current_node == dest_node:
            break

        for neighbour in G.successors(current_node):
            if neighbour in visited:
                continue

            edge_weight = min(d['length'] for d in G[current_node][neighbour].values())
            new_dist = current_dist + edge_weight

            if new_dist < distances[neighbour]:
                distances[neighbour] = new_dist
                previous[neighbour] = current_node
                heapq.heappush(min_heap, (new_dist, neighbour))

    # Path reconstruction
    path = []
    if dest_node in previous or origin_node == dest_node:
        curr = dest_node
        while curr in previous:
            path.append(curr)
            curr = previous[curr]
        path.append(origin_node)
        path.reverse()

    distance = distances[dest_node] if distances[dest_node] != float("inf") else 0.0
    return path, distance, nodes_explored


# ── Visualisation ─────────────────────────────────────────────────────────────

def visualise_route(G, path: list, filename: str = "output/route_map.html"):
    """
    Plot the route on an interactive map using folium and save as HTML.
    If folium is not installed, fall back to a static matplotlib plot.
    """
    try:
        import folium
        # Center point from origin coordinates
        start_coord = (G.nodes[path[0]]['y'], G.nodes[path[0]]['x'])
        m = folium.Map(location=start_coord, zoom_start=14, tiles="cartodbpositron")
        
        # Build list of points for polyline mapping
        route_points = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in path]
        folium.PolyLine(route_points, color="#4885ed", weight=5, opacity=0.8).add_to(m)
        
        # Add quick origin/destination markers
        folium.Marker(location=route_points[0], popup="Origin", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(location=route_points[-1], popup="Destination", icon=folium.Icon(color='red')).add_to(m)
        
        m.save(filename)
        print(f"Interactive map saved to: {filename}")
    except ImportError:
        # fallback: matplotlib static plot
        fig, ax = ox.plot_graph_route(G, path, route_linewidth=3, node_size=0, show=False)
        png_path = filename.replace(".html", ".png")
        fig.savefig(png_path, dpi=150, bbox_inches="tight")
        print(f"Static map saved to: {png_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Route: {LABEL}")
    print(f"  Origin:      ({ORIGIN_LAT}, {ORIGIN_LNG})")
    print(f"  Destination: ({DEST_LAT}, {DEST_LNG})\n")

    # 1. Download road network
    print("Loading road network (cached after first run)...")
    G = ox.graph_from_place("Hyderabad, India", network_type="drive")
    print(f"Graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges\n")

    # 2. Snap coordinates to nearest graph nodes
    origin_node = ox.nearest_nodes(G, X=ORIGIN_LNG, Y=ORIGIN_LAT)
    dest_node   = ox.nearest_nodes(G, X=DEST_LNG,   Y=DEST_LAT)

    # 3. Run A*
    astar_path, astar_dist, astar_explored = astar(G, origin_node, dest_node)

    # 4. Run Dijkstra
    dijkstra_path, dijkstra_dist, dijkstra_explored = dijkstra(G, origin_node, dest_node)

    # 5. Print comparison
    print(f"{'Algorithm':<12} {'Nodes explored':>16} {'Distance':>12}")
    print("-" * 42)
    print(f"{'A*':<12} {astar_explored:>16,} {astar_dist/1000:>11.2f} km")
    print(f"{'Dijkstra':<12} {dijkstra_explored:>16,} {dijkstra_dist/1000:>11.2f} km")

    if dijkstra_explored > 0:
        saving = (1 - astar_explored / dijkstra_explored) * 100
        print(f"\nA* explored {saving:.0f}% fewer nodes for the same result.")

    # 6. Visualise
    if astar_path:
        visualise_route(G, astar_path)


if __name__ == "__main__":
    main()