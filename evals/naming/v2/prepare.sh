#!/usr/bin/env bash
# Build one arm's input: prompt.md filled with that commit's `ogy kinds --map`, `ogy glossary` and the exercise.
# Usage: evals/naming/v2/prepare.sh ARM COMMIT [--no-like]      (ARM is A, C0, C or B)
# --no-like removes the "kinds, like and unlike:" block from the map and from the glossary (arm C0).
# Writes evals/naming/v2/inputs/ARM.md, replaces the ARM line of inputs/arms.txt ("ARM <full commit> <sha256 of
# exercise.md> <like or no-like>"), then runs check-neutral.py over every built input and fails when a fact uses a
# name of any arm or a content word that only some arms' map and glossary carry.
# The commit is exported to a temporary folder; no checkout or worktree of this repository changes.
set -euo pipefail
arm=$1
commit=$2
like=like
if [ "${3:-}" = "--no-like" ]; then like=no-like; fi
here=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
sha=$(git -C "$repo" rev-parse --verify "$commit^{commit}")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$repo" archive "$sha" | tar -x -C "$tmp"
(cd "$tmp" && export MISE_TRUSTED_CONFIG_PATHS="$tmp" && uv run ogy kinds --map >"$tmp/map.txt" && uv run ogy glossary >"$tmp/glossary.txt")
mkdir -p "$here/inputs"
python3 -I - "$here" "$tmp" "$arm" "$like" <<'PY'
import sys
from pathlib import Path

here, tmp, arm, like = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]


def without_like(text: str) -> str:
    kept, skipping = [], False
    for line in text.splitlines():
        if line.startswith("kinds, like and unlike:"):
            skipping = True
        elif skipping and not line.startswith(" "):
            skipping = False
        if not skipping:
            kept.append(line)
    return "\n".join(kept)


text = (here / "prompt.md").read_text()
for mark, path in (("MAP", tmp / "map.txt"), ("GLOSSARY", tmp / "glossary.txt"), ("EXERCISE", here / "exercise.md")):
    part = path.read_text()
    if like == "no-like" and mark != "EXERCISE":
        part = without_like(part)
    text = text.replace("{{" + mark + "}}", part.rstrip())
(here / "inputs" / f"{arm}.md").write_text(text + "\n")
PY
exercise=$(sha256sum "$here/exercise.md" | cut -d' ' -f1)
touch "$here/inputs/arms.txt"
grep -v "^$arm " "$here/inputs/arms.txt" >"$tmp/arms.txt" || true
echo "$arm $sha $exercise $like" >>"$tmp/arms.txt"
sort "$tmp/arms.txt" >"$here/inputs/arms.txt"
echo "wrote $here/inputs/$arm.md for $sha"
python3 -I "$here/check-neutral.py"
