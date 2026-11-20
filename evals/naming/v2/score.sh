#!/usr/bin/env bash
# One scorer session over one batch of blind runs, in a folder that holds nothing else.
# Usage: evals/naming/v2/score.sh TAG MODEL EFFORT BATCH SCORER
#   BATCH is a line number of scoring/TAG/batches.txt (the pooled arms), or B<number> for a line of
#   scoring/TAG/batches-own.txt (arm B, scored apart); both files are written by blind.py. SCORER is 1 or 2.
# The scorer works in an empty temporary folder that gets only key.md, rubric.md, exercise.md and the batch's
# R<id>.md files, with the tools Read and Write confined to that folder (--restricted) and the same isolation
# flags as run.sh. After scoring a pooled batch, the same session (--resume) is asked to guess each run's arm;
# a batch of arm B is not asked (there is nothing to tell apart inside it).
# Writes scoring/TAG/scores/b<BATCH>-s<SCORER>.md, scoring/TAG/guesses/b<BATCH>-s<SCORER>.md and, in
# scoring/TAG/meta/, the two harness results and the list of files the scorer's folder held.
# Confirmed by the smoke runs of GO.md (2026-11-20): --session-id with --resume under -p works, and --restricted
# confines Read to the folder. The scorer may not list its folder, so the prompt names the batch's files.
set -uo pipefail
if [ $# -ne 5 ]; then
  echo "usage: score.sh TAG MODEL EFFORT BATCH SCORER" >&2
  exit 2
fi
tag=$1 model=$2 effort=$3 batch=$4 scorer=$5
case "$model" in claude-*-*) ;; *)
  echo "MODEL must be a full model id (claude-...), not an alias: $model" >&2
  exit 2
  ;;
esac
here=$(cd "$(dirname "$0")" && pwd)
dir="$here/scoring/$tag"
name="b$batch-s$scorer"
case "$batch" in
  B*)
    list="$dir/batches-own.txt"
    line=${batch#B}
    ;;
  *)
    list="$dir/batches.txt"
    line=$batch
    ;;
esac
ids=$(sed -n "${line}p" "$list")
if [ -z "$ids" ]; then
  echo "no batch $batch in $list" >&2
  exit 2
fi
if [ -e "$dir/scores/$name.md" ]; then
  echo "exists: $dir/scores/$name.md" >&2
  exit 2
fi
mkdir -p "$dir/scores" "$dir/guesses" "$dir/meta"
work=$(mktemp -d)
cp "$here/key.md" "$here/rubric.md" "$here/exercise.md" "$work/"
for id in $ids; do cp "$dir/blind/$id.md" "$work/"; done
ls "$work" >"$dir/meta/$name.files"
session=$(python3 -I -c 'import uuid; print(uuid.uuid4())')
flags=(--model "$model" --effort "$effort" --safe-mode --restricted --disable-slash-commands --strict-mcp-config
  --tools "Read,Write" --permission-mode acceptEdits --permission-prompts none --output-format json)
runs=$(for id in $ids; do printf '%s.md ' "$id"; done) # the scorer may not list its folder: name the runs
{
  cat "$here/scorer-prompt.md"
  printf '\nThe runs of this batch: %s\n' "$runs"
} | (cd "$work" && claude -p "${flags[@]}" \
  --session-id "$session") >"$dir/meta/$name.json"
if [ ! -s "$work/scores.md" ]; then
  echo "no scores.md from $name; see $dir/meta/$name.json" >&2
  exit 1
fi
cp "$work/scores.md" "$dir/scores/$name.md"
case "$batch" in B*)
  echo "scored batch $batch as scorer $scorer: $dir/scores/$name.md (no arm guess)"
  exit 0
  ;;
esac
(cd "$work" && claude -p "${flags[@]}" --resume "$session" <"$here/guess-prompt.md") >"$dir/meta/$name.guess.json"
if ! cmp -s "$work/scores.md" "$dir/scores/$name.md"; then echo "warning: scores.md changed during the guess; the first copy is kept" >&2; fi
if [ -s "$work/guess.md" ]; then cp "$work/guess.md" "$dir/guesses/$name.md"; else echo "no guess.md from $name" >&2; fi
echo "scored batch $batch as scorer $scorer: $dir/scores/$name.md"
