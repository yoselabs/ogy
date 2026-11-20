load common

# drive.sh is copied beside a run.sh stub that logs each call and exits with STATUS_<arm>_<n> (default 0).
setup() {
  hermetic
  v2=$BATS_TEST_TMPDIR/v2
  mkdir -p "$v2/inputs"
  cp "$ROOT/evals/naming/v2/drive.sh" "$v2/"
  cat >"$v2/run.sh" <<'STUB'
#!/usr/bin/env bash
echo "$4-$5" >>"$STUB_LOG"
var=STATUS_${4}_${5}
exit "${!var:-0}"
STUB
  chmod +x "$v2/run.sh"
  for arm in A C0 C B; do echo prompt >"$v2/inputs/$arm.md"; done
}

calls() { tr '\n' ' ' <"$STUB_LOG"; }

@test "fewer than three arguments is refused" {
  run bash "$v2/drive.sh" tag model
  [ "$status" -eq 2 ]
  [[ "$output" == *usage* ]]
}

@test "an arm without an input is refused before any run" {
  run bash "$v2/drive.sh" tag model medium 1 "A Z"
  [ "$status" -eq 2 ]
  [ ! -s "$STUB_LOG" ]
}

@test "runs interleave the arms, one number at a time" {
  run bash "$v2/drive.sh" tag model medium 2
  [ "$status" -eq 0 ]
  [ "$(calls)" = "A-1 C0-1 C-1 B-1 A-2 C0-2 C-2 B-2 " ]
  grep -q "sitting ends" "$v2/runs/tag/drive.log"
}

@test "an excluded run is replaced by the next free number" {
  STATUS_C_1=3 run bash "$v2/drive.sh" tag model medium 1 "A C"
  [ "$status" -eq 0 ]
  [ "$(calls)" = "A-1 C-1 C-2 " ]
  grep -q "arm C: replacements used 1" "$v2/runs/tag/drive.log"
}

@test "after two replacements the arm stays short and the fact is logged" {
  STATUS_C_1=3 STATUS_C_2=3 STATUS_C_3=3 run bash "$v2/drive.sh" tag model medium 1 C
  [ "$status" -eq 0 ]
  [ "$(calls)" = "C-1 C-2 C-3 " ]
  grep -q "tag/C more than 2 exclusions: no replacement for C-3" "$v2/runs/excluded.txt"
}

@test "any other failure stops the sitting" {
  STATUS_C0_1=2 run bash "$v2/drive.sh" tag model medium 2
  [ "$status" -eq 1 ]
  [ "$(calls)" = "A-1 C0-1 " ]
  grep -q "STOP: run.sh failed with 2 on C0-1" "$v2/runs/tag/drive.log"
}

@test "the defaults are six runs of four arms" {
  run bash "$v2/drive.sh" tag model medium
  [ "$status" -eq 0 ]
  [ "$(wc -l <"$STUB_LOG")" -eq 24 ]
}
