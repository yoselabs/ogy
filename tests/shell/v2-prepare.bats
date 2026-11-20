load common

# The script is copied into a throwaway repository; check-neutral.py is a fixture whose exit status the case sets.
setup() {
  hermetic
  repo=$BATS_TEST_TMPDIR/repo
  v2=$repo/evals/naming/v2
  mkdir -p "$v2"
  cp "$ROOT/evals/naming/v2/prepare.sh" "$v2/"
  printf 'MAP\n{{MAP}}\nGLOSSARY\n{{GLOSSARY}}\nEXERCISE\n{{EXERCISE}}\n' >"$v2/prompt.md"
  echo "THE-EXERCISE" >"$v2/exercise.md"
  printf 'import os, sys\nprint("neutral checked")\nsys.exit(int(os.environ.get("NEUTRAL_EXIT", "0")))\n' >"$v2/check-neutral.py"
  commit_all "$repo"
  sha=$(git -C "$repo" rev-parse HEAD)
  script=$v2/prepare.sh
}

@test "the arm line carries the commit, the exercise hash and like" {
  run bash "$script" A HEAD
  [ "$status" -eq 0 ]
  hash=$(sha256sum "$v2/exercise.md" | cut -d' ' -f1)
  [ "$(cat "$v2/inputs/arms.txt")" = "A $sha $hash like" ]
  grep -q "^kinds, like and unlike:" "$v2/inputs/A.md"
  [[ "$output" == *"neutral checked"* ]]
}

@test "--no-like drops the like block from the map" {
  run bash "$script" C0 HEAD --no-like
  [ "$status" -eq 0 ]
  ! grep -q "like and unlike" "$v2/inputs/C0.md"
  ! grep -q "hidden line" "$v2/inputs/C0.md"
  grep -q "^tail" "$v2/inputs/C0.md"
  grep -q " no-like$" "$v2/inputs/arms.txt"
}

@test "building an arm again replaces its line and keeps the others, sorted" {
  bash "$script" C0 HEAD --no-like
  bash "$script" A HEAD
  bash "$script" C0 HEAD
  [ "$(wc -l <"$v2/inputs/arms.txt")" -eq 2 ]
  [ "$(cut -d' ' -f1 "$v2/inputs/arms.txt" | tr '\n' ' ')" = "A C0 " ]
  grep -q "^C0 .* like$" "$v2/inputs/arms.txt"
}

@test "a failing neutrality check fails the build" {
  NEUTRAL_EXIT=1 run bash "$script" A HEAD
  [ "$status" -eq 1 ]
}

@test "an unknown commit fails" {
  run bash "$script" A no-such-commit
  [ "$status" -ne 0 ]
}
