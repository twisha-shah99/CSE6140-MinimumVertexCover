import os
import subprocess
import sys


def main() -> int:
    time = 10
    seed = 1

    folders = ["data/test", "data/small", "data/large"]

    for folder in folders:
        if not os.path.isdir(folder):
            continue

        for filename in sorted(os.listdir(folder)):
            if not filename.endswith(".in"):
                continue

            inst = os.path.join(folder, filename[:-3])  # strip ".in"
            cmd = [
                sys.executable,
                "mvc.py",
                "-inst",
                inst,
                "-alg",
                "Approx",
                "-time",
                str(time),
                "-seed",
                str(seed),
            ]
            print(" ".join(cmd))
            subprocess.run(cmd, check=True)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

