# Naming eval v2: old names against mainstream names, made sensitive

Status: **designed, not run; all four arms built; no-go until [GO.md](GO.md) is all ticked** (open there: the
runner and scorer smoke tests, the model ids, the freeze commit) (2026-11-20, bead ogy-yy9.75). Replaces
[v1](../README.md), whose arm A sat at a ceiling: kind 16.3 of 17, links 13 of 17, 0.67 misplacements, no error
blamed on a name. v1's files and scores stay as they are; v2 results are not comparable with them.

Fill before the freeze:

- frozen at: `<commit of v2/>`
- `small` model id: `<full id, as the modelUsage key of its smoke run>`, effort `<level>`
- `default` model id: `<full id, as the modelUsage key of its smoke run>`, effort `<level>`
- scorer model id: `<full id>`, effort `<level>`
- arm B commit: `43f15fc` (main after stage 3 and the clean-up of old words; full hash in `inputs/arms.txt`),
  pinned 2026-11-20
- arms C0 and C commit: `dd9293d` (branch `eval-stage1-clean`, on origin), pinned 2026-11-20
- exercise sha256: `270848a8f93aec8b1442c0f8193082215c0577f67b40149c149d36190e3f687e` (in `inputs/arms.txt`, four times)

## Files

| file | who reads it |
|---|---|
| [exercise.md](exercise.md), [prompt.md](prompt.md), `inputs/` | the runs |
| [key.md](key.md), [rubric.md](rubric.md) | the scorers, with the exercise and the blind runs; nothing else |
| [design.md](design.md), [blame.md](blame.md) | the coordinator only: names per arm, expected pulls, the unblinded pass |
| `prepare.sh`, `run.sh`, `drive.sh`, `check-run.py` | build an arm, run once, run a sitting, test an output |
| `blind.py`, `vocab.tsv`, `score.sh`, `scorer-prompt.md`, `guess-prompt.md`, `guess-rate.py` | blind, score, test the blinding |
| [GO.md](GO.md) | the checklist that must be all ticked before the first run that counts |
| `check-neutral.py`, `names-extra.txt`, `overlap-allowed.txt` | keep the facts free of every arm's words |

## What changed from v1

| | v1 | v2 |
|---|---|---|
| facts | 17, one per kind | 28: 1 anchor and 27 target facts, each on a confusion a rename aims at, look-alikes placed apart |
| primary metric | misplacements of 17 | link items hit, of 51: each required link or filled field scored 0 or 1 |
| arms | before, after | before, names only (C0), names with like/unlike lines (C), after (B) |
| runner | the Agent tool, model not recorded | `claude -p` through `run.sh` for runs and scorers, full model ids, the main id recorded per run |
| blinding | kind names show the arm | A, C0 and C rewritten into one vocabulary and scored pooled; B, which cannot be rewritten, scored in batches of its own; scorer key without arms; name blame in a later open pass; scorers' old-against-new guesses on A and C0 reported |
| scoring | one scorer, one re-scored run per arm | every run scored twice, in a folder holding only the batch, the key, the rubric and the exercise; scorers guess the arm afterwards |
| neutrality | by eye | `check-neutral.py`: no kind or field name of any arm, no enum member and no content word that only some arms print |
| reading rule | ranges barely overlap | numbers fixed below, with a ceiling gate |

The look-alike groups: a decided number ([4], [17], [22]) against a fact kept per thing ([5], [27]) against an
amount with currency ([14]); a closed list ([6]) against free remarks ([12]) against lifecycle stages ([2]); the
code that takes the payment ([7]) against the HTTP call ([10]) against a library function ([16]); a knob that
holds a URL ([9]) against a knob that falls back to a decided number ([22]); what we call ([3], [16]) against what
calls us ([13], [20]); a must-hold statement ([15], [25]) against what the owner puts above all ([8]) against the
point of the product ([23]) against an ability of it ([26]); an open question ([11]) against the AI's own pick
([21]) against the owner's pick ([28]); a vendor's surprise with what we do about it ([19]) against our own wish
([25]); a screen used twice ([18]) against what an API call sends back ([24]).

## Question

Do mainstream names let a fresh agent write a product's facts with the right links and in the right kinds more
often than the old names?

Primary metric: **link items hit per run, of 51** (facts [2] to [28], without 15b). Also reported: the names
subset of [design.md](design.md) (19 marks), misplacements of 27, false friends, wrong links; apart: fact [12],
item 15b, the four absence items (9b, 11b, 21c, 25b), the anchor 1a.

## Arms

| arm | commit | built with | what it is |
|---|---|---|---|
| A | tag `eval-before` = `46f0564` | `prepare.sh A eval-before` | main before the renames |
| C0 | `dd9293d` | `prepare.sh C0 dd9293d --no-like` | stage 1 names; the two "kinds, like and unlike" blocks removed |
| C | `dd9293d` | `prepare.sh C dd9293d` | stage 1 names with the like/unlike lines |
| B | `43f15fc` (main) | `prepare.sh B 43f15fc` | the final map: stage 1, the merge of `view` and `command` into `interface` (stage 2), and the structure of stage 3 (`rule.constrains`, `satisfies` on behaviour kinds only, `dependency.realizes -> actor`, `interface.allows`, `term.names`, the "nothing links to" rules) |

`dd9293d` is `1fb0e39` (the stage 1 merge) plus two eval-only commits that copy from main the cleaned glossary
texts of actor, decision, read-back and proof and the term id `proposal`; nothing of stage 2 or 3. Measured on
one and the same exercise text, the C0 and C inputs differ from their `1fb0e39` builds in those four glossary
lines and nothing else, and B at `43f15fc` differs from B at `511a27e` in the same four lines. The glossary of
every arm now speaks that arm's own words ("never an external" in A, "never a dependency" in C0, C and B).

| comparison | what it isolates | weight |
|---|---|---|
| **A against C0** | the names alone | decides |
| C0 against C | the like/unlike lines | describes |
| C against B, A against B | the `interface` merge together with the stage 3 structure (they cannot be told apart here); the whole change | describes; given on the 51 and on the 45 common-homes items of [design.md](design.md) |

## Models

Every arm runs on two models, because a strong model reads past a poor name (v1) and a small one leans on it:

| tag | model | why |
|---|---|---|
| `small` | the smallest current Claude model the harness offers (the Haiku tier) | most likely to follow a name and not the field list: the sensitive reading |
| `default` | the model v1's arm A ran on, the harness default | the model that does the real work: the reading that decides adoption |

Runs: **6 per arm per model** (48 with B). One model per sitting: `drive.sh TAG MODEL EFFORT` runs all arms of
that model on one day, interleaved (A, C0, C, B, A, ...), and replaces excluded runs. The `default` model is
likely to sit at the ceiling as in v1; then the `small` model carries the verdict alone, and the result says so.

Every run and every scorer session goes through `claude -p` (`run.sh`, `score.sh`), never through the Agent
tool: a subagent inherits the session's context, this repository's CLAUDE.md included, which names kinds of one
arm. `run.sh` starts in an empty temporary folder with `--safe-mode --restricted --disable-slash-commands
--strict-mcp-config --no-session-persistence --tools Write`, so that no CLAUDE.md, memory, skill, plugin, hook,
settings file or MCP server of this machine reaches the run, and the one tool is the one the prompt needs.
(`--bare` isolates as well but accepts only an API key.) The flags were read from the help of Claude Code
2.1.326; no script here has been executed against a model: the smoke runs of GO.md confirm them.

Models are passed as full ids; `run.sh` refuses an alias. Recording: `run.sh` checks `is_error` in the harness
result, keeps the result in `runs/<tag>/meta/` and adds one line to `runs/models.txt`:
`<tag>/<run file> main=<id> aux=<ids or -> asked=<id> effort=<level> <date> <harness version>`. `modelUsage` is
a record keyed by model id and may hold more than one: `main` is the key with the most output tokens, the others
are auxiliary (a title call, a background helper) and are listed, not grounds to discard. The id pinned above is
the `main` key of the smoke run, and that string is what later runs are asked for.

## What a run gets

One message: [prompt.md](prompt.md) (the same bytes as v1's) filled with the output of `uv run ogy kinds --map` and
`uv run ogy glossary` at the arm's commit, then [exercise.md](exercise.md), then the line `Output path: answer.md`.
The prompt and the exercise are the same bytes in every arm and for every model: only the map and the glossary
differ. `inputs/arms.txt` holds, per arm, the commit, the sha256 of the exercise it was built from and whether the
like/unlike blocks are in; the hashes must be equal.

## How to run

0. Tick every line of [GO.md](GO.md).
1. Freeze. Smoke and pilot runs go to tags of their own (`runs/smoke-...`, `pilot/`), never enter a result, and
   the exercise and the key may change after them. Then fill the list at the top, commit `v2/` and write the
   commit there. After the freeze the exercise, the rubric, the neutral columns of the key, the item sets (51, 45,
   the names subset, the B-only addendum B1 to B6, the contents of B's absolute report) and the reading rule do not change.
2. Build the inputs with the four commands of the arms table. Each call rebuilds `inputs/<arm>.md`, updates
   `inputs/arms.txt` and runs `check-neutral.py`; a fact that uses a name of any arm, or a content word that only
   some arms print, fails the build (it did when B was first built; the facts were reworded before the freeze).
   A failure after the freeze changes the exercise: that is a new freeze and every arm is rerun.
3. Run: `drive.sh small <id> <effort>`, and on its own day `drive.sh default <id> <effort>`.
4. Exclude, before anyone scores; `run.sh` does it. A run is excluded when the harness reports an error
   (`is_error`), when no answer file was written, when `check-run.py` calls the answer malformed (no table, a fact
   row missing or twice, a row without four cells or without a kind), or when its main model id is not the one
   asked for. Nothing else excludes a run: never its content. An excluded run stays on disk
   (`runs/<tag>/excluded/`, `meta/`), gets a line in `runs/excluded.txt` and is replaced by `drive.sh` with a fresh
   run of the next number, at most 2 replacements per arm per model. Exclusions are reported per arm.
5. Blind, per model: `python3 -I evals/naming/v2/blind.py evals/naming/v2/runs/small evals/naming/v2/scoring/small
   <seed>`, the same for `default`. It rewrites every run with `vocab.tsv` so that the renamed kinds and fields
   read alike (to arm A's words), and writes two lists. `batches.txt`: A, C0 and C pooled, 6 batches of one run
   per arm. `batches-own.txt`: B alone, 2 batches of 3. B is never pooled with the others: its `interface` cannot
   be rewritten away and would mark its runs, and its `satisfies` is a different field and is left as written.
   Not blinded away inside the pooled batches: `many`, `heard`, `realizes` on a capability, the types `one` and
   `list` (arm A only). The guess rate of step 7 is read against this list.
6. Score: `score.sh TAG <scorer id> <effort> BATCH 1` and `... BATCH 2` for every batch (`1` to `6`, then `B1`,
   `B2`): two sessions per batch that never see each other. A scorer's folder holds only its batch, key.md,
   rubric.md and exercise.md (`scoring/<tag>/meta/*.files` lists what it held); never `map.txt`, `inputs/`,
   `runs/`, design.md, blame.md or this file. A run's marks are the mean of its two scorers. Scorer disagreement
   is reported two ways: the mean absolute difference in link items hit, of 51, and the mean count of link items
   on which the two differ, per run. An item on which they differ in more than a third of the runs is named, and
   the result is given with and without it.
7. Test the blinding: after scoring a pooled batch, the scorer session is asked to guess each run's version
   (`guess-prompt.md`: old, new, new with lines). `python3 -I guess-rate.py scoring/<tag>` counts **only the runs
   of A and C0**, old against new, next to the 50% of blind guessing; C is given beside it, B is not asked. Report
   it. If scorers are on the right side in more than three quarters of their guesses on A and C0, say that the
   scoring of the deciding comparison was not blind in effect.
8. Unblind with each `map.txt`, do the [blame pass](blame.md) with its B part (the absolute report and the
   addendum), fill the tables below, add a ledger row and the metric rows.

## Result (to fill)

One table per model. Means with per-run ranges.

| arm | link items (of 51) | common homes (of 45) | names subset (of 19) | misplacements (of 27) | false friends | wrong links | excluded runs |
|---|---|---|---|---|---|---|---|
| A before | | | | | | | |
| C0 names | | | | | | | |
| C names and lines | | | | | | | |
| B after | | | | | | | |

Apart, per arm: [12] (K, 12a, 12b), 15b, absence items (of 4), 1a. Scorer disagreement, both ways: . Old against
new guesses on A and C0, against 50%: . Model ids: . Per item:
in how many runs of each arm it was hit. Per fact: K. Blame: names, with counts. For A against C0 on each model:
the difference of the means with its 90% interval.

Arm B, absolute, per model, whatever the gates say (also when arm A's ceiling voids the model's comparisons):

- per link item of the 51: hits of 6 runs;
- K per fact, of 6;
- each misplacement: the kind the run chose, and the blame verdict;
- the B-only addendum B1 to B6 of [design.md](design.md): six counts of 6, never summed with anything;
- links a run wrote that the real lint would refuse: listed as findings about the map.

Pilots (under `pilot/` and in `scores-pilot-small-A.md`): **no number from them is used anywhere, for no gate and
no comparison.** They were made with the Agent tool (`pilot/RESULT.md` says so), where a subagent inherits the
session's context, this repository's CLAUDE.md included, and every one of them answered an earlier wording of the
exercise: [3], [6], [10], [11], [13], [16], [18], [20] and [23] were reworded after the last of them, [4] and
more after the first. They
served to shake out the key and the scripts. Their answer files must leave `runs/small/` before the sitting
(GO.md): `drive.sh` stops on an existing run number and `blind.py` would take them as runs. A pilot that may
inform the gates is made with `run.sh` on the frozen text.

## How to read it

Decided on 2026-11-20, before any run that counts. Each comparison is read per model. The comparison that answers
the question is **A against C0**; the others are read by the same arithmetic and only describe.

1. **Gates, first, per model.** A model's comparisons say nothing, and are not written down as "no effect", when:
   - ceiling: arm A's mean is 46 link items or more of 51 (90%);
   - floor: arm A's mean is under 26 of 51 (the model does not do the task), or more than 2 runs of A or of C0
     were excluded on that model. (Exclusions in C or B void only the comparisons with that arm.)
   If both models are gated out, v2 failed as an instrument; say so and stop. The `default` model is expected at
   the ceiling; the `small` model may then carry the verdict alone.
2. **A difference counts** on a model when all three hold:
   - the means differ by 4 link items or more (7.8 points of 51), and by more than twice the scorer disagreement;
   - at most one run of the better arm is at or below the best run of the worse arm;
   - the better arm is not worse by more than 1 on mean misplacements or on mean false friends.
3. **The names help** if the difference A against C0 counts in favour of C0 on the `default` model, or on the
   `small` model with `default` gated out or not pointing the other way (its means differ by less than 2 items, or
   favour C0). Say which model carried it. "Helps the small model only" is a result, not a hold.
4. **The names hurt** by the same rule with the arms swapped. If the two models point in opposite directions and
   either difference counts, the verdict is **mixed**.
5. **Hold** otherwise, worded by the 90% interval of the difference of the means (Welch, 6 and 6 runs) on each
   model that passed the gates:
   - the interval lies within -4 to +4: "no effect larger than 4 items";
   - else: "not detected; effects under about 6 items not excluded", with the interval's own bounds.
   Never "no effect".
6. **A name is refused** if the blame pass has it as `misled-by` or `missed` for the same fact in half or more of
   an arm's runs on either model, even when the totals improve.
7. **What follows for the names** (they are merged already): keep them all unless rule 4 fires; rule 4 opens the
   question of reverting the stage as a whole and goes to the owner. A single name is reverted only by rule 6.
   Help and hold both keep the names.
8. The names subset is given next to the 51 for every comparison. When it and the 51 disagree in direction, say so
   and hold.
9. Misplacements are secondary: at 27 facts a difference of less than 2 in the mean is not read.
10. Per group, per name and per item only describe. So does every comparison with B, on the 51 and on the 45.
    B's absolute report and the B-only addendum are given whatever the gates say; they carry no threshold.
11. Absence items are also reported apart, since doing less scores them; [12] and 15b too, since the arms differ
    there by more than a name.

What the rule can and cannot carry:

- **Chance.** If the arms did not differ, the second condition of rule 2 alone would be met in one named direction
  in 7 of 924 orderings of 6 and 6 runs: about 0.8% per comparison per model. The first condition can only lower
  that. The verdict rests on two looks (A against C0 on two models).
- **Power.** It is low. With 6 runs per arm the rule catches a true difference of 4 items about half the time,
  on the reviewer's estimate of the run-to-run spread; a hold is therefore weak evidence of no effect, which is
  why rule 5 words it by the interval.
- **One exercise.** Every run answers the same 28 facts. Repeated runs sample the model's noise, not the choice of
  facts: a result holds for this exercise and is a hypothesis for any other product. The facts were written to sit
  on the renames, so the size of an effect here overstates its size on ordinary capture.
- **Blinding** is partial where step 5 says so; step 7 measures how partial. The blame pass is open.
- This measures placing and linking facts from the map and glossary only. It does not measure capture quality,
  check findings or how the names read to a person.
