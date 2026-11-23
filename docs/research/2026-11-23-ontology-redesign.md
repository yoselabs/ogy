# Ontology redesign: one consolidated proposal (Fable, read-only, 2026-11-23)

Nothing was written. Every change is a proposal until the owner answers it in `ogy review`.

Verdict:
- The ontology needs **one new kind** (`system`), **two new fields** (`area.system`, `effect.to`), **one wider link** (`satisfies` from area and system), **eight small new checks** and **one new declaration block** (`derived:` in kind files).
- Almost everything else collected is already in the graph. It needs to be **computed once in the engine**, not in board JavaScript.
- The worst fault is not a missing kind. It is the `rule` kind: 66 of 74 rules link to nothing (`rules-need-a-check`).
- Many beads are behind the KB. The KB says the owner answered them; 13 answers in force carry the hedge "Yes, I guess".
- Three targets are kept apart: **K** = shipped kind files, **O** = ogy's own KB entries, **T** = the tool-library fixture.

## A. Ledger

"§" is the move in B. "KB:" is the recorded state where a bead is behind. Items that only repeat another are folded into its source cell.

| id | source | item | disposition | § |
|---|---|---|---|---|
| R1 | research A2.1; owner | No raw input entry; no link from an entry to its passage | change (`doc:` takes line ranges) + process | M3 |
| R2 | A2.2; owner | No "not ready for design" mark; unready parts hidden; "no missing decisions" | derive-not-store | M4 |
| R3 | A2.3; owner | No audience or hat; points of view on one KB | derive (hat = layer filter); audiences as actors in O | M2 |
| R4 | A2.4; A1; owner | Profile, values, proportion (proof of concept, startup, product) | merge with `principle`: a system cites them with `because` | M2 |
| R5 | A2.5 | "I don't know" answer | process (delegated answer) | M2 |
| R6 | A2.6; owner; ful.2, ful.29; validation | No kind for the program we ship; "is the CLI its own software?"; contexts answered, nothing built | add kind `system` | M1 |
| R7 | A2.7; owner | Read-only role; engineer cannot change the KB | defer (one person; `answer.by` is additive later) | M2 |
| R8 | A2.8; owner | A rule for everything, one part, or one endpoint | add link (`satisfies` from area, system) | M6 |
| R9 | research | `product-map`: the redraw. KB: `pages` in force, firm, 2026-11-22; a `canvas` option exists | process: ask again; no new option needed | E |
| R10 | A1 | Levels of utilisation = delegation by scope | defer (trigger: a second person) | M2 |
| R11 | N3; owner | Mark a step no software covers | derive (work `unserved`, row with no handler) | M8 |
| R12 | A3 | Software areas do not match product areas by name | add link (both name one system) | M1 |
| C1 | card spec 7.1; feedback 9 | Effect has no value | add field `effect.to` | M5 |
| C2 | 7.2; yy9.29 M2 | What a program actor sends back | process (the reply is an enum `when` reads) | M5 |
| C3 | 7.3 | No "an actor nothing links to" | new check | M6 |
| C4 | 7.4 | Actor to interface is derived only | derive, declared once | M8 |
| C5 | 7.5 | `shows`/`accepts`/`offers` have no order or primary | defer (`view-hint-fields`: viewer-only for now) | M0 |
| C6 | 7.6 | Attribute example or format | remove the idea: text in `says` (`term.example` was dropped before) | M5 |
| C7 | 7.7 | Goal has no measure | defer; guidance now | M7 |
| C8 | 7.8 | Workflow importance or frequency | derive a rank; no field | M7 |
| C9 | 7.9; feedback 5, 8; ful.22 | No short step name; names inconsistent | process: `title` exists on every kind; the skill fills it | M5 |
| C10 | spec 3, 4 | About 25 relations each card derives in JavaScript | derive-not-store, declared in kind files | M8 |
| C11 | spec 4 | Program actor with no dependency is owed work | derive | M8 |
| C12 | spec 1 | A gap shows the rule's own sentence | UI-only (reads `requires.error`) | M8 |
| C13 | spec 1 | Area is a frame, never a card | UI-only; the system is the outer frame | M1 |
| O1 | owner | No connection between product and software | add link + derive | M1, M8 |
| O3 | owner | "I go into interface, I see nothing" | UI-only: the links exist | M8 |
| O4 | owner | A decision does not show what it impacts | derive | M7 |
| O5 | owner | "Figma for product people" | UI-only; layout deferred (C5) | M0 |
| O7 | owner | "We did not think about why, outcomes" | derive (why chain in the engine) | M7 |
| O9 | owner | Live listening on a call | process (skill) | M3 |
| O12 | owner | AI proposes a design; see what it connects to | keep: sketch, then proposal on a decision (`staged-changes-home`) | M4 |
| O17 | owner | AI-factory operator sees ready, running, blocked | derive | M4 |
| O18 | owner | One person all hats; a business-only person | process (delegation) | M2 |
| O19 | owner | Questions tuned to the person | derive from the decision's layer; skill | M2 |
| O20 | owner | C4, ArchiMate, IcePanel | change: system = C4 software system; no new layer | M1 |
| O22 | owner | "Keep all my inputs" | process: an inputs folder cited by `doc:` | M3 |
| F1 | feedback 1, 6, 10, 11, 14; ful.19 | Labels, icons, badges, style | UI-only | M0 |
| F2 | feedback 2; this read | "serves goal" against `realizes`; `realizes` has three meanings | UI-only; rename considered and rejected | C |
| F3 | feedback 3 | Capability and goal repeat each other | process (guidance); keep both kinds | M7 |
| F4 | feedback 4; ful.21 | Split a call into call then handle? | UI-only; keep one calling step | M5 |
| F7 | feedback 7 | Actor must not decide its own drawing | UI-only (viewer owns renderers) | M8 |
| F12 | feedback 12 | State and case styled the same | UI-only; they are different kinds | M0 |
| F13 | feedback 13 | "Returned, and no one handles return" | new check + UI | M5 |
| B1 | ful.1 | `review --all`. KB: `review-all-fills-the-round` answered, hedged | process: confirm; no ontology change | E |
| B3 | ful.3 | `map-layers`. KB: answered, hedged | derive ("what limits a step") | M8 |
| B4 | ful.4 | close-loan listens to a transition nothing fires | change in T, after the owner decides | M5 |
| B5 | ful.5 | Problems view | derive from work + new checks | M8 |
| B8 | ful.8, ful.17 | Rendering spec, style book. KB: `view-contract`, `style-book-home` hedged; `view-hint-fields` firm: viewer-only for now | defer (his trigger: a stable web version) | M0 |
| B10 | ful.10 | Placeholders in `invoked_as`. KB: `checked`, hedged | new check | M5 |
| B12 | ful.12 | "Open proposals". KB: all answered | process: close the bead | M9 |
| B14 | ful.14, ful.15 | Problem a workflow solves; justify everything. KB: both answered, hedged | derive, in the engine | M7 |
| B16 | ful.16 | Parity. KB: `viewer-is-an-interface` = declared, hedged | add entries in O; derive the gap | M8 |
| B18 | ful.18 | Several lifecycles, final states, once-only | new check; grouping deferred | M5 |
| B23 | ful.23 | Actor cards | UI-only, fed by M8 | M8 |
| B28 | ful.28; yy9.81; validation | 66 unlinked rules (84 when yy9.81 was written). KB: `keep-checkable`, firm | remove (with `--why` that decision) | M6 |
| B30 | ful.6, .7, .9, .11, .13, .20, .27, .30; ibt | Layout, immersion, real board, decision mode, answer POST, snapshot | UI-only | M0 |
| B31 | 8 answered board decisions | agent-points-owner, agent-session-view, answer-drawer, board-answers-in-v1, click-is-an-answer, board-follows-agent-calls, frontend-vendored-libraries, view-state-store | UI-only; no ontology change | M0 |
| Y1 | yy9.12 | Said, derived, assumed on every entry | merge with computed status + `src` + `because` | M3 |
| Y2 | yy9.15, .39 | Quote or message kind | defer (parked by the owner; KB keeps no quotes) | M3 |
| Y3 | yy9.1, .4, .2 | Hazard kind, platform layer, repeat promise as a value | defer (triggers are on the beads) | M0 |
| Y4 | yy9.29 M7 | One trigger per workflow | defer | M0 |
| Y5 | yy9.35, .40, .41 | Generic engine, repository kinds, guide renderer | defer (`repository-kinds`: not now) | M0 |
| Y6 | yy9.42 | Field audit: too many fields | process: every add here names its reader | C |
| Y7 | yy9.46, .61 | A rule that constrains nothing is an error. KB: `unused-is-work` = work, firm | defer (answer stands) | C |
| Y8 | yy9.62, .87 | Two rules claim a check that does not exist | remove or build, in the B28 batch | M6 |
| Y9 | yy9.69, .74 | `says` optional on end and state | change | M5 |
| Y10 | yy9.73 | An interface may realize a capability | defer (`inspection-steps-are-modelled` went the other way) | M0 |
| Y11 | yy9.84-.86, .76, .33 | Held lints; option.label; disposal | defer (triggers stand) | M0 |
| Y12 | yy9.8 | Tray shape: the ontology shows the empty slot | merge with M8 (gaps are declared requirements) | M8 |
| Y13 | yy9.21 | Twelve findings F1-F12 | defer: not read (see F) | M0 |
| Y14 | 33 yy9 beads, numbers in F | Process, eval and tooling threads | defer: titles only read | M0 |
| D1 | status | 37 entries decided by AI and unagreed (27 `software/viewing`, 10 `product/inspection`) | process: one review round | M9 |
| D2 | KB | 13 hedged answers in force | process: confirm in a round | E |
| D3 | `answer.yml` | `where` takes only ai, bd, path | change: add `ui` | M3 |
| D4 | brief | Sketch Keep cannot write steps or ends | defer: not reproduced (see F) | M4 |
| D5 | `settle.py` | `uneven-options` | keep; the sketch tool fills the `null`s | C |
| V3 | validation | Avoided word "open" in KB text | process: cleanup in O | M9 |
| V4 | validation | Interface `view` says `ogy serve`; its proof is named "writes the page"; `view-server` overlaps | change in O | M9 |
| V5 | this read | "row" is used in six rule sentences and is no term | add entry in O (term) | M5 |
| X1 | board code | Why chain, option reach, standing, owed, "fired by", "would touch" computed for the board | derive in the engine, not the page | M7, M8 |
| X2 | board-data | Spotlight and sketch state | UI-only; never in the KB | M0 |

## B. The design

### Current and proposed topology

```
CURRENT
constitution  principle
product   area · goal ◄realizes─ capability ◄realizes─ workflow ─ step ─ choice|case|timeout ─ effect(do,on)
          actor ◄for─ goal · entity ─ attribute, state, transition · enum quantity rule term decision
software  area · interface ─serves► step ─offers► choice ─shows/accepts► entity
          handler ─performs► row ─uses► dependency ─realizes► actor · setting rule decision
          (which product area a software area builds: computed, printed nowhere; 66 rules float)

PROPOSED
constitution  principle
product   SYSTEM ◄system─ area (both layers) · system ─satisfies► rule ─because► principle
          goal ◄─ capability ◄─ workflow ─ step ─ row ─ effect(do, on, TO)
          actor (unused check) · entity ─ state (reached check), transition
software  as today · area ─satisfies► rule · rules: linked or gone
computed  ready / waits on · why chain · derived relations (declared in kind files) · coverage · limits
```

### M1. `system`: what we ship (R6, R12, C13, O1, O20)

**Problem.** `area` is a topic folder. Nothing says "the engine is one thing, the board another". Product area `inspection` and software areas `viewing` and `cli` are tied only by links no command prints.

**Change (K).**
- Kind `system`: one thing the owner ships and names. Field `says` (required). Shape `list`, file `systems.yml`, layer `product`, home `product/shared`. Like a C4 software system. Unlike an area (a topic) or an actor of nature program (someone else's).
- Link `area.system -> system` on areas of both layers. Software names product, so `link_direction` holds. A `shared` area names none.
- "System step" then reads correctly: the system of that workflow's area acts.

**Why a kind, not a word on the area.** His question needs a sentence to read, a card to open, and a holder for rules (M6) and principles (M2).

**Replaces.** The unbuilt "context". The glossary stays one language.

**Migration.** Additive. O: about three systems and a link on 18 areas. T: one system `library` on both `lending` areas; `test_tool_library` sees `system.says` and `area.system` filled.

**Checks.** An area names a system: work `unused` (not a finding). A system no area names: `unused`.

**Then computed.** One frame per system, product areas above its software areas. A link between two systems is a boundary stub.

### M2. Hats and audiences: no ontology change (R3-R5, R7, R10, O18, O19)

- **Hat** = a filter, never a permission. Business: product layer. Design: both layers plus readiness. Build: software layer plus work and proofs. A decision's layer says whose question it is.
- **Audiences** are actors in O (`analyst`, `architect`, `engineer`, `operator`, nature human): "different permitted actions make a new actor". Goals name them with `for`.
- **"I don't know"**: one standing decision per KB, "when the owner does not know, may the agent decide that one question?". After a yes, the click is `ogy answer --delegated <that decision>` with a `note`. `ogy dropped` already lists such answers for a veto.
- **Values and proportion**: a system cites principles with the common `because`.
- **Deferred, additive:** `answer.by -> actor`; delegation limited to a layer.

### M3. Intake (R1, O9, O22, Y1, Y2, D3)

**Problem.** `src` takes `doc:<commit>:<path>#<anchor>`: Markdown, a heading at the finest. A transcript has no headings.

**Change (K, `ontology.yml`).** `evidence.doc` reads a section or a line range, `#L10-L14`; the pinned commit keeps lines stable. `answer.where` gains the scheme `ui`.

**Process.** Raw inputs live in the repository outside the KB, as `owner-inputs.md` does. The KB holds a pointer and a paraphrase, never the words. A stakeholder's sentence is an input; only the person at the desk answers.

**No `input` kind.** "New from this input" is every entry whose `src` names that file.

**T.** One entry with a line-range `src`.

### M4. Readiness: computed, never stored (R2, O12, O17, D4)

**Definition.** An entry **waits** when (1) an unanswered decision names it in `sets` or is cited by its `because`; or (2) `ogy status` classes it "decided by AI" or "changed since agreed"; or (3) one of its parts, or an entry its rows name in `on` or `when`, waits. Else it is **ready**. Entries from code or docs, and areas, are never held by (2).

Today (1) marks nothing: 0 questions. (2) marks 43 entries directly: 37 decided by AI, 6 changed.

**Change.** `ready` joins `reserved.computed`; one glossary term. `ogy work software` lists a row owed for a waiting product entry apart, with the address it waits on. `ogy status` counts ready per area.

**Then computed.** The design hat greys waiting product parts with the reason. "No missing decisions" = nothing waits in the system.

### M5. Flow and data precision (C1, C2, C6, C9, F4, F13, B4, B10, B18, Y9, V5)

1. **`effect.to`** (K): an expression (text plus the links it reads, the type of `when` and `derived`), only with `do: write`. A changed quantity it reads makes the row work. `value` was dropped from effect in a field cut (commit b6d3470); this brings the fact back with a reader.
2. **State reached** (K): a state no transition leads to is `unused`. Final states stay computed. A second lifecycle is an attribute `of` an enum, or its own entity.
3. **Calling step stays one step** with `covers_ends`, as a BPMN call activity.
4. **Program reply** (guidance): an enum the next case's `when` reads.
5. **`title` on steps** (skill, T).
6. **`says` optional on end and state** (K).
7. **Command inputs** (K): each placeholder in `invoked_as` matches an `accepts`.
8. **Term `row`** (O): a choice, case or timeout of a step. The three kinds stay.
9. **close-loan** (T): after the owner decides.

**T.** Fill `effect.to` and step `title`. `UNEXERCISED` stays empty.

### M6. Rules: linked or gone, and scope (R8, C3, B28, Y8)

- **O:** remove the unlinked rules in batches, `ogy remove --why software/ontology/decision/rules-need-a-check`. `decision-stands-alone` already says the chosen option is the record.
- **K:** `satisfies` may also come from `area` and `system`; every behaviour entry inside is then held to the rule (computed). Scope becomes: system, area, interface, row.
- **K, fix-the-class:** `unused` work for an actor, an entity, and a handler that performs nothing.
- An unused rule stays work, as answered. The capture skill stops writing mirror rules.

**T.** `WORK` in `test_tool_library.py` may gain `unused` rows from the three new checks. T keeps two unused rules on purpose; they stay.

### M7. Why and impact (C7, C8, F3, O4, O7, B14, X1)

- **`ogy why <address>`**: the chain to goal and principle that `software/viewing/rule/typed-reasons` describes, as one engine operation for CLI, MCP and board.
- **Decision impact**: `sets` plus every entry citing the decision with `because`. A decision with neither says "sets nothing".
- **Goal**: `says` states the result and how one knows it is reached. No `pain` or `measure` field until a check reads one.
- **Capability stays**: the feature level between goal and workflow.

### M8. Derived relations declared once (C4, C10-C12, O3, F7, B3, B5, B16, B23, R11, Y12, X1)

**Problem.** Requirements are declared in kind files, "never in Python". Derived relations are not, so the board re-invents acts in, told by, fired by, changed by, with its own words.

**Change (K).** A `derived:` block per kind: a name and a path in the hop syntax of `requires`, for example on actor `acts_in: ["<-actor"]`, `told_by: ["<-on?do=tell"]`. `kindlint` validates paths; inspection emits them; names join `reserved.computed`.

This is meaning, not drawing. Icons, order and layout stay in the viewer.

**Then computed.** Coverage, the problems view, "what limits this step" (through `satisfies`, `performs`, `uses`), parity, every lab 29C card.

### M9. Hygiene in O (B12, D1, V3, V4)

One review round for the 37 entries. Reword interface `view`; resolve its overlap with `view-server`. Close answered beads.

### M0. Not now

Deferred rows keep their triggers.

## C. Conflicts and picks

1. **Removing mirror rules against decision impact.** They were what many decisions "settled". Pick: remove. A false target is worse than "sets nothing".
2. **yy9.46 (unused rule is an error) against `unused-is-work`.** Pick: his answer. T also keeps unused rules and must pass a landing check.
3. **`effect.to` against "too many fields".** Pick: add. It has a reader, and he asked for the value twice.
4. **A `system` kind against his answer `area-field`, and against `examples-before-kinds`.** Pick: the kind, as a new option on `context-form`.
5. **Scope `satisfies` against `rule-constrains`** ("satisfies only for behaviour kinds"). Pick: widen, as a new option there. An area or system holds behaviour.
6. **Renaming `dependency.realizes`.** Rejected. `dependency-realizes-actor` is a firm answer, and "reaches" already means flow and impact.
7. **Audience actors against `who-may-say-yes`** ("a second human actor is a finding"; no check exists). Pick: actors; the sentence is reworded in the M6 batch.
8. **Intake against "no quotes".** Pick: a pointer to pinned lines.
9. **Rendering in the ontology against viewer-only.** Pick: meaning in kind files, drawing in the viewer.
10. **Readiness hides against one person seeing all.** Pick: a hat greys; it never forbids.
11. **`uneven-options` against sketched alternatives.** Pick: keep. "Not mentioned" must never mean "does not exist".
12. **Corners cut for one person:** no identity on answers, no permissions, no profile. All additive later. Not cut: `system`, readiness, line-range `src`, declared derivations.

## D. Adoption plan

| Stage | Content | Eval for the ledger | Unblocks |
|---|---|---|---|
| 0 | M9; confirm hedged answers; term `row` | untested (KB only) | honest data |
| 1 | M6 rule removal; three unused checks | untested as an agent eval; count of work-left rows before and after | coverage view without noise |
| 2 | M8 `derived:`, M7 `ogy why`, M4 readiness | untested as an agent eval; machine check: inspection's derived relations equal lab 29C's on T | lab 29C cards; coverage view; hats |
| 3 | M1 `system`; M6 scope | new eval. Question: does an agent place a requirement "for the whole product" correctly? Arms: scope link against today. Metric: misplaced rules per scenario | system frames; scale test on O |
| 4 | M5 | new eval. Question: do captured writes carry their value? Arms: `effect.to` against today, tool-library scenario. Metric: write effects with a correct value | effect badges; lifecycle graph |
| 5 | M3 | ledger thread 2 (mis-cites). Arms: section against line-range `src`. Metric: mis-cites per citation | intake mock on real input |
| 6 | M2 | untested (process) | "one question, three people" |

Each stage keeps `just check`, `just test` and `ogy check` green alone.

## E. Decisions to record (not answered here)

Most set no entries: the chosen option is the record.

**Round 0: confirm the 13 hedged answers in force.** `contexts-above-areas`, `style-book-home`, `view-contract`, `derive-justification`, `command-inputs-are-accepted`, `human-decision-mode`, `map-layers`, `map-modes`, `preview-a-new-requirement`, `why-chain-on-board`, `view-delivery`, `review-all-fills-the-round`, `viewer-is-an-interface`. Also ask `product-map` again: `pages` is in force, and on 2026-11-23 he said the canvas was more interesting.

**Round 1: shape.**
1. *`context-form`, new option* (prior: `area-field`, word not chosen). What do areas group into? (a) `area-field`: a word on the area. (b) `system-kind`: a kind with a sentence; areas link to it. (c) `defer`. Recommended b.
2. *The word.* `system`, `product` or `program`. Recommended `system`: it fits "system step" and "outside system".
3. *Readiness.* (a) computed; (b) a stored mark; (c) no. Recommended a: a stored mark drifts.
4. *Derived relations.* (a) declared in kind files; (b) each viewer computes. Recommended a.
5. *`rule-constrains`, new option* (prior: `split`). (a) keep; (b) area and system may `satisfies`; (c) a new kind for such requirements. Recommended b.

**Round 2: precision.**
6. *Effect value.* (a) `to` on a write; (b) text in the row's `says`; (c) no. Recommended a.
7. *Lifecycles.* (a) the reached check only; (b) add a lifecycle grouping; (c) no. Recommended a.
8. *close-loan (T).* (a) it performs return; (b) it reacts, and another workflow fires return. Recommended a.
9. *Unused checks* for actor, entity, handler: yes or no. Recommended yes.

**Round 3: people and intake.**
10. *Audiences.* (a) four actors now; (b) not now. Both name the same four addresses in `product/shared/actor/`; b sets them `null`. Recommended a.
11. *"I don't know".* (a) a standing delegation; (b) a new answer field; (c) he always chooses. Recommended a.
12. *Intake.* (a) inputs folder plus line-range `src`; (b) an input kind in the KB; (c) inputs stay outside Git. Recommended a.
13. *`where: ui`.* yes or no. Recommended yes.

## F. Not verified, not read

- **Fable's earlier ontology validation** (source 8): text not found in `docs` or the session scratchpad. V3 and V4 come from the brief and the KB.
- **Sketch Keep refusing steps and ends** (D4): `sets_problems`, `_apply` and `web/sketch.py` show no such refusal; not run.
- **Not read in full:** `critique.md` (headings, greps), `inspect.py` (outline), `board-data.md` (parts), `README` (lines 229-316), `evals/metrics.md`, `docs/agents/*`, `docs/reviews/*`, `docs/findings-2026-11-17.md`, lab sources, the transcript.
- **yy9 beads read by title only:** 3, 5, 6, 7, 9, 11, 13, 14, 16-20, 22-28, 30-32, 34, 37, 38, 45, 60, 75, 80, 83, 88.
- **Not shown one by one:** the 74 rules, the 27 `software/viewing` entries, most `software/ontology` decisions. `ogy review` was not run.
- **Assumed, not tested:** `title` is accepted on a step (the map says every kind takes it; T sets none); an area may hold a link to another layer; link order is outside the fingerprint.
- **Counts.** 66 rules and 140 rows are from decision text. I counted 13 hedged answers in force (the brief says 11), 37 AI-decided entries and 20 areas.
- **Words.** `ogy find` and the reserved list: `system` is free as an entry word (17 hits, all prose); `ready` is free. `to` also exists on transition with another meaning.
