# Shared setup: stubs first on PATH, a hermetic git, a log the stubs write to.
ROOT=$(cd "$BATS_TEST_DIRNAME/../.." && pwd)

hermetic() {
  PATH="$BATS_TEST_DIRNAME/stubs:$PATH"
  export PATH
  export STUB_LOG="$BATS_TEST_TMPDIR/stub.log"
  : >"$STUB_LOG"
  unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
  export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com
}

# A repository in "$1" with everything already there committed.
commit_all() {
  git -C "$1" init -q
  git -C "$1" add -A
  git -C "$1" commit -q -m init
}
