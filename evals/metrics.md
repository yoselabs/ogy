# OGY eval metrics: what each one told us

Status: **record**, kept current by every eval. One row per metric. "Moved" = the arms differed beyond scorer noise
(±1 on most counts, see [protocol](README.md)). Add a row before using a new metric; update the row after every eval.

## Capture quality (product requirements)

| Metric | Definition | Evals | What happened | Status | Lesson |
|---|---|---|---|---|---|
| Must-ask settled | of the key's must-ask holes (money, external party, permission, irreversible), how many the first N owner questions settle | E9 (post hoc), E10, E11 | E10: 3.4 vs 5.1 of 6, ranges 3-4 vs 4-6; E11: 3.5 vs 4.75 of 7 | **discriminating** | the best single signal for elicitation; ranges separate |
| Settled by N questions | holes the first N owner questions would settle (N = 7) | E9 (post hoc), E10, E11 | E9: 10.4 vs 9.75 (no gain); E10: 10.1 vs 11.6; E11: 8.5 vs 10.6 | **discriminating** | needs an equal budget in both arms |
| Missed | holes in neither questions, read-back nor open marks | E10 | 4.5 vs 3.1 | discriminating, weak | which holes are missed matters more than the count: H19-H21 missed by almost every run |
| Invisible invention | a trap hole given a specific value or policy as fact, unmarked | E8, E9, E10 | E8 cards: 4 (all one slot `?max`); prose arms 0-0.5 everywhere | **floor** for prose + `?open` | keep as a guard (it caught the cards' slot problem); it will not separate two good arms |
| Visible invention | same, but marked assumed | E9 | 12.6 vs 7.9 | reported only | not good or bad by itself; read-back makes it cheap to confirm |
| Holes noticed | holes marked or asked, no budget | E8, E9 | E8: 63-65 of 65; E9: 18.8 vs 19.3 | **ceiling** | useless when the prompt asks for gaps or the scenario is short |
| Questions (count) | owner questions listed | E8, E9 | E9: both about 18 | **contaminated** | an open "list your questions" prompt removes any budget; replace with a fixed budget |
| Wasted asks | questions or read-back items answered by the scenario or derivable | E9, E10 | E9: 0.1 vs 0.4; E10: 3.75 vs 2.1 | weak | scorers disagree on "partial"; report the list, not just the count |
| Derived | of the key's derivable facts, captured as fact without asking | E9, E10 | 7.6-7.9 (E9), 6.3 vs 6.8 (E10) | ceiling | Sonnet derives well; drop unless a scenario hides derivations deeper |
| Read-back holes | holes covered only by the batch read-back | E10 | 8.1 vs 8.1 | neutral | shows the batch carries about a third of the holes; keep, it measures owner load |
| Mis-cited | entries citing sentences that do not support them at that scope | E9, E10, E11 | E9: 1.5 vs 1.0; E10: 0.9 vs 2.9; E11 rate: 2.7% vs 3.2% per citation | **use the rate** | counts grow with citation volume; the rate is about 3% with or without the skill. Widening marked as said survives a read-aloud test |
| Misfiled | entry in the wrong kind or layer | E8 | 0-1 | noise | drop |
| Size | output bytes per run | E8-E11 | E8 cards +45-55%; E9 +59%; E10 +18%; E11 +2% | cost, always report | an addition that costs over +25% needs a large gain |

| Hazard holes surfaced | of the key's hazard holes (environment, timing, outside failure), how many are open, asked, read back or answered with a mark | E11 | 6.25 vs 8.9 of 12, ranges 5-7 vs 7-11 | **discriminating** | the hazard pass needs its own step; product capture alone stops near half |

Shelf snapshot adoption (2026-11-22, ogy-whb) has regression and gate validation only; no agent eval ran and no agent metric changed.

## Exploration and hazards (system behaviour)

| Metric | Definition | Evals | What happened | Status | Lesson |
|---|---|---|---|---|---|
| Counterexample false-alarm rate | candidates that turn out guarded in code | E1-E7 table, P17 | docs-only capture: 5 of 6 false; code-reading grid: 0 firm false | **discriminating** | the capture source decides precision: read code before a counterexample counts |
| Grid noise | grid cells that are not real business or technical questions | P16 | 11 of 69 (16%) | single run | needs na codes; repeat before trusting |
| Structural vs operational finds | which findings each reader form makes | E6 | ontology reader: exitless states, off-by-one; prose reader: operational facts | qualitative | complementary; capture must keep operational facts |
| Kind usage | which kinds and fields the captures used | E1-E7 | tags, adds, each, wait, conflict nearly unused | qualitative | cut candidates for v4 |

## Reading and upkeep (format)

| Metric | Evals | What happened | Lesson |
|---|---|---|---|
| Row form vs prose for reading | P1 | no reading advantage for rows (one run, weak reader) | rows must be justified by diff, currency and checks, not by reading |
| False suspects on hash change | P6 | 16% of changed rows (4% without one column-adding commit) | content hashes are usable as change signals |
| Reader confusion between workflow forms | P11 | one run per form | single-run probe; treat as a hypothesis |
| Link items hit, of 51 (placing facts from the map and glossary alone) | naming v2 | `default` model: 47.5 to 50.8 across arms, at the ceiling; `small`: A 44.25, C0 44.5, C 45.0, B 47.0, ranges overlap; scorer disagreement 0.12 and 0.46 | a strong model sits at the ceiling even with 28 harder facts; only a small model separates arms, and 6 runs per arm resolve about 4 items, not less |
| Misplacements, of 27 | naming v2 | 0.8 to 2.5 per arm on both models; fact [24] wrong in 45 of 48 runs on every arm | secondary; a fact every arm misses points at the key or the map, not at the names |
| Old against new guesses (blinding) | naming v2 | 0 of 24 on the right side on both models; 18 and 24 "could not tell" | rewriting into one vocabulary hides the direction, not the grouping: article slips from the rewrite let scorers separate rewritten runs from the rest; fix the articles in the rewrite next time |
