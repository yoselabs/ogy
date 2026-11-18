# E10: elicitation with an equal question budget (2026-11-17)

Rerun of [E9](../E9-provenance/README.md) with its two faults fixed. Both arms get the same budget: at most 7 owner
questions, everything else as proposed answers for one batch read-back ([prompt-A.md](prompt-A.md),
[prompt-B.md](prompt-B.md)). Arm A = spec-v3. Arm B = spec-v3 + a 16-line revised addition
([spec-addition.md](spec-addition.md)):
- `src` is the default mark; `because` covers any widening, with a read-aloud test;
- a decision may be a fill-in, so one "price list" question settles every amount;
- decisions are ranked: money, external, irreversible and permission first.

Same scenario and key as E9. 8 Sonnet runs per arm, scored blind by 4 Opus agents ([rubric.md](rubric.md),
[scores-blind.md](scores-blind.md), [blind-map.txt](blind-map.txt)). A 5th agent re-scored 4 runs
([scores-agreement.md](scores-agreement.md)) and stays within ±1 on most counts; one "missed" count differs by 2.

| Arm | Holes settled by the 7 questions (of 24) | Must-ask settled (of 6) | Read-back holes | Missed | Invisible invention | Wasted asks | Mis-cited | Derived (of 8) | Size |
|---|---|---|---|---|---|---|---|---|---|
| A spec-v3 | 10.1 (9-11) | 3.4 (3-4) | 8.1 | 4.5 | 0.50 | 3.75 | 0.9 | 6.3 | 28.9 KB |
| B + revised addition | 11.6 (10-13) | 5.1 (4-6) | 8.1 | 3.1 | 0.25 | 2.1 | 2.9 | 6.8 | 34.0 KB |

Reading:
- **Elicitation works in this shape.** With the same 7 questions, B settles 1.5 more holes and 1.75 more must-ask
  holes. The must-ask ranges barely touch: A 3-4, B 4-6. The fill-in "price list" decision recovered the money
  question that E9's options-only decision lost. B also misses fewer holes and wastes fewer asks.
- **Mis-cited rose (0.9 to 2.9 per run).** B cites a sentence for every entry, so more citations get checked; the
  error rate per citation was not measured. Typical errors are still a widening marked `src`, which means the
  read-aloud test did not stop them. A tool cannot check this; a second-agent review or the owner's read-back can.
- **Invention stays at the floor** in both arms (0.25-0.5; scorers differ by ±1).
- **Cost:** +18%, against E9's +59%.
- **Shared blind spots:** H19 (no volunteer on shift), H20 (late fee on closed days) and H21 (a reminder email fails)
  were missed by nearly every run in both arms. These are environment and interruption holes, the kind the hazard
  grid (tl-8bh9.14.172.10.5) asks for and a product capture does not.

Verdict: adopt the revised elicitation (fill-in and choice decisions, the rank, the budget, and read-back) for spec v4.
Provenance: keep `src`/`because`, but checking them needs a review step, not a lint.
