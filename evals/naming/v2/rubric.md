# Scoring rubric (naming eval v2)

Inputs: [exercise.md](exercise.md), [key.md](key.md) and the blind runs. A run is one table: fact, kind, links, why.
All runs were rewritten into one vocabulary. Score the home and the links a run chose. Read each line; do not
keyword-search. Do not guess where a run came from and do not judge the names: no mark depends on either.

## Per fact

1. **Link items, 0 or 1 each** (primary). Take the fact's items from the key (`4a`, `4b`, ...) one at a time.
   - An item is 1 when the run states that link or that filled field, in the links cell, in the kind cell, or as a
     `new:` entry. A link counts when either end states it: the row of the fact, or the row of the fact it points
     at.
   - The field must be one the key's last table gives for that meaning. A link under a field that means something
     else is 0. A link with the right field and the wrong target is 0.
   - A link named only in the "why" cell, or only as "would" or "could", is 0.
   - An absence item ("no ...") is 1 when the fact has an entry and the named link is not there; it is 0 when the
     link is there, and 0 when the fact has no entry (`none`).
   - Items are judged on their own, also when K = 0. An item that the chosen kind cannot carry is 0.
2. **K, kind correct, 0 or 1.** The run's kind is the key's home for that fact. A part needs its parent right too.
   Where the home is two entries ([22]), both must be there; a `new:` entry in the links cell counts.
3. **F, no false friend, 0 or 1.** 0 when the run puts the fact, or a copy of it, in a false-friend home listed in
   the key, or in any other home whose name in ordinary software speech means this fact but whose meaning in the
   key does not. F is separate from K: a wrong kind that is no false friend scores K 0, F 1; the right kind plus a
   duplicate in a false-friend home scores K 1, F 0.
4. **Wrong links, a count.** Each link the run states that points at a wrong target or sits in a field with another
   meaning. An absence item that scored 0 is counted here too.

## Per run

- **Link items hit** (primary): the sum over facts [2] to [28] without 15b, of 51. Give 1a and 15b apart.
- **Misplacements**: the count of facts [2] to [28] with K = 0, of 27.
- **False friends**: the count of facts with F = 0.
- **Wrong links**: the sum.

## Ties and partial answers

- Two kinds offered ("X or Y"): score the first. If the first is right and the second is a false friend, K 1, F 0.
- Several entries for one fact, the key's home among them and none a false friend: K 1.
- Fact split correctly beyond the key: K 1.
- `none`, or "outside the knowledge base": K 0, every item 0, F 1; for [16] it is a listed false friend, F 0.
- A kind or field word that the key's last table does not have for any fact and that you cannot place: K 0 (kind)
  or item 0 (field), F 1, note `unknown word`.
- Right kind, wrong part or wrong parent: K 0, F 1.
- Items the key calls "not scored" change no mark; list them in the notes.
- A doubt the key does not settle: score 0, write one line under "Doubts". Do not extend the key while scoring.

## Output

`## <run id>`, then one line per fact:

`n: K F | <item>=<0 or 1> ... | wrong links: <count> | note`

for example `4: 1 1 | 4a=1 4b=0 | wrong links: 0 | number read by nothing`. Then one table:

| run | link items (of 51) | 1a | 15b | misplacements (of 27) | false friends | wrong links |
|---|---|---|---|---|---|---|

Then `## Doubts`, one line each.
