from __future__ import annotations

from typing import Iterable, List, Tuple


Edge = Tuple[int, int]


def solve(n: int, edges: List[Edge]) -> List[int]:
    m = len(edges)
    if m == 0:
        return []

    inc: List[List[int]] = [[] for _ in range(n + 1)]
    for i, (u, v) in enumerate(edges):
        if 1 <= u <= n:
            inc[u].append(i)
        if 1 <= v <= n:
            inc[v].append(i)

    uncovered = [True] * m
    remaining = set(range(m))
    in_cover = [False] * (n + 1)

    while remaining:
        i = next(iter(remaining))
        u, v = edges[i]

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

        if not (1 <= u <= n) and not (1 <= v <= n):
            uncovered[i] = False
            remaining.discard(i)

    cover = [vertex for vertex in range(1, n + 1) if in_cover[vertex]]
    cover.sort()
    return cover


def is_vertex_cover(cover: Iterable[int], edges: Iterable[Edge]) -> bool:
    cover_set = set(cover)
    for u, v in edges:
        if (u not in cover_set) and (v not in cover_set):
            return False
    return True

