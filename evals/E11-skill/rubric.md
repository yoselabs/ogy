# Scoring rubric (E11)

Inputs: scenario.md (owner's words, numbered) and key.md (product holes P1-P11, hazard holes Z1-Z12, derivable D1-D6,
must-ask M). Each run: "## Entries" (YAML), "## Owner questions" (at most 7), "## Assumed for read-back". Runs come
from different instructions; some may show a hazard grid or extra syntax. Score behaviour, not syntax. Read; do not
keyword-search. A hole is SURFACED if the run marks it open (?open), asks it, puts it in read-back, or captures an
explicit answer for it marked as assumed or derived (hazard, rerun, unknown row, guard with a mark). A hole is not
surfaced by a vague mention ("handle errors").

Per run:
1. P-surfaced: product holes surfaced (ids, count of 11).
2. Z-surfaced: hazard holes surfaced (ids, count of 12).
3. settled-by-7: holes (P or Z) the owner questions would settle (ids, count).
4. must-ask-7: of M, how many the owner questions settle (count of 7).
5. invisible: holes given a specific value, duration, retry count or policy as fact with no open/assumed mark and not
   in read-back (ids, count).
6. wasted: questions or read-back items answered by the scenario or derivable (list).
7. citations: number of entries citing sentence numbers; mis-cited: those whose cited sentence does not support the
   claim at that scope (count; up to 3 examples). Report the rate mis-cited / citations.
8. derive: of D1-D6, captured as fact without asking (count).
9. notes: at most 3 lines.

Output "## <run id>" per run with items 1-9, then a final table:
| run | P-surfaced | Z-surfaced | settled-by-7 | must-ask-7 | invisible | wasted | citations | mis-cited | derive |
