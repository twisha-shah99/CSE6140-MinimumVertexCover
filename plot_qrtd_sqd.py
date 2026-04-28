#!/usr/bin/env python3
"""
QRTD and SQD plots for large1 and large12 for LS1 and LS2 Algorithms

Trace file locations
------------------------------
LS1:  final_outputs/LS1_seeds/large/large1_LS1_25_<seed>.trace   (cutoff=25s)
LS2:  final_outputs/LS2_seeds/large/large1_LS2_25_<seed>.trace  (cutoff=25s)

Each trace file has lines:  elapsed_time  cover_size

QRTD (Qualified Run-Time Distribution):
  x-axis : run-time
  y-axis : P(finding cover with rel_err ≤ q within time t)
  curves : one per quality threshold q

SQD (Solution Quality Distribution):
  x-axis : relative error [%]
  y-axis : P(finding cover with rel_err ≤ q within time cutoff t)
  curves : one per time cutoff t
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")       
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))

# Values obtained based on out files

REF = {
    "large1":  3303,
    "large12": 1438,
}

#For seed 1 to 20
SEEDS = list(range(1, 21))

ALG_CFG = {
    "LS1": {
        "trace_dir": os.path.join(BASE, "final_outputs", "LS1_seeds", "large"),
        "cutoff":    25,
        "pattern":   "{inst}_LS1_25_{seed}.trace",
    },
    "LS2": {
        "trace_dir": os.path.join(BASE, "final_outputs", "LS2_seeds", "large"),
        "cutoff":    25,
        "pattern":   "{inst}_LS2_25_{seed}.trace",
    },
}

# Quality thresholds for QRTD curves (relative error)
Q_THRESHOLDS = [
    (0.000, "opt (0%)"),
    (0.005, "0.5%"),
    (0.010, "1%"),
    (0.020, "2%"),
    (0.050, "5%"),
]

# Time cutoffs for SQD curves
TC_LS1 = [1, 3, 5, 10, 15, 20, 25]    # seconds (≤ 25s cutoff)
TC_LS2 = [1, 3, 5, 10, 15, 20, 25]    # seconds (≤ 25s cutoff)


def read_trace(path):
    """Return list of (elapsed_time, cover_size) from a trace file."""
    rows = []
    try:
        with open(path) as fh:
            for line in fh:
                parts = line.strip().split()
                if len(parts) >= 2:
                    rows.append((float(parts[0]), int(parts[1])))
    except FileNotFoundError:
        pass
    return rows


def load_all_traces(alg, inst):
    """Return {seed: [(t, c), ...]} for every seed that has a file."""
    cfg    = ALG_CFG[alg]
    traces = {}
    for seed in SEEDS:
        fname = cfg["pattern"].format(inst=inst, seed=seed)
        path  = os.path.join(cfg["trace_dir"], fname)
        data  = read_trace(path)
        if data:
            traces[seed] = data
    return traces


def best_cover_at(trace, t_limit):
    """Minimum cover size achieved at or before t_limit."""
    best = None
    for t, c in trace:
        if t > t_limit:
            break
        best = c if best is None else min(best, c)
    return best


#QRTD Calculation
def compute_qrtd(traces, ref, time_pts, q_values):
    """
    For each quality threshold q and each time point t:
      P = fraction of seeds that achieved rel_err ≤ q within time t.

    Returns {q: np.array of probabilities aligned with time_pts}.
    """
    n = len(traces)
    if n == 0:
        return {q: np.zeros(len(time_pts)) for q in q_values}

    result = {}
    for q in q_values:
        target = ref * (1.0 + q)      
        probs  = []
        for t in time_pts:
            count = sum(
                1 for trace in traces.values()
                if (b := best_cover_at(trace, t)) is not None and b <= target
            )
            probs.append(count / n)
        result[q] = np.array(probs)
    return result


# SQD Calculation

def compute_sqd(traces, ref, q_pts, time_cutoffs):
    """
    For each time cutoff tc and each quality point q:
      P = fraction of seeds whose best cover at tc gives rel_err ≤ q.

    Returns {tc: np.array of probabilities aligned with q_pts}.
    """
    n = len(traces)
    if n == 0:
        return {tc: np.zeros(len(q_pts)) for tc in time_cutoffs}

    result = {}
    for tc in time_cutoffs:
        bests = [best_cover_at(tr, tc) for tr in traces.values()]
        bests = [b for b in bests if b is not None]
        probs = []
        for q in q_pts:
            target = ref * (1.0 + q)
            probs.append(sum(1 for b in bests if b <= target) / n)
        result[tc] = np.array(probs)
    return result


#Plotting functions

def draw_qrtd(ax, qrtd, time_pts, q_labels, title, n_runs):
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(q_labels)))
    for (q, label), color in zip(q_labels, colors):
        if q in qrtd and qrtd[q].max() > 0:
            ax.plot(time_pts, qrtd[q], label=label, color=color,
                    linewidth=2, marker="None")
    ax.set_xlim(time_pts[0], time_pts[-1])
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Run-time [seconds]", fontsize=9)
    ax.set_ylabel("P(solve)", fontsize=9)
    ax.set_title(f"{title}\n({n_runs} seeds)", fontsize=9, fontweight="bold")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(True, alpha=0.3, which="both", linestyle="--")


def draw_sqd(ax, sqd, q_pts, tc_labels, title, n_runs):
    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(tc_labels)))
    for (tc, label), color in zip(tc_labels, colors):
        if tc in sqd and sqd[tc].max() > 0:
            ax.plot(q_pts * 100, sqd[tc], label=label, color=color,
                    linewidth=2, marker="None")
    ax.set_xlim(0, q_pts[-1] * 100)
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Relative solution quality [%]", fontsize=9)
    ax.set_ylabel("P(solve)", fontsize=9)
    ax.set_title(f"{title}\n({n_runs} seeds)", fontsize=9, fontweight="bold")
    ax.legend(fontsize=7, loc="lower right")
    ax.grid(True, alpha=0.3, linestyle="--")

def collect_box_data(alg, inst):
    """Return (rel_errors, times_to_best) lists across all seeds at cutoff."""
    cfg    = ALG_CFG[alg]
    cutoff = cfg["cutoff"]
    ref    = REF[inst]
    traces = load_all_traces(alg, inst)

    rel_errors     = []
    times_to_best  = []
    for trace in traces.values():
        best = best_cover_at(trace, cutoff)
        if best is not None:
            rel_errors.append((best - ref) / ref * 100)
        # time at which best was first achieved
        final_best = None
        t_best     = None
        for t, c in trace:
            if t > cutoff:
                break
            if final_best is None or c < final_best:
                final_best = c
                t_best     = t
        if t_best is not None:
            times_to_best.append(t_best)
    return rel_errors, times_to_best


def draw_boxplots(instances, algs):
    """Produce two figures: one for relative error, one for time-to-best."""
    labels = [f"{alg}\n{inst}" for inst in instances for alg in algs]

    err_data  = []
    time_data = []
    for inst in instances:
        for alg in algs:
            rel_err, ttb = collect_box_data(alg, inst)
            err_data.append(rel_err)
            time_data.append(ttb)

    for data, ylabel, fname, title in [
        (err_data,  "Relative error [%]",   "boxplot_quality.png",
         "Solution Quality Box Plots — LS1 & LS2 on large instances"),
        (time_data, "Time to best [seconds]", "boxplot_time.png",
         "Time-to-Best Box Plots — LS1 & LS2 on large instances"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 6))
        bp = ax.boxplot(
            data,
            labels=labels,
            patch_artist=True,
            medianprops=dict(color="black", linewidth=2),
            whiskerprops=dict(linewidth=1.5),
            capprops=dict(linewidth=1.5),
            flierprops=dict(marker="o", markersize=4, alpha=0.6),
            notch=False,
        )
        colors = ["#4C72B0", "#DD8452", "#4C72B0", "#DD8452"]  # LS1 blue, LS2 orange
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(True, axis="y", alpha=0.35, linestyle="--")
        ax.tick_params(axis="x", labelsize=9)
        for i, d in enumerate(data, start=1):
            ax.text(i, ax.get_ylim()[0], f"n={len(d)}",
                    ha="center", va="bottom", fontsize=7, color="gray")

        fig.tight_layout()
        out = os.path.join(BASE, fname)
        fig.savefig(out, dpi=150, bbox_inches="tight")
        print(f"Saved → {out}")
        plt.close(fig)


#Main entry point
def main():
    instances = ["large1", "large12"]
    algs      = ["LS1", "LS2"]

    fig_q, axes_q = plt.subplots(2, 2, figsize=(14, 10))
    fig_s, axes_s = plt.subplots(2, 2, figsize=(14, 10))
    fig_q.suptitle("QRTD Plots — LS1 & LS2 on large instances",
                   fontsize=13, fontweight="bold")
    fig_s.suptitle("SQD Plots — LS1 & LS2 on large instances",
                   fontsize=13, fontweight="bold")

    for col, alg in enumerate(algs):
        cfg    = ALG_CFG[alg]
        cutoff = cfg["cutoff"]

        # Time axis for QRTD
        t_min    = 0.001
        time_pts = np.logspace(np.log10(t_min), np.log10(cutoff), 400)

        # SQD time cutoffs for this algorithm
        raw_tcs  = TC_LS1 if alg == "LS1" else TC_LS2
        tc_labels = [(t, f"{t}s") for t in raw_tcs if t <= cutoff]

        # Quality axis for SQD (0 – 4%)
        q_pts = np.linspace(0, 0.04, 500)

        for row, inst in enumerate(instances):
            ref    = REF[inst]
            traces = load_all_traces(alg, inst)
            n      = len(traces)
            print(f"{alg:4s} | {inst:7s} | {n} trace files found "
                  f"(seeds: {sorted(traces.keys())})")

            title = f"{alg} — {inst}  (ref = {ref})"

            # ---- QRTD ----
            qrtd = compute_qrtd(
                traces, ref, time_pts,
                [q for q, _ in Q_THRESHOLDS]
            )
            draw_qrtd(axes_q[row, col], qrtd, time_pts,
                      Q_THRESHOLDS, title, n)

            # ---- SQD ----
            sqd = compute_sqd(
                traces, ref, q_pts,
                [t for t, _ in tc_labels]
            )
            draw_sqd(axes_s[row, col], sqd, q_pts,
                     tc_labels, title, n)

    for fig, fname in [(fig_q, "qrtd_plots.png"), (fig_s, "sqd_plots.png")]:
        fig.tight_layout()
        out = os.path.join(BASE, fname)
        fig.savefig(out, dpi=150, bbox_inches="tight")
        print(f"Saved → {out}")

    # Save each subplot individually
    subplot_cfg = [
        (fig_q, axes_q, "qrtd"),
        (fig_s, axes_s, "sqd"),
    ]
    alg_names  = ["LS1", "LS2"]
    inst_names = ["large1", "large12"]
    for fig, axes, kind in subplot_cfg:
        for row, inst in enumerate(inst_names):
            for col, alg in enumerate(alg_names):
                ext   = fig.get_axes()[0].get_figure()  
                fname = f"{kind}_{alg}_{inst}.png"
                out   = os.path.join(BASE, fname)
                bbox = axes[row, col].get_tightbbox(
                    fig.canvas.get_renderer()
                ).transformed(fig.dpi_scale_trans.inverted())
                fig.savefig(out, dpi=150, bbox_inches=bbox)
                print(f"Saved → {out}")

    #Box Plots
    draw_boxplots(instances, algs)


if __name__ == "__main__":
    main()
