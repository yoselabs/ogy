load common

# run.sh is copied beside fixtures; check-run.py is a fixture whose exit status the case sets.
setup() {
  hermetic
  v2=$BATS_TEST_TMPDIR/v2
  mkdir -p "$v2/inputs"
  cp "$ROOT/evals/naming/v2/run.sh" "$v2/"
  echo "the prompt" >"$v2/inputs/A.md"
  printf 'import os, sys\nprint("MALFORMED: bad table" if os.environ.get("CHECK_EXIT") else "fine")\nsys.exit(int(os.environ.get("CHECK_EXIT", "0")))\n' >"$v2/check-run.py"
  export STUB_ANSWER=1
  export STUB_JSON='{"is_error": false, "modelUsage": {"claude-test-1": {"outputTokens": 9}, "claude-aux-1": {"outputTokens": 1}}}'
  model=claude-test-1
}

@test "the wrong number of arguments is refused" {
  run bash "$v2/run.sh" tag "$model" medium A
  [ "$status" -eq 2 ]
  [[ "$output" == *usage* ]]
}

@test "an alias is not a model" {
  run bash "$v2/run.sh" tag opus medium A 1
  [ "$status" -eq 2 ]
  [ ! -s "$STUB_LOG" ]
}

@test "an arm without an input is refused before anything runs" {
  run bash "$v2/run.sh" tag "$model" medium Z 1
  [ "$status" -eq 2 ]
  [ ! -s "$STUB_LOG" ]
}

@test "a run that already exists is not overwritten" {
  bash "$v2/run.sh" tag "$model" medium A 1
  run bash "$v2/run.sh" tag "$model" medium A 1
  [ "$status" -eq 2 ]
  [[ "$output" == *"exists: tag/A-1"* ]]
}

@test "a good run keeps its answer and logs the model line" {
  run bash "$v2/run.sh" tag "$model" medium A 1
  [ "$status" -eq 0 ]
  [ "$(cat "$v2/runs/tag/A-1.md")" = "answer" ]
  [ -s "$v2/runs/tag/meta/A-1.json" ]
  grep -q "^tag/A-1.md main=claude-test-1 aux=claude-aux-1 asked=claude-test-1 effort=medium .* 9.9.9 (stub)$" "$v2/runs/models.txt"
  [ ! -e "$v2/runs/excluded.txt" ]
}

@test "the session is isolated: the safe flags and one tool" {
  bash "$v2/run.sh" tag "$model" medium A 1
  for flag in --safe-mode --restricted --disable-slash-commands --strict-mcp-config --no-session-persistence "--tools Write" "--model $model"; do
    grep -q -- "$flag" "$STUB_LOG"
  done
}

@test "the input goes to claude on standard input, not on the command line" {
  bash "$v2/run.sh" tag "$model" medium A 1
  ! grep -q "the prompt" "$STUB_LOG"
}

@test "a harness error excludes the run (3) and says why" {
  STUB_JSON='{"is_error": true, "subtype": "boom", "modelUsage": {"claude-test-1": {"outputTokens": 9}}}' run bash "$v2/run.sh" tag "$model" medium A 1
  [ "$status" -eq 3 ]
  [[ "$output" == *"EXCLUDED tag/A-1: harness error: boom"* ]]
  grep -q "^tag/A-1 harness error: boom" "$v2/runs/excluded.txt"
  [ -s "$v2/runs/tag/excluded/A-1.md" ]
  [ ! -e "$v2/runs/tag/A-1.md" ]
}

@test "a different main model excludes the run" {
  run bash "$v2/run.sh" tag claude-other-1 medium A 1
  [ "$status" -eq 3 ]
  [[ "$output" == *"is not claude-other-1"* ]]
}

@test "no answer file excludes the run" {
  STUB_ANSWER= run bash "$v2/run.sh" tag "$model" medium A 1
  [ "$status" -eq 3 ]
  [[ "$output" == *"no answer file"* ]]
}

@test "a malformed answer excludes the run" {
  CHECK_EXIT=1 run bash "$v2/run.sh" tag "$model" medium A 1
  [ "$status" -eq 3 ]
  [[ "$output" == *"malformed: bad table"* ]]
}

@test "an unreadable harness result excludes the run" {
  STUB_JSON='not json' run bash "$v2/run.sh" tag "$model" medium A 1
  [ "$status" -eq 3 ]
  [[ "$output" == *"harness result unreadable"* ]]
}
