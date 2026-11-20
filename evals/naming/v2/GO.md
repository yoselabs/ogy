# Go / no-go for the naming eval v2

No run that counts starts before every line is ticked. Write the date and the evidence after each tick.

## Arms

- [x] Stage 3 has landed on main and arm B's commit is written in README.md.
      2026-11-20: B is pinned on main `43f15fc` (stage 3, then the clean-up of old words 6cdf42e, 810c47d and the
      engine rename 43f15fc); README.md, top list and arms table. The builds at `810c47d` and `43f15fc` are the
      same bytes; against the first build at `511a27e` (same exercise text) B differs in four glossary lines only.
- [x] C0 and C are pinned on a commit with a clean glossary (no "never an external", "guess and answers", "rule
      or value").
      2026-11-20: `dd9293d`, branch `eval-stage1-clean` (on origin: `git branch -r --contains dd9293d`), which is
      `1fb0e39` plus two eval-only commits touching `docs/kb/product/shared/glossary.yml` and
      `docs/kb/software/shared/glossary.yml` only. Diff of the C0 and C inputs against their `1fb0e39` builds, on
      one exercise text: four lines each, the glossary lines of actor ("never a dependency"), decision ("options,
      proposal and answers"), read-back ("proposed") and proof ("a rule or quantity"); the map is unchanged. The
      earlier "limit accepted" is withdrawn; the limit paragraphs are out of README.md and design.md.
- [x] `prepare.sh` was run for A, C0 (`--no-like`), C and B; `inputs/arms.txt` has four lines with one and the same
      exercise hash, and C0 is the only `no-like` line.
      2026-11-20: A `46f0564`, C0 and C `dd9293d`, B `43f15fc`; one hash `270848a8...3f687e`; like/unlike blocks
      counted in the inputs: A 0, C0 0, C 2, B 2. The exercise changed twice on this day (next line), so every
      earlier input and every pilot run is on an older text.
- [x] `python3 -I check-neutral.py` prints "facts are neutral" with B's input present; names now in a built map are
      out of `names-extra.txt`; `overlap-allowed.txt` is empty or every line has its reason.
      2026-11-20: "arms read: A B C C0; names checked: 95; members only some arms print: 11; arm-only words: 120;
      facts are neutral". History: it failed with B on `http`, `library`, `belongs`, `point`, and "handles" leaned
      on `handler` ([3], [10], [16], [20], [23] reworded). Then "that message" in [13] was found by review: the
      checker had read the prompt line above the map as given text. It now reads map and glossary only and bans
      every enum member that only some arms print; that also caught `one` ([6], A's `type one`), `list` ([18]) and
      "table" ([11]); [6], [11], [13], [18] reworded. `names-extra.txt` holds no name. `overlap-allowed.txt` has
      one line, `one`, with its reason (the number word).

## Key

- [x] No `(verify)` is left in design.md: [10], [18], [24], [13], [20] and 15b are settled against `inputs/B.md`.
      2026-11-20: design.md, "Arm B: settled against inputs/B.md", one row per cell with the map line it rests on;
      still true at `43f15fc` (the map did not change after `511a27e`).
- [x] D15 was read: whether [9], [10] or [19] must carry a proof in B is written in design.md (credit only).
      2026-11-20: commit `27bea9f`. Setting, interface and workaround need a proof in B, but the printed map and
      glossary do not say so and the three facts name no test: no item, no credit, an invented proof changes no mark.
- [x] The last table of key.md gives B's words for [10], [18], [20], [24] and 15b; its neutral columns did not
      change.
      2026-11-20: rows 10, 13, 15, 16, 18, 20, 24 of "The words the runs use". Fixed there for every arm alike: a
      state or attribute of the hire or bike counts as that thing for 15b; bike facts that [10] shows are part of
      the home of [24]; an interface entry for geolib is the listed false friend of [16]. One neutral cell was put
      back to its first wording (15b, "from either end"): the note about the form used is no longer needed.
- [x] key.md says what a scorer does with B's own fields: `satisfies` on a behaviour kind, `accepts`, `form` and
      `realizes` on a dependency are not scored and never a wrong link; `satisfies` on a data kind is 0 for 15b.
      2026-11-20: the closing paragraph of key.md. `blind.py` no longer rewrites B's `satisfies` to `by`
      (vocab.tsv, fourth column `A,C0,C`); tested on synthetic A, C and B files.
- [x] B-only form traps are written down: `form: web` on [18] and `form: http` on [10] are required by B's map and
      are not in the 51; a missing or wrong `form` changes no mark; `form: library` for [16] is the false friend.
      2026-11-20: design.md, row `form` of the settled table; key.md rows 10 and 16.
- [x] B's absolute report and the B-only addendum (B1 to B6) are fixed before any run, with the rule that the
      addendum is never summed with the 51, the 45 or the names subset.
      2026-11-20: design.md ("B's absolute report", "B-only addendum", "What the eval does not measure in B"),
      blame.md ("Arm B, in the same pass"), README.md (Result; rule 10).
- [x] The B-structure pressures on the items are listed: 4b, 6b, 22c, 9b, 26a, 7a, 13b, 15b.
      2026-11-20: design.md, "Where arms differ by more than a name", the table.
- [x] `vocab.tsv` holds true 1:1 renames only, and none for B.
      2026-11-20: stages 2 and 3 bring no 1:1 rename (`interface` merges two kinds, the rest is new or narrowed).
      B is scored in batches of its own (`batches-own.txt`), so "a B run and an A run read alike" is no longer
      asked of the blinding.
- [ ] Smoke: after `blind.py`, an A run and a C0 run of the smoke test read alike apart from the words README
      step 5 lists; `batches.txt` holds no B run and `batches-own.txt` only B runs.

## Runner

- [ ] `runs/small/` and `runs/default/` hold no answer file from a pilot (today: `A-1.md`, `A-2.md`, `C0-1.md`,
      `C0-2.md` and two `old-text-*` files in `runs/small/`, seen in `git show --stat 4f9d3b5`): moved to `pilot/`.
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
- [ ] `guess-rate.py` runs on the smoke scoring folder and counts A and C0 runs only.
- [ ] `score.sh ... B1 1` scores a batch of arm B and asks no arm guess.

## Paper

- [ ] README.md: status, freeze commit, three model ids, B's commit, 6 runs per arm, 51 items, both gates.
      Done 2026-11-20: status, B's commit `43f15fc`, C0 and C on `dd9293d`, the exercise hash, 6 runs per arm, 51
      items (45 for B's second score), ceiling gate and floor gate ("more than 2 excluded runs of A or of C0").
      Open: the three model ids (from the smoke runs) and the freeze commit.
- [x] The Agent-tool pilot is nowhere used as a number.
      2026-11-20: figures removed from README.md (pilot paragraph) and design.md (names under test); README says
      no pilot number is used for any gate or comparison, on the ground that every pilot answered an older text.
      `scores-pilot-small-A.md` and `pilot/` stay as records and still hold their figures; `pilot/RESULT.md` now
      says "an earlier v2 text (not frozen)", 6 runs asked, Agent tool, no number used.
- [x] README.md, guess-prompt.md and design.md describe B as the whole final map (the merge and the stage 3
      structure), not as the merge alone.
      2026-11-20: README arms and comparison tables; guess-prompt.md no longer names B at all (B is not guessed).
- [ ] v2/ is committed and that commit is the "frozen at" of README.md.
