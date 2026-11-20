#!/usr/bin/env bash
# One run of one arm on one model, isolated from this machine's Claude Code customisation.
# Usage: evals/naming/v2/run.sh TAG MODEL EFFORT ARM N      e.g. run.sh small <full model id> medium C0 3
# Writes runs/TAG/ARM-N.md (the answer), runs/TAG/meta/ARM-N.json (the harness result) and one line in
# runs/models.txt. NOT EXECUTED YET: the flags were read from `claude --help` of 2.1.326; the shape of the json
# result (`modelUsage`, keyed by model id, each with `outputTokens`) is to be confirmed on the first pilot run.
#   --safe-mode               no CLAUDE.md, skills, plugins, hooks, MCP servers, custom agents (auth stays normal;
#                             --bare would also do it but needs an API key, not a subscription login)
#   --disable-slash-commands  no skills or commands
#   --strict-mcp-config       no MCP servers from any configuration
#   --tools Write             the one tool the prompt needs; no reading, no shell, no web
#   --no-session-persistence  nothing kept for a later run to find
# The run starts in an empty temporary folder, so no project file is in reach.
set -euo pipefail
tag=$1 model=$2 effort=$3 arm=$4 n=$5
here=$(cd "$(dirname "$0")" && pwd)
out="$here/runs/$tag"
mkdir -p "$out/meta"
if [ -e "$out/$arm-$n.md" ]; then echo "exists: $out/$arm-$n.md" >&2; exit 1; fi
work=$(mktemp -d)
{ cat "$here/inputs/$arm.md"; printf '\nOutput path: answer.md\n'; } | (cd "$work" && claude -p \
  --model "$model" --effort "$effort" --safe-mode --disable-slash-commands --strict-mcp-config \
  --no-session-persistence --tools Write --permission-mode acceptEdits --output-format json) >"$out/meta/$arm-$n.json"
cp "$work/answer.md" "$out/$arm-$n.md"
python3 -I - "$out/meta/$arm-$n.json" "$tag/$arm-$n.md" "$model" "$effort" "$(claude --version)" >>"$here/runs/models.txt" <<'PY'
import json
import sys
from datetime import date

path, run, asked, effort, harness = sys.argv[1:6]
usage = json.load(open(path))["modelUsage"]
ranked = sorted(usage, key=lambda model: usage[model].get("outputTokens", 0), reverse=True)
aux = ",".join(ranked[1:]) or "-"
print(f"{run} main={ranked[0]} aux={aux} asked={asked} effort={effort} {date.today()} {harness}")
PY
tail -1 "$here/runs/models.txt"
python3 -I "$here/check-run.py" "$out/$arm-$n.md"
