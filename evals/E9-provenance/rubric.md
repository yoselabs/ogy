# Scoring rubric (E9)

Inputs: the owner's words (scenario.md, sentences numbered [n]) and the hidden key (key.md). Each run file is one
agent's capture: "## Entries" (YAML) and "## Questions for the owner". Runs come from different instructions; some use
extra syntax (quote, said, because, decision, origins). Do not reward or punish syntax itself; score only the
behaviour below. Judge each item by reading the run, not by keyword search.

Status of a fact in a run:
- MARKED = shown as not settled by the owner: ?open, assumed, a decision default, "TBD", or covered by an owner question.
- STATED = written as fact with no such mark (including marked `said:` or `because:`).

Per run, report:
1. invisible: list of key trap holes (H1-H7, H9, H11-H15, H20, H22) where the run states a specific amount, duration,
   threshold or policy as STATED. Count.
2. visible: same holes where a specific value/policy appears but MARKED (assumed/default). Count.
3. coverage: of H1-H24, which are MARKED or asked (a question counts if its answer would settle the hole). List ids, count.
4. questions: number of numbered owner questions (count sub-bullets inside one numbered question as one).
5. yield: (holes covered by questions) / questions. Also list question numbers that cover >=2 holes.
6. must-ask: of M = {H1, H2, H4, H5, H8, H15}, how many appear in the first 7 questions.
7. wasted: questions whose answer is in the scenario or derivable (D1-D8 or a stated fact). List them.
8. false-said: entries marked `said:` (or citing a quote) whose cited sentence does not state it. Count (0 if none used).
9. derive: of D1-D8, how many are captured as fact without a question and without an open mark. List ids.
10. notes: anything striking (an invented fact type not in the key, shape errors, unusual strengths), at most 3 lines.

Output: one Markdown section per run: "## <run id>", then the 10 items as a list. End with a table:
| run | invisible | visible | coverage | questions | yield | must-ask | wasted | false-said | derive |
