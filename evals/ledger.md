# OGY eval ledger

Status: **record**. One row per eval, newest first. Each row: the question, the arms, n, what moved, the verdict and
what it left open. Metric definitions and their history: [metrics](metrics.md). How to run one: [protocol](README.md).
Full outputs stay in the eval's own folder under `evals/`; probes are in `docs/probes/`.

| Eval | Question | Arms (n) | What moved | Verdict | Left open | Folder |
|---|---|---|---|---|---|---|
| (untested) 2026-11-18 | ogy stores no messages and no quotes: an answer keeps `said` (a short paraphrase), `from` (human or ai), `at` and `where`; a person's yes is `agreed` on the entry; `guess.heard` is a paraphrase; live capture records the answer with a paraphrase at once and shows it in the read-back (skills and AGENTS block) | none | none | untested; behaviour covered by `tests/test_writes.py`, `tests/test_reply.py`, `tests/test_settle.py` | whether agents write paraphrases short and faithful, and whether owners correct them in the read-back | none |
| (untested) 2026-11-18 | A move records nothing (no `moved` removed.yml item; every address rewritten in the same write, messages and answers included; `check --base` detects a move by kind, id and fingerprint); every finding is an error (area named like the product is `product-area`, no warnings) | none | none | untested; behaviour covered by `tests/test_move.py`, `tests/test_structure.py` | whether agents still reach for remove and put | none |
| (untested) 2026-11-17 | Persona needs no evidence (`evidence: none`); an answer agrees to no sentence (D9 `answer-not-agreed` removed; entries settled by an answered decision read "from your words") | none | none | untested; behaviour covered by `tests/test_gaps.py`, `tests/test_writes.py`, `tests/test_reply.py` | whether owners read sentences back; no card yet for entries that read "from your words" | none |
| E11 2026-11-17 | Does the capture skill (hazard pass, elicitation, read-back) surface more and settle more? | spec-v4 vs + skill (8+8 Sonnet, 4 blind Opus + 1 agreement) | hazard holes 6.25→8.9 (ranges 5-7 vs 7-11); settled 8.5→10.6; must-ask 3.5→4.75; mis-cite rate 3% both; size +2% | **adopt the skill** | harder derivations; review pass for the 3% mis-cites; hazard pass on code | E11-skill |
| E10 2026-11-17 | Does decision-shaped elicitation settle more with the same 7 questions? | spec-v3 vs + 16-line addition (fill-in + choice decisions, rank, src/because) (8+8 Sonnet, 4 blind Opus scorers + 1 agreement) | must-ask 3.4→5.1; settled 10.1→11.6; missed 4.5→3.1; mis-cited 0.9→2.9; size +18% | **adopt elicitation** for v4 | mis-cite rate per citation; H19-H21 missed by all | E10-elicitation |
| E9 2026-11-17 | Do provenance marks and a decision kind cut invention and owner questions? | spec-v3 vs + Fable's 33-line addition (8+8, same scoring) | invention at floor both; options-only decisions dropped money (must-ask 3.9→2.75); size +59% | **not adopted**; led to E10 | question count contaminated by the prompt | E9-provenance |
| E8 2026-11-17 | Does a tray-shaped ontology (cards, skeleton) make an AI notice gaps? | prose vs cards vs cards+skeleton (5+5+5, 1 blind Opus) | ceiling on noticing; cards invented 4 values in one slot; size +45-55% | inconclusive; slots need an "unknown" option | rerun on a harder scenario with companion-only holes | E8-tray |
| P17 2026-11-17 | Does the hazard grid on code beat a docs capture for real defects? | one Fable run on land code | 0 firm false alarms vs 5 of 6 from docs; one new candidate (F2) | promising, single run | F2 unverified; A/B with the grid not run | ../docs/probes (P17 ) |
| P16 2026-11-17 | Does the six-question hazard grid fit a product? | one Fable run on booking | 69 cells: 33 business, 25 technical, 11 noise | fits with two wordings and a 7th question | worklist not tool-built; repeat | ../docs/probes (P16 ) |
| E1-E7 2026-11-17 | Can spec-v3 describe task-loop itself; does it find edge cases? | one Sonnet run per area; E6 ontology vs prose; E7 Quint by hand | 5 of 6 candidates false (docs-only capture); unused fields listed | capture must read code; environment block needed | v4 items (bead .10.11) | E1-E7 |
| P15 2026-11-17 | Can an interview capture requirements? | 3 Sonnet runs, role-played | over-engineering list | interview works; owner never writes entries | not compared with doc capture | ../docs/probes (P15 ) |
| P11-P14 2026-11-16 | Do products fit the ontology; do readers confuse forms? | simulations (10 products), readers | v2 fixed structure; computed facts were the gap | led to FEEL subset in v3 | | ../docs/probes (P11-P14 ) |
| P1-P10 2026-11-15 | Plans, rows, upkeep, Git cost, tracker reads | single probes | see each | inputs to the KB design | | ../docs/probes (P1-P10 ) |

## Threads to continue (next evals, in order)

1. Done as E11 (adopted). Next: hazard pass on code as an A/B (P17 style), false-alarm rate as the metric.
2. **Mis-cites:** the rate is about 3% per citation (E11). Test a second-agent review pass against the owner's read-back.
3. **E8 rerun:** tray cards vs prose on the tool-library scenario, without asking for gaps.
4. **Hazard grid A/B:** grid vs free hunt on the same code area, false-alarm rate and real finds (bead .10.6).
