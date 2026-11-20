"""Blind the runs of one model for scoring: one vocabulary, new names, scorer batches.

Usage: python3 -I blind.py RUNS_DIR OUT_DIR SEED
Runs are files named <arm>-<n>.md (A-1.md, C0-3.md, B-5.md). Every run is rewritten with vocab.tsv (the same table
for every arm), copied to OUT_DIR/blind/R<id>.md, and listed in OUT_DIR/map.txt. Prints the batches: batch i holds
one run of every arm while runs last, so no run is dropped whatever the count per arm. Every batch goes to two
scorers who do not see each other's marks. Unlike evals/blind.py, which reads the arm from the first letter and
forms groups of two runs per arm (a fifth run falls out).
"""

import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def vocabulary() -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in (HERE / "vocab.tsv").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            old, new = line.split("\t")
            pairs[old] = new
            if not old.endswith("s"):
                pairs.setdefault(old + "s", new + "s")
    return pairs


def one_vocabulary(text: str, pairs: dict[str, str]) -> str:
    pattern = re.compile(r"\b(" + "|".join(sorted(pairs, key=len, reverse=True)) + r")\b", re.IGNORECASE)
    return pattern.sub(lambda m: pairs[m.group(1).lower()], text)


def main(runs_dir: Path, out_dir: Path, seed: int) -> None:
    rng = random.Random(seed)
    runs = sorted(p.stem for p in runs_dir.glob("*-*.md"))
    ids = rng.sample(range(100, 1000), len(runs))
    names = {run: f"R{i}" for run, i in zip(runs, ids, strict=True)}
    pairs = vocabulary()
    (out_dir / "blind").mkdir(parents=True, exist_ok=True)
    for run, name in names.items():
        text = (runs_dir / f"{run}.md").read_text()
        (out_dir / "blind" / f"{name}.md").write_text(one_vocabulary(text, pairs))
    (out_dir / "map.txt").write_text("".join(f"{run} {name}\n" for run, name in names.items()))
    pools: dict[str, list[str]] = {}
    for run in runs:
        pools.setdefault(run.rsplit("-", 1)[0], []).append(names[run])
    for pool in pools.values():
        rng.shuffle(pool)
    while any(pools.values()):
        batch = [pool.pop() for pool in pools.values() if pool]
        rng.shuffle(batch)
        print(" ".join(batch))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]))
