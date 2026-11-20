# Naming eval v2: old names against mainstream names, made sensitive

Status: **designed, piloted on arm A, not run** (2026-11-20, bead ogy-yy9.75). Replaces [v1](../README.md), whose
arm A sat at a ceiling: kind 16.3 of 17, links 13 of 17, 0.67 misplacements, no error blamed on a name. v1's files
and scores stay as they are; v2 results are not comparable with them (other facts, other metric).

## Files

| file | who reads it |
|---|---|
| [exercise.md](exercise.md), [prompt.md](prompt.md), `inputs/` | the runs |
| [key.md](key.md), [rubric.md](rubric.md) | the scorers, with the exercise and the blind runs; nothing else |
| [design.md](design.md), [blame.md](blame.md) | the coordinator only: names per arm, expected pulls, the unblinded pass |
| `prepare.sh`, `run.sh`, `check-run.py`, `blind.py`, `vocab.tsv` | build an arm, run once, test an output, blind |
| `check-neutral.py`, `names-extra.txt`, `overlap-allowed.txt` | keep the facts free of every arm's words |

## What changed from v1

| | v1 | v2 |
|---|---|---|
| facts | 17, one per kind | 28: 1 anchor and 27 target facts, each on a confusion a rename aims at, look-alikes placed apart |
| primary metric | misplacements of 17 | link items hit, of 51: each required link or filled field scored 0 or 1 |
| arms | before, after | before, names only (C0), names with like/unlike lines (C), after (B) |
| models | one, not recorded | a small model and the default model, the main model id recorded per run |
| blinding | kind names show the arm | every run rewritten into one vocabulary; scorer key without arms; name blame in a later open pass |
| scoring | one scorer, one re-scored run per arm | every run scored twice |
| neutrality | by eye | `check-neutral.py`: no kind or field name of any arm, no content word only some arms print |
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
| C0 | `1fb0e39` | `prepare.sh C0 1fb0e39 --no-like` | stage 1 names; the two "kinds, like and unlike" blocks removed |
| C | `1fb0e39` | `prepare.sh C 1fb0e39` | stage 1 names with the like/unlike lines |
| B | main once all stages have landed: write the commit here | `prepare.sh B <commit>` | all renames, `interface`, `rule.constrains`, later links |

| comparison | what it isolates |
|---|---|
| **A against C0** (primary) | the names alone |
| C0 against C | the like/unlike lines |
| C against B | the `interface` merge and the later model changes |
| A against B | the whole change |

A, C0 and C can run now. Known limit of C0 and C: the glossary at `1fb0e39` still carries old words ("never an
external", "options, guess and answers", "a rule or value"); see [design.md](design.md). Pin a cleaned commit
before the freeze if one exists by then, else report the limit with the result.

## Models

Every arm runs on two models, because a strong model reads past a poor name (v1) and a small one leans on it:

| tag | model | why |
|---|---|---|
| `small` | the smallest current Claude model the harness offers (the Haiku tier) | most likely to follow a name and not the field list: the sensitive reading |
| `default` | the model v1's arm A ran on, the harness default | the model that does the real work: the reading that decides adoption |

Before the freeze, write here the full model id and the effort of each tag: `small = <id>, <effort>`;
`default = <id>, <effort>`. Runs: **5 per arm per model** (40 runs with B). All arms of one model on the same
day, arms interleaved (A, C0, C, B, A, ...).

A run is one call of `run.sh TAG MODEL EFFORT ARM N`. It starts `claude -p` in an empty temporary folder with
`--safe-mode --disable-slash-commands --strict-mcp-config --no-session-persistence --tools Write`, so that no
CLAUDE.md, memory, skill, plugin, hook or MCP server of this machine reaches the run, and the one tool is the one
the prompt needs. (`--bare` isolates as well but accepts only an API key.) The flags were read from the help of
Claude Code 2.1.326; the script has not been executed: confirm on the first pilot run that the answer file
appears and that the json result has `modelUsage`.

Recording the model: `run.sh` keeps the harness result in `runs/<tag>/meta/` and adds one line to
`runs/models.txt`: `<tag>/<run file> main=<id> aux=<ids or -> asked=<id> effort=<level> <date> <harness version>`.
`modelUsage` is a record keyed by model id and may hold more than one: `main` is the id with the most output
tokens, the others are auxiliary (a title call, a background helper) and are listed, not grounds to discard. A run
is discarded only when its `main` id is not the id pinned for its tag, or cannot be read. Never record an alias
or the model's own answer about itself.

## What a run gets

One message: [prompt.md](prompt.md) (the same bytes as v1's) filled with the output of `uv run ogy kinds --map` and
`uv run ogy glossary` at the arm's commit, then [exercise.md](exercise.md), then the line `Output path: answer.md`.
The prompt and the exercise are the same bytes in every arm and for every model: only the map and the glossary
differ. `inputs/arms.txt` holds, per arm, the commit, the sha256 of the exercise it was built from and whether the
like/unlike blocks are in; the hashes must be equal.

## How to run

1. Freeze. Pilot runs (arm A, `small`) live in `pilot/` or are named as pilot, never enter a result, and the
   exercise and the key may change after them. Then fill the model ids above, commit `v2/` and write the commit
   here: `frozen at: <commit>`. After the freeze the exercise, the rubric, the neutral columns of the key, the
   names subset and the reading rule do not change.
2. Build the inputs with the four commands of the arms table. Each call rebuilds `inputs/<arm>.md`, updates
   `inputs/arms.txt` and runs `check-neutral.py`; a fact that uses a name of any arm, or a content word that only
   some arms print, fails the build. When B's map is printed: delete from `names-extra.txt` the names it now
   carries, add B's 1:1 renames to `vocab.tsv`, settle every `(verify)` cell of design.md and the last table of
   key.md against `inputs/B.md`. If a fact then fails the check, the exercise changes: that is a new freeze and
   every arm is rerun.
3. Run with `run.sh`. It ends with `check-run.py` on the answer.
4. Exclude, before anyone scores. A run is excluded when `check-run.py` calls it malformed (no table, a fact row
   missing or twice, a row without four cells or without a kind), when no answer file was written, or when its
   main model id is wrong. Nothing else excludes a run: never its content. An excluded run stays on disk, gets a
   line in `runs/excluded.txt` (`<tag>/<run> <reason>`) and is replaced by a fresh run with the next number, at
   most 2 replacements per arm per model. Exclusions are reported per arm; an arm with more than 2 on a model is
   itself a finding, and that model's comparisons with the arm are a hold.
5. Blind, per model: `python3 -I evals/naming/v2/blind.py evals/naming/v2/runs/small evals/naming/v2/scoring/small
   <seed>`, the same for `default`. It rewrites every run with `vocab.tsv`, the same table for all arms, so that
   the renamed kinds and fields read alike (to arm A's words), and prints batches of one run per arm. Not blinded
   away: `many`, `heard`, `realizes` on a capability, and B's `interface` with its fields. Scorers get
   `scoring/<tag>/blind/`, key.md, rubric.md and exercise.md; never `map.txt`, `inputs/`, `runs/`, design.md,
   blame.md or this file.
6. Score: every batch goes to two Opus scorers who do not see each other. A run's marks are the mean of its two
   scorers. Scorer disagreement is reported two ways: the mean absolute difference in link items hit, of 51, and
   the mean count of link items on which the two differ, per run. An item on which they differ in more than a
   third of the runs is named, and the result is given with and without it.
7. Unblind with each `map.txt`, do the [blame pass](blame.md), fill the tables below, add a ledger row and the
   metric rows.

## Result (to fill)

One table per model. Means with per-run ranges.

| arm | link items (of 51) | names subset (of 19) | misplacements (of 27) | false friends | wrong links | excluded runs |
|---|---|---|---|---|---|---|
| A before | | | | | | |
| C0 names | | | | | | |
| C names and lines | | | | | | |
| B after | | | | | | |

Apart, per arm: [12] (K, 12a, 12b), 15b, absence items (of 4), 1a. Scorer disagreement, both ways: . Model ids: .
Per item: in how many runs of each arm it was hit. Per fact: K. Blame: names, with counts.

Pilot (arm A, `small`, 2 runs, the first wording of the exercise and the first key): 43.5 of 53 link items, under
the gate; [10] written as `operation` in both runs, blamed on the name. To be re-scored on key.md; note that [4]
was reworded after the pilot (its first wording contradicted [17]), so item 4b of a pilot run is read with care.

## How to read it

Decided on 2026-11-20, before any run that counts. Each comparison is read per model. The comparison that answers
the question is **A against C0**; the others are read by the same rule and named as what they isolate.

1. **Ceiling gate, first.** If arm A's mean is 46 link items or more of 51 (90%) on a model, that model is at a
   ceiling: its comparisons say nothing and are not written down as "no effect". If both models are at a ceiling,
   v2 failed as an instrument; say so and stop.
2. **A difference counts** on a model when all three hold:
   - the means differ by 4 link items or more (7.8 points of 51), and by more than twice the scorer disagreement;
   - at most one run of the better arm is at or below the best run of the worse arm;
   - the better arm is not worse by more than 1 on mean misplacements or on mean false friends.
3. **The names help** if the difference A against C0 counts in favour of C0 on the `default` model, or on the
   `small` model with `default` not pointing the other way (its means differ by less than 2 items, or favour C0).
   Say which model carried it. "Helps the small model only" is a result, not a hold.
4. **The names hurt** by the same rule with the arms swapped. If the two models point in opposite directions and
   either difference counts, the verdict is **mixed**: no adoption on this evidence.
5. **Hold** otherwise.
6. **A name is refused** if the blame pass has it as `misled-by` or `missed` for the same fact in half or more of
   an arm's runs on either model, even when the totals improve.
7. The names subset is given next to the 51 for every comparison. When it and the 51 disagree in direction, say so
   and hold.
8. Misplacements are secondary: at 27 facts a difference of less than 2 in the mean is not read.
9. Per group, per name and per item only describe: they point at the next eval and decide nothing.
10. Absence items are also reported apart, since doing less scores them; [12] and 15b too, since the arms differ
    there by more than a name.

What the rule can and cannot carry:

- **Chance.** If the arms did not differ, the second condition of rule 2 alone would be met in one named direction
  in 6 of 252 orderings of 5 and 5 runs: about 2.4% per comparison per model (4 of 20, 20%, with 3 runs; 7 of 924,
  0.8%, with 6). The first condition can only lower that. Four comparisons on two models are eight looks: across
  them the chance of one false "counts" in a named direction is up to about 18%, which is why only A against C0
  decides and the rest describe.
- **One exercise.** Every run answers the same 28 facts. Repeated runs sample the model's noise, not the choice of
  facts: a result holds for this exercise and is a hypothesis for any other product. The facts were written to sit
  on the renames, so the size of an effect here overstates its size on ordinary capture.
- **Blinding** is partial where the table in step 5 says so, and the blame pass is open.
- This measures placing and linking facts from the map and glossary only. It does not measure capture quality,
  check findings or how the names read to a person.
