#!/usr/bin/env bash
# Build one arm's input: prompt.md filled with that commit's `ogy kinds --map`, `ogy glossary` and the exercise.
# Usage: evals/naming/prepare.sh ARM COMMIT      (ARM is one letter: A, B or C)
# Writes evals/naming/inputs/ARM.md and appends "ARM <full commit>" to inputs/arms.txt.
# The commit is exported to a temporary folder; no checkout or worktree of this repository changes.
set -euo pipefail
arm=$1
commit=$2
here=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
sha=$(git -C "$repo" rev-parse --verify "$commit^{commit}")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$repo" archive "$sha" | tar -x -C "$tmp"
(cd "$tmp" && uv run ogy kinds --map >"$tmp/map.txt" && uv run ogy glossary >"$tmp/glossary.txt")
mkdir -p "$here/inputs"
python3 -I - "$here" "$tmp" "$arm" <<'PY'
import sys
from pathlib import Path

here, tmp, arm = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
text = (here / "prompt.md").read_text()
for mark, path in (("MAP", tmp / "map.txt"), ("GLOSSARY", tmp / "glossary.txt"), ("EXERCISE", here / "exercise.md")):
    text = text.replace("{{" + mark + "}}", path.read_text().rstrip())
(here / "inputs" / f"{arm}.md").write_text(text + "\n")
PY
echo "$arm $sha" >>"$here/inputs/arms.txt"
echo "wrote $here/inputs/$arm.md for $sha"
