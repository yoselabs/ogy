# Design key (never shown to runs or scorers)

What the eval expects and how arms differ. Scorers get [key.md](key.md) only. This file is for whoever builds the
arms, runs the unblinded [blame pass](blame.md) and writes the result.

## Kind names per arm

A = `eval-before`. C0 and C = stage 1 with the glossary cleaned (`dd9293d`, branch `eval-stage1-clean`), C0 without
the like/unlike blocks: the same names. B = after all stages (`43f15fc`), read from `inputs/B.md`; the section below says how each open cell was settled. "same" means
the same as the column to its left.

| fact | A (before) | C0, C (stage 1) | B (after) |
|---|---|---|---|
| 1 | `actor` x2, nature human | same | same |
| 2 | `entity` > `state` x4, `transition` x3 | same | same |
| 3 | `external` (`pin`) | `dependency` (`pin`) | same |
| 4 | `value`; read by `attr.max`, a `when`, `timeout.after` or `attr.derived` | `quantity`; the same readers | same |
| 5 | `entity > attr`, type number or duration | `entity > attribute` | same |
| 6 | `set`; `attr` type one, `of ->` it | `enum`; `attribute.of ->` it (the map allows `of` without `type`) | same |
| 7 | `operation` (`uses`, `performs`) | `handler` | same |
| 8 | `principle` | same | same |
| 9 | `config_key` (`name`), no `binds` | `setting` (`name`), no `default` | same |
| 10 | `command` (`invoked_as`, `serves`) | same | `interface` (`form: http`, `invoked_as`; `shows` or `serves`) |
| 11 | `decision > option` x2, no `answer`, no `guess` | no `proposal` | same |
| 12 | `entity > attr`, type list or text | `entity > attribute`, type text, `many` or not | same |
| 13 | `actor`, nature program | same | same; credit `dependency.realizes -> actor` on [3] |
| 14 | `entity > attr`, type money, `derived` | `entity > attribute` | same |
| 15 | `rule` + `proof`; 15b `by` on the entity | `rule` + `proof`; 15b `satisfies` on the entity | 15b `rule.constrains ->` the entity or a part of it; `satisfies` on the entity is 0 |
| 16 | `external` (`pin`) | `dependency` (`pin`) | same |
| 17 | `value` | `quantity` | same |
| 18 | `view`, `serves` both steps | same | `interface`: `serves` both steps, or `includes` from both screens |
| 19 | `external > deviation` (`when`) | `dependency > workaround` (`when`) | same |
| 20 | `actor`, nature program; step `actor` | same | `allows ->` it on the interface of [10], or the served step's `actor` |
| 21 | `decision > option` x2 + `guess` | + `proposal` | same |
| 22 | `value` + `config_key` (`binds`) | `quantity` + `setting` (`default`) | same |
| 23 | `goal`, `for` | same | same |
| 24 | on the `command` of [10] | same | on the `interface` of [10] (`says` or `shows`) |
| 25 | `rule` + `proof`; not a `deviation` | not a `workaround` | same |
| 26 | `capability`, `serves ->` [23] | `capability`, `realizes ->` [23] | same |
| 27 | `entity > attr`, type number | `entity > attribute` | same |
| 28 | `decision > option` x2 + `answer` | same | same |

## Arm B: settled against `inputs/B.md` (43f15fc, 2026-11-20)

B is scored twice: on the full 51, and on the **common-homes subset** of 45 items, the 51 without 10a, 10b, 18a,
18b, 20b and 13b (the items whose home or link exists in another form in B). Both are fixed. Every comparison with
B describes and decides nothing.

What B's map prints, and what the key takes from it. The neutral columns of key.md did not change; its last
table carries these words.

| cell | B's map | settled as |
|---|---|---|
| [10] | `interface: !form(web\|cli\|http\|mcp\|library\|file\|message) invoked_as serves->>step shows->>entity\|attribute ... allows->>actor`; `invoked_as` is required of a command line only; `serves` is required only of one that accepts input or offers choices | home `interface`. 10a: `invoked_as` with the call, or `form: http` (the call string has no required field in B). 10b: `serves ->` a step, or `shows ->` the bike or its attributes |
| [18] | `includes->>interface`; `serves->>step` stays | 18a, 18b: the tile serves both steps, or each of the two screen interfaces names it with `includes` |
| [24] | `shows->>entity\|attribute` | home: on the interface of [10], as text or as `shows`. New attributes of the bike that it shows are part of the home (credit, as before); an entity made to hold the reply stays a false friend |
| [13] | `dependency: ... realizes->actor`; rule "a row that tells a program actor has a handler that uses a dependency realizing it" | home unchanged: an `actor`, nature program (the owner: a business party that is a program lives in product). `realizes -> [13]` on [3] is credit, never an item, and is not "folding into [3]" while the actor entry exists |
| [20] | rule "an interface that serves a step takes who may use it from the steps' actors; `allows` is for one that serves none" | 20b: `allows -> [20]` on [10], or [20] as the `actor` of the step [10] serves |
| 15b | `rule: !says constrains->>quantity\|enum\|setting\|entity\|attribute\|state`; `satisfies->>rule` only on workflow, step, case, choice, timeout, dependency, handler, interface; no longer a field every kind takes | 15b in B is `rule.constrains ->` the hire or the bike, or a state or attribute of it. `satisfies` on an entity is not in B's map: 0 |
| D15 | not printed: the map and the glossary say nothing about which kinds need a proof; `proof` is a field every kind takes, in every arm | owner's decision (27bea9f): rows, rule, interface, setting and workaround need a proof, an entity only with transitions, not step, handler or quantity. Facts [9], [10] and [19] name no test, so a run has nothing to put there: no item, no credit, and a `proof` a run invents for them changes no mark. [15] and [25] name a check; 15a and 25a stand in every arm |
| vocab.tsv | stages 2 and 3 add no 1:1 rename: `interface` is a merge of two kinds, `constrains`, `allows`, `includes`, `shows`, `accepts`, `names` are new, `satisfies` is narrowed | nothing added |
| names-extra.txt | every name that stood there is in B's map | emptied; `check-neutral.py` passes with B |
| `form` | `!form(web\|cli\|http\|mcp\|library\|file\|message)` is required on every interface | [18] needs `form: web` and [10] `form: http` to be valid in B. Neither is in the 51 (10a accepts `form: http` or `invoked_as`); a missing or wrong `form` changes no mark there. `form: http` on [10] is addendum item B2. An interface with `form: library` for [16] is the false friend |

15b needs no correction after unblinding: B's `satisfies` is not rewritten (vocab.tsv), B is scored in batches of
its own, and key.md tells the scorer that `satisfies` on an entity is 0 and that `satisfies` on a behaviour kind
is unscored and never a wrong link. A part of the entity counts as the entity in every arm.

The map was first settled on `511a27e`; the builds at `810c47d` and `43f15fc` differ from it in four glossary
lines only (actor, decision, read-back, proof) and from each other in nothing.

### B's absolute report (fixed before any run)

Given for B on each model whatever the gates say, also when arm A's ceiling voids the model's comparisons: per
link item of the 51, in how many of the 6 runs it was hit; K per fact; and for each misplacement the kind the run
chose and the blame verdict. No threshold is attached; it describes how the final map reads on its own.

### B-only addendum (fixed before any run)

Six items on existing facts that only B's map can carry. Scored in the blame pass, open, on B runs only; each 0
or 1 per run; reported as six counts of 6 per model. **Never summed** with the 51, the 45 or the names subset:
B4 overlaps 15b, B6 overlaps 20b, B2 overlaps 10a.

| item | fact | 1 when the run writes |
|---|---|---|
| B1 | [3], [13] | `realizes -> [13]` on the dependency of [3] |
| B2 | [10] | `form: http` on the interface |
| B3 | [24] | `shows ->` naming facts kept about the bike (code, sort, battery level), on the interface of [10] |
| B4 | [15] | `constrains ->` the hire, the bike or a part of one, on the rule |
| B5 | [25] | something that `satisfies -> [25]`: the handler of [7], or a step, case or choice of the paying flow |
| B6 | [20] | `allows -> [20]` on the interface of [10], or [20] as the actor of the step it serves |

### What the eval does not measure in B

- Layer direction (product never names software; a business party that is a program lives in product). A run names
  kinds, not layers.
- The work-left statuses `unused`, `unrealized`, `unserved`.
- Which kinds need a proof (D15): not printed in the input.
- Whether the real lint accepts what a run wrote. A B run may write a link the map seems to offer and the lint
  refuses. The blame pass counts each such link as a finding about the map (it read as allowed), not as a run's
  error, and lists them.

The exercise changed twice after B was first built. First `check-neutral.py` found four words of the facts that
only B's map or like-lines print (`http` and `library`, members of `interface.form`; `belongs`; `point`), and
"handles" in [3] leaned on `handler`: [3], [10], [16], [20] and [23] were reworded. Then "that message" in [13]
was found to carry another member of `form`; the checker had missed it because it read the prompt line above the
map as given text. It now reads the map and glossary only and bans every enum member that only some arms print;
[13], [6] ("exactly one of", A's `type one`), [18] ("list", A's `type list`) and [11] ("on the table") were
reworded. Every run made before this (the pilots) answered an older text.

## Where arms differ by more than a name

- 15b. In A the map prints `by` only as a field "every kind also takes", with no target and no direction; C names
  it `satisfies` and the rule's like-line says "satisfied by entries". A cannot express the link as clearly as C,
  so 15b is outside the 51 and reported apart.
- [12]. A has a `list` type; C has `type text` plus a `many` mark. 12b accepts text or list and ignores `many`, so
  both arms can hit it with one field. Still reported apart.
- [10], [18], [24]. Two kinds in A, C0 and C, one in B. C against B on these is the merge, not a name.
- [13], [20]. B adds links: `dependency.realizes -> actor`, `interface.allows -> actor`.
- B's structure presses on items of the 45 and beyond, through new fields and the new "nothing links to" rules. A
  gain or loss of B on these may come from those lines and not from a name. This touches comparisons with B only,
  never A against C0:

  | item | what B's map adds |
  |---|---|
  | 4b, 22c | `rule.constrains -> quantity\|setting`; rules "a quantity nothing links to", "a setting nothing links to" |
  | 6b | `rule.constrains -> enum`; rule "a enum nothing links to" |
  | 9b | rule "a setting nothing links to" invites a link from or to the knob (a loss on the absence item) |
  | 26a | rule "a capability realizes a goal" |
  | 7a | rules "a dependency nothing links to" and "a row that tells a program actor has a handler that uses a dependency realizing it" |
  | 13b (outside the 45) | rule "a transition no effect fires"; `dependency.realizes -> actor` |
  | 15b (outside the 51) | `rule.constrains`; rule "a rule nothing satisfies and that constrains nothing" |

- The glossary. C0 and C are pinned on `dd9293d`: stage 1 plus the term texts of actor, decision, read-back and
  proof as on main, so that the glossary says "never a dependency", "options, proposal and answers", "a rule or
  quantity" where `1fb0e39` still had the old words. The four lines are the only difference from the `1fb0e39`
  inputs. A's glossary says the same things in A's words ("never an external"). So in C0 the actor line now
  speaks for [13] and [20] exactly as A's does: no arm is handicapped by a stale word any more.
- Facts that say in other words what a like/unlike line says: [3] and [16] (not ours), [13] and [20] (it
  contacts us), [12] (free remarks), [27] (a tally), [23] and [26], [25] (our own wish), [8], [15]. The facts share
  no content word with those lines (`check-neutral.py`), but the meaning overlaps by design: that is what C0
  against C measures.

## Names under test

| old (A) | new | home of | expected wrong pull of the old name | expected wrong pull of the new name |
|---|---|---|---|---|
| `value` | `quantity` | 4, 17, 22 | [8] (what the owner values); [14] (a value object); [5], [27] (any number) | [5], [27] (a measured amount); [14]; missed for [17] |
| `set` | `enum` | 6 | [12] (a set of remarks); missed for [6] | [2] stages as an enum |
| `operation` | `handler` | 7 | [10] (an API operation); [16] (a library function) | [10] (a request handler); [13] (a webhook handler) |
| `external` | `dependency` | 3, 16 | [13], [20] (anything outside); missed for [16] | read as a link, not an entry; missed for [3] |
| `config_key`, `binds` | `setting`, `default` | 9, 22 | 9b lost (3 of 3 runs in v1) | [4], [17] (a business setting) |
| `deviation` | `workaround` | 19 | missed for [19]; [25] | [25] |
| `guess` | `proposal` | 21 | few expected | [11] or [28] |
| `by` | `satisfies` (C), `constrains` (B) | 15 | 15b missed (3 of 3 runs in v1) | direction of 15b wrong |
| `serves` (capability) | `realizes` | 26 | 26a missed | confused with the flow's `realizes` |
| `view`, `command` | `interface` (B) | 10, 18, 24 | [10] as `view`; [7] as `command` | [7]; a code contract for [10]; missed for [18] |
| `attr` | `attribute` | 5, 12, 14, 27 | none expected | none expected |

## Names subset (fixed before any run)

Reported next to the 51, read by the same counting rule, never the verdict on its own: 19 marks per run.

- 8 link items that a renamed field or a renamed target kind carries: 4b, 6b, 7a, 9b, 15b, 19a, 22c, 26a.
- K on the 11 facts a renamed name is expected to pull in or lose: [2], [5], [8], [10], [12], [13], [14], [16],
  [20], [25], [27]. F on the same facts is given as a count beside it.

## Expected, to compare with the result

Gains of C0 over A on 9b, 22c, 15b, [10]. On [13] and [20] the glossary line "never a dependency" (C0) mirrors
A's "never an external", so a gain there would be the name `dependency` alone; a small one is expected, since
"external" invites anything outside. [21] and the number facts: none expected from the glossary now. Further gains
of C over C0 on [12], [27], [20], [16], [25].
Possible losses of C0 against A on [5], [14], [27] (`quantity` read as any measured amount) and on [10]
(`handler` read as a request handler).
