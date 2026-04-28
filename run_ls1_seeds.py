#!/usr/bin/env python3
"""
Run LS1 over 20 predefined seeds per instance.
For each seed, read the last line of the trace file (best solution + time-to-best).
Average time-to-best and cover size across seeds, compute relative error.
Report rounded to 2 decimal places. Save to results_ls1_seeds.txt.
"""
import os
import subprocess
import sys

BASE     = os.path.dirname(os.path.abspath(__file__))
DATA     = os.path.join(BASE, "data", "data")
OUT_ROOT = os.path.join(BASE, "final_outputs", "LS1_seeds")
MVC      = os.path.join(BASE, "mvc.py")

SEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
         11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
# SEEDS = [42]

DATASETS = {
    "test":  ([f"test{i}"  for i in range(1, 6)],   2),
    "small": ([f"small{i}" for i in range(1, 19)],  2),
    "large": ([f"large{i}" for i in range(1, 13)], 25),
}


def read_ref(path):
    try:
        with open(path) as f:
            return int(f.readline().strip())
    except Exception:
        return None


def read_last_trace(path):
    """Return (time_to_best, cover_size) from last non-empty trace line."""
    try:
        with open(path) as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        if not lines:
            return None
        parts = lines[-1].split()
        return float(parts[0]), int(parts[1])
    except Exception:
        return None


def fmt(val, decimals=2):
    if isinstance(val, (int, float)):
        return f"{val:.{decimals}f}"
    return str(val)


def main():
    report_lines = []
    all_results  = []

    for dataset, (names, cutoff) in DATASETS.items():
        out_dir    = os.path.join(OUT_ROOT, dataset)
        os.makedirs(out_dir, exist_ok=True)
        cutoff_str = str(int(cutoff)) if float(cutoff).is_integer() else str(cutoff)

        header = (f"\n=== LS1 | {dataset} | cutoff={cutoff}s "
                  f"| seeds {SEEDS[0]}..{SEEDS[-1]} ({len(SEEDS)} runs) ===")
        col_hdr = (f"{'Instance':<12} {'AvgTimeToBest(s)':>18} "
                   f"{'AvgCover':>10} {'Ref':>6} {'RelErr':>8}")
        sep = "-" * 58

        print(header);   report_lines.append(header)
        print(col_hdr);  report_lines.append(col_hdr)
        print(sep);      report_lines.append(sep)

        for name in names:
            inst_path = os.path.join(DATA, dataset, name)
            ref       = read_ref(inst_path + ".out")

            times   = []
            covers  = []

            for seed in SEEDS:
                cmd = [
                    sys.executable, MVC,
                    "-inst", inst_path,
                    "-alg",  "LS1",
                    "-time", str(cutoff),
                    "-seed", str(seed),
                ]
                subprocess.run(cmd, cwd=out_dir, check=False,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                trace_path = os.path.join(out_dir,
                                          f"{name}_LS1_{cutoff_str}_{seed}.trace")
                result = read_last_trace(trace_path)
                if result is not None:
                    t, c = result
                    times.append(t)
                    covers.append(c)

            if times:
                avg_time  = round(sum(times)  / len(times),  2)
                avg_cover = round(sum(covers) / len(covers), 2)
                rel_err   = round((avg_cover - ref) / ref,   2) if ref else None
            else:
                avg_time = avg_cover = rel_err = None

            row = (f"{name:<12} {fmt(avg_time):>18} "
                   f"{fmt(avg_cover):>10} "
                   f"{str(ref) if ref is not None else 'N/A':>6} "
                   f"{fmt(rel_err) if rel_err is not None else 'N/A':>8}")
            print(row);  report_lines.append(row)
            all_results.append((dataset, name, avg_time, avg_cover, ref))

    # ---- Summary ----
    sum_header = "\n=== SUMMARY ==="
    sum_col    = (f"{'Dataset':<8} {'Instance':<12} {'AvgTimeToBest(s)':>18} "
                  f"{'AvgCover':>10} {'Ref':>6} {'RelErr':>8}")
    sum_sep    = "-" * 66

    print(sum_header);  report_lines.append(sum_header)
    print(sum_col);     report_lines.append(sum_col)
    print(sum_sep);     report_lines.append(sum_sep)

    for dataset, name, avg_time, avg_cover, ref in all_results:
        rel_err = (round((avg_cover - ref) / ref, 2)
                   if (avg_cover is not None and ref) else None)
        row = (f"{dataset:<8} {name:<12} {fmt(avg_time):>18} "
               f"{fmt(avg_cover):>10} "
               f"{str(ref) if ref is not None else 'N/A':>6} "
               f"{fmt(rel_err) if rel_err is not None else 'N/A':>8}")
        print(row);  report_lines.append(row)

    report_path = os.path.join(BASE, "results_ls1_seeds.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
