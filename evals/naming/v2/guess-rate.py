"""How often the scorers guessed a run's arm: the test of the blinding.

Usage: python3 -I guess-rate.py SCORING_DIR      (e.g. evals/naming/v2/scoring/small)
Reads SCORING_DIR/map.txt ("<arm>-<n> R<id>") and every SCORING_DIR/guesses/*.md ("R<id> <label>"). Prints the
share of exact hits, the share of "?" and the share of hits on old against not old, each next to what blind
guessing would give. A "?" counts as a miss.
"""

import sys
from pathlib import Path

LABEL = {"A": "old", "C0": "new", "C": "new+lines", "B": "latest"}


def main(scoring: Path) -> None:
    arm_of = {}
    for line in (scoring / "map.txt").read_text().splitlines():
        run, blind = line.split()
        arm_of[blind] = LABEL[run.rsplit("-", 1)[0]]
    total = exact = unsure = coarse = 0
    for path in sorted((scoring / "guesses").glob("*.md")):
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) != 2 or parts[0] not in arm_of:
                continue
            truth, guess = arm_of[parts[0]], parts[1]
            total += 1
            unsure += guess == "?"
            exact += guess == truth
            coarse += guess != "?" and (guess == "old") == (truth == "old")
    if not total:
        print("no guesses read")
        return
    arms = len(set(arm_of.values()))
    old_share = sum(1 for label in arm_of.values() if label == "old") / len(arm_of)
    print(f"guesses: {total}; arms: {arms}")
    print(f"exact arm: {exact / total:.0%} (blind guessing: {1 / arms:.0%})")
    print(f"old against not old: {coarse / total:.0%} (always saying 'not old': {1 - old_share:.0%})")
    print(f"could not tell: {unsure / total:.0%}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
