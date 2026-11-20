"""Say whether run outputs are well formed, before anyone scores them.

Usage: python3 -I check-run.py RUN.md [RUN.md ...]
A run is well formed when it holds one Markdown table whose data rows carry the facts [1] to [28], each exactly
once, in four cells (fact, kind, links, why), with a kind cell that is not empty. Text around the table is
tolerated and reported. Prints one line per file and exits 1 when any file is malformed.
"""

import re
import sys
from pathlib import Path

FACTS = 28


def problems(text: str) -> list[str]:
    seen: dict[int, int] = {}
    found: list[str] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        number = re.fullmatch(r"\[?(\d+)\]?", cells[0])
        if not number:
            continue
        n = int(number.group(1))
        seen[n] = seen.get(n, 0) + 1
        if len(cells) != 4:
            found.append(f"row {n} has {len(cells)} cells")
        elif not cells[1]:
            found.append(f"row {n} has no kind")
    missing = [n for n in range(1, FACTS + 1) if n not in seen]
    if missing:
        found.append("missing rows " + ", ".join(map(str, missing)))
    found += [f"row {n} appears {k} times" for n, k in sorted(seen.items()) if k > 1]
    found += [f"row {n} is no fact" for n in sorted(seen) if not 1 <= n <= FACTS]
    return found


def main(paths: list[str]) -> int:
    bad = 0
    for name in paths:
        text = Path(name).read_text()
        found = problems(text)
        extra = sum(1 for line in text.splitlines() if line.strip() and not line.lstrip().startswith("|"))
        note = f" ({extra} lines outside the table)" if extra else ""
        sys.stdout.write((f"{name}: {'MALFORMED: ' + '; '.join(found) if found else 'ok'}{note}") + "\n")
        bad += bool(found)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
