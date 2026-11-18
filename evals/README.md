# OGY eval suite: how to run an eval

Status: **proposed** protocol, distilled from E8-E10. Every eval updates the [ledger](ledger.md) and the
[metrics](metrics.md) record before it counts as done.

## Steps

1. **Question and primary metric.** Write the question and pick one primary metric from [metrics](metrics.md)
   (a discriminating one). Name the adoption rule before running: what result adopts, refuses or holds.
2. **Scenario and key.** Reuse a frozen scenario when comparing with an earlier eval; otherwise write a new one in the
   owner's voice, sentences numbered `[n]`. The key, hidden from runs, lists:
   - holes, each with a cluster (the one decision that settles it);
   - must-ask holes;
   - trap holes (a plausible default the owner never gave);
   - derivable facts.
   Never put hints in the scenario.
3. **Arms.** Change one thing. Both arms get the same prompt, the same question budget and the same output sections.
   Never ask runs to "list every gap" (ceiling, E8) or for an open question list (contamination, E9).
4. **Runs.** 8 per arm, Sonnet, background, one output file each, read-only otherwise.
5. **Blind.** `python3 -I blind.py <runs dir> <out dir> <seed>` renames runs and splits them into 4 groups, each with
   two runs from each arm. Keep the map out of the scorers' reach.
6. **Score.** One Opus scorer per group with the rubric, key and scenario. One more scorer re-scores the first run of
   each group, for agreement. Report the differences.
7. **Unblind and report.** Report means and per-run ranges per arm, and the agreement. A difference counts only if it
   is larger than the scorers' disagreement and the ranges barely overlap.
8. **Record.** Write the eval's README (question, arms, table, reading, verdict). Add a ledger row. Update every
   metric row you used, including any metric that turned out to be at a ceiling, at a floor, noisy or contaminated.
   Add follow-ups to the ledger's threads and to the bead.

## Pitfalls already paid for

| Pitfall | Seen in | Rule |
|---|---|---|
| Prompt asks for gaps, short scenario | E8 | ceiling: no prompt for gaps; scenario with companion-only holes |
| Budget differs between arms | E9 | same budget and sections for both arms |
| Counts grow with output volume | E10 mis-cited | report a rate per item (per citation, per entry) |
| Docs-only capture explored by a checker | E1-E7 | counterexamples need code-level capture before they count |
| Single run reported as a result | P11, P16, P17 | single runs are hypotheses; mark them so |
| Arm syntax reveals the arm | E9, E10 | blinding is partial; score behaviour, not syntax |
