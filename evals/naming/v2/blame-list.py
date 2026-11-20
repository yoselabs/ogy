"""List the errors the blame pass reads: where both scorers gave K 0, or F 0, or the same item 0.

Usage: python3 -I blame-list.py SCORING_DIR RUNS_DIR
Prints, per error, `run fact what`, the scorers' notes, and the run's original row (not the rewritten copy).
"""

import re
import sys
from pathlib import Path

LINE = re.compile(r"^(\d+): ([01]) ([01]) \|(.*?)\| wrong links: \d+ \|?(.*)$")


def main(scoring, runs):
    arm_of = dict(reversed(line.split()) for line in (scoring / "map.txt").read_text().splitlines())
    marks = {}
    for path in sorted((scoring / "scores").glob("*.md")):
        run = None
        for line in path.read_text().splitlines():
            if line.startswith("## R"):
                run = line[3:].strip()
            elif run and (m := LINE.match(line)):
                items = dict(re.findall(r"(\d+[a-z])=([01])", m.group(4)))
                marks.setdefault((run, int(m.group(1))), []).append((m.group(2), m.group(3), items, m.group(5).strip()))
    for (run, fact), pair in sorted(marks.items(), key=lambda kv: (arm_of[kv[0][0]], kv[0][1])):
        if len(pair) != 2:
            continue
        errors = [w for w, i in (("K", 0), ("F", 1)) if pair[0][i] == pair[1][i] == "0"]
        errors += [k for k in pair[0][2] if pair[0][2][k] == "0" and pair[1][2].get(k) == "0"]
        if not errors:
            continue
        label = arm_of[run]
        rows = [r for r in (runs / f"{label}.md").read_text().splitlines() if re.match(rf"^\|\s*\[?{fact}\]?\s*\|", r)]
        print(f"{label} [{fact}] {' '.join(errors)}\n  s1: {pair[0][3]}\n  s2: {pair[1][3]}\n  row: {rows[0] if rows else '?'}\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
