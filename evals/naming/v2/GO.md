# Go / no-go for the naming eval v2

No run that counts starts before every line is ticked. Write the date and the evidence after each tick.

## Arms

- [ ] Stage 3 has landed on main and arm B's commit is written in README.md.
- [ ] C0 and C are pinned: on a commit with a clean glossary (no "never an external", "guess and answers", "rule
      or value"), or on `1fb0e39` with the limit accepted in writing here.
- [ ] `prepare.sh` was run for A, C0 (`--no-like`), C and B; `inputs/arms.txt` has four lines with one and the same
      exercise hash, and C0 is the only `no-like` line.
- [ ] `python3 -I check-neutral.py` prints "facts are neutral" with B's input present; names now in a built map are
      out of `names-extra.txt`; `overlap-allowed.txt` is empty or every line has its reason.

## Key

- [ ] No `(verify)` is left in design.md: [10], [18], [24], [13], [20] and 15b are settled against `inputs/B.md`.
- [ ] D15 was read: whether [9], [10] or [19] must carry a proof in B is written in design.md (credit only).
- [ ] The last table of key.md gives B's words for [10], [18], [20], [24] and 15b; its neutral columns did not
      change.
- [ ] `vocab.tsv` holds B's true 1:1 renames and nothing else; a B run and an A run of the smoke test read alike
      after `blind.py`, apart from the words README step 5 lists.

## Runner

- [ ] One smoke run per model with `run.sh smoke-<tag> <full id> <effort> A 1`: exit 0, the answer file is in
      `runs/smoke-<tag>/`, `check-run.py` says ok, `runs/models.txt` has a line with `main=` read from `modelUsage`.
- [ ] The `main=` strings are written in README.md as the pinned ids; `asked=` equals `main=` in a second smoke run.
- [ ] The smoke answer shows no trace of this machine: no word of a CLAUDE.md, a skill or another arm.
- [ ] A forced failure (a wrong model id) ends with exit 3 and a line in `runs/excluded.txt`.
- [ ] `drive.sh smoke-<tag> <id> <effort> 1 "A C0"` runs two arms in order and writes `drive.log`.

## Scorers

- [ ] The scorer model id and effort are written in README.md.
- [ ] One smoke scorer session with `score.sh` over a smoke batch: `scores.md` follows the rubric's output,
      `guess.md` exists, and `scoring/<tag>/meta/*.files` lists only the batch, key.md, rubric.md, exercise.md.
- [ ] Isolation confirmed: the smoke scorer, asked to read `../` or this repository, cannot (`--restricted`).
- [ ] `--session-id` with `--resume` under `-p` works; if it does not, the guess is asked in a second fresh session
      given the scores, and score.sh says so.
- [ ] `guess-rate.py` runs on the smoke scoring folder.

## Paper

- [ ] README.md: status, freeze commit, three model ids, B's commit, 6 runs per arm, 51 items, both gates.
- [ ] The Agent-tool pilot is nowhere used as a number.
- [ ] v2/ is committed and that commit is the "frozen at" of README.md.
