# CSE6140 / CX4140 — Minimum Vertex Cover

## Requirements

- Python 3.8 or later (no external packages required)

## Code Structure

| File | Purpose |
|---|---|
| `mvc.py` | Entry point — parses arguments, calls the chosen algorithm, writes output files |
| `bnb.py` | Exact Branch-and-Bound algorithm |
| `approx.py` | Greedy 2-approximation algorithm |
| `ls1.py` | Local Search 1 — Simulated Annealing |
| `ls2.py` | Local Search 2 — NuMVC stochastic local search |
| `run_bnb.py` | Batch runner for BnB experiments |
| `run_approx.py` | Batch runner for Approx experiments |
| `run_ls1_seeds.py` | Batch runner for LS1 over multiple seeds |
| `run_ls2_seeds.py` | Batch runner for LS2 over multiple seeds |
| `plot_qrtd_sqd.py` | Generates QRTD / SQD / box plots from trace files |

## Running the Program

```
python3 mvc.py -inst <instance> -alg [BnB|Approx|LS1|LS2] -time <cutoff> -seed <seed>
```

| Argument | Description |
|---|---|
| `-inst` | Path to the instance **without** the `.in` extension |
| `-alg` | Algorithm: `BnB`, `Approx`, `LS1`, or `LS2` |
| `-time` | Time limit in seconds |
| `-seed` | Random seed (used by LS1 and LS2; required but ignored by BnB and Approx) |

### Examples

```bash
python3 mvc.py -inst data/test/test1 -alg BnB    -time 10  -seed 1
python3 mvc.py -inst data/small/small1 -alg Approx -time 600 -seed 1
python3 mvc.py -inst data/small/small1 -alg LS1   -time 600 -seed 42
python3 mvc.py -inst data/large/large1 -alg LS2   -time 600 -seed 7
```

## Output Files

Each run produces the following files in the **current working directory**.

### Solution file — `<instance>_<alg>_<cutoff>[_<seed>].sol`

```
12
1 4 7 9 10 11 15 18
```

Line 1: size of the vertex cover  
Line 2: space-separated vertex indices included in the cover  
The seed suffix is included only for randomized algorithms (LS1, LS2).

### Trace file — `<instance>_<alg>_<cutoff>[_<seed>].trace`

```
0.12 41
0.87 38
2.31 35
```

Each line: `<elapsed_seconds> <best_cover_size>` logged whenever a new best solution is found.  
Trace files are produced for BnB, LS1, and LS2. Approx does not produce a trace file.

## Input Format

The `.in` file is read automatically from the path given to `-inst`:

```
5 6       ← n (vertices) and m (edges)
1 2
1 3
2 3
2 4
3 5
4 5
```

Vertices are indexed 1 … n.
