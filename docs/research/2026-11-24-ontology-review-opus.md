# Ontology audit, second pass (Opus 5.5, 2026-11-24)

Method: the `iorlas-wip:ontology-designer` AUDIT branch (`audit.md`), run by Claude Opus 5.5 as a read-only subagent. It attacks
`docs/research/2026-11-23-ontology-redesign.md` (Fable, "the redesign") and `docs/research/2026-11-24-ontology-review.md` (Sonnet 5.5,
"the Sonnet pass") instead of trusting either. Nothing in `src/`, the kind files or `docs/kb` was changed. Nothing was put, answered,
replied or removed. Every proposal in section 7 waits for another session to record it with `ogy put` and for the owner to answer it
from `ogy review`.

Revision read: the worktree at `1b52dcf`, including the Sonnet pass's uncommitted edits to six decisions and its three new decision
files. Counts tagged **(ogy)** come from `just ogy status|work|show|find|kinds --map|glossary`. Counts tagged **(script)** come from
a PyYAML census I wrote in the scratchpad. PyYAML reads the keys `on`, `yes` and `no` as booleans, so a script count that compares
option keys may be off by up to 5 (5 `chose` values are such keys).

## 1. Scope and coverage

- **Scope:** the whole shipped ontology: 29 kinds in `src/ogy/ontologies/software/kinds/`, `ontology.yml` and `starts.yml`. Also ogy's
  own KB in `docs/kb` (20 areas, 370 files) and the fixture `tests/fixtures/tool-library`.
- **Coverage:** examined 29 of 29 kinds. All 29 kind files were read in full. Every KB and fixture entry was counted per kind, field
  and enum member.
- **Input documents read:** AGENTS.md, owner-inputs.md, FEEDBACK.md, CARD-SPEC.md (sections 0-2 and 4-8; the per-kind table in
  section 3, lines 31-59, was not read), the audiences research (skimmed by heading and grep), the constitution and the glossary
  (`ogy glossary`).
- **Not read in full:** about 140 decisions. They were read through script fields, and about 25 were opened by hand.
- **Above about 40 concepts:** the skill suggests auditing one module per run. I covered all 29 kinds in one run because they form a
  single module (one kind folder). No module remains.

## 2. Ontology now

The **(ogy)** figures come from `kinds --map` and `status`; the per-kind counts come from the **(script)** census.

- **Shape:** 29 kinds in one flat list with no is-a. Of these, 16 are top-level and 13 are parts. The parts are step, end, case,
  choice, timeout, effect, attribute, state, transition, option, answer, proposal and workaround. Depth is at most 3: workflow, then
  step, then row, then effect.
- **Layers:** two layers (product and software) plus the fixed folder `constitution/`.
- **Largest sibling group:** the 16 top-level kinds, which is past "about a dozen". Layer and `shape` group them; no grouping level
  exists.
- **Relation types:** about 30 link fields:
  - satisfies, constrains, realizes (x3), for, start, schedule, event, calls, actor, then, covers_ends, after, on
  - serves, offers, shows, accepts, includes, allows
  - performs, uses, default, of, max, unlike, names, because, chose, delegated
  - from, to
  - plus the expression readers `when` and `derived`.
- **Instances:** ogy's KB is weighted towards decisions. It holds 170 decisions with 436 options and 203 answers. By contrast it
  holds 31 steps, 6 entities and 6 effects.

### Inventory (every kind; "def" is quoted from the kind file's `about`)

| kind | part of | def (quoted) | KB | fixture | notes from the census (script) |
|---|---|---|---|---|---|
| actor | - | "whoever uses or operates the product" | 8 | 4 | nature: human 5, ai 1, program 2; 4 of the 5 humans link to nothing |
| area | - | "what one area of a layer covers" | 20 | 3 | unlike 18/20 |
| capability | - | "something the product can do" | 18 | 1 | realizes 12/18 |
| goal | - | "a result the product exists to reach" | 6 | 1 | for: owner 6, agent 1 |
| workflow | - | "a result reached by steps" | 16 | 4 | schedule 0, event 0, satisfies 3 |
| step | workflow | "an actor step ... a system step ... or a calling step" | 31 | 6 | satisfies 0 |
| end | workflow | "one way a workflow ends" | 27 | 7 | |
| case | step | "one condition of a system or calling step" | 29 | 9 | satisfies 0, effects on 4 |
| choice | step | "one thing the actor is offered" | 20 | 2 | satisfies 0, when 0, effects on 1 |
| timeout | step | "what happens when the actor does nothing for a time" | **0** | 1 | |
| effect | row | "one thing a row changes or tells" | 6 | 5 | do: write 1, create 2, delete 1, transition 2, tell **0** (fixture: tell 3, create 1, transition 1) |
| entity | - | "a thing the product keeps facts about" | 6 | 2 | proof 0 |
| attribute | entity | "one fact kept about an entity" | 13 | 5 | type: text 10, flag 1; money/date/datetime/duration 0 in KB **and** fixture |
| state | entity | "one state of an entity's lifecycle" | 5 | 2 | |
| transition | entity | "one allowed move between states" | 3 | 2 | 1 of 3 unused (ogy) |
| enum | - | "a closed list of named members" | 9 | 1 | 6 of 9 unused (ogy) |
| quantity | - | "a number with its unit ... that someone decides" | 7 | 4 | 6 of 7 unused (ogy) |
| rule | - | "a statement that must stay true" | 74 | 6 | proof **0/74**, constrains 3, satisfied by something 8 (ogy) |
| term | - | "a word of the glossary" | 33 | 2 | names 0, says 33 |
| decision | - | "one question, its options, the AI's proposal and the owner's answers" | 170 | 5 | 155 answered, 15 open (ogy); proof 0, src 0 |
| option | decision | "one way to answer a decision" | 436 | 8 | sets 202/436 |
| proposal | decision | "what is built while a decision has no answer" | 170 | 5 | on all 170 decisions, answered ones included; `sets` 0 in KB |
| answer | decision | "a person (or an agent under their delegation) chose an option" | 203 | 4 | where: `ai:` on all of them; `bd:` and `path:` 0 |
| interface | - | "a point where an actor reaches the product" | 26 | 4 | form: cli 22, web 3, library 1; http/mcp/message 0 in KB and fixture; shows or accepts on 5/26 |
| handler | - | "the code unit that performs rows" | 11 | 2 | satisfies 3 |
| dependency | - | "a library or service the product depends on" | 5 | 1 | realizes **0**, workarounds 0 |
| workaround | dependency | "how a dependency behaves against expectation" | **0** | 1 | |
| setting | - | "a real setting the product reads" | 4 | 2 | default 0/4, and 4/4 unused (ogy) |
| principle | constitution | "a value every design decision is judged against" | 6 | 1 | |

## 3. Checks

Finding numbers refer to section 4.

- **A. Names:** F3, F6, F14.
- **B. Differentia:** F5. I compared every actor pair in `product/shared/actors.yml`, plus goal against capability, quantity against
  setting, and option against proposal `sets`.
- **C. Identity:** F1. The proposal has one identity (one per decision) but two meanings.
- **D. Rigidity:** F5. The audience actors differ by what they read, not by what they may do.
- **E. Is-a:** none found. The meta-model has no is-a; `part_of` was checked for every part kind and is honest. F12 notes that the
  Sonnet pass's "family" would introduce the first is-a.
- **F. Shape:** 16 top-level kinds sit past a dozen. That is a smell, and grouping them by layer already happens in folders; no
  finding beyond that.
- **G. Dead weight:** F8, F10, F11. Counts per kind, field and enum member were taken in KB and fixture. The Sonnet pass did not
  run this check.
- **H. Overload:** F1 (proposal), F4 (interface.form single-valued).
- **I. Relations:** F6 (`realizes` has three meanings), F12 (`satisfies` exercised only by AI-decided entries).
- **J. Encoding:** F15.
- **K. Contexts:** F9 (decisions about kind files live in a KB that cannot address kind files), F16.
- **L. Two homes:** F2, F7, F8.
- **M. Borrowed values:** F8 (mirror enums), F17 (a "knob" quantity with no setting).

## 4. Findings

| # | severity | check | concepts | evidence | smallest fix | cost |
|---|---|---|---|---|---|---|
| F1 | 1 law (L1, L2) | C, H, L | proposal, decision, answer | see F1 below | adjust: `proposal.at` (P1) | 1 field, 1 computed rule, review code; 22 old proposals stay inert |
| F2 | 1 law (L6) + 2 conflict | L, G | rule, option, decision | see F2 | combine: P1, then per-decision re-ask or link (P2) | 61 rules; 61 answers or about 61 links |
| F3 | 2 conflict (L2), L5 | A, K | proposed kind `system`, step, case | see F3 | defer the kind (P3) | 0 now |
| F4 | 2 conflict | H, L | interface.form | see F4 | adjust: `form` many (P4) | 18 entries gain `mcp` |
| F5 | 1 law (L1: actor's own guidance) + 2 | B, D | actor | see F5 | value: audiences `not-now` (P5) | 4 entries set null |
| F6 | 2 conflict (L2) | A, I | dependency.realizes | see F6 | adjust: rename (P6) | 0 KB, 1 fixture link |
| F7 | 2 conflict | L, M | effect create/delete, transition | see F7 | adjust: guidance and one requires line (P7) | 0 entries move under the recommended option |
| F8 | 2 conflict | L, M, G | enum, quantity, setting in O | see F8 | data: an option setting the copies null (P8) | 5 enums; harm-tags needs P1; where-schemes is already wrong |
| F9 | 2 conflict | K | decision about kind files | see F9 | express: `proof` on such decisions (P9, needs P1) | 50 answered decisions |
| F10 | 2 (L5) | G | proposed effect value | see F10 | defer (P10) | 0 |

### F1. Re-asking an answered decision has no home; `proposal` holds two meanings

The definitions say a proposal belongs to an unanswered decision:

- The glossary defines a proposal as "The option or values the AI builds on **until the owner answers** a decision"
  (`ogy glossary`, product/shared).
- `proposal.yml:3` says: "what is built while a decision has no answer".

The engine ignores a proposal once an answer exists:

- `status.py:293-295` makes cards only `if not decision.answers or delegated(decision)`.
- `status.py:177` says: "once a decision has an answer its proposal is inert".
- `status.py:184` blanks the reason whenever `decision.answers` is set.
- `settle.py:66` (`in_force`) reads the proposal only when no dated answer exists.

The KB nonetheless uses the proposal slot on answered decisions:

- 22 of 155 answered decisions have a proposal that names another option than the answer in force **(script)**.
- Most of these are stale. For example, `glossary-per-layer` proposes `per-area` while `per-area-shared` was answered.
- Three are new re-proposals written by commit `d24f415` (the redesign's recording):
  - `context-form` proposes `system-kind`. This is the gate for the redesign's whole M1.
  - `rule-constrains` proposes `area-and-system-satisfy`.
  - `product-map` proposes `canvas-again`.
- Nothing tells the two apart, and no review round will ever show the three new ones.
- The Sonnet pass's option `triage-by-catchability` sits on the answered `rules-need-a-check` and is equally unseen. Its section 4
  says "the owner is asked from `ogy review`", which is false for this one.
- `system-word` says it "Comes up only if context-form is answered system-kind". So system-word waits on a question that is never
  asked: a deadlock.
- The workaround already exists and admits the gap. `confirm-hedged-answers` says in its context: "ogy has no mechanism for
  re-confirming an answer".

That makes three independent cases (the hedged 13, the redesign's re-proposals and the rule triage), so the rule of three holds.
Smallest fix: adjust. Give the proposal an `at`; a proposal newer than the newest answer makes the decision a question again
(one that names the option in force asks for a confirmation, which covers the hedged 13; one that names another option asks to
change it). It is shown with the answer in force beside it. The 22 old proposals carry no `at` and stay inert. Proposal P1.

### F2. The 61 "floating" rules are the settled output of answers in force

Of the 66 rules `ogy work` lists as `unused` **(ogy)**:

- 61 are given fields by the option **in force** of an answered decision **(script: every option's `sets` against all 74 rule
  addresses)**.
- Only 5 are settled by no decision: `area-named-like-the-product-is-an-error`, `init-and-mcp-are-no-tools`, `kb-is-docs-kb`,
  `rename-is-a-move` and `write-is-put-back-on-a-new-error`.
- The 8 linked rules are all "nobody agreed: decided by AI" (`ogy show`, each one) in `software/viewing` and `product/inspection`.
  None of them is set by a decision.

So neither proposed removal can run:

- `ogy remove` refuses such a rule: `removal.py:110-125` gives the reason "`<decision>` in force gives fields to `<rule>`".
- A hand removal would give a `not-in-force` finding: `settle.py` `_in_force`, D6, "is absent but the option in force gives it fields".
- `rules-need-a-check` cannot set the 61 to `null` either, because D4 `_two_homes` reports an address settled by two decisions.

The lawful path is a new answer on each of up to 61 decisions, choosing an option that sets the rule `null`. That path needs F1
first, because those decisions are all answered.

History neither document cites:

- `decision-stands-alone` (answered `alone`, 2026-11-19) already found "56 of 66 decisions only set one rule that repeats the
  option".
- The owner did **not** take its option `alone-and-sort` ("Yes, and sort the 60 mirror rules now").
- Three days later he answered `keep-checkable`.

So the forward rule (write no mirror rules) is decided. The backlog has twice been left to a later step. Proposal P2.

### F3. `system` would be the third meaning of one word; the kind has one real case

The word already has two opposite meanings in the shipped text:

- `step.yml:2`: "a system step (cases ...); no actor means the product itself". Here the system is **ours**.
- `case.yml:14`, `choice.yml:15` and `timeout.yml:15`: "a row that tells an outside system has a no-answer path". Here the system is
  **someone else's** (a program actor or a dependency).
- The proposed kind adds a third meaning: what we ship.

The proposal for `system-word` gives as its reason that the word "fits the phrases system step and outside system". Those two
phrases point at opposite sides of the boundary.

On L5 (a real case must exist today), ogy's KB holds one shipped thing:

- `mcp-is-a-subcommand`, rule `mcp-is-the-ogy-mcp-command`: "The MCP server is the subcommand ogy mcp, and each CLI command is a
  tool".
- The board is `ogy view`, interface `view-server`.
- All three surfaces ship in one package. Rule `init-and-mcp-are-no-tools` says the MCP tools are "generated from the CLI and
  return the same operation results". Whether every handler is shared was not checked.

So the owner's "is the CLI its own software?" (owner-inputs, 2026-11-23) is answered today at the **express** rung. The CLI is the
22 interfaces of `form: cli` (plus `mcp`, see F4), and the board is the 3 of `form: web`. The fixture has one "system" only by
illustration. The trigger for the kind is the audiences research's own open question, "What is the next real thing you will build
with ogy?" (line 154): a KB that holds two shipped things that share no handler. Smallest fix: defer the kind; P3.

Where M1's other jobs go if the kind is deferred (AGENTS.md: deleting a mechanism lists its jobs):

- **R12 and O1 (which software area builds which product area):** computed from links that exist, handler `performs` a product
  row and interface `serves` a product step, and printed by the engine. This is the redesign's own M8 or M7 derivation; no field.
- **C13 (the outer frame):** the area stays the frame. A single KB is one shipped thing until the trigger fires.
- **Rule holder (R8: a rule for everything or one part):** `satisfies` on the existing behaviour kinds. A rule for the whole
  product is a rule nothing satisfies, which `unused-is-work` already shows as work. The widening waits for F12's evidence.
- **Principles and proportion (R4):** the constitution, as the Sonnet pass's N2 recommends (`proportion-home`: not-now).
- **Answered `context-form` = `area-field`:** still unbuilt (F9). Re-proposing `defer` needs P1.

### F4. `interface.form` holds one value; 18 interfaces are reached two ways

- `interface.yml`: `form: {type: enum, of: [web, cli, http, mcp, library, file, message], required: true}`, which holds a single
  value.
- The answered rule `mcp-is-the-ogy-mcp-command` says each CLI command is a tool.
- `init-and-mcp-are-no-tools` lists the exceptions: init, mcp, hook and view.
- That leaves 18 of the 22 cli interfaces as MCP tools too. Yet `form: mcp` appears 0 times in KB and fixture **(script)**.
- The fact lives only in prose, in two rules that are themselves `unused` (ogy).
- This is the Customer/Vendor case: a single-valued field cannot say "both". Parity between agent and board (B16,
  `agent-inspection-parity`) and the owner's "which software is this" both need it.

Smallest fix: adjust `form` to a list. P4, as an option on the answered `interface-form`, so it also needs P1.

### F5. The four audience actors break the actor kind's own guidance

- `actor.yml` guidance: "Different permitted actions make a new actor".
- The four actors that `d24f415` built from the unanswered `audiences` proposal differ only in what they **read**:
  - analyst: "reads the product layer"
  - architect: "reads both layers"
  - engineer: "builds from the software layer"
  - operator: "watches".
- The redesign itself says a hat is "a filter, never a permission" (M2). R7, the read-only role, is deferred.
- `analyst` ("states what the business needs and answers its questions") and `owner` ("decides the product's business questions")
  have no differentia, so they are near-duplicates.
- Nothing links to the four (`ogy find` / grep: 0 references outside `audiences.yml`).
- They sit in `product/shared`, whose `says` is "What two or more areas of this layer use". No area uses them.
- They contradict the answer in force on `who-may-say-yes`, whose rule says "a second human actor is a finding". The KB holds five
  human actors and `ogy check` says `ok`, so that answered rule is not enforced.
- With `unused-actor-entity-handler` = yes, they become 4 `unused` rows at once.
- The research's own analogue is the ArchiMate *viewpoint* and IcePanel *tags* (research lines 91, 93). That is a view filter, not
  an actor.

Smallest fix: value (the hat is a computed filter). Answer `audiences` with `not-now`; P5.

### F6. `realizes` has two meanings, and the word was never decided

- `workflow.realizes -> capability` and `capability.realizes -> goal` mean "the lower level brings about the higher" (ArchiMate
  realization).
- `dependency.realizes -> actor` means "this library stands in for that role". That is a different relation.
- The redesign rejected the rename because "`dependency-realizes-actor` is a firm answer" (C6). That decision asked "How does the
  product layer name an outside system the product tells?". Its options were `realizes` and "Rows tell the dependency directly". It
  settled the **direction**, not the word.
- The Sonnet pass says "ArchiMate uses realization for all three". `mainstream-field-names` itself records the ArchiMate reading as
  "recalled from the ArchiMate 3 specification, not re-read". I did not check it either (Not checked).
- Owner feedback 2 (FEEDBACK.md) says: "if a name does not fit, fix the ontology name".
- Instances: 0 in KB, 1 in the fixture.

Smallest fix: rename. P6.

### F7. Two homes for "an entity comes into being"

- `effect.yml` guidance: "`transition` names a transition (it also creates an entity with a lifecycle); `create`, `delete` an entity
  without one".
- No `requires` line enforces this.
- The fixture's model row `borrow/step/record/case/otherwise` does **both** to `loan`: `do: create` and `do: transition` on `start`,
  a transition with no `from`.
- ogy's own `remove-entry` deletes `entry`, which has a lifecycle (transitions `agree` and `change`).
- So 2 of the 4 create/delete effects (KB 3, fixture 1) break the guidance **(script)**.
- The engine already leans the other way. `attribute.yml`'s never-written path counts `<-on?do=write|create` on the entity, and
  `create-writes-attributes` (answered `counted`, 2026-11-20) says a create writes the attributes. A from-less transition writes
  nothing. Dropping the fixture's create would make loan's attributes `unwritten`.

Smallest fix: adjust the guidance, not the data. A create brings an entity into being and writes its attributes; a transition
without `from` only sets its first state; a delete may end any entity. Add one `requires` line so a from-less transition has a
create on the same row. P7.

### F8. Mirror enums, quantities and settings; one has already drifted

Neither document counted the non-rule half of the unused entries. `ogy work` lists 18 non-rule entries as `unused`:

- 4 of 4 settings
- 6 of 9 enums
- 6 of 7 quantities
- the dependency `shelf`
- the transition `entry/change`.

Five of the enums copy a list whose owner is a shipped file:

- `harm-tags` copies `ontology.yml` `harms`.
- `layers` copies `ontology.yml` `layers`.
- `where-schemes` copies `answer.yml` `where.schemes`.
- `checks` and `landing-checks` copy `check.py`.

`where-schemes` is already wrong:

- It lists `ai, bd, file`, while `answer.yml:16` has `schemes: [ai, bd, path]`.
- Its `src` is `code:src/ogy/cli.py#WHERE`, which is now a help string (`cli.py:23`).
- `ogy check` passes because a `code:` source proves only that the symbol exists.

`harm-tags` is given fields by `harm-names` (answered `rename`, in force), so `ogy remove` refuses it (F2 mechanics) and it needs a
new answer there. The other four are settled by no decision **(grep of every decision for the five addresses)**.

The constitution's `one-owner-per-fact` says: "Copies drift". Smallest fix: data, through a decision whose option sets the four copies
`null`, and a new option on `harm-names` for the fifth. This is not reorganising: the reason is a requirement, one owner per fact,
shown broken by a copy that already disagrees with its owner. P8.

### F9. Decisions about the kind files cannot record whether they were built

- 50 of the 69 answered `software/ontology` decisions set nothing **(script)**. Their effect lands in a kind file, which no entry can
  address.
- 0 of 170 decisions carry `proof` or `src` **(script)**.
- `evidence` schemes read `.py` and `.md` only (`ontology.yml:26-27`), so nothing points at a kind file.

Real case:

- `context-form` was answered `area-field` on 2026-11-22.
- `area.yml` has the fields `says` and `unlike` only.
- Nothing reports the answer unbuilt. The redesign then proposed a different design on top of it, inertly (F1).

The competency question "which answered ontology decisions are not in the kind files yet?" fails. Smallest fix: express. `proof` is a
common field already; an answered decision with `structure: true` that sets nothing carries a proof (a test that reads the kind file),
and is work until it has one. `which-kinds-need-proof` already asks which kinds need a proof (answered `behaviour`), so P9 is a new
option there and needs P1.

### F10. The effect value has no real case (L5)

- CARD-SPEC.md:177: "'due date set to +14 days' is a lab invention in `src/model.js`".
- The fixture's `loan` has no due-date attribute and the fixture has **0** write effects **(script)**.
- ogy's KB has 1 write effect, on `entry` as a whole, which has no scalar value.
- So `effect.to` (the redesign) and `becomes` (the Sonnet pass) would each enter with no record to hold, and the fixture would have to
  invent a write to "fill every field".
- The owner's first half, "which fields change" (FEEDBACK 9), is already expressible: `do: write` with `on: <attribute>`, and
  `create-writes-attributes` covers create.

Smallest fix: defer, with the demand stated. P10 changes the proposal on the open `effect-value`.

### Further findings (one line each)

- **F11 dead values (G):** these values are never used, in KB or fixture **(script)**:
  - `attribute.type` money, date, datetime and duration.
  - `interface.form` http, mcp and message.
  - `effect` `tell` on a dependency. It is guarded by 6 `requires` lines (case, choice and timeout, 2 each). It is also the option
    `dependency-realizes-actor` rejected for product ("Rows tell the dependency directly").
  - `answer.where` `bd:` and `path:`. All 378 `where` values in answers and agreements are `ai:`, yet `answer-where-ui` proposes a
    fourth scheme.
  - `proposal.sets`: 0 of 170 in the KB.
  - `timeout` and `workaround`: 0 in the KB. These are generic kinds kept for other products; the rest are candidates to supersede
    (L6) or to stage.
- **F12 `satisfies` (I):**
  - Of the 10 entries that carry `satisfies`, 9 are "nobody agreed: decided by AI" and 1 (`software/cli/interface/view-server`) is
    "changed since you agreed" (`ogy show`, each one). Rows and steps carry 0.
  - Widening `satisfies` to area and system (the redesign's M6, `rule-constrains`) widens a link that no entry the owner agreed
    as it stands uses today.
  - The Sonnet pass's `rows-are-a-family` would be the first is-a in a meta-model with none, and the `requires` lines differ per
    member: case uses `["^","/case",...]`, choice `["^","/timeout"]`, timeout `["then","/timeout"]`. So a family removes the triple
    from 4 link lists, not the 18 duplicated `requires` lines.
- **F13 data, outside the ontology:**
  - 21 of 26 interfaces record no `shows` or `accepts` **(script)**. The redesign's O3 ("I go into interface, I see nothing": "UI-only:
    the links exist") is false for the data.
  - The `answer` interface's `invoked_as` still offers `[--from human|ai]`, which `ogy answer` no longer takes (`cli.py:257-266`).
  - `migrate` and `move` have no interface entry.
- **F14 `rules:` (A):** `ogy kinds --map` titles the kind files' `requires` lines "rules:". `rule` is also a kind. Both documents
  slide between "a rule the engine checks" and "a rule entry".
- **F15 L7 smell (J):** kind files carry storage (`shape`, `file`, `key`, `holds`) beside meaning. The glossary term `shape` ("How a
  kind is stored") and the principle `storage-is-a-projection` keep the meaning clean, so no action is needed alone. Group the storage
  keys under one key when the kind-file format next changes.
- **F16 outside, K:**
  - 87 of 203 answer paraphrases mention Fable, a recommendation or "yes all" **(script, keyword match)**.
  - 13 answers carry "Yes, I guess", and 10 carry "accepted the recommendation as shown".
  - "Decided by you" therefore often means "accepted the AI's pick". Readiness (R2) and the `dont-know-answer` design should not treat
    an answer as stronger than that.
- **F17 (M):** `code-constants` kept 3 quantities as "knobs a person may tune" (`rounds-kept`, `history-limit` and `near-addresses`).
  The setting guidance says a tuned value is a setting with a `default`, yet `setting.default` is 0 of 4 and the 3 knobs are
  unlinked (ogy).

## 5. New against the Sonnet pass

Findings the Sonnet pass did not make: F1, F2 (the settling and removal mechanics), F3 (word clash and L5), F4, F5, F6 (decision
misread), F7, F8, F9, F10 (L5), F11 to F17. It skipped check G entirely ("Not run: G dead weight beyond the rules").

## 6. Where the Sonnet pass is wrong

| # | its claim (file:line) | what is true | evidence |
|---|---|---|---|
| W1 | N1 "61 cite no decision" (review.md:72) | 61 of 66 are **settled** by the option in force; the link runs decision to rule through `sets`. "61 have no `because`" is right, but the conclusion is wrong | F2 (script) |
| W2 | N1 fix: triage, whose recorded option says "removed with its own reason, one by one" (rules-need-a-check.yml:10, the option N1 recorded) | `ogy remove` refuses all 61 (`removal.py:110-125`); each needs a new **answer**, not a reason | F2 |
| W3 | §4 "the owner is asked from `ogy review`" (review.md:124) | its option on the answered `rules-need-a-check` is never carded (`status.py:293-295`); neither are the redesign's re-proposals on `context-form`, `rule-constrains` and `product-map` | F1 |
| W4 | R6 "confirm the kind" (review.md:37); N3 `container` (review.md:84-88) | the CLI and MCP are two forms of one interface set (rule `mcp-is-the-ogy-mcp-command`), not two containers. The kind has one real case. `system` already means both "ours" and "theirs" | F3, F4 |
| W5 | F2 "confirm reject: ArchiMate uses realization for all three" (review.md:50) | the decision cited settled direction, not the word; the ArchiMate reading was never re-read | F6 |
| W6 | N7 "43 entries, 37 of them in software/viewing" (review.md:111) | 37 is the number of AI-decided entries in total: 27 in viewing and 10 in inspection, plus 6 changed (`ogy status`) | ogy |
| W7 | N5 confirms the effect value and renames it (review.md:96-98) | the owner's example is "a lab invention" (CARD-SPEC.md:177). The fixture has 0 write effects, so L5 fails | F10 |
| W8 | "B differentia ... nothing found", "D rigidity ... no kind is a role", "H ... only overload is the rule" (review.md:119-121) | owner and analyst have no differentia; the 4 audiences break actor's guidance; the proposal is overloaded | F5, F1 |
| W9 | "O1-O22 confirm" (review.md:49) | O3's "the links exist" is false: 21 of 26 interfaces have no shows or accepts | F13 |
| W10 | "0 of 66 have `proof`" (review.md:14) | not wrong, only narrow: 0 of **74** rules have a proof, the 8 linked ones included | script |
| W11 | Stage order fix: "triage before stage 1, word before stage 3" (review.md:60) | both stages first need the re-ask mechanism (F1). Without it, no answered decision can change | F1 |
| W12 | N4 family "conditions for a shared parent hold" (review.md:92) | the meta-model has no is-a (its own check E); the family saves the triple in link lists only | F12 |

The Sonnet pass also missed contradictions inside the redesign:

- E9 (unused-actor check, yes) plus E10 (four actors) gives 4 new work rows on day one.
- C7 says it will "reword `who-may-say-yes` in the M6 batch". That rule is settled by an answer in force, so rewording it is a
  `not-in-force` finding and needs a new answer (F1 again).

Right in the Sonnet pass and kept:

- N2: proportion is not-now.
- N6: reverse links by field word (`ogy show` prints "referenced by X (field)", verified on `product/shared/actor/owner`).
- N6b: program-actor direction. Both program actors (`committer`, `mcp-client`) call us.
- N8: `parked`.

## 7. Ready proposals (for another session to record with `ogy put`; none answered)

Every proposal below that lands on an **answered** decision stays invisible until P1 is built, so P1 is the first one to record and
answer. Each one changes a kind file or KB content, so for the evals ledger it reads "untested (design review)".

**P1** new decision `software/ontology/decision/ask-an-answered-decision-again`

- structure: true
- title: Asking an answered decision again
- question: How is a decision the owner already answered asked again, when an agent proposes another option or the owner's answer
  was hedged?
- context: A proposal is inert once a decision has an answer (`status.py:177`, cards only for unanswered or delegated decisions,
  `status.py:293-295`). Three re-proposals (`context-form`, `rule-constrains`, `product-map`) and one new option (`rules-need-a-check`)
  are never shown. `confirm-hedged-answers` works around it. 22 answered decisions keep an older proposal that names another option.
- options:
  - `proposal-at`: "The proposal gains `at`. A proposal newer than the newest answer makes the decision a question again, shown
    with the answer in force beside it: the same option asks for a confirmation, another option asks to change. A proposal without
    `at` stays inert."
  - `listing-decision`: "Re-asking goes through a decision that lists the addresses to revisit, as confirm-hedged-answers does;
    nothing re-asks by itself."
  - `not-now`: "Not now; an answered decision changes only when the owner raises it."
- proposal: chose `proposal-at`.
- why: One field reused from answer (`at`), one computed rule. It lets the owner see re-proposals and confirm hedged answers, while
  the older proposals stay silent. A listing decision hides the question behind an address list.
- heard: The owner wants every proposed adjustment thought through again and asked, and cost is no reason to skip it.

**P2** new option on `software/ontology/decision/rules-need-a-check`, plus a re-proposal with `at` once P1 lands

- option `link-or-reask`: "A rule an engine check already enforces stays and is linked with `satisfies` from a handler in
  software/checks that models that check, keeping its agreement. Every other rule set by an answer in force is asked again on its own
  decision with an option that sets it null; `ogy remove` alone cannot remove it."
- proposal why: 61 of 66 unlinked rules are given fields by the option in force, so removal is refused (`removal.py:110-125`) and
  the answer `keep-checkable` cannot be carried out by removal.

**P3** changed proposal on the open `software/ontology/decision/system-word`, plus a new option

- option `none-yet`: "No kind yet: the word already means the product in 'system step' and someone else's program in 'outside
  system'; ask again when one knowledge base holds two shipped things that share no handler."
- proposal: chose `none-yet`.
- why: There is one real case (ogy). The CLI, MCP and the board are interface forms of it. A third meaning of `system` would break
  one-name-one-meaning.
- Also, once P1 exists, re-propose `defer` on `context-form`.

**P4** new option on `software/ontology/decision/interface-form` (answered `enum`; needs P1)

- option `enum-list`: "`form` is a list of the same enum. An interface reached as a command and as an MCP tool says both; 18 ogy
  commands become cli and mcp."
- proposal why: The answered rule `mcp-is-the-ogy-mcp-command` says each CLI command is a tool. Today that fact is prose, and
  `form: mcp` has 0 entries.

**P5** changed proposal on the open `product/language/decision/audiences`

- proposal: chose `not-now`.
- why: The four differ only in what they read. The actor kind's guidance ("Different permitted actions make a new actor"), the
  answer in force on `who-may-say-yes` and the hat-as-filter design all say they are no actors. A hat is a computed filter on layer
  and readiness.
- heard: The owner described different people with different questions on one knowledge base.
- Order for the applier (not checked): with `not-now` as the proposal in force, the four existing actors give a `not-in-force`
  finding (D6), and `ogy remove` refuses them while `four-actors` is in force (`removal.py:110-125`). The proposal change and the
  four removals must land so that `ogy check` stays clean; whether one `put` can carry both was not checked.

**P6** new decision `software/ontology/decision/dependency-actor-word`

- structure: true
- question: A workflow realizes a capability and a capability realizes a goal, but a dependency "realizes" a program actor in
  another sense: it stands in for that program actor, which a vendor swap replaces. Does that link keep the word `realizes`?
- options:
  - `realizes`: "Keep `realizes`."
  - `plays`: "Rename to `plays`: the dependency plays the program actor; `renamed: {realizes: plays}` in dependency.yml for ogy
    migrate."
- proposal: chose `plays`.
- why: One word, one meaning. 0 KB entries and 1 fixture link move. The owner asked that a name that does not fit be fixed (feedback
  2).

**P7** new decision `software/ontology/decision/create-on-a-lifecycle`

- question: The effect guidance says a transition without `from` creates an entity with a lifecycle and a create is only for an
  entity without one, yet never-written counts only a create as writing the attributes. Which one brings an entity into being?
- options:
  - `create-always`: "A create brings any entity into being and writes its attributes; a transition without `from` only sets its
    first state, and a check asks for a create on the same row; a delete may end any entity. The guidance changes; no entry moves."
  - `transition-creates`: "A transition without `from` creates an entity with a lifecycle and counts as writing its attributes;
    a create names only an entity without one. The fixture's borrow row drops its create."
- proposal: chose `create-always`.
- why: It agrees with `create-writes-attributes` (answered `counted`) and the never-written path, so no data and no check changes
  meaning. The other option moves the fixture and changes the engine path.

**P8** new decision `software/storage/decision/lists-copied-from-shipped-files`, plus a new option on `harm-names` (needs P1)

- question: Four enums copy a list whose owner is a shipped file (`software/storage/enum/layers`, `software/cli/enum/where-schemes`,
  `software/checks/enum/checks`, `software/checks/enum/landing-checks`). Nothing links to them, and `where-schemes` already says
  `file` where answer.yml says `path`. Do they stay?
- options (both name the same four addresses, as `uneven-options` asks):
  - `owner-only`: "The shipped file is the only owner; the four copies do not exist." `sets` each of the four to `null`.
  - `keep-and-fix`: "Keep the four and correct where-schemes to ai, bd, path." `sets` each of the four with its `members` (the
    applier copies the three unchanged lists as they are now).
- proposal: chose `owner-only`.
- why: one-owner-per-fact. A copy already disagrees with its owner, and `code:` evidence checks only that the symbol exists.
- On `product/review/decision/harm-names`, new option `owner-only` sets `product/review/enum/harm-tags` to `null`. Its other options
  must then name the address too, which they already do.

**P9** new option on `software/ontology/decision/which-kinds-need-proof` (answered `behaviour`; needs P1)

- option `behaviour-and-built-decisions`: "As behaviour, and an answered structure decision whose options set nothing carries a
  `proof`, a test that reads the kind file; until it has one it is work."
- proposal: chose `behaviour-and-built-decisions`, with `at` once P1 exists.
- why: `context-form` was answered `area-field` on 2026-11-22, and `area.yml` has no such field. Nothing shows it. `proof` is
  already a common field.

**P10** changed proposal on the open `software/ontology/decision/effect-value`

- proposal: chose `none`.
- why: There is no real record yet. The due date was a lab invention (CARD-SPEC 7.1), the fixture has no write effect, and "which
  fields change" is already a write on an attribute. Ask again when a real row needs its value.
- heard: The owner asked twice to see which fields a row changes and, ideally, to what value.

## 8. Rest

- **Clean:** E is-a, comparing every `part_of`. No kind has a parent link, and there is no cycle (`acyclic: [includes]` on
  interface).
- **Not checked:**
  - whether the engine can read `proposal.at`, or hold `interface.form` as a list (P4)
  - whether one `put` can change the `audiences` proposal and leave `ogy check` clean (P5)
  - the ArchiMate 3 relationship table for realization to an actor
  - the board code and `inspect.py`
  - the session transcript and the yy9 beads.
- **Not run:** `ogy review` (it saves a round, and only 10 are kept).
- **Script counts:** PyYAML boolean keys may move the option comparisons (the 22 and the 50) by up to 5.
- **Demands:** none blocking the audit. To lift F3 and F10 the owner names a real case: a second shipped product in one KB, and a row
  whose value someone needs.
- **Pressure:** none. The brief set the scope and the output file only.
- **First move:** P1, the re-ask mechanism (F1). It comes first because every other fix that touches an answered decision depends on
  it: the 61 mirror rules (F2), `context-form` and `system-word` (F3), `interface-form` (F4) and `rule-constrains`. Without it,
  recording them only adds proposals the owner never sees.

## Appendix A. Counts re-verified against the two documents

| claim | source | my count | how |
|---|---|---|---|
| 66 of 74 rules link to nothing | both | 66 | `ogy work`: 66 `unused` rule rows |
| work left | redesign 254 / decision text 140 | 253 rows: unbuilt 155, unused 84 (66 rules, 18 other), no-workflow 8, unrealized 6 | `ogy work` |
| rules in software/ontology | Sonnet 17 | 17 (18 with product/ontology's 1) | `ogy work` |
| 13 hedged answers in force | both | 13 notes "Yes, I guess" | script, `answer.note` |
| AI-decided and changed entries | redesign 37 + 6 | 37 (viewing 27, inspection 10) + 6 changed | `ogy status` |
| open questions | redesign "0 questions" (M4) | 15 | `ogy status` |
| `system` free as an entry word | both | no entry or term named system; the word is in kind text twice (F3) | `kinds --map`, grep |
| row triple written in 8 kind files and ontology.py | Sonnet | 8 + ontology.py | grep |

## Appendix B. Field census (script; KB / fixture)

- actor: says 8/4, nature 8/4, agreed 3/3, src 2/0, title 1/0
- answer: chose, said, at, where 203/4; note 51/1; delegated 16/1
- area: says 20/3, unlike 18/1
- attribute: says 9/3, type 11/3, of 2/2, many 4/1, max 1/1, optional 2/1, derived 4/1
- capability: says 18/1, realizes 12/1, src 14/1
- case: then 29/9, order 15/4, when 15/3, covers_ends 4/2, effects 4/2, satisfies 0/1
- choice: label 20/2, then 20/2, when 0/1, effects 1/0, satisfies 0/1
- decision: question 170/5, context 156/1, structure 64/1, title 71/1, because 6/0, proof 0/0, src 0/0
- dependency: says 5/1, pin 2/1, src 5/0, realizes 0/1, satisfies 0/1, workarounds 0/1
- effect: do 6/5
- end: says 27/7, result 27/7
- entity: says 6/2, proof 0/1, states 3/1, transitions 3/1
- enum: says 9/1, members 9/1
- goal: says 6/1, for 6/1
- handler: says 11/2, performs 11/2, uses 8/2, satisfies 3/1
- interface (KB 26): form 26/4, serves 25/3, invoked_as 22/1, shows 5/2, accepts 2/1, includes 2/1, offers 1/2, allows 1/1, satisfies 4/1,
  proof 1/0
- option: label 436/8, sets 202/8
- principle: says 6/1, why 3/1
- proposal: chose 170/4, why 170/5, heard 50/1, sets 0/1
- quantity: says, is, unit 7/4
- rule: says 74/6, constrains 3/3, because 13/0, agreed 16/0, proof 0/1, title 3/0
- setting: says 4/2, name 4/2, default 0/1
- step: says 31/6, actor 19/1, calls 2/1, satisfies 0/1
- term: word 33/2, says 33/1, names 0/1, avoid 16/1
- timeout: 0/1 (after, then, effects, satisfies 0/1)
- transition: from 3/1, to 3/2
- workaround: 0/1
- workflow: says 16/4, start 16/4, realizes 10/1, satisfies 3/1, schedule 0/1, event 0/1
