"""Blind the runs of one model for scoring: one vocabulary, new names, scorer batches.

Usage: python3 -I blind.py RUNS_DIR OUT_DIR SEED
Runs are files named <arm>-<n>.md (A-1.md, C0-3.md, B-5.md). Every run is rewritten with vocab.tsv (the same table
for every arm), copied to OUT_DIR/blind/R<id>.md, and listed in OUT_DIR/map.txt. Writes and prints the batches
(OUT_DIR/batches.txt, one per line): batch i holds one run of every arm while runs last, so no run is dropped
whatever the count per arm. Every batch goes to two scorers who do not see each other's marks (score.sh).
Unlike evals/blind.py, which reads the arm from the first letter and
forms groups of two runs per arm (a fifth run falls out).
"""

import argparse
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def vocabulary() -> tuple[dict[str, str], dict[str, str]]:
    """Kind names, rewritten wherever they stand, and field names, rewritten only where they stand as a field."""
    kinds: dict[str, str] = {}
    fields: dict[str, str] = {}
    for line in (HERE / "vocab.tsv").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            old, new, where = line.split("\t")
            if where == "field":
                fields[old] = new
                continue
            kinds[old] = new
            if not old.endswith("s"):
                kinds.setdefault(old + "s", new + "s")
    return kinds, fields


def one_vocabulary(text: str, kinds: dict[str, str], fields: dict[str, str]) -> str:
    names = "|".join(sorted(kinds, key=len, reverse=True))
    text = re.sub(rf"\b({names})\b", lambda m: kinds[m.group(1).lower()], text, flags=re.IGNORECASE)
    names = "|".join(sorted(fields, key=len, reverse=True))
    # a field: in a code span, after a dot, or before "->", "->>" or ":"
    text = re.sub(rf"`({names})`", lambda m: "`" + fields[m.group(1)] + "`", text)
    text = re.sub(rf"(?<=\.)({names})\b", lambda m: fields[m.group(1)], text)
    return re.sub(rf"\b({names})(?=\s*(->|:))", lambda m: fields[m.group(1)], text)


def main(runs_dir: Path, out_dir: Path, seed: int) -> None:
    rng = random.Random(seed)
    runs = sorted(p.stem for p in runs_dir.glob("*-*.md"))
    ids = rng.sample(range(100, 1000), len(runs))
    names = {run: f"R{i}" for run, i in zip(runs, ids, strict=True)}
    kinds, fields = vocabulary()
    (out_dir / "blind").mkdir(parents=True, exist_ok=True)
    for run, name in names.items():
        text = (runs_dir / f"{run}.md").read_text()
        (out_dir / "blind" / f"{name}.md").write_text(one_vocabulary(text, kinds, fields))
    (out_dir / "map.txt").write_text("".join(f"{run} {name}\n" for run, name in names.items()))
    pools: dict[str, list[str]] = {}
    for run in runs:
        pools.setdefault(run.rsplit("-", 1)[0], []).append(names[run])
    for pool in pools.values():
        rng.shuffle(pool)
    batches = []
    while any(pools.values()):
        batch = [pool.pop() for pool in pools.values() if pool]
        rng.shuffle(batch)
        batches.append(" ".join(batch))
    (out_dir / "batches.txt").write_text("".join(line + "\n" for line in batches))
    sys.stdout.write(("\n".join(batches)) + "\n")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description="Blind-rename the naming eval v2 runs and split them into scorer batches.")
    cli.add_argument("runs_dir", type=Path, help="folder of run files")
    cli.add_argument("out_dir", type=Path, help="folder the blinded runs and the map are written to")
    cli.add_argument("seed", type=int, help="seed of the shuffle")
    args = cli.parse_args()
    main(args.runs_dir, args.out_dir, args.seed)
