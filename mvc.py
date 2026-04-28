#!/usr/bin/env python3
import argparse
import os
import time
from typing import List, Optional, Tuple


def read_graph(inst_path_no_ext: str):
    in_path = inst_path_no_ext + ".in"
    with open(in_path, "r") as f:
        header = f.readline().strip().split()
        if len(header) != 2:
            raise ValueError(f"Invalid header in {in_path!r}: expected 'n m'")
        n = int(header[0])
        m = int(header[1])
        edges = []
        for _ in range(m):
            line = f.readline()
            if not line:
                raise ValueError(f"Unexpected EOF in {in_path!r}")
            u_str, v_str = line.strip().split()
            edges.append((int(u_str), int(v_str)))
    return n, edges


def instance_base_name(inst_path_no_ext: str) -> str:
    return os.path.basename(inst_path_no_ext.rstrip("/"))


def _write_sol(path: str, cover: List[int]) -> None:
    with open(path, "w") as f:
        f.write(f"{len(cover)}\n")
        f.write(" ".join(str(v) for v in cover) + "\n")


def _write_trace(path: str, trace: List[Tuple[float, int]]) -> None:
    with open(path, "w") as f:
        for t, size in trace:
            f.write(f"{t:.2f} {size}\n")


def write_outputs(
    inst_name: str,
    alg: str,
    cutoff_str: str,
    seed: int,
    cover: List[int],
    trace: Optional[List[Tuple[float, int]]],
) -> None:
    randomized = alg in ("LS1", "LS2")
    if randomized:
        base = f"{inst_name}_{alg}_{cutoff_str}_{seed}"
    else:
        base = f"{inst_name}_{alg}_{cutoff_str}"

    _write_sol(base + ".sol", cover)
    if trace is not None:
        _write_trace(base + ".trace", trace)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-inst", required=True,
                        help="instance path without .in extension")
    parser.add_argument("-alg", required=True,
                        choices=["BnB", "Approx", "LS1", "LS2"])
    parser.add_argument("-time", required=True, type=float,
                        help="cutoff time in seconds")
    parser.add_argument("-seed", required=True, type=int,
                        help="random seed (used by randomized algorithms)")
    args = parser.parse_args()

    n, edges = read_graph(args.inst)
    inst_name = instance_base_name(args.inst)
    cutoff_str = (
        str(int(args.time)) if float(args.time).is_integer() else str(args.time)
    )

    trace = None

    if args.alg == "Approx":
        import approx
        cover = approx.solve(n, edges)
        # Approx is deterministic; no trace file required by the spec.

    elif args.alg == "LS1":
        import ls1
        cover, trace = ls1.solve(n, edges, args.time, args.seed)

    elif args.alg == "LS2":
        import ls2
        cover, trace = ls2.solve(n, edges, args.time, args.seed)

    elif args.alg == "BnB":
        import bnb
        import approx
        # Use the 2-approximation as the initial upper bound for BnB
        approx_cover = approx.solve(n, edges)
        cover, trace = bnb.solve(n, edges, args.time, initial_cover=approx_cover)

    else:
        raise ValueError(f"Unknown algorithm: {args.alg!r}")

    write_outputs(inst_name, args.alg, cutoff_str, args.seed, cover, trace)


if __name__ == "__main__":
    main()
