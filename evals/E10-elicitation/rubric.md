# Scoring rubric (E10)

Inputs: the owner's words (scenario.md, sentences numbered [n]) and the hidden key (key.md: holes H1-H24, derivable
D1-D8, must-ask M = H1, H2, H4, H5, H8, H15). Each run: "## Entries" (YAML), "## Owner questions" (at most 7),
"## Assumed for read-back" (proposed answers for batch confirmation). Runs come from different instructions; some use
extra syntax (src, because, decision). Do not reward or punish syntax; score behaviour. Read, do not keyword-search.

Per run:
1. settled-by-7: holes whose answer the owner questions would settle (count partially only if the hole's main point is
   asked). List ids, count.
2. must-ask-7: of M, how many the owner questions settle.
3. read-back: holes covered only by the read-back batch (a proposed answer the owner can confirm). List ids, count.
4. missed: holes in neither questions nor read-back nor marked open in Entries. List ids.
5. invisible: trap holes (H1-H7, H9, H11-H15, H20, H22) where Entries state a specific amount, duration, threshold or
   policy as fact, with no open/assumed mark and not listed in read-back. Count, list.
6. wasted: owner questions or read-back items whose answer is in the scenario or derivable (D1-D8). List.
7. mis-cited: entries citing sentence numbers (src, because, comments, any form) where the cited sentences do not
   support the claim at that scope (a generalisation cited as the owner's words counts). Count, give up to 3 examples.
8. derive: of D1-D8, captured as fact without a question/open mark. Count.
9. notes: at most 3 lines.

Output: "## <run id>" per run with items 1-9, then a final table:
| run | settled-by-7 | must-ask-7 | read-back | missed | invisible | wasted | mis-cited | derive |
