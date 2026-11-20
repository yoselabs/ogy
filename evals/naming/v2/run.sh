#!/usr/bin/env bash
# One run of one arm on one model through `claude -p`, isolated from this machine's Claude Code customisation.
# Usage: evals/naming/v2/run.sh TAG MODEL EFFORT ARM N      e.g. run.sh small claude-<full id> medium C0 3
# MODEL is a full model id, never an alias. Writes runs/TAG/ARM-N.md (the answer), runs/TAG/meta/ARM-N.json (the
# harness result) and one line in runs/models.txt. Exit 0: the run counts. Exit 3: the run is excluded (harness
# error, no answer file, malformed table, or a main model that is not MODEL); its answer, if any, goes to
# runs/TAG/excluded/ and one line goes to runs/excluded.txt. Exit 2: wrong call, nothing was run.
# Flags read from `claude --help` of 2.1.326 and confirmed by the smoke runs of GO.md (2026-11-20):
#   --safe-mode               no CLAUDE.md, skills, plugins, hooks, MCP servers, custom agents (auth stays normal;
#                             --bare would also do it but needs an API key, not a subscription login)
#   --restricted              no user, project or local settings; file tools confined to the working folder
#   --disable-slash-commands  no skills or commands
#   --strict-mcp-config       no MCP servers from any configuration
#   --tools Write             the one tool the prompt needs; no reading, no shell, no web
#   --permission-prompts none nothing waits for a person; --permission-mode acceptEdits lets the one file be written
#   --no-session-persistence  nothing kept for a later run to find
# The run starts in an empty temporary folder, so no project file is in reach.
set -uo pipefail
if [ $# -ne 5 ]; then
  echo "usage: run.sh TAG MODEL EFFORT ARM N" >&2
  exit 2
fi
tag=$1 model=$2 effort=$3 arm=$4 n=$5
case "$model" in claude-*-*) ;; *)
  echo "MODEL must be a full model id (claude-...), not an alias: $model" >&2
  exit 2
  ;;
esac
here=$(cd "$(dirname "$0")" && pwd)
out="$here/runs/$tag"
if [ ! -f "$here/inputs/$arm.md" ]; then
  echo "no input for arm $arm" >&2
  exit 2
fi
if [ -e "$out/$arm-$n.md" ] || [ -e "$out/meta/$arm-$n.json" ]; then
  echo "exists: $tag/$arm-$n" >&2
  exit 2
fi
mkdir -p "$out/meta" "$out/excluded"
work=$(mktemp -d)
{
  cat "$here/inputs/$arm.md"
  printf '\nOutput path: answer.md\n'
} | (cd "$work" && claude -p \
  --model "$model" --effort "$effort" --safe-mode --restricted --disable-slash-commands --strict-mcp-config \
  --no-session-persistence --tools Write --permission-mode acceptEdits --permission-prompts none \
  --output-format json) >"$out/meta/$arm-$n.json"
harness=$(claude --version)
python3 -I - "$here" "$tag" "$arm-$n" "$model" "$effort" "$work/answer.md" "$harness" <<'PY'
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

here, tag, run, asked, effort, answer, harness = sys.argv[1:8]
here, answer = Path(here), Path(answer)
out = here / "runs" / tag
main, aux, reason = "?", "-", ""
try:
    result = json.loads((out / "meta" / f"{run}.json").read_text())
    usage = result.get("modelUsage") or {}
    ranked = sorted(usage, key=lambda model: usage[model].get("outputTokens", 0), reverse=True)
    if ranked:
        main, aux = ranked[0], ",".join(ranked[1:]) or "-"
    if result.get("is_error"):
        reason = "harness error: " + " ".join(str(result.get("result") or result.get("subtype") or "is_error").split())[:80]
    elif not ranked:
        reason = "no modelUsage in the harness result"
    elif not main.startswith(asked):
        reason = f"main model {main} is not {asked}"
except (OSError, ValueError) as error:
    reason = f"harness result unreadable: {type(error).__name__}"
if not reason and not answer.exists():
    reason = "no answer file"
if not reason:
    check = subprocess.run([sys.executable, "-I", str(here / "check-run.py"), str(answer)], capture_output=True, text=True)
    if check.returncode:
        reason = "malformed: " + check.stdout.strip().split("MALFORMED: ", 1)[-1]
line = f"{tag}/{run}.md main={main} aux={aux} asked={asked} effort={effort} {date.today()} {harness}"
if reason:
    if answer.exists():
        shutil.copy(answer, out / "excluded" / f"{run}.md")
    with (here / "runs" / "excluded.txt").open("a") as log:
        log.write(f"{tag}/{run} {reason} | {line}\n")
    print(f"EXCLUDED {tag}/{run}: {reason}")
    sys.exit(3)
shutil.copy(answer, out / f"{run}.md")
with (here / "runs" / "models.txt").open("a") as log:
    log.write(line + "\n")
print("ok " + line)
PY
