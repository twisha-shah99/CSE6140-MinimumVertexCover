import math
import random
import time
from typing import List, Tuple

import approx as _approx

Edge = Tuple[int, int]


def solve(
    n: int,
    edges: List[Edge],
    cutoff: float,
    seed: int,
) -> Tuple[List[int], List[Tuple[float, int]]]:
    random.seed(seed)
    start_time = time.time()
    m = len(edges)

    if m == 0:
        return [], []

    # inc[v] = list of edge indices incident to v
    inc: List[List[int]] = [[] for _ in range(n + 1)]
    for i, (u, v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)

    # Warm-start from the approx 2-approximation
    init_cover = _approx.solve(n, edges)
    in_cover = [False] * (n + 1)
    for v in init_cover:
        in_cover[v] = True

    # edge_cover_count[i] = number of cover endpoints in edge i (0, 1, or 2)
    edge_cover_count = [0] * m
    for i, (u, v) in enumerate(edges):
        edge_cover_count[i] = int(in_cover[u]) + int(in_cover[v])

    uncovered_count = 0  # approx produces a valid cover
    cover_size = len(init_cover)

    best_cover = list(init_cover)
    best_size = cover_size
    trace: List[Tuple[float, int]] = [(0.0, best_size)]

    # --- SA hyper-parameters ---
    PENALTY = 3
    T0 = 1.0
    T_MIN = 1e-3
    CHECK_INTERVAL = 500  # iterations between time checks

    T = T0
    iteration = 0

    while True:
        if iteration % CHECK_INTERVAL == 0:
            elapsed = time.time() - start_time
            if elapsed >= cutoff or T <= T_MIN:
                break               
            # Geometric schedule: T = T0 * (T_MIN/T0)^(elapsed/cutoff)
            frac = elapsed / cutoff
            T = T0 * math.exp(frac * math.log(T_MIN / T0))

        # --- Pick a random vertex to flip ---
        vtx = random.randint(1, n)

        if in_cover[vtx]:
            delta_size = -1
            delta_uncov = sum(1 for ei in inc[vtx] if edge_cover_count[ei] == 1)
        else:
            delta_size = 1
            delta_uncov = -sum(1 for ei in inc[vtx] if edge_cover_count[ei] == 0)

        delta_energy = delta_size + PENALTY * delta_uncov

        # Metropolis acceptance
        if delta_energy <= 0 or random.random() < math.exp(-delta_energy / T):
            if in_cover[vtx]:
                in_cover[vtx] = False
                for ei in inc[vtx]:
                    edge_cover_count[ei] -= 1
            else:
                in_cover[vtx] = True
                for ei in inc[vtx]:
                    edge_cover_count[ei] += 1
            cover_size += delta_size
            uncovered_count += delta_uncov

            if uncovered_count == 0 and cover_size < best_size:
                best_size = cover_size
                best_cover = [v for v in range(1, n + 1) if in_cover[v]]
                trace.append((time.time() - start_time, best_size))

        iteration += 1

    return sorted(best_cover), trace
