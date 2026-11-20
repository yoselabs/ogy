"""Blind-rename eval runs and split them into scorer groups (OGY eval protocol, step 5).

Usage: python3 -I blind.py RUNS_DIR OUT_DIR SEED
Runs are files named <arm><n>.md (A1.md, B3.md, ...). Writes OUT_DIR/blind/R<id>.md and OUT_DIR/map.txt, and prints
the groups: each holds two runs of every arm, shuffled. The first run of each group goes to the agreement scorer.
"""

import argparse
import random
import shutil
import sys
from pathlib import Path


def main(runs_dir: Path, out_dir: Path, seed: int) -> None:
    rng = random.Random(seed)
    runs = sorted(p.stem for p in runs_dir.glob("*.md"))
    ids = rng.sample(range(100, 1000), len(runs))
    names = {run: f"R{i}" for run, i in zip(runs, ids, strict=True)}
    (out_dir / "blind").mkdir(parents=True, exist_ok=True)
    for run, name in names.items():
        shutil.copy(runs_dir / f"{run}.md", out_dir / "blind" / f"{name}.md")
    (out_dir / "map.txt").write_text("".join(f"{run} {name}\n" for run, name in names.items()))
    arms = sorted({run[0] for run in runs})
    pools = {arm: [names[r] for r in runs if r[0] == arm] for arm in arms}
    for pool in pools.values():
        rng.shuffle(pool)
    groups = []
    while all(len(pool) >= 2 for pool in pools.values()):
        group = [pools[arm].pop() for arm in arms for _ in range(2)]
        rng.shuffle(group)
        groups.append(group)
    for group in groups:
        sys.stdout.write((" ".join(group)) + "\n")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description="Blind-rename eval runs and split them into scorer groups.")
    cli.add_argument("runs_dir", type=Path, help="folder of run files")
    cli.add_argument("out_dir", type=Path, help="folder the blinded runs and the map are written to")
    cli.add_argument("seed", type=int, help="seed of the shuffle")
    args = cli.parse_args()
    main(args.runs_dir, args.out_dir, args.seed)
