# Naming eval scores, arm A (eval-before / baseline names)

Scored against key.md, column A (before), with rubric.md. K = kind correct, L = required links present,
F = no false friend (1 = clean, 0 = false friend). Misplacement = K 0. "Misleading name" is taken only from the
run's own "why" line; `structural` means the line gives a structural reason, `-` means no error to attribute.

## A-1

| fact | K | L | F | misplaced | misleading name | note |
|---|---|---|---|---|---|---|
| 1 | 0 | 0 | 0 | yes | structural | Homed as `rule`, 50 EUR left in the rule's text (false friend "a number left in text"); `value` only offered as an optional split, not made. Why: "the fact is the condition, not a number on its own". |
| 2 | 1 | 1 | 1 | no | - | `set`; new order attr channel `of -> [2]`. |
| 3 | 1 | 1 | 1 | no | - | entity + 3 states + 2 transitions, each with from/to. |
| 4 | 1 | 1 | 1 | no | - | `entity > attr` on order, type money. |
| 5 | 1 | 1 | 1 | no | - | `external`, pin 2024-06; [13] states `uses ->> [5]`. |
| 6 | 1 | 1 | 1 | no | - | `external > deviation` inside [5]; extra handling case in a workflow is additional, not a branch alone. |
| 7 | 1 | 0 | 1 | no | - | `config_key` name PAYRIGHT_URL; L 0 for `binds -> new: value` (URL per environment is no decided number; see ambiguities). |
| 8 | 1 | 1 | 1 | no | - | `actor` x2, human; extra new goals, harmless. |
| 9 | 1 | 1 | 1 | no | - | `actor`, nature program, kept separate from [5]. |
| 10 | 1 | 0 | 1 | no | - | `workflow > step > case`, then -> failure end; but `when` reads new `attr locked (flag)`, not the locked state of account. |
| 11 | 1 | 1 | 1 | no | - | One `view`, `serves` both steps. |
| 12 | 1 | 1 | 1 | no | - | `command`, `invoked_as`, `serves` new step. |
| 13 | 1 | 1 | 1 | no | - | `operation`, `performs` new checkout-confirm case, `uses` [5]. |
| 14 | 1 | 0 | 1 | no | - | `rule` + proof test; no link with [4] (`by` from [4]) at either end. |
| 15 | 1 | 1 | 1 | no | - | `principle` in constitution/. |
| 16 | 1 | 1 | 1 | no | - | `decision` + 2 options, no answer; credit `guess` not taken ("no guess"). |
| 17 | 1 | 1 | 1 | no | - | `workflow`, schedule nightly, step case deletes basket; extra operation. |

Rubric lines: 1: 0 0 0 \| structural \| rule, number in text. 7: 1 0 1. 10: 1 0 1. 14: 1 0 1. All others 1 1 1.

## A-2

| fact | K | L | F | misplaced | misleading name | note |
|---|---|---|---|---|---|---|
| 1 | 1 | 0 | 1 | no | - | `value` is 50, unit EUR; nothing reads it (no branch condition or rule linked). |
| 2 | 1 | 0 | 1 | no | - | `set`; the order attr `of -> [2]` appears only as "would point" in the why line, no entry made. |
| 3 | 1 | 1 | 1 | no | - | entity + states + transitions with from/to. |
| 4 | 1 | 1 | 1 | no | - | `entity > attr`, money, part of order. |
| 5 | 1 | 1 | 1 | no | - | `external`, pin; [13] `uses -> [5]`. |
| 6 | 1 | 1 | 1 | no | - | `external > deviation` inside [5]. |
| 7 | 1 | 0 | 1 | no | - | `config_key` name; `binds -> new: value` judged a wrong target, as in A-1. |
| 8 | 1 | 1 | 1 | no | - | `actor` x2, human. |
| 9 | 1 | 1 | 1 | no | - | Kind column is `workflow > step > choice`, but it creates `new: actor PayRight notifier (nature program)`: several entries, key's home among them, none a false friend, so K 1 (see ambiguities). Why line is structural. |
| 10 | 1 | 0 | 1 | no | - | Case with failure end and tell; `when` reads new `attr locked (flag)`, not a state. |
| 11 | 1 | 1 | 1 | no | - | One `view`, serves both steps. |
| 12 | 1 | 1 | 1 | no | - | `command`, `invoked_as`, `serves`; extra read of new entity product (a read target, not a copy). |
| 13 | 1 | 1 | 1 | no | - | `operation`, `performs` new choice in checkout, `uses` [5]. |
| 14 | 1 | 0 | 1 | no | - | `rule` + proof; [4] only "in says", no `by` link. |
| 15 | 1 | 1 | 1 | no | - | `principle`. |
| 16 | 1 | 1 | 1 | no | - | `decision` + 2 options, no answer; credit `guess` not taken. |
| 17 | 1 | 1 | 1 | no | - | `workflow`, schedule, step case deletes basket; extra operation. |

Rubric lines: 1: 1 0 1. 2: 1 0 1. 7: 1 0 1. 10: 1 0 1. 14: 1 0 1. All others 1 1 1.

## A-3

| fact | K | L | F | misplaced | misleading name | note |
|---|---|---|---|---|---|---|
| 1 | 0 | 0 | 0 | yes | structural | `rule`, links `-`; 50 EUR in text, `value` split only suggested. Why: "the condition is the fact and the number is only part of it". |
| 2 | 1 | 1 | 1 | no | - | `set`; new order attr channel `of -> [2]`. |
| 3 | 1 | 1 | 1 | no | - | entity + states + transitions with from/to. |
| 4 | 1 | 1 | 1 | no | - | `entity > attr`, money, parent order. |
| 5 | 1 | 1 | 1 | no | - | `external`, pin; [13] `uses ->> [5]`. |
| 6 | 1 | 1 | 1 | no | - | `external > deviation`; part of [5]. |
| 7 | 1 | 0 | 1 | no | - | `config_key` name; `binds -> new: value` judged a wrong target, as in A-1. |
| 8 | 1 | 1 | 1 | no | - | `actor` x2, human. |
| 9 | 1 | 1 | 1 | no | - | `actor`, nature program, separate from [5]. |
| 10 | 1 | 1 | 1 | no | - | Case, `when ->> new: state` locked of new entity account, `then -> new: end` failure. |
| 11 | 1 | 1 | 1 | no | - | One `view`, serves both steps. |
| 12 | 1 | 1 | 1 | no | - | `command`, `invoked_as`, `serves`. |
| 13 | 1 | 1 | 1 | no | - | `operation`, `performs` new confirm choice, `uses` [5]. |
| 14 | 1 | 0 | 1 | no | - | `rule` + proof; [4] named only in the why text, no `by` link. |
| 15 | 1 | 1 | 1 | no | - | `principle`. |
| 16 | 1 | 1 | 1 | no | - | `decision` + 2 options, no answer; credit `guess` not taken. |
| 17 | 1 | 1 | 1 | no | - | `workflow`, schedule, explicit system step deleting baskets, success end. |

Rubric lines: 1: 0 0 0 \| structural \| rule, number in text. 7: 1 0 1. 14: 1 0 1. All others 1 1 1.

## Summary

| run | kind (of 17) | links (of 17) | no false friend (of 17) | misplacements (of 17) | false friends | name-caused | names blamed |
|---|---|---|---|---|---|---|---|
| A-1 | 16 | 13 | 16 | 1 | 1 | 0 | - |
| A-2 | 17 | 12 | 17 | 0 | 0 | 0 | - |
| A-3 | 16 | 14 | 16 | 1 | 1 | 0 | - |
| mean | 16.33 | 13.00 | 16.33 | 0.67 | 0.67 | 0 | - |
| range | 16-17 | 12-14 | 16-17 | 0-1 | 0-1 | 0 | - |

## Facts most often misplaced

- [1] free shipping from 50 euros: misplaced in 2 of 3 (A-1, A-3), both as `rule` with the number in text (also F 0).
  Names blamed: none. Both why lines are structural ("the condition is the fact"); they name `value` only as the
  rejected or optional kind, without reading the name as meaning something else.
- No other fact was misplaced.

Most frequent link losses (not misplacements): [7] 3/3 (`binds -> value`), [14] 3/3 (no `by` link with [4]),
[1] 3/3 (number not read by anything / not split out), [10] 2/3 (flag attr instead of the locked state), [2] 1/3.

## Ambiguities and decisions

- [7] `binds -> new: value`: the key requires no link and lists "a decided number" as a false friend. All three runs
  bind the knob to a new value holding the per-environment URL. I could not check whether the map defines
  `binds`. Decided: L 0 (a per-environment URL is not a decided number, so a wrong target), F 1 (the knob itself
  sits in `config_key`; the value is a separate bound entry, not the knob). A stricter reading would give F 0 in
  all three runs.
- [9] in A-2: the kind column is `workflow > step > choice`, yet the run creates `new: actor PayRight notifier
  (nature program)`. Applied the rubric's "several entries for one fact, the key's home among them" rule: K 1. A
  stricter "score the kind column" reading gives K 0 and 1 misplacement for A-2 (why line structural either way).
- `choice` (A-2 [9], [13]; A-3 [13]) is not in the key's A column, which shows only `case`. I could not read the map,
  so I did not mark it an invented kind; it changes no mark except A-2 [9] under the stricter reading above.
- [10]: the key requires the condition to read the locked *stage* (`when ->> state`). A-1 and A-2 read a new
  `attr locked (flag)`: L 0, K 1.
- [17]: the key asks for "a system step". A-1 and A-2 give a step with a delete case and no actor, but do not say
  "system". Decided L 1 (a step in a schedule-started flow with no actor is the system step); only A-3 states it.
- [2] in A-2: the `of -> [2]` link appears only hypothetically ("would point") in the why line; no entry made, so L 0.
- [14]: mentioning [4] in the why or in `says` text is not a link; L 0 in all runs.
- [1]: a `rule` could be the must-hold statement that reads the number, but no run made the number entry, so the
  rule holds the number in text: listed false friend "a number left in text", F 0.
- Credit items: no run recorded a `guess` for [16] (all said no guess); no credit item exists for [9] in arm A.
- The rubric's output format (one line per fact) and the requested tables differ; I gave the tables and, under
  each, the rubric lines for non-perfect facts.
