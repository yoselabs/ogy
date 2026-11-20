#!/usr/bin/env bash
# One sitting: every run of one model, arms interleaved (A, C0, C, B, A, C0, ...), exclusions replaced.
# Usage: evals/naming/v2/drive.sh TAG MODEL EFFORT [RUNS] [ARMS]      default RUNS=6, ARMS="A C0 C B"
# One model per sitting: call it once per tag, on one day. A run that run.sh excludes is replaced at once by a
# fresh run with the next free number, at most 2 replacements per arm; after that the arm is left short and the
# fact is logged (README: more than 2 excluded runs of A or C0 put the model under the floor gate). Logged in
# runs/TAG/drive.log; exclusions are in runs/excluded.txt (written by run.sh).
set -uo pipefail
if [ $# -lt 3 ]; then echo "usage: drive.sh TAG MODEL EFFORT [RUNS] [ARMS]" >&2; exit 2; fi
tag=$1 model=$2 effort=$3 runs=${4:-6} arms=${5:-"A C0 C B"}
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$here/runs/$tag"
log="$here/runs/$tag/drive.log"
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$log"; }
declare -A replaced
for arm in $arms; do
  replaced[$arm]=0
  if [ ! -f "$here/inputs/$arm.md" ]; then echo "no input for arm $arm" >&2; exit 2; fi
done
say "sitting starts: tag=$tag model=$model effort=$effort runs=$runs arms=$arms"
for n in $(seq 1 "$runs"); do
  for arm in $arms; do
    number=$n
    while :; do
      say "run $arm-$number"
      "$here/run.sh" "$tag" "$model" "$effort" "$arm" "$number" >>"$log" 2>&1
      status=$?
      if [ $status -eq 0 ]; then break; fi
      if [ $status -ne 3 ]; then say "STOP: run.sh failed with $status on $arm-$number"; exit 1; fi
      if [ "${replaced[$arm]}" -ge 2 ]; then
        say "arm $arm: $arm-$number excluded and both replacements are used; the arm stays short"
        echo "$tag/$arm more than 2 exclusions: no replacement for $arm-$number" >>"$here/runs/excluded.txt"
        break
      fi
      replaced[$arm]=$((replaced[$arm] + 1))
      number=$((runs + replaced[$arm]))
      say "arm $arm: excluded, replacement ${replaced[$arm]} of 2 is $arm-$number"
    done
  done
done
say "sitting ends"
for arm in $arms; do say "arm $arm: replacements used ${replaced[$arm]}"; done
