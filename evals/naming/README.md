# Naming eval: old names against mainstream names

Status: **designed, not run** (2026-11-20, bead ogy-yy9.75). Follows [the protocol](../README.md) with the changes
named below.

## Question

Do mainstream names let a fresh agent put a product's facts in the right kinds more often than the old names?
Mainstream: the UML/SysML anchor, ArchiMate layers and verbs, BPMN flow (`quantity`, `enum`, `handler`,
`dependency`, `setting`, `attribute`, `interface`, `satisfies`, `proposal`, `workaround`, and a like/unlike line per
kind). Old: `value`, `set`, `operation`, `external`, `config_key`, `attr`, `view`, `command`, `by`, `guess`,
`deviation`.

Primary metric: **misplacements per run**, the facts of 17 written in the wrong kind. Also reported: false friends
per run, links of 17, and which name each wrong answer blames.

## Arms

| arm | commit | what it is |
|---|---|---|
| A | tag `eval-before` = `46f0564` | main before the renames |
| B | main once stages 1 to 3 have landed: write the commit here | all renames, `interface`, like/unlike lines |
| C (optional) | the stage 1 commit: write it here | renames and like/unlike only; `view` and `command` still apart |

C separates the effect of the names from the effect of merging `view` and `command`. Without C, a gain on facts
[11] and [12] cannot be put down to naming.

## What a run gets

One message: [prompt.md](prompt.md) filled with the output of `uv run ogy kinds --map` and `uv run ogy glossary` at
the arm's commit, then [exercise.md](exercise.md). No README, no source, no kind files, no tools beyond writing its
one output file. The exercise never uses a kind name of any arm. The prompt and the exercise are the same bytes in
every arm: only the map and the glossary differ.

## How to run

1. Pin the arms: fill the table above. Check the B and C columns of [key.md](key.md) against the printed maps and
   correct them. Check the exercise still uses no kind name of the B map.
2. Build the inputs: `evals/naming/prepare.sh A eval-before`, then the same for `B <commit>` and `C <commit>`. It
   writes `inputs/<arm>.md` and records the full commits in `inputs/arms.txt`.
3. Run: a fresh agent per run, with no memory of this repository, started in an empty folder. At least 3 runs per
   arm (8 to match the protocol), the same model for every run, all arms on the same day, arms interleaved. Output
   to `runs/<arm><n>.md` (`A1.md`, `B3.md`).
4. Blind: `python3 -I evals/blind.py evals/naming/runs evals/naming/scoring <seed>`. Scorers get `scoring/blind/`,
   never `scoring/map.txt` or `inputs/arms.txt`. With fewer than 4 runs per arm, ignore the printed groups: one
   scorer scores every run.
5. Score: one Opus scorer with [rubric.md](rubric.md), [key.md](key.md) and [exercise.md](exercise.md). A second
   scorer re-scores one run of each arm for agreement. Do not tell a scorer the question or which names are new.
6. Unblind with `scoring/map.txt`, fill the table below, add a ledger row and the metric rows.

Blinding is partial: a run's kind names show its arm (pitfall "arm syntax reveals the arm"). The guards: the kind
mark is a lookup in the key's table, the rubric forbids inferring a misleading name the "why" line does not give,
and the agreement scorer.

## Result (to fill)

| arm | misplacements (of 17) | false friends | links (of 17) | name-caused | names blamed, with counts |
|---|---|---|---|---|---|
| A before | | | | | |
| C stage 1 | | | | | |
| B after | | | | | |

Means with per-run ranges. Add a per-fact line: in how many runs of each arm fact n was misplaced.

## How to read it

Decided before running:

- **The renames help** if B's mean misplacements are lower than A's by more than the scorers' disagreement and the
  ranges barely overlap, and B's false friends are not higher.
- **Hold** if the ranges overlap. With 3 runs per arm a difference is a hypothesis: rerun with 8 before recording it.
- **A name is refused** if one new name is blamed in half or more of an arm's runs for the same fact, even when the
  totals improve. Look at the per-fact line first: the totals can hide one bad name behind several good ones.
- Facts where every arm scores full ([3], [8] are likely) are at a ceiling and say nothing. Facts whose key is the
  same in every arm ([3], [8], [10], [15], [16], [17]) measure spill-over: a renamed neighbour pulling a fact away.
- A against C is the names alone. C against B is the `interface` merge and the later model changes.
- This measures placing facts from the map and glossary only. It does not measure capture quality, check findings
  or how the names read to a person.
