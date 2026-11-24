# Ontology review: the 2026-11-23 redesign tested again (2026-11-24)

Method: the `iorlas-wip:ontology-designer` audit branch (no single impulse) on the whole ontology, run by Claude Sonnet 5.5, not Fable
(the brief asked for Fable; the session model was Sonnet 5.5, so a Fable pass over this review is still worth doing). Inputs: the redesign
(`docs/research/2026-11-23-ontology-redesign.md`, ledger R/C/O/F/B/Y/D/V/X, moves M0-M9), the audiences research, `CARD-SPEC.md`, `FEEDBACK.md`,
`docs/thoughts/owner-inputs.md`, the kind files, the 12 waiting decisions. Nothing in `src/` or the kind files changed. Every proposal is
recorded as a decision or a new option (section 4); no answer was recorded for the owner.

## 1. What I verified (R1/R2: counts I ran, not read)

| claim in the redesign | result |
|---|---|
| 66 of 74 rules link to nothing | **Confirmed**: `ogy work` lists 66 `unused` rules (in 13 areas; 17 in software/ontology, 11 in software/storage, 8 in software/writes) |
| none carries a proof | **Confirmed** for the 66: 0 have `proof`; 61 have no `because` |
| (not in the redesign) what the 66 hold | **New**: 16 carry an owner agreement (`agreed:`) |
| 13 hedged answers in force | **Confirmed** (13 listed; two more files match the phrase: the confirm decision itself and `product-map`, whose hedge sits on a superseded answer) |
| `title` is accepted on a step | **Confirmed**: `common: title` in `ontology.yml`; the fixture sets it only on a quantity and a decision |
| an area may link across layers | **Confirmed**: `link_direction: later-to-earlier` (software names product) |
| `system` and `ready` are free as entry words | **Confirmed** (`ogy find system`: 25 rows, the redesign counted 17; none is a term) |
| `to` also exists on transition | **Confirmed** (`transition.to -> state`), and it matters: see N5 |
| the "row" triple is repeated | **Confirmed**: `case, choice, timeout` is written in 8 kind files and in `ontology.py` |

Not verified (redesign section F, still open): the sketch Keep refusing steps and ends (D4); `inspect.py`, `board-data.md`, the transcript, 28
`yy9` beads read by title only; the claim of "about 25" derived relations (I did not read the board code). No `ogy review` card was shown.

## 2. The ledger, item by item

Disposition is mine against the redesign's: **confirm**, **change**, **reject**. Items that only repeat another follow it.

| id | mine | reason |
|---|---|---|
| R1 intake | confirm, add detail | `evidence.doc` reads `files: [.md]` and a section; a line range also needs the file type widened (a transcript may be `.txt`). Detail for the applier, see Open 1 |
| R2 readiness | **change** | the rule conflates two things: N7 |
| R3 hats | confirm | a filter is right; nothing to store |
| R4 values and proportion | **change** | "merge with principle" cannot work per system: N2 |
| R5 "I don't know" | **change** | delegation alone decides for the owner on his hesitation: N8 (new option `parked`) |
| R6 `system` kind | confirm the kind, **change the word** | N3 (C4 levels); the kind is justified: the owner asked "is the CLI its own software?" (owner-inputs, 2026-11-23) |
| R7, R10 read-only role, utilisation | confirm defer | one person; trigger a second one |
| R8 rule scope | confirm | widening `satisfies` is needed only for rules that really bind an area; see N1 before using it as a way to un-orphan rules |
| R9 product-map | confirm | ask again; he said canvas interested him, `pages` is in force |
| R11 mark an uncovered step | confirm | derive |
| R12 areas differ by name | confirm | solved by `area.system`; nothing else |
| C1 effect value | confirm the field, **change the name** | N5 |
| C2 program reply | confirm | an enum read by `when` |
| C3 unused actor | confirm | decision `unused-actor-entity-handler` |
| C4, C10 derived relations | **change** | N6 (smaller design: reverse by field word; declare only multi-hop) |
| C5-C9, C12, C13, F1, F3, F4, F7, F12 | confirm | UI-only or guidance |
| C11 program actor owed a dependency | **change** | false positive on every caller: N6b |
| O1-O22, X1, X2 | confirm | derive in the engine, UI-only otherwise |
| F2 rename `realizes` | confirm reject | ArchiMate uses *realization* for all three (workflow to capability, capability to goal, dependency to actor); the board's wrong word was a viewer bug |
| F13, B10, B18, Y9, V5 | confirm | checks and small fields |
| B1, B12, D1, D2, V3, V4, M9 | confirm | hygiene in O |
| B28 remove the 66 unlinked rules | **change** | N1 (reads the answer `keep-checkable` too narrowly, loses 16 agreements) |
| Y8 rules claiming a missing check | confirm | build or remove, with the B28 triage |
| Y1, Y2, Y3-Y5, Y10-Y14 | confirm defer | triggers stand; Y13 and Y14 still unread |
| D3 `where: ui` | confirm | a click has no honest address |
| D4 sketch Keep | defer, not reproduced | not run in this review either |
| D5 `uneven-options` | confirm keep | |
| Decisions to record 1-13 (E) | confirm, with the options in section 4 added to them | |
| Stage order D (0..6) | **change** | stage 1 (rule removal) must follow the triage of N1, and stage 3 `system` needs the word of N3 first |

Too timid: the redesign leaves the repeated row triple as a glossary word only (N4). Too bold: removing 66 rules in batches (N1) and storing a
per-system proportion through the constitution (N2). Nothing in the ledger needed a flat reject.

## 3. New findings (audit checks A-M applied)

Severity from the audit ranking: 1 law breach, 2 conflict, 3 smell.

**N1. The 66 unlinked rules are not "rules nothing can catch" (severity 2, check L/G).**
Evidence: the sampled rules (every sixth: `glossary-is-an-ontology-kind`, `area-entry`, `address-keeps-the-area`, `layers-are-mandatory`,
`agreement-lives-on-the-entry`, `write-is-put-back-on-a-new-error` ...) state what the engine's loader and checks already enforce; 0 of 66 have a
proof; 16 carry an owner agreement; 61 cite no decision. The answer `keep-checkable` says a rule stays "when a handler, interface, test or check *can*
satisfy it". The redesign read "can" as "is linked", and the reason they are unlinked is that the engine's own behaviour (check, loader, write path)
is barely modelled as handlers and interfaces in the KB. Removing them (M6) turns that missing model into deleted agreed text, against AGENTS.md
("remove only when a requirement changes, never to reorganise") and loses 16 agreements that a `put` cannot restore. Smallest fix: a triage, rule by
rule: link to a modelled engine behaviour where one exists or can be written, and remove with its own reason only a rule nothing could catch.
Recorded as option `triage-by-catchability` on `rules-need-a-check`.

**N2. A system's proportion cannot live in the constitution (severity 2, check K/L).**
`constitution/` is one fixed set printed to every agent; two systems of different proportion (a proof of concept and a product) cannot cite different
principles with `because`. Today there is one real case (ogy), so a field would be early (rule of three). Recorded as decision `proportion-home`,
recommended `not-now`.

**N3. `system` is the wrong C4 level for what the owner asked about (severity 3, check A/K).**
In C4, ogy is one software system; the CLI, the board and the MCP server are its containers. The redesign calls the new kind "a C4 software system"
and counts "about three systems" in ogy's own KB, which are containers. Naming the kind `system` and then putting the CLI and the board under it
sets the wrong word against the owner's source (he named C4). Smallest fix: a fourth option on `system-word`: `container`, one level, no nesting field
until a second level has a real case. Recorded.

**N4. The row triple wants a parent (severity 3, check F/E, re-layer up).**
`case, choice, timeout` is repeated in 8 kind files and `ontology.py`; handler `performs`, rule scope, effect parent and 3 checks all name the
triple. Three children, queried together, shared fields (`satisfies`, `then`, `effects`, handler): the conditions for a shared parent hold. A merge
into one kind fails the differentia test (a button, a condition and a clock have different required fields and identities). The redesign's
term-only `row` leaves the triple in the kind files. Recorded as decision `rows-are-a-family` (engine support not checked).

**N5. `effect.to` is a homonym, and `value` is a dropped field (severity 2, check A).**
`transition.to` links a state; `effect.to` would hold an expression. `effect.yml` says `dropped: [value]`, so reusing `value` makes `ogy migrate`
print a drop. Smallest fix: a name that is neither: `becomes`. Recorded as option `becomes-on-write` on `effect-value`.

**N6. Derived relations: a smaller design exists (severity 3, check I/J).**
`ogy show` already prints every reverse link ("referenced by X (because)"). Most of the "about 25" derived relations are the reverse of one link
(actor of a step, offers of an interface), possibly filtered. Declaring a `derived:` block for all of them copies `requires` and adds a block a viewer
alone reads, against `rigid-where-checked`. Smaller: the engine names every reverse link by its field word (which is also what the owner asked: use
only the ontology's own words, feedback 2), and only multi-hop paths (actor to interface through a step; limits through `performs` and `uses`) are
declared. Recorded as option `reverse-by-field-word` on `derived-relations-declared`.
**N6b. C11 is wrong as worded (severity 2).** "A program actor with no dependency is owed work" would flag every actor that calls us (an MCP client,
a scheduler: `actor.yml` says program includes "an MCP client calling a tool"; the two program actors in software are such callers). The direction is
in the links. Recorded as decision `program-actor-direction`, recommended `derive`.

**N7. Readiness counts "unagreed" as "missing" (severity 2, check M).**
The redesign marks an entry waiting when it is decided by AI or changed since agreed (43 entries, 37 of them in software/viewing). The owner's wish was
"no missing decisions". An AI-decided entry has a decision; it lacks a yes. Mixing both means "no missing decisions" will not read true until every
yes is in. Smallest fix: wait only on an unanswered decision, and count unagreed apart. Recorded as option `computed-unanswered-only`.

**N8. "I do not know" as delegation decides on hesitation (severity 3).**
AGENTS.md: "words that fit two options ... ask at once", and an owner's "I do not know" is more often "not yet" than "you pick". A third outcome that
leaves the question waiting costs nothing and decides nothing. Recorded as option `parked` on `dont-know-answer`.

Checks run with nothing found: **B** differentia (goal, capability, workflow: about 6 goals and 18 capabilities counted by hand, many-to-one, not duplicates);
**D** rigidity (no kind is a role or a state; `actor.nature` is a value); **E** is-a (the ontology has no inheritance); **H** overload (`decision`
carries question and options by design; the only overload is the rule of N1); **K** contexts (one language by decision, `area-word`).
Not run: **G** dead weight beyond the rules (instance counts per field were not made).

## 4. What is recorded (all unanswered; the owner is asked from `ogy review`)

New options: `software/ontology/decision/derived-relations-declared/option/reverse-by-field-word`; `.../readiness-computed/option/computed-unanswered-only`;
`.../effect-value/option/becomes-on-write`; `.../system-word/option/container`; `product/capture/decision/dont-know-answer/option/parked`;
`software/ontology/decision/rules-need-a-check/option/triage-by-catchability` (that decision is answered; the new option is a proposal to refine the
answer, not an edit of it).
New decisions with proposals: `software/ontology/decision/rows-are-a-family`, `program-actor-direction`, `proportion-home`.

## 5. Open (detail questions, recommended answers)

1. Widen `doc` evidence to `.txt` and line ranges together with the line-range change, or only line ranges for `.md`? Recommended: widen both.
2. The old stage order: run the triage of N1 before stage 1, and choose the word of N3 before stage 3. Recommended: yes.
3. Run the same review again with Fable on this document (the brief asked for it; this run used Sonnet 5.5).

Eval: untested; this is a design review, no skill, ontology or checker changed (AGENTS.md: ledger only needed when one does).
