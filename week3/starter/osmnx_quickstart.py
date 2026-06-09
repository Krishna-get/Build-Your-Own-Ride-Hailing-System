"""
starter/osmnx_quickstart.py
===========================
A minimal working example to get comfortable with OSMnx
before writing your A* implementation.

Run this first. It downloads your city's road network,
prints some stats, and saves a plot.

Usage:
    pip install osmnx matplotlib
    python osmnx_quickstart.py
"""

import osmnx as ox
import matplotlib.pyplot as plt

# ── 1. Download a road network ────────────────────────────────────────────────
# network_type options: 'drive', 'walk', 'bike', 'all'
# dist = radius in metres around the centre point

print("Downloading road network from OpenStreetMap...")
print("(This may take 10–30 seconds on first run, then it's cached.)\n")

G = ox.graph_from_place("Hyderabad, India", network_type="drive")

# ── 2. Inspect the graph ──────────────────────────────────────────────────────
print(f"Nodes (intersections): {G.number_of_nodes():,}")
print(f"Edges (road segments):  {G.number_of_edges():,}")

# Look at one node
sample_node = list(G.nodes)[0]
node_data = G.nodes[sample_node]
print(f"\nSample node {sample_node}:")
print(f"  Latitude:  {node_data['y']}")
print(f"  Longitude: {node_data['x']}")

# Look at one edge
sample_edge = list(G.edges(data=True))[0]
u, v, data = sample_edge
print(f"\nSample edge {u} → {v}:")
print(f"  Length:  {data.get('length', 'N/A')} metres")
print(f"  Name:    {data.get('name', 'unnamed')}")

# ── 3. Find the nearest node to a lat/lng point ───────────────────────────────
# This is how you'll snap your origin/destination coordinates to the graph

origin_lat, origin_lng = 17.3850, 78.4867
nearest_node = ox.nearest_nodes(G, X=origin_lng, Y=origin_lat)
print(f"\nNearest graph node to ({origin_lat}, {origin_lng}): {nearest_node}")

# ── 4. Plot the graph ─────────────────────────────────────────────────────────
print("\nPlotting... (close the window to continue)")
fig, ax = ox.plot_graph(G, node_size=2, edge_linewidth=0.5, show=True, close=False)
plt.savefig("output/road_network.png", dpi=100, bbox_inches="tight")
print("Saved to output/road_network.png")

# ── Key takeaways ─────────────────────────────────────────────────────────────
# 1. G is a NetworkX MultiDiGraph (directed — one-way streets are respected)
# 2. Node attributes: G.nodes[n]['y'] = latitude, G.nodes[n]['x'] = longitude
# 3. Edge attributes: G.edges[u, v, 0]['length'] = length in metres
# 4. ox.nearest_nodes(G, X=lng, Y=lat) snaps a coordinate to the graph
# 5. G.neighbors(node) gives outgoing neighbours (use G.successors(node) too)
# 6. For edge weight: G.edges[u, v, 0]['length']
#    (use min over keys 0,1,2... for multigraph: min(d['length'] for d in G[u][v].values()))
