load common

# score.sh is copied beside the files it hands a scorer; the claude stub writes scores.md / guess.md on request.
setup() {
  hermetic
  v2=$BATS_TEST_TMPDIR/v2
  dir=$v2/scoring/tag
  mkdir -p "$dir/blind"
  cp "$ROOT/evals/naming/v2/score.sh" "$v2/"
  for f in key rubric exercise scorer-prompt guess-prompt; do echo "$f" >"$v2/$f.md"; done
  printf 'R1 R2\nR3\n' >"$dir/batches.txt"
  for id in R1 R2 R3; do echo "$id" >"$dir/blind/$id.md"; done
  echo secret >"$v2/other.md"
  export STUB_SCORES=1 STUB_GUESS=1
  model=claude-test-1
}

@test "the wrong number of arguments is refused" {
  run bash "$v2/score.sh" tag "$model" medium 1
  [ "$status" -eq 2 ]
  [[ "$output" == *usage* ]]
}

@test "an alias is not a model" {
  run bash "$v2/score.sh" tag sonnet medium 1 1
  [ "$status" -eq 2 ]
}

@test "a batch that does not exist is refused" {
  run bash "$v2/score.sh" tag "$model" medium 9 1
  [ "$status" -eq 2 ]
  [[ "$output" == *"no batch 9"* ]]
}

@test "scores are not overwritten" {
  bash "$v2/score.sh" tag "$model" medium 1 1
  run bash "$v2/score.sh" tag "$model" medium 1 1
  [ "$status" -eq 2 ]
  [[ "$output" == *exists* ]]
}

@test "the scorer's folder holds the key, rubric, exercise and the batch's runs, nothing else" {
  run bash "$v2/score.sh" tag "$model" medium 1 1
  [ "$status" -eq 0 ]
  [ "$(LC_ALL=C sort "$dir/meta/b1-s1.files" | tr "\n" " ")" = "R1.md R2.md exercise.md key.md rubric.md " ]
}

@test "scores and guesses are kept, and the guess resumes the same session" {
  run bash "$v2/score.sh" tag "$model" medium 2 2
  [ "$status" -eq 0 ]
  [ "$(cat "$dir/scores/b2-s2.md")" = "scores" ]
  [ "$(cat "$dir/guesses/b2-s2.md")" = "guess" ]
  session=$(sed -n 's/.*--session-id \([^ ]*\).*/\1/p' "$STUB_LOG")
  [ -n "$session" ]
  grep -q -- "--resume $session" "$STUB_LOG"
}

@test "no scores.md is a failure and no guess is asked for" {
  STUB_SCORES= run bash "$v2/score.sh" tag "$model" medium 1 1
  [ "$status" -eq 1 ]
  [[ "$output" == *"no scores.md"* ]]
  ! grep -q -- "--resume" "$STUB_LOG"
}

@test "a missing guess is reported, the scores stay" {
  STUB_GUESS= run bash "$v2/score.sh" tag "$model" medium 1 1
  [ "$status" -eq 0 ]
  [[ "$output" == *"no guess.md"* ]]
  [ -s "$dir/scores/b1-s1.md" ]
}
