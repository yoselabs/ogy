# Naming eval key (hidden from runs)

One correct home per fact, in neutral words. The table below it maps each home to the kind names of every arm.
Written on 2026-11-20, before the after arm existed: **check the "after" and "stage 1" columns against the map
printed at the pinned commits before scoring, and correct them here.** The neutral column is the authority.

## Homes

| fact | correct home (neutral) | required links and fields | false friends |
|---|---|---|---|
| 1 free shipping from 50 euros | a decided number with its unit | 50 and the unit on it; something reads it: a branch condition of the buying flow, or a must-hold statement | a fact kept about the order; an environment knob; a statement held above all; a number left in text |
| 2 three channels | a closed list of words | the order's channel (a new fact kept about [3]) is `of` this list | lifecycle stages of the order; three acting parties; free text |
| 3 order: placed, paid, shipped | a kept thing, with three lifecycle stages and two moves between them as its parts | each move names from and to | a closed list of words for the stages; a flow with three steps and no kept thing |
| 4 order total | a fact kept about a thing, typed money | written inside [3] | a decided number; a kept thing of its own |
| 5 PayRight, version 2024-06 | an outside service we depend on and do not own | the version on it; [13] uses it (either end may state it) | an acting party; a kept thing; only a "which provider" question |
| 6 double notice, we ignore the second | a known surprise of an outside service, with what we do about it, written inside that service | inside [5] | a must-hold statement alone; a branch alone; a note in text |
| 7 `PAYRIGHT_URL` | an environment knob the program reads, under its real name | the name `PAYRIGHT_URL` on it; no link required | a decided number; a fact kept about [5]; the version field of [5] |
| 8 shopper, admin | two acting parties, both human | none | one party with a role field; a kept thing "account" |
| 9 PayRight's notifier | an acting party that is a program; separate from [5] | none required; credit if [5] is linked as what stands behind it, where the map has such a link | folding it into [5]; the code that receives the call; an API endpoint |
| 10 locked account cannot check out | a branch of the buying flow's checkout step: when the account is locked, go to a failed ending | the condition reads the locked stage of a new kept thing "account"; the branch leads to a failed ending | a must-hold statement alone (plausible, not the home: score kind 0, false friend 1); a new acting party "locked shopper" (false friend) |
| 11 product tile on two pages | one screen entry, reused | one entry linked to both places: by the reuse link if the map has one, else by serving both steps | two entries; a kept thing "product"; the code that renders it |
| 12 `GET /products/{id}` | an API call offered to outside programs, read-only | the call's form on it; what it shows (name, price) or the step it serves, as the map requires | the code unit doing work; a code-level contract (class or protocol); a screen, where the map has a separate kind for calls; the outside service kind |
| 13 code that charges the card | the code unit that does the work behind a branch | uses [5]; performs the "shopper confirms" branch (new) | an API call offered to actors; the outside service; a flow |
| 14 total never negative | a must-hold statement with a test | the test named as its check; linked with [4] in the direction the map gives | a statement held above all; a decided number "0"; a type note on [4] only |
| 15 checkout must feel fast | a statement held above all, that later calls are judged against (the fixed folder) | none | a decided number; a must-hold statement with a test; an aim of a party |
| 16 guest checkout or account | an open question with two listed ways, none chosen | two ways as parts; no pick recorded; credit, not required: the agent's own pick marked as its own, not the owner's | recording a pick as the owner's; an aim; a must-hold statement |
| 17 nightly basket clean-up | a flow the system starts on a timetable | the timetable on it; a system step whose branch deletes baskets | the code unit alone; "outside the knowledge base, a plain task"; a must-hold statement |

## Kind names per arm

A = `eval-before`. C = stage 1 only (renames, screens and calls still two kinds). B = after all stages.
`>` means "written inside".

| fact | A (before) | C (stage 1) | B (after) |
|---|---|---|---|
| 1 | `value` | `quantity` | `quantity` |
| 2 | `set`; `attr.of -> set` | `enum`; `attribute.of -> enum` | `enum`; `attribute.of -> enum` |
| 3 | `entity` > `state` x3, `transition` x2 | same | same |
| 4 | `entity > attr` (type money) | `entity > attribute` | `entity > attribute` |
| 5 | `external` (`pin`) | `dependency` (`pin`) | `dependency` (`pin`) |
| 6 | `external > deviation` | `dependency > workaround` | `dependency > workaround` |
| 7 | `config_key` (`name`) | `setting` (`name`) | `setting` (`name`) |
| 8 | `actor` x2, nature human | same | same |
| 9 | `actor`, nature program | same | same; credit `dependency.realizes -> actor` |
| 10 | `workflow > step > case` (`when ->> state`, `then -> end` with result failure) | same | same |
| 11 | `view`, `serves` both steps | `view`, `serves` both steps | `interface`, named by `includes` of the cart and orders interfaces |
| 12 | `command` (`invoked_as`, `serves`) | `command` (`invoked_as`, `serves`) | `interface` (`form`, `shows`; no step needed) |
| 13 | `operation` (`uses`, `performs`) | `handler` (`uses`, `performs`) | `handler` (`uses`, `performs`) |
| 14 | `rule` + `proof`; [4] names it with `by` | `rule` + `proof`; [4] names it with `satisfies` | `rule` + `proof`; `rule.constrains -> attribute` |
| 15 | `principle` | `principle` | `principle` |
| 16 | `decision > option` x2, no `answer`; credit `guess` | same; credit `proposal` | same; credit `proposal` |
| 17 | `workflow` (`schedule`), system `step`, `case > effect` delete | same | same |

## Names under test

The false friend each name is expected to invite. Scorers record the name a run's "why" line blames, listed or not.

| name | arm | expected wrong pull |
|---|---|---|
| `value` | A | [15] (what the business values); a value object for [4] |
| `set` | A | missed for [2] (reads as a verb or a collection) |
| `operation` | A | [12] (an API operation) |
| `external` | A | [9] (anything outside) |
| `command`, `view` | A, C | [12] as `view` (it shows data); [13] as `command` |
| `config_key` | A | few expected: baseline for `setting` |
| `deviation` | A | missed for [6] (reads as a defect or a variance) |
| `guess` | A | few expected: baseline for `proposal` |
| `interface` | B | [13] or a code contract for [12]; missed for [11] |
| `handler` | C, B | [12] (a request handler is the endpoint); [9] (a webhook handler) |
| `dependency` | C, B | a link between entries, not an entry; missed for [5] |
| `quantity` | C, B | [4] (a measured amount); missed for [1] (a price is not a "quantity") |
| `enum` | C, B | [3] stages as an enum |
| `setting` | C, B | [1] (a shop setting) |
| `workaround` | C, B | few expected |
