# Lab 29C card spec: what each kind shows at each level

Written by Fable (read-only advisor), 2026-11-23, answering the owner's "what do you expect to see for every example entity; ask on each level what actually is important". Field names verified against `just ogy kinds --map`; example data is `tests/fixtures/tool-library`. Not checked against the `software/viewing` entries or the `product/inspection` board decisions beyond their titles.

## 0. What is wrong in lab 29B

- Map cards for actors repeat the icon: Member = icon + "Member" + icon + "human"; Mail relay = icon + "program".
- The "weird icon" is the `robot` glyph in `src/icons.js` (face with antenna, sub-2px features, nearly the same box as `ai`).
- Icons collide in `KI` (`src/core.js:13`) and `FORMIC` (`src/icons.js:7`): entity = attribute (`doc`); step = handler = setting (`gear`); case = choice (`gate`); rule = enum (`list`); http = mcp = web; library = `doc`.
- Only five kinds have cards (`VIEWS`, `src/cards.js:97`): workflow, goal, capability, actor, entity. Interface, handler, dependency, rule, setting, quantity, enum, decision have none, so product and software look unconnected.

## 1. Vocabulary

T = plain text. chip = one mention (icon + title, kind colour, clickable). n = a count that is a link. word = the ontology field word, small grey, before chips. gap = red triangle + the ontology rule's own sentence. status = 6px dot in the header (awaiting the owner / changed since agreed / open decision touches it). work = small grey `unbuilt`, `changed`, `unused` from `ogy work`.

Levels: Map under 75% (card at most 4 lines); Flow 75-135% (at most 8 lines); Detail 135%+ (everything, grouped).
Cards: goal, capability, workflow, entity, actor, interface, handler, dependency, rule, setting, quantity, enum, decision.
Rows inside a parent card: step, case, choice, timeout, end, effect, attribute, state, transition, option, proposal, answer, workaround.
Never a card: area (a frame around its cards), principle (a `because` chip; card only in the constitution frame), term (hover).

## 2. Rules for all cards

1. Header: kind icon, title, kind word small in the corner, status dot. Nature or form word replaces a second icon; never the same icon twice on a card.
2. Attention order: gap, status, `says`, what it does (derived relations), what it has (own fields), `because`/`proof`/`src`. Drop whole lines from the bottom when pixels run out; never truncate mid-line except `says` at Map (one line, ellipsis).
3. A relation drawn as an edge to a visible card is not repeated as a chip; if the other end is off-screen or collapsed, show the chip. Counts always stay.
4. Thin entry: when own fields are only `says`, fill the body with derived relations. A card never shows less than `says` + one derived line or one gap.
5. At most 3 chips per field word, then "+N" count link. Map shows counts only.
6. Only ontology field words and rule sentences. Title is `title`, else the humanized key. The same entry looks the same everywhere.

## 3. Cards per kind (ordered content per level; anything not listed is hidden)

| Kind: question on landing | Map | Flow | Detail | Thin / gap |
|---|---|---|---|---|
| goal: whom is this for, is anything delivering it? | `says` (1 line); n capabilities (reverse `realizes`) | + `for` chips; capability chips | + workflows under each capability (n); `because`; `src` | gap: a goal no capability realizes |
| capability: what can the product do, and how? | `says`; n workflows (reverse `realizes`) | + `realizes` goal chip; workflow chips with ends ✓n ✗n | + actors of those workflows (derived via step `actor`); `because` principle chips | gap: no workflow realizes the capability |
| workflow: what starts it, who acts, how can it end? | starter chip (first-step `actor`, or `schedule` quantity with value, or `event` transition); `says`; n steps; ends ✓n ✗n | opens into steps and ends; + `realizes` chip; `satisfies` n | + effect badges, interfaces per step, handlers per row | gaps: nothing starts this yet; an end not reached; a step that reaches no end |
| entity: what do we keep, what happens to it? | `says`; states "open → returned"; n attributes; gap count | attributes (name, type or `of` chip; `optional`/`many`/`derived` as small words); lifecycle graph | + per transition: firing workflows (effect `transition`), `event` workflows; `create`/`write`/`delete` by; `shows`/`accepts` by interfaces; rules that `constrains` it; `proof` | gaps: a transition no effect fires; a never-written attribute |
| actor: who or what is this, where does it touch the product? | nature word after title; `says`; one derived line (see section 4) | + `for` goals; acts in (step `actor`); told by (effect `tell`) | + interfaces that `serves` its steps (form-icon chips) and `allows`; read in `when`; program: dependency `realizes` it with `pin`, handlers that `uses` it | never icon only; gaps in section 4 |
| interface: what does the person see, type and press here? | form word; `says`; `invoked_as` in mono if cli; n shows, n accepts, n offers | `serves` step chip; `offers` choice labels as buttons; `shows` and `accepts` chips | + `includes` and "included by"; who may use it; `satisfies`; `proof`; work | gaps: an actor step with no serving interface (on the step); cli without `invoked_as`; accepts but serves no step |
| handler: which rows does this code do, with what? | `says`; n rows (`performs`); dependency chips (`uses`) | rows as workflow · step · row label, with effect badges | + `satisfies`; `src` as code path; work | gap on the row: a row with an effect has a handler |
| dependency: what outside thing, what surprises? | `pin`; `says`; `realizes` actor chip; n workarounds | + handlers that `uses` it; workaround rows (`when` → `says`) | + `satisfies`; deciding decision; rows that tell its actor | gap: a dependency nothing links to |
| rule: what must hold, who is held to it? | `says` (2 lines); n satisfied by; n constrains | `constrains` chips; satisfied-by chips grouped by kind | + `proof`; decision that set it; work | gap: a rule nothing satisfies and that constrains nothing; missing `proof` |
| setting: what knob, what default? | `name` mono; default as value + unit | + `says`; who reads it | + `proof`; `src` | gap: a setting nothing links to |
| quantity: what number, who depends on it? | `is` + `unit` large ("3 tools"); `says` | used by, per field word: `max`, `after`, `schedule`, `default`, `when` reads, `constrains` | + deciding decision and its answer `said` | gap: a quantity nothing links to |
| enum: what values are allowed? | `members` pills; n used by | + `says`; attributes `of` it | + `when` reads; rules that `constrains` it | gap: an enum nothing links to |
| decision: what was asked, chosen, changed? | `question` (2 lines); state open/proposed/answered + chosen option `label` | options as rows, chosen marked; `sets` targets as chips (the impact) | + `context`; proposal `why` and `heard`; answers (`said`, `at`, `note`); `sets` as old → new | open with no proposal: status dot, never red |

Rows inside parent cards:

| Row | Flow | Detail |
|---|---|---|
| step | `says`; `actor` chip, or "system", or `calls` chip; rows as today | + serving interface chips; `satisfies`. Gap: actor step with no serving interface |
| case | `when` text or "Otherwise"; `then` target | + `order`; `when` reads; `covers_ends`; effect badges; handler chip; `satisfies` |
| choice | `label` as button; `then` | + `when`; effects; handler; the interface that `offers` it |
| timeout | `after` quantity as value; `then` | + effects; handler |
| end | ✓ or ✗ by `result`; `says` | + who `covers_ends` it |
| effect | badge: `do` icon + `on` chip | same; field values are not in the ontology (section 7) |
| attribute | name; `type` or `of` chip | + `says`; `max`; `optional`/`many`; `derived` text and reads; written/accepted by |
| state | pill | + `says`; `when` reads |
| transition | arrow `from` → `to` with name | + firing rows; `event` workflows |
| workaround | `when` text → `says` | + reads chips |

Area frame: title + `says` in the frame header at Map; `unlike` chips at Detail. Principle: `says`, then `why` at Detail, then n entries citing it with `because`.

## 4. Actors in full (the owner's complaint)

Derived lines; Map shows the first non-empty: (1) "acts in n steps of n workflows" (step `actor`); (2) "told by n rows" (effect `tell` `on` it); (3) "n goals are for it" (goal `for`); (4) "uses n interfaces" (interface `serves` its steps, plus `allows`); (5) program only: "realized by <dependency> · <pin>".

By nature: human leads with the steps it acts in and the interfaces it uses. ai: same, header says "ai". program leads with the dependency that `realizes` it and the handlers that `uses` that dependency (the product-to-software link the owner misses).

Gaps: program actor told by a row with no handler/dependency chain ("a row that tells a program actor has a handler that uses a dependency realizing it"); program actor with no dependency: grey "no dependency realizes it yet" (work owed, not red); actor in no step, effect, goal or interface: grey "nothing links to it" (not a checked rule).

Member (human, agreed):
```
MAP                              FLOW
+------------------------------+ +--------------------------------------+
|(o) Member · human      ACTOR | |(o) Member · human              ACTOR |
| A person who borrows tools.  | | A person who borrows tools.          |
| acts in 1 step · told by 2   | | for    (@) Tools reach members       |
| 3 interfaces                 | | actor  Borrow · The member asks...   |
+------------------------------+ | tell   Borrow · Timeout              |
                                 |        Notify · Sent                 |
                                 | uses   [web] Borrow page  +2         |
                                 +--------------------------------------+
DETAIL
+----------------------------------------------------------+
|(o) Member · human                                  ACTOR |
| A person who borrows tools.                              |
| GOALS      for    (@) Tools reach members                |
| ACTS IN    actor  Borrow · The member asks for a tool.   |
|                   [Borrow a tool] [Leave]  (T) 2 days    |
| IS TOLD    tell   Borrow · Timeout                       |
|            tell   Notify · The mailer takes... · Sent    |
| REACHES IT serves [web] Borrow page  [>_] Borrow CLI     |
|                   [web] Leave button                     |
| READ IN    when   Borrow · Leave                         |
| agreed 2026-11-25                                        |
+----------------------------------------------------------+
```

Mail relay (program, not agreed):
```
MAP                              FLOW
+------------------------------+ +--------------------------------------+
|[=] Mail relay · program  * A | |[=] Mail relay · program     * ACTOR  |
| The mail relay a reminder    | | The mail relay a reminder is         |
| is handed to...              | | handed to, whichever mailer runs it. |
| realized by Mailer · smtplib | | realizes  (plug) Mailer · smtplib    |
| told by 1 row                | | tell      Notify · Sent              |
+------------------------------+ | uses      </> Send reminder  </> Lend|
  * = awaiting the owner         | /!\ 1 workaround                      |
                                 +--------------------------------------+
DETAIL
+----------------------------------------------------------+
|[=] Mail relay · program            * awaiting owner ACTOR|
| The mail relay a reminder is handed to, whichever        |
| mailer runs it.                                          |
| IS TOLD    tell     Notify · The mailer takes... · Sent  |
| READ IN    when     Notify · Sent                        |
| REALIZED   realizes (plug) Mailer   pin smtplib (Py 3.15)|
|            workaround: the mailer answers after reply-   |
|            wait -> The reminder is sent again the next   |
|            morning.                                      |
| CODE       uses     </> Send reminder (performs Notify · |
|                     Sent)   </> Lend                     |
| RULES      satisfies (via Mailer) One reminder a day     |
| ACTS IN    no step: it is only told                      |
+----------------------------------------------------------+
```

## 5. Entity Loan

```
MAP                              FLOW
+------------------------------+ +--------------------------------------+
|[#] Loan               ENTITY | |[#] Loan                       ENTITY |
| One tool lent to one member  | | One tool lent to one member until... |
| open -> returned             | | Tool       -> [#] Tool               |
| 3 attributes   /!\ 1         | | Condition  -> Tool condition  opt    |
+------------------------------+ | Renewals   number  max 3 tools       |
                                 | (*)-Start->(Open)-Return->(Returned) |
                                 | /!\ Return: a transition no effect   |
                                 |     fires                            |
                                 +--------------------------------------+
DETAIL
+----------------------------------------------------------+
|[#] Loan                              changed      ENTITY |
| One tool lent to one member until it comes back.         |
| /!\ Return: a transition no effect fires                 |
| ATTRIBUTES                                               |
|  Tool       -> [#] Tool            The tool lent.        |
|  Condition  -> Tool condition      optional  good|damaged|
|  Renewals   number                 max Max loans (3 tools)|
| LIFECYCLE  (*)-Start->(Open)-Return->(Returned)          |
|  Open      The member has the tool.                      |
|  Returned  The tool is back.                             |
|  Start     transition by  Borrow · Otherwise             |
|  Return    event of       Close loan     fired by: none  |
| CHANGED BY create  Borrow · The library records... ·     |
|                    Otherwise   </> Lend                  |
| SEEN IN    shows   [file] Loans report  (allows Owner)   |
| RULES      constrains  At most max loans (Renewals)      |
| READ BY    derived Tool · Out                            |
| proof tests/test_loans.py::test_loan_lifecycle           |
+----------------------------------------------------------+
```
Differences from lab 29B: the gap moves to the top; attributes lose the repeated `doc` icon and gain `says`, `max`, `optional`; states gain `says`; card height follows content.

## 6. Icons

Constraints: 16-unit viewBox, 1.5 stroke, no fill, at most 4 strokes, no feature under 3 units, each glyph unique. Avoid: faces, eyes, antennae, sparkles on a box, a diamond with a question mark inside, generic `doc` for anything that is not a file, gears for more than one kind.

goal: target (2 rings + dot), keep. capability: bolt, keep (delete duplicate). workflow: two boxes joined by an elbow, keep. entity: table (box, header line, one column line), replaces `doc`. attribute and state: no icon (type word / pill). transition: single arrow. actor human: person, keep. actor ai: four-point star alone, 10 units wide, replaces box-face. actor program: two stacked slabs each with a dot (server), replaces `robot`. interface web: window with title bar; cli: window with `>_`; http: `{ }`; mcp: wrench; library: three book spines; file: sheet with two lines; message: envelope. handler: `</>`, replaces gear. dependency: plug. setting: two sliders. rule: shield with tick. enum: three bullets with lines. quantity: hash. decision: question mark, no frame (the 12px one). principle: compass needle. step: none (system step = small gear, the only gear). case/choice/timeout: fork / button outline / timer. end: ✓ / ✗ circle.

## 7. What the ontology cannot answer yet (proposals for the owner, not decisions)

1. Effect values: an effect has only `do` and `on`; "due date set to +14 days" is a lab invention in `src/model.js`. Proposal: an optional value (`to`) on a write effect.
2. What a program actor sends back: Mail relay's answer exists only as free `when` text; no field for a reply or message shape.
3. Unused actor: no rule "an actor nothing links to" (exists for quantity, enum, setting, dependency).
4. Actor to interface is derived only (step `actor` + interface `serves`); a program actor that reaches us (an MCP client) has no direct "reaches the product through" link unless it is a step actor or in `allows`.
5. `shows`/`accepts`/`offers` are unordered sets; a card cannot say what is primary on a screen.
6. Attributes have no example value or format.
7. A goal has only `says` and `for`: no measure of how one knows it is reached.
8. No importance or frequency of a workflow; the Map cannot rank cards except by structure.
9. A step's `says` is optional and steps have no `title`, so mentions are long and no short step name exists.

## 8. Notes for the implementer

- Extend `VIEWS` in `src/cards.js` with the eight missing kinds; one renderer per (kind, level).
- Compute derived relations once in `src/model.js` as reverse indexes keyed by field word.
- Card height follows content; no fixed-height empty bodies.
- Extend `qa/check.mjs`: no card body with fewer than two lines; no icon drawn twice on one card; every icon unique per kind, nature and form.
