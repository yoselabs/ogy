# Blame pass (after unblinding, not blind)

Done once both scorers are finished and `map.txt` is open. One reader, with [design.md](design.md), the scorers'
marks and the original runs in `runs/<model tag>/` (not the rewritten copies).

For each fact of each run where both scorers gave K = 0, or both gave F = 0, or both gave the same link item 0,
read the run's "why" line and record one of:

- `misled-by: <name>` when the line reasons from what a kind's or a field's *name* means elsewhere (UML, REST, a
  framework, plain English) and not from the map's fields or a glossary line; add `missed: <name>` when it says it
  read the right name as something else;
- `structural` when it gives a reason from the map's fields, rules or glossary;
- `unclear` when it is silent on the point.

Never infer a name the line does not mention. The reader knows the arm, so this pass is not blind: it feeds the
"a name is refused" rule and the description of the result, never the counts that decide the verdict.

Output: `blame-<model tag>.md`, one line per error: `run fact item-or-K-or-F | verdict | the words of the why line`.
Then a table: name, arm, fact, runs blamed of runs in the arm.

## Arm B, in the same pass

- The absolute report: per link item, hits of 6; K per fact; for each misplacement the kind chosen and the verdict
  above. Written whatever the gates say.
- The addendum of [design.md](design.md): B1 to B6, 0 or 1 per B run, six counts per model, never summed with any
  other number.
- Links the lint would refuse: when a B run writes a link the printed map seems to offer but the real map does
  not take (a `satisfies` on a data kind, a product entry naming a software one), list it as `map finding`, with
  the map line that made it look allowed. It is a finding about the map, not a run's error.

