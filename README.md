# CSE6140 / CX4140 — Minimum Vertex Cover

## Requirements

- Python 3.8 or later (no external packages required)

## Code Structure

| File | Purpose |
|---|---|
| `mvc.py` | Entry point — parses CLI arguments, calls the chosen algorithm, writes output files |
| `bnb.py` | Exact Branch-and-Bound algorithm |
| `approx.py` | Greedy 2-approximation algorithm |
| `ls1.py` | Local Search 1 — Simulated Annealing |
| `ls2.py` | Local Search 2 — NuMVC stochastic local search with randomised-greedy restarts |
| `run_bnb.py` | Batch runner: runs BnB on all test/small/large instances |
| `run_approx.py` | Batch runner: runs Approx on all test/small/large instances |
| `run_ls1_seeds.py` | Batch runner: runs LS1 over 20 seeds per instance, prints and saves averaged results |
| `run_ls2_seeds.py` | Batch runner: runs LS2 over 20 seeds per instance, prints and saves averaged results |
| `plot_qrtd_sqd.py` | Generates QRTD, SQD, and box plots from trace files |

---

## Running a Single Instance (via `mvc.py`)

```
python3 mvc.py -inst <instance> -alg [BnB|Approx|LS1|LS2] -time <cutoff> -seed <seed>
```

| Argument | Description |
|---|---|
| `-inst` | Path to the instance **without** the `.in` extension |
| `-alg` | Algorithm: `BnB`, `Approx`, `LS1`, or `LS2` |
| `-time` | Time limit in seconds |
| `-seed` | Random seed (used by LS1 and LS2; required but ignored by BnB and Approx) |

Output files are written to the **current working directory**.

### Examples

```bash
python3 mvc.py -inst data/data/test/test1   -alg BnB    -time 10  -seed 1
python3 mvc.py -inst data/data/small/small1 -alg Approx -time 600 -seed 1
python3 mvc.py -inst data/data/small/small1 -alg LS1    -time 600 -seed 42
python3 mvc.py -inst data/data/large/large1 -alg LS2    -time 600 -seed 7
```

---

## Batch Runners

These scripts run the corresponding algorithm across **all** instances automatically
and print a per-instance summary table. Run them from the project root directory.

### BnB — all instances

```bash
python3 run_bnb.py
```

- Cutoffs: **10 s** (test), **20 s** (small), **300 s** (large)
- Seed: 42 (fixed; BnB is deterministic so the seed has no effect)
- Prints per-instance Time, Cover size, Reference, and RelErr
- Summary table printed at the end and saved to `output_bnb.txt`

### Approx — all instances

```bash
python3 run_approx.py
```

- Cutoff: **10 s** (all datasets; Approx always finishes in under 2 s)
- Approx is deterministic — seed is ignored
- Prints per-instance Time, Cover size, Reference, and RelErr
- Summary saved to `output_approx.txt`

### LS1 — 20 seeds per instance

```bash
python3 run_ls1_seeds.py
```

- Seeds: 1 through 20
- Cutoffs: **2 s** (test/small), **25 s** (large)
- For each instance, averages time-to-best and cover size across all 20 seeds
- Prints averaged AvgTimeToBest, AvgCover, Reference, and RelErr per instance
- Full summary saved to `results_ls1_seeds.txt`

### LS2 — 20 seeds per instance

```bash
python3 run_ls2_seeds.py
```

- Seeds: 1 through 20
- Cutoffs: **2 s** (test/small), **25 s** (large)
- Same format as LS1 runner
- Full summary saved to `results_ls2_seeds.txt`

### Generating plots

```bash
python3 plot_qrtd_sqd.py
```

Reads trace files from `final_outputs/` and writes all plots to `plots/`.

---

## Output Organisation

```
CSE6140-MinimumVertexCover/
│
├── outputs/                        # BnB and Approx single-run outputs
│   ├── BnB/
│   │   ├── test/                   # test1..test5  .sol + .trace
│   │   ├── small/                  # small1..small18  .sol + .trace
│   │   └── large/                  # large1..large12  .sol + .trace
│   └── Approx/
│       ├── test/                   # test1..test5  .sol  (no trace)
│       ├── small/                  # small1..small18  .sol
│       └── large/                  # large1..large12  .sol
│
├── final_outputs/                  # LS1 and LS2 multi-seed outputs
│   ├── LS1_seeds/
│   │   ├── test/                   # <inst>_LS1_<cutoff>_<seed>.sol/.trace  (seeds 1-20)
│   │   ├── small/
│   │   └── large/
│   └── LS2_seeds/
│       ├── test/
│       ├── small/
│       └── large/
│
├── results_ls1_seeds.txt           # Averaged LS1 summary table (all instances)
├── results_ls2_seeds.txt           # Averaged LS2 summary table (all instances)
├── output_bnb.txt                  # BnB per-instance results table
├── output_approx.txt               # Approx per-instance results table
│
└── plots/                          # All generated figures
    ├── qrtd_LS1_large1.png
    ├── qrtd_LS1_large12.png
    ├── qrtd_LS2_large1.png
    ├── qrtd_LS2_large12.png
    ├── sqd_LS1_large1.png
    ├── sqd_LS1_large12.png
    ├── sqd_LS2_large1.png
    ├── sqd_LS2_large12.png
    ├── boxplot_time.png
    └── boxplot_quality.png
```

### Output file formats

**Solution file** — `<instance>_<alg>_<cutoff>[_<seed>].sol`
```
12
1 4 7 9 10 11 15 18
```
Line 1: cover size. Line 2: space-separated vertex indices.
The `_<seed>` suffix is included only for randomised algorithms (LS1, LS2).

**Trace file** — `<instance>_<alg>_<cutoff>[_<seed>].trace`
```
0.12 41
0.87 38
2.31 35
```
Each line: `<elapsed_seconds> <best_cover_size>` logged on every improvement.
Produced by BnB, LS1, and LS2. Approx does not produce a trace file.

---

## Input Format

```
5 6       ← n (vertices)  m (edges)
1 2
1 3
2 3
2 4
3 5
4 5
```

The `.in` file is read automatically from the path given to `-inst`.
Vertices are indexed 1 … n.
