#!/usr/bin/env python3
"""Run BnB on all test, small, and large instances.

Outputs (.sol, .trace) are written to:
  outputs/BnB/test/
  outputs/BnB/small/
  outputs/BnB/large/

Per-instance wall-clock time is printed. A summary table is printed at the end.
"""
import os
import subprocess
import sys
import time

BASE    = os.path.dirname(os.path.abspath(__file__))
DATA    = os.path.join(BASE, "data", "data")
OUT_ROOT = os.path.join(BASE, "outputs", "BnB")
MVC     = os.path.join(BASE, "mvc.py")

DATASETS = {
    "test":  ([f"test{i}"  for i in range(1, 6)],  10),
    "small": ([f"small{i}" for i in range(1, 19)], 20),
    "large": ([f"large{i}" for i in range(1, 13)], 300),
}

SEED = 42


def read_ref(path):
    try:
        with open(path) as f:
            return int(f.readline().strip())
    except Exception:
        return None


def main():
    results = []
    for dataset, (names, cutoff) in DATASETS.items():
        out_dir = os.path.join(OUT_ROOT, dataset)
        os.makedirs(out_dir, exist_ok=True)

        print(f"\n=== BnB | {dataset} | cutoff={cutoff}s ===")
        print(f"{'Instance':<12} {'Time(s)':>8} {'Cover':>8} {'Ref':>6} {'RelErr':>8}")
        print("-" * 48)

        for name in names:
            inst_path = os.path.join(DATA, dataset, name)
            ref = read_ref(inst_path + ".out")

            cmd = [
                sys.executable, MVC,
                "-inst", inst_path,
                "-alg",  "BnB",
                "-time", str(cutoff),
                "-seed", str(SEED),
            ]

            t0 = time.time()
            subprocess.run(cmd, cwd=out_dir, check=False)
            elapsed = time.time() - t0

            # Read cover size from the produced .sol file
            cutoff_str = str(int(cutoff)) if float(cutoff).is_integer() else str(cutoff)
            sol_file = os.path.join(out_dir, f"{name}_BnB_{cutoff_str}.sol")
            got = None
            if os.path.exists(sol_file):
                with open(sol_file) as f:
                    got = int(f.readline().strip())

            rel_err = f"{(got - ref) / ref:.4f}" if (got is not None and ref is not None) else "N/A"
            ref_str = str(ref) if ref is not None else "N/A"
            got_str = str(got) if got is not None else "N/A"
            print(f"{name:<12} {elapsed:>8.2f} {got_str:>8} {ref_str:>6} {rel_err:>8}")
            results.append((dataset, name, elapsed, got, ref))

    print("\n=== SUMMARY ===")
    print(f"{'Dataset':<8} {'Instance':<12} {'Time(s)':>8} {'Cover':>8} {'Ref':>6} {'RelErr':>8}")
    print("-" * 58)
    for dataset, name, elapsed, got, ref in results:
        rel_err = f"{(got - ref) / ref:.4f}" if (got is not None and ref is not None) else "N/A"
        ref_str = str(ref) if ref is not None else "N/A"
        got_str = str(got) if got is not None else "N/A"

        if isinstance(rel_err, (int, float)):
            rel_err_str = f"{rel_err:>8.2f}"
        else:
            rel_err_str = f"{rel_err:>8}"

        print(f"{dataset:<8} {name:<12} {elapsed:>8.2f} {got_str:>8} {ref_str:>6} {rel_err_str}")

if __name__ == "__main__":
    main()
