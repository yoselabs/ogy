# Design key (never shown to runs or scorers)

What the eval expects and how arms differ. Scorers get [key.md](key.md) only. This file is for whoever builds the
arms, runs the unblinded [blame pass](blame.md) and writes the result.

## Kind names per arm

A = `eval-before`. C0 and C = stage 1 (`1fb0e39`), C0 without the like/unlike blocks: the same names. B = after
all stages; a forecast, every `(verify)` cell is settled against `inputs/B.md` before a B run is scored, and the
last table of key.md is corrected with it. "same" means the same as the column to its left.

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
| 10 | `command` (`invoked_as`, `serves`) | same | `interface` (`form`, `shows`) (verify) |
| 11 | `decision > option` x2, no `answer`, no `guess` | no `proposal` | same |
| 12 | `entity > attr`, type list or text | `entity > attribute`, type text, `many` or not | same |
| 13 | `actor`, nature program | same | same; credit `dependency.realizes -> actor` (verify) |
| 14 | `entity > attr`, type money, `derived` | `entity > attribute` | same |
| 15 | `rule` + `proof`; 15b `by` | `rule` + `proof`; 15b `satisfies` | 15b `rule.constrains` (verify) |
| 16 | `external` (`pin`) | `dependency` (`pin`) | same |
| 17 | `value` | `quantity` | same |
| 18 | `view`, `serves` both steps | same | `interface`, `includes` (verify) |
| 19 | `external > deviation` (`when`) | `dependency > workaround` (`when`) | same |
| 20 | `actor`, nature program; step `actor` | same | the tie to [10] as B's map gives it (verify) |
| 21 | `decision > option` x2 + `guess` | + `proposal` | same |
| 22 | `value` + `config_key` (`binds`) | `quantity` + `setting` (`default`) | same |
| 23 | `goal`, `for` | same | same |
| 24 | on the `command` of [10] | same | on the `interface` of [10] (`shows`) (verify) |
| 25 | `rule` + `proof`; not a `deviation` | not a `workaround` | same |
| 26 | `capability`, `serves ->` [23] | `capability`, `realizes ->` [23] | same |
| 27 | `entity > attr`, type number | `entity > attribute` | same |
| 28 | `decision > option` x2 + `answer` | same | same |

## Where arms differ by more than a name

- 15b. In A the map prints `by` only as a field "every kind also takes", with no target and no direction; C names
  it `satisfies` and the rule's like-line says "satisfied by entries". A cannot express the link as clearly as C,
  so 15b is outside the 51 and reported apart.
- [12]. A has a `list` type; C has `type text` plus a `many` mark. 12b accepts text or list and ignores `many`, so
  both arms can hit it with one field. Still reported apart.
- [10], [18], [24]. Two kinds in A, C0 and C, one in B. C against B on these is the merge, not a name.
- [13], [20]. B may add links (`dependency.realizes -> actor`).
- Stale words. The glossary at `1fb0e39` (C0, C) still says "never an external" (actor), "options, guess and
  answers" (decision) and "a rule or value" (proof) although the kinds are renamed. This works against the new
  names on [13], [20], [21] and the number facts. Either pin C0 and C on a commit that cleans these lines before
  the freeze, or report it as a limit. B must be pinned on a clean commit.
- Facts that say in other words what a like/unlike line says: [3] and [16] (not ours), [13] and [20] (it
  contacts us), [12] (free remarks), [27] (a tally), [23] and [26], [25] (our own wish), [8], [15]. The facts share
  no content word with those lines (`check-neutral.py`), but the meaning overlaps by design: that is what C0
  against C measures.

## Names under test

| old (A) | new | home of | expected wrong pull of the old name | expected wrong pull of the new name |
|---|---|---|---|---|
| `value` | `quantity` | 4, 17, 22 | [8] (what the owner values); [14] (a value object); [5], [27] (any number) | [5], [27] (a measured amount); [14]; missed for [17] |
| `set` | `enum` | 6 | [12] (a set of remarks); missed for [6] | [2] stages as an enum |
| `operation` | `handler` | 7 | [10] (an API operation: seen in 2 of 2 pilot runs); [16] (a library function) | [10] (a request handler); [13] (a webhook handler) |
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

Gains of C0 over A on 9b, 22c, 15b, [10], [20], [13]. Further gains of C over C0 on [12], [27], [20], [16], [25].
Possible losses of C0 against A on [5], [14], [27] (`quantity` read as any measured amount) and on [10]
(`handler` read as a request handler).
