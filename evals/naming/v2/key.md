# Scorer key (hidden from runs)

One correct home per fact and the link items each fact needs, in neutral words. The neutral columns are the
authority. The last table gives the words the runs use for these homes; every run was rewritten into one
vocabulary before you got it, so the same home carries the same word in every run, with the few exceptions the
table lists.

## Homes and link items

A link item is one link or one filled field. Each is scored 0 or 1 on its own. An item written "no ..." is an
absence item: it scores 1 when the fact has an entry and the named link is not there.

| fact | correct home (neutral) | link items | false friends |
|---|---|---|---|
| 1 rider, mechanic | two acting parties, both human | 1a both marked human | one party with a role field; a kept thing "account" |
| 2 hire: booked, out, returned, paid | a kept thing, with four lifecycle stages and three moves between them as its parts | 2a four stages written inside the hire; 2b three moves, each naming the stage it leaves and the stage it reaches | a closed list of words for the stages; a flow with four steps and no kept thing; a fact kept about the hire holding the stage as a word |
| 3 PayRight, version 2024-06 | an outside thing we use and do not own | 3a the version 2024-06 in the field for it | an acting party; a kept thing; an environment knob |
| 4 12 hours without a late fee | a decided number with its unit | 4a 12 and hours on it; 4b another entry reads it through a link: the upper limit of [5], a branch condition or a wait limit of a flow, or the worked-out link of [14] | a fact kept about the hire; an environment knob; a must-hold statement with 12 left in its text |
| 5 minutes a hire lasted | a fact kept about a thing, written inside the hire, a number or a length of time | 5a written inside the hire of [2]; 5b typed as a number or a length of time | a decided number with a unit; a kept thing of its own |
| 6 three sorts of bike | a closed list of words | 6a the three words listed on it; 6b a fact kept about a kept thing "bike" points at this list through the field for it (whatever else the run writes as that fact's type changes nothing) | lifecycle stages of the bike; three kept things; free text |
| 7 code that takes the payment | the code unit that does the work behind a branch | 7a it names [3] as what it talks to; 7b it names the branch where the rider hands the bike back as what it carries out | an API call offered to acting parties; the outside thing; a flow; an acting party |
| 8 no surprise charge | a statement held above all, that later work is judged against (the fixed folder) | none | a decided number; a must-hold statement with a check; the result the product is for |
| 9 `PAYRIGHT_URL` | an environment knob the product reads, under its real name | 9a the name `PAYRIGHT_URL` on it; 9b no link from the knob to a decided number or a closed list | a decided number; a fact kept about [3]; the version field of [3] |
| 10 `GET /stations/{id}/bikes` | an API call offered to outside programs, read-only | 10a the call's form in the field for it; 10b what the map requires of such an entry: the step it is offered at, or what it gives back | the code unit doing the work; the outside thing; a screen, where the run has a separate kind for calls; a flow alone |
| 11 two bikes at once? | an open question with two listed possibilities, none chosen | 11a two possibilities as parts; 11b no pick recorded, neither the owner's nor the builder's | a recorded pick; a must-hold statement; a decided number "2" |
| 12 remarks on a bike | a fact kept about the bike, free text | 12a written inside a kept thing "bike"; 12b typed as free text or as a list, and not pointed at a closed list (a mark for "several" is neither needed nor wrong) | a closed list of words; a glossary word per remark; a kept thing "remark" with stages |
| 13 PayRight's notifier | an acting party that is a program; separate from [3] | 13a marked as a program; 13b the move to "paid" of [2] is tied to what it does (it acts in the step whose branch makes the move, or the move is that branch's effect) | folding it into [3]; the code unit that receives the message; an API call alone |
| 14 what a hire cost | a fact kept about the hire, typed as an amount with currency, worked out from other entries | 14a written inside the hire of [2]; 14b typed as an amount with currency; 14c worked out from [5]; 14d worked out from [17] | a decided number; a kept thing of its own ("price", "amount") |
| 15 never out on two hires | a must-hold statement with a check | 15a the check named on it in the field for it; 15b (counted apart) tied by a link to the kept thing it limits, the hire or the bike, from either end | a statement held above all; a branch alone; text on the hire only |
| 16 geolib, version 3 | an outside thing we use and do not own | 16a the version 3 in the field for it | the code unit doing the work; an API call; a glossary word; `none` |
| 17 5 euros per hour over | a decided number with its unit | 17a 5 and euros (per hour) on it | a fact kept about the hire; an environment knob; a must-hold statement with 5 left in its text |
| 18 bike tile shown twice | one screen entry, used twice | 18a tied to the map screen or its step; 18b tied to the list of past hires or its step | two entries; a kept thing "bike"; the code that draws it |
| 19 PayRight rounds down | a known surprise of an outside thing, with what we do about it, written inside that thing | 19a written inside [3]; 19b its required link for what sets it off is filled and points at [3] or at a decided-number entry | a must-hold statement alone; a branch alone; a decided number "half a cent" alone |
| 20 the city's transport app | an acting party that is a program | 20a marked as a program; 20b tied to [10] the way the run's map gives: it acts in the step [10] is offered at, or [10] names it | the outside thing we use; folding it into [10]; a kept thing |
| 21 breakdown: the AI goes with "nothing" | an open question with two listed possibilities, plus the builder's own pick, not the owner's | 21a two possibilities as parts; 21b the builder's pick points at "it costs nothing"; 21c no owner's pick recorded | recording the pick as the owner's; a must-hold statement; a decided number "0" |
| 22 held 15 minutes, `HOLD_MINUTES` | two entries: a decided number, and an environment knob that falls back to it. Either may be a `new:` entry in the links cell | 22a 15 and minutes on the number; 22b the name `HOLD_MINUTES` on the knob; 22c a link from the knob to the number; 22d the booking's wait limit in a flow reads the number | the knob alone with 15 in its text; the number alone; a fact kept about the booking |
| 23 a free bike within five minutes' walk | the result the product is for | 23a tied to the rider of [1] as the party it is for | a statement held above all; a must-hold statement; a decided number "5 minutes" alone; what the product can do |
| 24 what [10] sends back | on the entry of [10] itself (its text or its fields); no entry of its own | none | a kept thing "response"; a closed list of the three words; a screen; a second API call entry |
| 25 no card that runs out within a month | a must-hold statement with a check; ours, not PayRight's | 25a the check named on it in the field for it; 25b not written inside [3] and not marked as a surprise of [3] | a known surprise of [3]; a statement held above all; an environment knob |
| 26 finding free bikes near a spot | what the product can do, apart from how | 26a tied by a link to [23] | a flow; an API call; the code unit; the result itself |
| 27 free bikes at a station | a fact kept about a thing, written inside a kept thing "station", a number | 27a written inside a kept thing "station"; 27b typed as a number | a decided number; a lifecycle stage; a kept thing of its own |
| 28 no helmets, settled | a question with two listed possibilities and the owner's recorded pick | 28a two possibilities as parts; 28b the owner's pick points at "no helmets"; 28c the date 3 March on the pick; 28d "on the phone" on the pick | the builder's own pick; a must-hold statement alone; a statement held above all |

Counted link items: 51, on facts [2] to [28], without 15b. Apart: 1a (one item) and 15b (one item).
Facts with no item: [8], [24].

Not scored, listed in your notes when present: for [3] and [16], a code unit named as using it, beyond [7]; for
[13], [3] linked as what stands behind the notifier; for [24], the three shown facts linked to facts kept about
the bike; for [26], a flow tied to it; for [27], marked as worked out from the hires; for [21], a reason on the
builder's pick. Extra entries that are no false friend (for [25] or [4], a branch of a flow next to the home)
change no mark.

## The words the runs use

`>` means "written inside". Where two words are given, either is right; do not ask which a run "should" use.

| fact | home, in the runs' words |
|---|---|
| 1 | `actor` x2, `nature` human |
| 2 | `entity` > `state` x4, `transition` x3 (`from`, `to`) |
| 3 | `external` (`pin`) |
| 4 | `value` (`is`, `unit`); read through `attr.max`, `case.when`, `choice.when`, `timeout.after` or `attr.derived` |
| 5 | `entity > attr`, `type` number or duration |
| 6 | `set` (`members`); an `attr` of bike with `of ->` it |
| 7 | `operation` (`uses`, `performs`) |
| 8 | `principle` |
| 9 | `config_key` (`name`), no `binds` |
| 10 | `command` (`invoked_as`, `serves`), or `interface`. 10a: `invoked_as` holding the call, or on an `interface` `form: http`. 10b: `serves ->` a step, or `shows ->` the bike or facts kept about it |
| 11 | `decision > option` x2, no `answer`, no `guess` |
| 12 | `entity > attr`, `type` text or list, with or without `many`, no `of` |
| 13 | `actor`, `nature` program; `step.actor`, an `effect` on the `transition`. `realizes ->` this actor on the entry of [3] is not scored and is not "folding into [3]" as long as the actor entry exists |
| 14 | `entity > attr`, `type` money, `derived ->>` [5], [17] |
| 15 | `rule` with `proof`; 15b: `by` on the entity pointing at the rule, or `constrains` on the rule pointing at the entity. A `state` or an `attr` of that entity counts as the entity, at either end. `satisfies` on an entity, `attr` or `state` is 0 |
| 16 | `external` (`pin`). An `interface` or `command` entry for geolib, whatever its `form`, is the false friend "an API call" |
| 17 | `value` (`is`, `unit`) |
| 18 | `view` or `interface` with `serves` to both steps, or an `interface` that the two screens' `interface` entries each name with `includes` |
| 19 | `external > deviation` (`when ->` [3] or a `value`, `says`) |
| 20 | `actor`, `nature` program; 20b: the `actor` of the step that [10] `serves`, or `allows ->` this actor on the entry of [10] |
| 21 | `decision > option` x2 with a `guess` (`chose`), no `answer` |
| 22 | `value` and `config_key` (`name`, `binds ->` the value); `timeout.after ->` the value |
| 23 | `goal`, `for ->` [1] |
| 24 | on the `command` or `interface` of [10]: in its `says`, or as `shows ->` the bike or facts kept about it. New `attr` entries of the bike that [10] `shows` belong to this home and are no false friend; a kept thing made only to hold the reply is one |
| 25 | `rule` with `proof`; not a `deviation` |
| 26 | `capability`, with `serves` or `realizes` `->` [23] |
| 27 | `entity > attr`, `type` number |
| 28 | `decision > option` x2 with an `answer` (`chose`, `at`, `where`) |

Some batches hold runs with the kind `interface` and the fields `constrains`, `satisfies`, `allows`, `accepts`,
`includes`, `shows`, `form`. In those runs:

- `satisfies ->` a rule, written on an `operation`, a `step`, a `case`, a `choice`, a `timeout`, a `workflow`, an
  `external` or an `interface`, is a field of their map. It is not scored and is never a wrong link, whichever
  rule it names. The same holds for `accepts`.
- `form` with any member is never a wrong link. It is scored in one place only: `form: http` on the entry of [10]
  hits 10a, as row 10 says.
- `allows`, `shows`, `includes` and `constrains` are scored exactly as rows 10, 15, 18, 20 and 24 give them.
- `satisfies` on an `entity`, an `attr` or a `state` is not a field of their map: 15b is 0.
- `realizes ->` an actor on an `external` is not scored and is never a wrong link.
