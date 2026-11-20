# Prose rules: which a check could read (2026-11-20)

Status: **decided** for every listed item (2026-11-21), by the coordinator under the owner's delegation (decision
`product/review/decision/judgement-delegation`; each answer is listed by `ogy dropped` for his veto). Fates are in "Listed: decided" below.
First written as proposed. A sweep of the rules that live in prose in `skills/`, `docs/guidance.md`, `docs/agents/`, the whole README and
the kinds' `about`, `guidance` and `unlike` text, against the principle rigid-where-checked ("a fact that a check, work left or
impact reads is a field or a link"). It applies two principles proposed today, `fix-the-class` (a gap found is fixed for
its whole class) and `one-owner-per-fact` (a rule is a check or prose on its entry, never both). They wait for the
owner's review on the local branch `proposed-words`, so no entry cites them yet.

The sweep started from misfit M4. The no-answer rule lived only in the capture skill, and is now work (`a983a47`). The README's command, writing, layout
and kind-change sections describe checks that exist; read whole, they add no prose-only rule beyond L7 and the actor naming row.

Fates:

- **checked**: a check or a work requirement reads it. Either it was already checked and the prose only explains it, or
  this sweep built the check and deleted the prose copy.
- **listed**: a check could read it, but it needs a design choice, a new field or kind, or counting the grammar cannot
  do. Each one has a recommendation below. Nothing was built.
- **prose**: only a reader needs it (judgement, process or naming). No check could read it.

## Counts

| Fate | Rules |
|---|---|
| checked, built | 3 (no-answer path; capability with no workflow; goal with no capability, L10) |
| checked already | 24 |
| held, with a trigger | 6 (L1, L2, L3 on ogy-yy9.2; L5 ogy-yy9.84; L6 ogy-yy9.85; L11 ogy-yy9.86) |
| prose, decided | 4 (L4, L7, L8, L9) |
| prose | 21 |

## Built today

| # | Rule | Was in | Now |
|---|---|---|---|
| B1 | A row that tells an outside system owes a no-answer path and a rule on whether a repeat is safe | capture skill, hazard question 3 | work `no-answer-path` on case, choice and timeout (`a983a47`); the question left the skill (`cf4f6c0`) |
| B2 | A workflow realizes a capability | capability guidance | work `no-workflow` on capability (`cea25d2`); the words left the guidance. Nobody agreed it as a requirement, so the decision `software/ontology/decision/capability-realized-by-workflow` asks the owner (proposal: work). 7 capabilities on ogy's own KB read `no-workflow` |

## Listed: decided (2026-11-21)

Four models reviewed the eleven items; the coordinator decided under the owner's delegation.

| # | Fate | How |
|---|---|---|
| L1 | held | One root cause with L2 and L3 (the no-answer rule reads that some rule and some failure case exist, not what they say): a note on ogy-yy9.2. Trigger: a row clears `no-answer-path` with an unrelated rule |
| L2 | held | As L1. Trigger: a "declined" case clears it on a real knowledge base |
| L3 | held | As L1. Trigger: a capture misses a stale-read path; then the B1 shape (a failure path on the same step) |
| L4 | prose, superseded | The rule `shared-entries-home` said "ogy check enforces it"; nothing counts the areas that use an entry, and `layout.py` reads only which kinds may live in `shared`. The sentence (and the option in force) now says the placement is guidance. No lint built |
| L5 | held, ogy-yy9.84 | 0 of 112 decisions have one option; a fill-in answered in review adds the owner's answer as the one option (`reply.py` `_fill`), so a one-option check would misfire |
| L6 | held, ogy-yy9.85 | A digit lint fires on dates, versions and codes. Trigger: a hidden number changes behaviour |
| L7 | prose, kept | The "Not here" sentence stays; `unlike` stays the link a check reads |
| L8 | prose, decided | Decision `software/ontology/decision/handler-performs-rows-without-effect`: may. The handler kind no longer says it performs only rows with an effect (the check handler performs rows with none) |
| L9 | prose, decided | Decision `software/ontology/decision/dependency-choice-is-a-decision`: prose; a dependency need not link a decision |
| L10 | checked, built | Decision `software/ontology/decision/goal-realized-by-capability`: work. goal.yml's `unused` requirement is back (`tests/test_requires.py`); 0 goals on ogy's KB read it |
| L11 | held, ogy-yy9.86 | No live sentence holds a full address today; a bare id misfires; answers are append-only, so a lint skips them |

The fix-the-class scan of every rule's `says` (after L4) also corrected `software/ontology/rule/examples-before-kinds` (it called a
rule that constrains nothing an error; it is `unused` work) and listed two decided rules that claim a check nothing makes, on bead
ogy-yy9.87: `product/language/rule/term-use-is-computed` (a term no area uses is an error) and `software/writes/rule/who-may-say-yes`
(a second human actor is a finding).

## Listed: what was asked (2026-11-20)

| # | Rule | Where | Why not built | Recommendation |
|---|---|---|---|---|
| L1 | The repeat rule is about repeats | B1 | The check reads that the row satisfies some rule, not what the rule says. Nothing marks a rule as being about repeats | Hold. If rows clear B1 with unrelated rules, add a closed value on the row (`rerun: same / checks / never`, bead ogy-yy9.2) rather than a marker on the rule |
| L2 | The no-answer case is a case for no reply | B1 | Any case ending in failure on the row's step or the next counts, a "declined" case too. Nothing in a case says it is the no-reply one | Hold, with the same trigger as L1. A marker would be a new field |
| L3 | A fact read from an outside system (a `when` that reads a program actor or a dependency) may be missing or stale | capture skill hazard pass ("every read of an outside fact"); bead ogy-yy9.2 | Grammar can find these rows (`when?nature=program`), but what they owe is a design choice: a no-answer path as in B1, or a rule on freshness | Decide on ogy-yy9.2. Recommend the B1 shape (a failure path on the same step), so one word covers both |
| L4 | A term, an actor or an enum that two areas use lives in `shared`; one that one area uses stays in it | capture skill section 6; term and enum guidance | The check needs the number of distinct areas that link to an entry. The `requires` grammar cannot count | Build as a Python lint in `lints.py` (one owner per fact), as work, not as a fault: the move is `ogy move` |
| L5 | A decision has no options (a fill-in) or at least two | capture skill section 4; elicit section 3 ("2-4 options") | This is counting again. A one-option decision is legal today | Build as a check in `settle.py` beside `uneven-options`. A one-option decision is an entry with `src` |
| L6 | Every number lives in a quantity, never in text | quantity `about` and guidance | A digit lint over sentences would also fire on dates, versions, codes and examples. Which text counts is a choice | Hold. If wanted, lint only the `says` of rules, cases and timeouts, where a hidden number changes behaviour |
| L7 | An area's `says` ends `Not here: <what>: <area>` | area guidance | This is a text pattern, and the `unlike` links carry the same fact | **Prose, kept** (owner-delegated, 2026-11-21): the sentence tells a reader where to look in the area's own words; `unlike` stays the link a check reads. Nothing is dropped |
| L8 | A handler performs rows that have an effect | handler `about` and guidance | `requires` can test "holds a part" only as a condition, not as what is needed | Hold until a handler is seen performing an effectless row; then add `needs_part` to the grammar |
| L9 | Choosing a dependency is a decision | dependency guidance | Work "a dependency with no `because` to a decision" is expressible today, but nobody agreed that every dependency needs one | Ask the owner: work, or prose |
| L10 | A goal is realized by a capability | the sibling of B2 (`fix-the-class`); no prose says it | Work `unused` on goal is expressible today and was built in `cea25d2`, then taken out, because no guidance or decision says a goal must be realized | Ask the owner with B2's decision; recommend work, as for B2 |
| L11 | A sentence that names an entry is a link | `docs/guidance.md` ("the guards"); the rule `software/ontology/rule/examples-before-kinds` (answered) | Agreed, but not built. A text scan must decide what counts as naming: an address, an id or a term's word | Build as a lint in `lints.py`; start with full addresses and ids in `says`, which never misfire |

## Checked already (the prose explains a check)

| Rule | Where it is said | What reads it |
|---|---|---|
| A condition reads at least one entry | case guidance | the `expr` field type |
| `otherwise` has no `when`; one per system step | case and step `about` | `step-shape` |
| Only an actor step has a timeout | timeout guidance | `step-shape` |
| A timeout waits a decided quantity | timeout guidance | the field type (`after: quantity`) |
| An actor step keeps one choice without `when` | choice and step guidance | `requires` on step |
| A calling step names every end of its callee | end guidance | `uncovered-end` |
| A workflow is started by an actor, a schedule, an event or a caller | workflow guidance | `never-started` |
| The product layer never names a dependency | dependency guidance | `layer-direction` |
| A row that tells a program actor has a handler using a dependency realizing it | dependency guidance, README | work `unhandled` |
| What each effect's `on` may be | effect guidance | `requires` on effect |
| A row with an effect has a performing handler | effect guidance | work `unhandled` |
| A derived attribute is never written and has no `max` | attribute guidance | `requires` on attribute and effect |
| An attribute is written somewhere | README | work `unwritten` |
| An interface that accepts or offers serves a step; `allows` only without `serves`; a cli says `invoked_as` | interface guidance | `requires` on interface |
| A term says one line under 15 words | term guidance | `term-too-long` |
| A word the glossary avoids is refused | capture skill section 1 | `avoided-word` |
| A term or principle is agreed before it lands | capture skill section 8 | `term-not-agreed`, `proposed-term` |
| A rule is proved by a test | rule guidance | `missing-proof`, work `unbuilt` |
| A rule is satisfied or constrains something; a quantity, enum, setting or dependency is linked; a transition fires | rule, quantity guidance | work `unused` |
| A capability realizes a goal | capability guidance | work `unrealized` |
| An actor step is served by an interface | README | work `unserved` |
| Every area holds its `area.yml` | capture skill section 6 | `missing-entry` |
| Never edit `removed.yml` or an answer; never reuse an id | capture skill section 6 | `edited-append-only`, `id-reused`, `bad-snapshot` |
| A structural decision is never in an accept-all; at most 7 cards a round | capture skill sections 6 and 7; elicit section 4 | `ogy reply`, `ogy review` |

## Prose: only a reader needs it

| Rule | Where |
|---|---|
| Different permitted actions make a new actor; a threshold name is never an actor; name a product actor by its role | actor guidance |
| A recorded move the product reacts to is a state; a fact that changes the outcome is an attribute | actor, attribute and state guidance |
| Use a case when the path differs, a choice's `when` when the screen offers fewer choices | case and choice guidance |
| Start a new step when another actor acts or the product waits | step guidance |
| Add an end when the outcome differs for whoever waits on it | end guidance |
| Something done on a clock is a workflow with a `schedule`; a one-off act is a plain task | timeout and workflow guidance; `docs/guidance.md` |
| A closed list is an enum, a number a quantity, a thing with facts an entity | entity and enum guidance |
| A decided limit nobody configures is only a quantity | setting guidance |
| A workaround is forced by the dependency, not chosen | workaround guidance |
| Keep few goals | goal guidance |
| Write a rule only where a test could catch it broken | option guidance |
| A refusal is a case that leads to a failure end | README |
| Search before proposing; a new option goes on the decision that already asks | decision guidance; both skills |
| Change an entry's area only with `ogy move` | area guidance; capture skill |
| Never fill an optional slot without evidence | capture skill section 2 |
| Code gives guarantees, docs give claims | capture skill section 1 |
| The six remaining hazard questions (twice, halfway, stale read, at once, silently not done, put right) | capture skill section 3; bead ogy-yy9.5 |
| Live capture: record the answer at once, with a paraphrase | both skills; AGENTS.md |
| A principle is one sentence | principle `about` |
| Every change names its eval in the ledger | AGENTS.md |
| How this repository is built and gated (test first, never skip a hook, files are truth) | `docs/agents/` (the repo's own gate enforces its parts; no ogy check reads them) |

One prose copy was wrong and is fixed: `docs/guidance.md` said a rule that constrains nothing is an error; the check makes it work (`unused`).
