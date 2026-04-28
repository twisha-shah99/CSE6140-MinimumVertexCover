# Minimum Vertex Cover (MVC)

## Problem
Given an undirected graph \(G = (V, E)\), a **vertex cover** is a set of vertices \(C \subseteq V\) such that every edge \((u, v) \in E\) has **at least one** endpoint in \(C\).

The **Minimum Vertex Cover** problem asks for a vertex cover with the **smallest** number of vertices.

## Algorithms
- **BnB (`bnb.py`)**: Exact **Branch-and-Bound** solver. Uses pruning + bounds to search for the optimal cover within a time cutoff (may time out on large instances).
- **Approx (`approx.py`)**: Deterministic **2-approximation**. Greedily picks an uncovered edge \((u,v)\), adds both endpoints, and removes covered edges. Fast and simple.
- **LS1 (`ls1.py`)**: Stochastic local search (simulated-annealing style). Starts from the Approx solution and tries random flips to improve within the cutoff.
- **LS2 (`ls2.py`)**: Stochastic local search (NuMVC-style + restarts). Uses heuristic add/remove moves and randomized restarts to find better covers within the cutoff.

## How to run (Approx)

### Run for a single instance
Run from the project root:

```bash
python3 mvc.py -inst data/data/test/test1 -alg Approx -time 10 -seed 42
```

> Note: Approx is deterministic, so `-seed` is ignored (it’s still required by the CLI).

### Run Approx across provided datasets
This script runs Approx on all `test/`, `small/`, and `large/` instances and saves solutions under `outputs/Approx/...`:

```bash
python3 run_approx.py
```

