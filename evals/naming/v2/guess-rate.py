"""How often the scorers told old names from new names: the test of the blinding.

Usage: python3 -I guess-rate.py SCORING_DIR      (e.g. evals/naming/v2/scoring/small)
Reads SCORING_DIR/map.txt ("<arm>-<n> R<id>") and every SCORING_DIR/guesses/*.md ("R<id> <label>"). Only the runs
of arms A and C0 are counted: they are the comparison that decides, and they differ in names alone. A guess is a
hit when it says `old` for an A run, or `new` or `new+lines` for a C0 run. A "?" counts as a miss. Blind guessing
gives 50%. Arm C is given beside it, never pooled in; arm B is scored in batches of its own and is not asked.
"""

import argparse
import sys
from pathlib import Path


def say(text: str) -> None:
    sys.stdout.write(text + "\n")


def main(scoring: Path) -> None:
    arm_of = {}
    for line in (scoring / "map.txt").read_text().splitlines():
        run, blind = line.split()
        arm_of[blind] = run.rsplit("-", 1)[0]
    counts = {"A": [0, 0, 0], "C0": [0, 0, 0], "C": [0, 0, 0]}  # guesses, hits, could not tell
    for path in sorted((scoring / "guesses").glob("*.md")):
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) != 2 or arm_of.get(parts[0]) not in counts:
                continue
            arm, guess = arm_of[parts[0]], parts[1]
            row = counts[arm]
            row[0] += 1
            row[1] += guess != "?" and (guess == "old") == (arm == "A")
            row[2] += guess == "?"
    total = counts["A"][0] + counts["C0"][0]
    if not total:
        say("no guesses on A or C0 runs read")
        return
    hits = counts["A"][1] + counts["C0"][1]
    unsure = counts["A"][2] + counts["C0"][2]
    say(f"old against new, arms A and C0: {hits} of {total} guesses, {hits / total:.0%} (blind guessing: 50%)")
    say(f"could not tell: {unsure} of {total}")
    for arm, (n, hit, _) in counts.items():
        if n:
            say(f"  arm {arm}: {hit} of {n} on the right side")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description="Print how often the scorers guessed each blinded run's arm.")
    cli.add_argument("scoring", type=Path, help="scoring folder holding map.txt and guesses/")
    main(cli.parse_args().scoring)
