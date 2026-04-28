import random
import time

import approx

# ---------------------------------------------------------------------------
# Randomised greedy initial cover (top-k random selection)
# ---------------------------------------------------------------------------
def _rand_greedy_cover(n, adj, rng, k=3):
    uncovered = set()
    for u in range(1, n + 1):
        for v in adj[u]:
            if u < v:
                uncovered.add((u, v))

    cover = set()
    deg   = [len(adj[u]) for u in range(n + 1)]

    while uncovered:
        active = [v for v in range(1, n + 1) if deg[v] > 0]
        if not active:
            break
        active.sort(key=lambda x: -deg[x])
        pool   = active[:max(1, k)]
        chosen = rng.choice(pool)
        cover.add(chosen)
        for v in adj[chosen]:
            e = (min(chosen, v), max(chosen, v))
            if e in uncovered:
                uncovered.discard(e)
                deg[v] -= 1
        deg[chosen] = 0

    return cover


# ---------------------------------------------------------------------------
# NuMVC inner loop
# Runs until time.time() >= slice_end.
# Returns (best_cover_set, best_size, trace_entries_with_absolute_timestamps)
# ---------------------------------------------------------------------------
def _numvc(n, adj, vertex_edges, clean, m, init_cover, slice_end, rng):
    is_in_cover     = [0] * (n + 1)
    edge_cov_cnt = [0] * m
    dscore       = [0] * (n + 1)
    loss         = [0] * (n + 1)
    age          = list(range(n + 1))

    for v in init_cover:
        is_in_cover[v] = 1

    for i, (u, v) in enumerate(clean):
        edge_cov_cnt[i] = is_in_cover[u] + is_in_cover[v]

    uncov = set(i for i in range(m) if edge_cov_cnt[i] == 0)

    for i, (u, v) in enumerate(clean):
        cc = edge_cov_cnt[i]
        if cc == 0:
            dscore[u] += 1; dscore[v] += 1
        elif cc == 1:
            if is_in_cover[u]: loss[u] += 1
            else:           loss[v] += 1

    step       = n + 1
    cur_size   = len(init_cover)
    best_cov   = set(init_cover)
    best_size  = cur_size
    last_added = -1
    trace      = []

    def add_v(v):
        nonlocal step
        is_in_cover[v] = 1; age[v] = step; dscore[v] = 0
        for ei, nb in vertex_edges[v]:
            cc = edge_cov_cnt[ei]
            if cc == 0:
                uncov.discard(ei); dscore[nb] -= 1; loss[v] += 1
            elif cc == 1:
                loss[nb] -= 1
            edge_cov_cnt[ei] = cc + 1

    def remove_v(v):
        nonlocal step
        is_in_cover[v] = 0; age[v] = step; loss[v] = 0; dscore[v] = 0
        for ei, nb in vertex_edges[v]:
            cc = edge_cov_cnt[ei]
            if cc == 1:
                uncov.add(ei); dscore[nb] += 1; dscore[v] += 1
            elif cc == 2:
                loss[nb] += 1
            edge_cov_cnt[ei] = cc - 1

    CHECK_EVERY = 2000

    while True:
        step += 1
        if step % CHECK_EVERY == 0:
            if time.time() >= slice_end:
                break

        if uncov:
            ei   = next(iter(uncov))
            u, v = clean[ei]

            du, dv = dscore[u], dscore[v]
            if du > dv:           add_cand = u
            elif dv > du:         add_cand = v
            elif age[u] < age[v]: add_cand = u
            else:                 add_cand = v

            rc = -1; bl = 10**9; ba = -1
            for nb in adj[add_cand]:
                if is_in_cover[nb] and nb != last_added:
                    l = loss[nb]; a = age[nb]
                    if l < bl or (l == bl and a > ba):
                        bl = l; ba = a; rc = nb
            if rc == -1:
                for nb in adj[add_cand]:
                    if is_in_cover[nb]:
                        l = loss[nb]; a = age[nb]
                        if l < bl or (l == bl and a > ba):
                            bl = l; ba = a; rc = nb

            add_v(add_cand); cur_size += 1; last_added = add_cand
            if rc != -1:
                remove_v(rc); cur_size -= 1

        else:
            if cur_size < best_size:
                best_size = cur_size
                best_cov  = set(v for v in range(1, n + 1) if is_in_cover[v])
                trace.append((time.time(), best_size))  

            to_rm = -1; bl = 10**9; ba = -1
            for v in range(1, n + 1):
                if is_in_cover[v]:
                    l = loss[v]; a = age[v]
                    if l < bl or (l == bl and a > ba):
                        bl = l; ba = a; to_rm = v
            if to_rm == -1:
                break
            remove_v(to_rm); cur_size -= 1; last_added = -1

    return best_cov, best_size, trace


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def solve(n, edges, cutoff, seed):
    """
    NuMVC + randomised-greedy restarts for Minimum Vertex Cover.

    Parameters
    ----------
    n       : number of vertices (1-indexed)
    edges   : list of (u, v) tuples
    cutoff  : wall-clock time limit in seconds
    seed    : random seed (fully reproducible)

    Returns
    -------
    best_sol : set of vertex indices forming the best cover found
    trace    : list of (elapsed_seconds, cover_size) at each improvement
    """
    rng   = random.Random(seed)
    start = time.time()
    end   = start + cutoff

    # ---- Build structures -------------------------------------------
    adj          = [[] for _ in range(n + 1)]
    vertex_edges = [[] for _ in range(n + 1)]
    clean        = []

    for u, v in edges:
        if u == v: continue
        i = len(clean); clean.append((u, v))
        vertex_edges[u].append((i, v)); vertex_edges[v].append((i, u))
        adj[u].append(v); adj[v].append(u)

    m = len(clean)
    if m == 0:
        return set(), [(0.0, 0)]

    best_sol  = None
    best_size = n + 1
    trace     = []

    # Time slice per restart: aim for ~20 restarts; floor at 0.05s
    TIME_SLICE = max(0.05, cutoff / 20.0)

    restart = 0
    while time.time() < end:
        k    = 1 if restart == 0 else 3
        # inside the restart loop:
        if restart == 0:
            init = set(approx.solve(n, clean))   # 2-approx for first restart
        else:
            init = _rand_greedy_cover(n, adj, rng, k=3)  # randomised greedy for diversity

        slice_end = min(time.time() + TIME_SLICE, end)

        run_cov, run_size, run_trace = _numvc(
            n, adj, vertex_edges, clean, m, init, slice_end, rng
        )

        for (abs_t, sz) in run_trace:
            elapsed = abs_t - start
            if sz < best_size:
                trace.append((elapsed, sz))

        if run_size < best_size:
            best_size = run_size
            best_sol  = run_cov

        restart += 1

    if best_sol is None:
        best_sol = set(range(1, n + 1))

    # Safety repair
    for u, v in clean:
        if u not in best_sol and v not in best_sol:
            best_sol.add(u)

    if not trace:
        trace = [(0.0, len(best_sol))]

    return best_sol, trace
