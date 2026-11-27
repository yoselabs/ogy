---
name: ogy-capture
description: Turn an owner's words, docs or code into entries of an ogy knowledge base (software ontology), find what is
  missing, and ask the owner the fewest questions that settle the most. Use when capturing or amending requirements.
---

# OGY capture (draft, 2026-11-17)

Status: **proposed**. The commands this skill names are the ones in the [README](../../README.md) table; `ogy put` (one
batch write for create and update), `proposal.heard`, `answer --said --where`, `answer.note` and a required
`remove --why` are being built and are **untested here**. Steps with no eval behind them are marked untested.
The skill holds the flow; the ontology (`ogy kinds [kind]`) holds the shapes; `ogy check` holds the lints. Never write
YAML by hand and never read a spec to learn a shape: ask `ogy kinds`. Read `ogy kinds <kind>` before you create the first
entry of that kind in a session: its guidance says when to use it rather than a neighbour (an actor, a state or an
attribute; a case or a choice's `when`; `satisfies` or `because`; an `interface`, where an actor reaches the product, or the `handler` behind it). `ogy kinds --map` shows the whole ontology and its rules (untested).

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
- What the code does today is an entry with `src` (`code:<path>#<symbol>`), written as it is and agreed in a review
  round; it is never a decision, because nobody chose it in front of you. The owner reads those only when asked
  (decision `code-facts-are-read-by-area`).

## 2. Capture (evaluated: E8-E10)
- Write each entry with evidence: `src` (`code:<path>#<symbol>` or `doc:<commit>:<path>#<anchor>`) or `because` (a principle,
  a decision or a pain: the reason, never a source) or a decision that settles it, or the owner's yes in a review round. What the owner said
  becomes an entry through a decision they answer: read the sentence aloud first; if it would not make the owner say
  "yes, that is what I meant", ask.
- A pain (what goes wrong for the people the product serves) is its own entry, one sentence, written once (`ogy find`
  first): a goal cites every pain it relieves, a decision the pain that raised it. Several pains in one text are several
  entries. Read from code, write the guessed pain as a pain, never as a decision: the goal owes its reason until the owner
  agrees to that pain by its own card (decision product/capture/decision/pain-kind).
- Never fill an optional slot without evidence. If you do not know a slot, leave it out and ask.
- Keep operational facts (labels, commands, what a person sees), not only structure (E6).
- Write with `ogy put`: a record or an array of records, one atomic, checked write per
  batch. Each write is checked and refused when it adds an error.
- Derive before asking (E9-E10: derived 6-8 of 8): what two sources entail, what is technical, what a stated rule
  already covers is held to it (`satisfies` on behaviour, `constrains` from the rule to the data). Never ask the owner what the words already settle.

## 3. Hazard pass (untested as a skill step; P16, P17 single runs)
Take every row with an effect, every read of an outside fact, every dependency, and ask six questions, in the
owner's wording for business rows:
1. What if it happens twice?
2. What if it stops halfway?
3. What if what we read has changed since?
4. What if two people do it at once?
5. What if it silently does not happen?
6. How do we put it right, and by when?

No question asks what happens when an outside system does not answer: `ogy work` lists each row that tells a program
actor or a dependency as `no-answer-path` until it has one (a timeout, or a case ending in failure) and satisfies a rule
on whether a repeat is safe.

Also ask of every outside fact: who keeps it true? Each cell gets an entry (`ogy kinds` lists the
kinds that hold it: `workaround`, `case`, `timeout`, `effect`) or a decision that asks it. E9-E10: "no volunteer on shift",
"fee on a closed day" and "the reminder email fails" were missed by almost all 32 runs without this pass.

Work goes in stages, one layer at a time (decision `a-layer-commits-alone`). Stop at your own layer: the product says what the
business needs, and the handler, interface or dependency a row will need is the next layer's, listed as work, never a
question this pass must settle first. Hand over with `ogy work <your layer>` (what your layer still owes) and
`ogy work <next layer>` (what you leave to it) (untested).

## 4. Decisions: ask, propose, hear
Run the `elicit` skill on what is still open. A decision needs an alternative the owner could pick: at least two
options a reasonable owner might choose. What the code does and nobody would choose otherwise is an entry with `src`
(section 1), not a decision with one real option. Every question is a `decision` entry before anyone is asked:
- **options**, each setting the entries it would create (`sets`); "no", "not now" and "removed" are an option whose
  address is `null`;
- **`proposal`**: the option you recommend, with `why`. If what the owner said leans to an option without choosing it, write
  `proposal.heard: <a short paraphrase>`; the card then reads "You said (paraphrased): .... Read as B." and one
  `yes` records the answer. Never put the owner's words into `why`;
- **`answer`**, only when the owner chose, with `said` (one short line, your paraphrase) and, when the owner hedged
  ("for now", "probably", "on condition that..."), a `note`, paraphrased too.
Words that fit two options, or a bare `no`, are not an answer: ask at once, while the owner is there.
A new principle (untested as a skill step) is checked against every principle first (`ogy glossary`): one that says the same
is sharpened, not repeated; one it covers is absorbed and removed with the decision as its reason. Its decision has one option
per fate: add it, replace a named principle, sharpen a named principle, or none (`null`). The printed sentences stay within the
budget `software/ontology/quantity/constitution-budget`. Two principles that pull apart on a real decision are a reason to make
both more concrete: that decision cites both and proposes a sharper sentence for each, not only a question to the owner.

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
`--delegated <that decision>` and list every such answer at the end as "decided by AI for you".

## 6. Proposals, "no" and removals
1. A proposal is a decision before anyone acts on it, or a new option of the decision that already asks the question.
   Prose in a consult is not kept. A consult never ends with "open points": the receiving session writes each
   proposal as a decision with a proposal part before it reports (P2).
2. Search before you propose: `ogy find <words>`, `ogy find --parent <address>`, `ogy history <address>`. A proposal made
   before gets an option in the old decision.
3. Deleting a mechanism or a field: list every job it did and, per job, the entry that now does it or the decision
   that drops it.
4. Remove only with `ogy remove <address> --why <decision or text>`. Never edit a `removed.yml`, never reuse an
   id. To bring something back, propose a decision built from the snapshot (`ogy find --removed`) under a new id.
5. Never edit an answer. A reversal is a new answer; the old one stays.
6. Structure (layout, layers, kinds, paths) is the owner's, and the folders `docs/kb/{constitution,product/<area>,software/<area>}`
   are mandatory:
   - Each layer has the area `shared`: only the terms, actors and enums that two of its areas use live there (`ogy move` an
     entry there when a second area starts to use it); everything else stays in the area that owns it and is linked.
   - Every area holds its `area.yml` (`says`: what it covers; `unlike`: what belongs next door). Read it before writing
     into an area; a new area brings its `area.yml` in the same `ogy put`.
   - Before recommending to remove or change structure, search the owner's earlier answers (`ogy find <words>`,
     `ogy history`). A conflict goes into the proposal's `heard` (a paraphrase), so the card shows "You said (paraphrased): ....".
   - "Unused in captures" is never by itself a reason to remove structure the owner asked for.
   - A decision asked again is answered with its own letter, never in an accept-all (`yes`, `yes all`, `decide`).

## 7. Read back
Read entries back with `ogy review` (at most 7 cards, with a count per area), in plain language, in three groups: what
the owner said, what you concluded (and from what), what you proposed (one batch to confirm or correct). The owner
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
3. Proposed for read-back: each open decision with its proposal.
4. Hazard cells left open.

## Judge critically (owner, 2026-11-17)
When re-absorbing a product's knowledge (docs, code, the glossary), do not copy: judge. Trim words plain English
already covers, fix statements that contradict the code or other sources, merge duplicates, drop what nobody needs.
Decide on your own (the owner delegated this), record each such decision through ogy, and list them at session end for
the owner's veto. Recorded as software/writes/decision/capture-judgement.
