#!/usr/bin/env python3
import argparse
import os
import time

# TODO: Generate comments!
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
            u = int(u_str)
            v = int(v_str)
            if u == v:
                edges.append((u, v))
            else:
                edges.append((u, v))
    return n, edges


def instance_base_name(inst_path_no_ext: str) -> str:
    return os.path.basename(inst_path_no_ext.rstrip("/"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-inst", required=True, help="instance path without .in extension (e.g., data/test/test1)")
    parser.add_argument("-alg", required=True, choices=["BnB", "Approx", "LS1", "LS2"])
    parser.add_argument("-time", required=True, type=float, help="cutoff time in seconds")
    parser.add_argument("-seed", required=True, type=int, help="random seed (used by randomized algs)")
    args = parser.parse_args()

    n, edges = read_graph(args.inst)
    inst_name = instance_base_name(args.inst)
    cutoff_str = str(int(args.time)) if float(args.time).is_integer() else str(args.time)

    start = time.time()

    if args.alg == "BnB":
        raise NotImplementedError("Not implemented yet.")
    if args.alg == "Approx":
        raise NotImplementedError("Not implemented yet.")
    if args.alg == "LS1":
        raise NotImplementedError("Not implemented yet.")
    if args.alg == "LS2":
        raise NotImplementedError("Not implemented yet.")

    raise ValueError(f"Unknown algorithm: {args.alg!r}")


if __name__ == "__main__":
    main()

