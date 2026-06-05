# starter/graph.py
# This is the 10-node weighted graph your Dijkstra implementation must run on.
# Do not modify this file. Import it from your deliverable/dijkstra.py.
#
# Graph layout (approximate):
#
#   0 ---4--- 1 ---8--- 7
#   |         |       / |
#   11        2    7    9
#   |         |  /      |
#   7 ---1--- 6 ---2--- 8
#   |       / |         |
#   8      4  14       10
#   |    /    |         |
#   6 ---2--- 5 --------+
#
# Each entry: (neighbour, weight)

GRAPH = {
    0: [(1, 4),  (7, 8)],
    1: [(0, 4),  (2, 8),  (7, 11)],
    2: [(1, 8),  (3, 7),  (5, 4),  (8, 2)],
    3: [(2, 7),  (4, 9),  (5, 14)],
    4: [(3, 9),  (5, 10)],
    5: [(2, 4),  (3, 14), (4, 10), (6, 2)],
    6: [(5, 2),  (7, 1),  (8, 6)],
    7: [(0, 8),  (1, 11), (6, 1),  (8, 7)],
    8: [(2, 2),  (6, 6),  (7, 7)],
}

SOURCE = 0

# Expected shortest distances from node 0:
# Node 0 →  0
# Node 1 →  4
# Node 2 → 12
# Node 3 → 19
# Node 4 → 21
# Node 5 → 11
# Node 6 →  9
# Node 7 →  8
# Node 8 → 14
#
# Use these to verify your implementation is correct.
EXPECTED_DISTANCES = {0: 0, 1: 4, 2: 12, 3: 19, 4: 21, 5: 11, 6: 9, 7: 8, 8: 14}
