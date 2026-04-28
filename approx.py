from __future__ import annotations

"""
2-approximation for Minimum Vertex Cover.

Idea:
- Repeatedly pick an uncovered edge (u, v)
- Add both endpoints to the cover
- This guarantees all chosen edges are covered, and the result is <= 2OPT
"""

from typing import Iterable, List, Tuple


Edge = Tuple[int, int]


def solve(n: int, edges: List[Edge]) -> List[int]:
    """Return a vertex cover (as a sorted list of vertices 1..n).

    Greedy 2-approximation:
    pick an uncovered edge, take both endpoints, and remove all edges they cover.
    """
    m = len(edges)
    if m == 0:
        return []

    # For fast updates: inc[v] = list of edge indices incident to vertex v.
    inc: List[List[int]] = [[] for _ in range(n + 1)]
    for i, (u, v) in enumerate(edges):
        if 1 <= u <= n:
            inc[u].append(i)
        if 1 <= v <= n:
            inc[v].append(i)

    # Track which edges are still uncovered.
    uncovered = [True] * m
    remaining = set(range(m))
    in_cover = [False] * (n + 1)

    while remaining:
        # Grab any uncovered edge and add both endpoints.
        i = next(iter(remaining))
        u, v = edges[i]

        # When we pick u or v, we also "delete" all incident edges from the uncovered set.
        if 1 <= u <= n and not in_cover[u]:
            in_cover[u] = True
            for ei in inc[u]:
                if uncovered[ei]:
                    uncovered[ei] = False
                    remaining.discard(ei)

        if 1 <= v <= n and not in_cover[v]:
            in_cover[v] = True
            for ei in inc[v]:
                if uncovered[ei]:
                    uncovered[ei] = False
                    remaining.discard(ei)

        # If the input has invalid vertex ids, avoid getting stuck.
        if not (1 <= u <= n) and not (1 <= v <= n):
            uncovered[i] = False
            remaining.discard(i)

    cover = [vertex for vertex in range(1, n + 1) if in_cover[vertex]]
    cover.sort()
    return cover
