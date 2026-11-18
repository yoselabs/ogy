---
name: ogy-capture
description: Turn an owner's words, docs or code into entries of an ogy knowledge base (software ontology), find what is
  missing, and ask the owner the fewest questions that settle the most. Use when capturing or amending requirements.
---

# OGY capture (draft, 2026-11-17)

Status: **proposed**. The commands this skill names are the ones in the [README](../../README.md) table; `ogy put` (one
batch write for create and update), `guess.heard`, `answer --said --where`, `answer.note` and a required
`remove --why` are being built and are **untested here**. Steps with no eval behind them are marked untested.
The skill holds the flow; the ontology (`ogy kinds [kind]`) holds the shapes; `ogy check` holds the lints. Never write
YAML by hand and never read a spec to learn a shape: ask `ogy kinds`.

## 1. Glossary first
Run `ogy glossary` before you read code or write a sentence (`ogy glossary <layer>/<area>` for one area and the shared
words it reads). Use its words; a word it avoids is refused. A word you need that is not there is a proposal (a `decision`
that proposes a term), not a quiet new entry: a word one area uses goes in `<layer>/<area>/glossary.yml`, one that two areas
use in the area `shared` of their layer (`product/shared/glossary.yml`). Search before you
propose: `ogy find <words>` covers live and removed entries.


Read the sources:
- Owner's words: record what they decide first (section 5), as a short paraphrase; ogy keeps no message and no quote.
- Docs and plans give claims. Code gives guarantees: transactions, locks, idempotency, what survives a restart.
  Whatever the system must survive, read from code, or cite the document (E1-E7: 5 of 6 doc-only alarms were false).
- A fact read from code is a fact, not a decision by anyone; the owner reads those only when asked (decision
  `code-facts-are-read-by-area`).

## 2. Capture (evaluated: E8-E10)
- Write each entry with evidence: `src` (`code:<path>#<symbol>` or `doc:<commit>:<path>#<anchor>`) or `because` (a chain
  of entries that reaches one) or a decision that settles it, or the owner's yes in a review round. What the owner said
  becomes an entry through a decision they answer: read the sentence aloud first; if it would not make the owner say
  "yes, that is what I meant", ask.
- Never fill an optional slot without evidence. If you do not know a slot, leave it out and ask.
- Keep operational facts (labels, commands, what a person sees), not only structure (E6).
- Write with `ogy put`: a record or an array of records, one atomic, checked write per
  batch. Each write is checked and refused when it adds an error.
- Derive before asking (E9-E10: derived 6-8 of 8): what two sources entail, what is technical, what a stated rule
  already covers goes in with `because`. Never ask the owner what the words already settle.

## 3. Hazard pass (untested as a skill step; P16, P17 single runs)
Take every row with an effect, every read of an external fact, every external, and ask seven questions, in the
owner's wording for business rows:
1. What if it happens twice?
2. What if it stops halfway?
3. What if we cannot tell whether it happened?
4. What if what we read has changed since?
5. What if two people do it at once?
6. What if it silently does not happen?
7. How do we put it right, and by when?

Also ask of every outside fact: who keeps it true? Each cell gets an entry (`ogy kinds` lists the
kinds that hold it: `deviation`, `guard`, `timeout`, `effect`) or a decision that asks it. E9-E10: "no volunteer on shift",
"fee on a closed day" and "the reminder email fails" were missed by almost all 32 runs without this pass.

## 4. Decisions: ask, guess, hear
Run the `elicit` skill on what is still open. Every question is a `decision` entry before anyone is asked:
- **options**, each setting the entries it would create (`sets`); "no", "not now" and "removed" are an option whose
  address is `null`;
- **`guess`**: the option you recommend, with `why`. If what the owner said leans to an option without choosing it, write
  `guess.heard: {said: <a short paraphrase>}`; the card then reads "You said (paraphrased): .... Read as B." and one
  `yes` records the answer. Never put the owner's words into `why`;
- **`answer`**, only when the owner chose, with `said` (one short line, your paraphrase) and, when the owner hedged
  ("for now", "probably", "on condition that..."), a `note`, paraphrased too.
Words that fit two options, or a bare `no`, are not an answer: ask at once, while the owner is there.

## 5. Live capture (P1, untested)
When the owner speaks, record the answer with a short paraphrase at once, before your next action, and show it to the
owner in the read-back. ogy stores no messages and no quotes: `said` is one plain line in your words, fitted to the
decision; `where` names the session (`ai:claude/<session-id>`); `at` defaults to now.
- in a review round: `ogy reply "<grammar line>" --said "<paraphrase>" --where <uri> --round <id> [--note "<their hedge>"]`.
  When the owner spoke in natural words ("Fine, go ahead, I suppose."), the grammar line is your reading (`yes`) and the
  hedge goes to `--note`;
- choosing an option outside a round: `ogy answer <decision> <option> --said "<paraphrase>" --where <uri> [--note ...]`;
  one sentence deciding several questions is one `answer` per decision, each with its own paraphrase;
- a rule, a correction, a delegation: write the decision that asks it, then `answer` it with what the owner said.
Never rebuild answers from a transcript later; the second pass already missed two of sixteen. Never answer or agree
for the owner. If the owner delegates ("decide on my behalf"), that is their answer to a decision; answer under it with
`--from ai --delegated <that decision>` and list every such answer at the end as "decided by AI for you".

## 6. Proposals, "no" and removals
1. A proposal is a decision before anyone acts on it, or a new option of the decision that already asks the question.
   Prose in a consult is not kept. A consult never ends with "open points": the receiving session writes each
   proposal as a decision with a guess before it reports (P2).
2. Search before you propose: `ogy find <words>`, `ogy find --parent <address>`, `ogy history <address>`. A proposal made
   before gets an option in the old decision.
3. Deleting a mechanism or a field: list every job it did and, per job, the entry that now does it or the decision
   that drops it.
4. Remove only with `ogy remove <address> --why <decision or text>`. Never edit a `removed.yml`, never reuse an
   id. To bring something back, propose a decision built from the snapshot (`ogy find --removed`) under a new id.
5. Never edit an answer. A reversal is a new answer; the old one stays.
6. Structure (layout, layers, kinds, paths) is the owner's, and the folders `docs/kb/{constitution,product/<area>,software/<area>}`
   are mandatory:
   - Each layer has the area `shared`: only the terms, actors and sets that two of its areas use live there (`ogy move` an
     entry there when a second area starts to use it); everything else stays in the area that owns it and is linked.
   - Every area holds its `area.yml` (`says`: what it covers; `distinct`: what belongs next door). Read it before writing
     into an area; a new area brings its `area.yml` in the same `ogy put`.
   - Before recommending to remove or change structure, search the owner's earlier answers (`ogy find <words>`,
     `ogy history`). A conflict goes into the decision's `heard` (a paraphrase), so the card shows "differs".
   - "Unused in captures" is never by itself a reason to remove structure the owner asked for.
   - Ask a structural decision (`structure: true`) on its own card, never in an accept-all (`yes`, `yes all`, `decide`).

## 7. Read back
Read entries back with `ogy review` (at most 7 cards, with a count per area), in plain language, in three groups: what
the owner said, what you concluded (and from what), what you assumed (one batch to confirm or correct). The owner
replies with `yes`, `yes all` (every recommendation), `yes 1 3`, `Q1 b`, `2: <new sentence>`, `no 4` or `later`; pass it to
`ogy reply` with `--said`, your paraphrase of what they said.

## 8. Check, hand over, end the session
1. `ogy check`: no error you may fix is left. `term-not-agreed` and other waits for the owner are not yours to clear;
   show the owner the waiting count (P4).
2. `ogy dropped`: show the owner what it lists.
3. The read-back opens with "Recorded today: N answers, M with a note", then the answers you recorded live, each with its
   paraphrase, so the owner can correct or veto one; any answer given for the owner under a delegation is listed as such (P6).
A checker counterexample counts as a defect only if its trace is code-captured.

## Output
1. The entries written (addresses).
2. Owner questions: from `ogy review`, at most 7, most important first.
3. Assumed for read-back, each with its guess.
4. Hazard cells left open.

## Judge critically (owner, 2026-11-17)
When re-absorbing a product's knowledge (docs, code, the glossary), do not copy: judge. Trim words plain English
already covers, fix statements that contradict the code or other sources, merge duplicates, drop what nobody needs.
Decide on your own (the owner delegated this), record each such decision through ogy, and list them at session end for
the owner's veto. Recorded as software/writes/decision/capture-judgement.
