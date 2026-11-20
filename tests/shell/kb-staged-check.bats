load common

setup() {
  hermetic
  repo=$BATS_TEST_TMPDIR/repo
  mkdir -p "$repo/docs/kb"
  echo one >"$repo/docs/kb/a.txt"
  commit_all "$repo"
  cd "$repo" || return
}

@test "a staged change outside the knowledge base is checked too: a code rename can break a code: source" {
  echo x >other.txt
  git add other.txt
  run sh "$ROOT/tools/kb-staged-check.sh"
  [ "$status" -eq 0 ]
  read -r _ _ _ rev verb <"$STUB_LOG"
  [ "$verb" = "check" ]
  [ "$(git show "$rev:other.txt")" = "x" ]
}

@test "a staged knowledge-base change is checked at a commit that holds the staged tree" {
  echo two >docs/kb/a.txt
  git add docs/kb/a.txt
  echo three >docs/kb/a.txt # unstaged on top: the check must not see it
  run sh "$ROOT/tools/kb-staged-check.sh"
  [ "$status" -eq 0 ]
  read -r _ _ _ rev verb <"$STUB_LOG"
  [ "$verb" = "check" ]
  [ "$(git show "$rev:docs/kb/a.txt")" = "two" ]
}

@test "the exit status of ogy check is the hook's" {
  echo two >docs/kb/a.txt
  git add docs/kb/a.txt
  STUB_JUST_EXIT=1 run sh "$ROOT/tools/kb-staged-check.sh"
  [ "$status" -eq 1 ]
}

@test "a first commit has no parent and is still checked" {
  rm -rf .git
  git init -q
  git add docs/kb/a.txt
  run sh "$ROOT/tools/kb-staged-check.sh"
  [ "$status" -eq 0 ]
  grep -q -- "--rev" "$STUB_LOG"
}
