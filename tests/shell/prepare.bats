load common

# The script is copied into a throwaway repository so that it builds there, never in this one.
setup() {
  hermetic
  repo=$BATS_TEST_TMPDIR/repo
  mkdir -p "$repo/evals/naming"
  cp "$ROOT/evals/naming/prepare.sh" "$repo/evals/naming/"
  printf 'MAP\n{{MAP}}\nGLOSSARY\n{{GLOSSARY}}\nEXERCISE\n{{EXERCISE}}\n' >"$repo/evals/naming/prompt.md"
  echo "THE-EXERCISE" >"$repo/evals/naming/exercise.md"
  commit_all "$repo"
  sha=$(git -C "$repo" rev-parse HEAD)
  script=$repo/evals/naming/prepare.sh
}

@test "builds the arm's input from the commit's map, glossary and the exercise" {
  run bash "$script" A HEAD
  [ "$status" -eq 0 ]
  input=$repo/evals/naming/inputs/A.md
  grep -q "^kinds, like and unlike:" "$input"
  grep -q "GLOSSARY-TEXT" "$input"
  grep -q "THE-EXERCISE" "$input"
  [ "$(cat "$repo/evals/naming/inputs/arms.txt")" = "A $sha" ]
}

@test "ogy runs in the exported commit, not in the working tree" {
  run bash "$script" A HEAD
  [ "$status" -eq 0 ]
  ! grep -q "$repo" "$STUB_LOG"
}

@test "a second arm is appended" {
  bash "$script" A HEAD
  bash "$script" B HEAD
  [ "$(wc -l <"$repo/evals/naming/inputs/arms.txt")" -eq 2 ]
}

@test "an unknown commit fails and writes nothing" {
  run bash "$script" A no-such-commit
  [ "$status" -ne 0 ]
  [ ! -e "$repo/evals/naming/inputs" ]
}

@test "missing arguments fail" {
  run bash "$script"
  [ "$status" -ne 0 ]
}

@test "a failing ogy stops the build" {
  STUB_UV_EXIT=1 run bash "$script" A HEAD
  [ "$status" -ne 0 ]
  [ ! -e "$repo/evals/naming/inputs/A.md" ]
}
