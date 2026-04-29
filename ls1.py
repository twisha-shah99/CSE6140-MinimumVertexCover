# ls1.py — Local Search 1: Simulated Annealing for Minimum Vertex Cover
# Warm-starts from the greedy 2-approximation, then runs SA with energy:
#   E = |cover| + PENALTY * |uncovered edges|
# Usage: python3 mvc.py -inst <instance> -alg LS1 -time <cutoff> -seed <seed>

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
    """
    Parameters
    ----------
    n       : number of vertices (labeled 1..n)
    edges   : list of (u, v) undirected edges
    cutoff  : time limit in seconds
    seed    : random seed for reproducibility

    Returns
    -------
    best_cover : sorted vertex indices of the best valid cover found
    trace      : list of (elapsed_seconds, cover_size) on each improvement
    """
    random.seed(seed)
    start_time = time.time()
    m = len(edges)

    if m == 0:
        return [], []

    # inc[v] = indices of edges incident to v (for O(deg) flips)
    inc: List[List[int]] = [[] for _ in range(n + 1)]
    for i, (u, v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)

    # Warm-start from the greedy 2-approximation
    init_cover = _approx.solve(n, edges)
    in_cover = [False] * (n + 1)
    for v in init_cover:
        in_cover[v] = True

    # edge_cover_count[i] = number of cover endpoints for edge i (0, 1, or 2)
    edge_cover_count = [0] * m
    for i, (u, v) in enumerate(edges):
        edge_cover_count[i] = int(in_cover[u]) + int(in_cover[v])

    uncovered_count = 0
    cover_size = len(init_cover)

    best_cover = list(init_cover)
    best_size = cover_size
    trace: List[Tuple[float, int]] = [(0.0, best_size)]

    # SA hyper-parameters
    PENALTY = 3        # penalty weight for uncovered edges in the energy function
    T0 = 1.0           # initial temperature
    T_MIN = 1e-3       # stopping temperature
    CHECK_INTERVAL = 500  # iterations between time/temperature checks

    T = T0
    iteration = 0

    while True:
        if iteration % CHECK_INTERVAL == 0:
            elapsed = time.time() - start_time
            if elapsed >= cutoff or T <= T_MIN:
                break
            # Exponential cooling: T(t) = T0 * (T_MIN/T0)^(t/cutoff)
            frac = elapsed / cutoff
            T = T0 * math.exp(frac * math.log(T_MIN / T0))

        # Propose a random vertex flip
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
