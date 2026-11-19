# Scoring rubric (naming eval)

Inputs: [exercise.md](exercise.md), [key.md](key.md) and the blind runs. A run is one table: fact, kind, links, why.
Runs use different kind names for the same homes; the key maps them. Score the home the run chose, not the
vocabulary. Read each line; do not keyword-search.

## Per fact, three marks of 0 or 1

1. **K, kind correct.** The run's kind is the key's home for that fact, in that run's vocabulary. A part needs its
   parent right too (`entity > attr`, not a bare `attr` under the wrong parent).
2. **L, links present.** Every required link and required field of the key is there, with no link to a wrong target.
   A link counts when either end states it. A "new:" target counts when it is the entry the key implies. If the key
   requires none, L = 1 unless the run invents a wrong link. L is judged on its own, also when K = 0.
3. **F, no false friend.** 0 when the run puts the fact, or a copy of it, in a false-friend home listed in the key,
   or in any other home whose name in ordinary software speech means this fact but whose meaning in the map does not.
   F is separate from K: a wrong kind that is no false friend scores K 0, F 1; the right kind plus a duplicate in a
   false-friend home scores K 1, F 0.

## Per run

- **Misplacements** (primary): the count of facts with K = 0, of 17.
- **False friends**: the count of facts with F = 0.
- **Links**: the sum of L, of 17.
- **Name-caused errors**: for each fact with K = 0 or F = 0, read the "why" line. If it reasons from what a kind's
  *name* means elsewhere (UML, REST, a framework, plain English) and not from the map's fields or the glossary line,
  record `misled-by: <name>` (the name that pulled the fact in) and, if said, `missed: <name>` (the right kind's
  name the run read as something else). If the "why" gives a structural reason, record `structural`. If it is silent,
  record `unclear`. Never infer a name the line does not mention.

## Ties and partial answers

- Two kinds offered ("X or Y"): score the first. If the first is right and the second is a false friend, K 1, F 0.
- Several entries for one fact, the key's home among them and none a false friend: K 1.
- Fact split correctly beyond the key (for example [1] as a number plus the branch that reads it): K 1.
- `none`, or "outside the knowledge base": K 0, L 0, F 1; for [17] it is a listed false friend, F 0.
- A kind name that is not in that run's map: K 0, F 1, note `invented kind`.
- Right kind, wrong part or wrong parent: K 0, F 1.
- Credit items in the key change no mark; list them in the notes.
- A doubt the key does not settle: score 0, write one line. Do not extend the key while scoring.

## Output

`## <run id>`, then one line per fact: `n: K L F | misled-by / missed / structural / unclear | note`. Then a table:

| run | misplacements | false friends | links (of 17) | name-caused | names blamed |
|---|---|---|---|---|---|
