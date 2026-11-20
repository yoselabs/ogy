# Scores: pilot, small, arm A (runs A1, A2)

Scored against key.md column A (`eval-before`) and rubric.md. Column A has no `(verify)` cells, so nothing was
stopped. Anchor [1] is reported apart from the 53 target link items.

Line format: `n: K F | items | wrong links | name blame | note`.

## A1

Anchor: `1: 1 1 | 1a=1 | wrong links: 0 | - |`

```
2: 1 1 | 2a=1 2b=1 | wrong links: 0 | - |
3: 1 1 | 3a=1 | wrong links: 0 | - |
4: 1 1 | 4a=1 4b=1 | wrong links: 0 | - | 4b from [5] max -> [4]
5: 1 1 | 5a=1 5b=1 | wrong links: 0 | - |
6: 1 1 | 6a=1 6b=1 | wrong links: 0 | - |
7: 1 1 | 7a=1 7b=1 | wrong links: 0 | - | performs -> case "take payment on return"
8: 1 1 | (none) | wrong links: 0 | - |
9: 1 0 | 9a=1 9b=0 | wrong links: 1 | unclear | binds -> new value "PayRight address"; F 0 for the URL copied into a value
10: 0 0 | 10a=0 10b=0 | wrong links: 1 | misled-by: operation; missed: command | "Our read-only HTTP operation ... Not command (no invocation)"; performs -> case counted wrong
11: 1 1 | 11a=1 11b=1 | wrong links: 0 | - |
12: 1 1 | 12a=1 12b=0 | wrong links: 1 | structural | list of a new entity "tag", not free text; of -> entity tag counted wrong
13: 0 0 | 13a=0 13b=0 | wrong links: 0 | structural | workflow; why folds the notifier into [3] ("part of PayRight, covered by external [3]")
14: 1 1 | 14a=0 14b=1 14c=1 14d=1 | wrong links: 0 | unclear | parent hire named only in the why line, no of -> [2]
15: 1 1 | 15a=1 15b=0 | wrong links: 0 | unclear | no `by` from the hire or bike
16: 1 1 | 16a=1 | wrong links: 0 | - |
17: 1 1 | 17a=1 | wrong links: 0 | - |
18: 1 1 | 18a=1 18b=1 | wrong links: 0 | - |
19: 1 1 | 19a=1 19b=0 | wrong links: 1 | structural | rounding only in why, half cent left out on purpose; when -> new value "payment amount to the cent" counted wrong
20: 1 1 | 20a=1 20b=0 | wrong links: 0 | unclear | tie to [10] only in why; [10] has no step
21: 1 1 | 21a=1 21b=1 21c=1 | wrong links: 0 | - | credit: reason on the guess
22: 1 1 | 22a=1 22b=1 22c=1 22d=0 | wrong links: 0 | unclear | no timeout.after
23: 1 1 | 23a=1 | wrong links: 0 | - |
24: 0 1 | 24a=0 | wrong links: 0 | structural | two attrs on bike, nothing on [10]
25: 1 1 | 25a=1 25b=1 | wrong links: 0 | - |
26: 1 1 | 26a=1 | wrong links: 0 | - |
27: 1 1 | 27a=1 27b=1 | wrong links: 0 | - |
28: 1 1 | 28a=1 28b=1 28c=1 28d=1 | wrong links: 0 | - |
```

## A2

Anchor: `1: 1 1 | 1a=1 | wrong links: 0 | - |`

```
2: 1 1 | 2a=1 2b=1 | wrong links: 0 | - | extra rule "never backwards" (no false friend)
3: 1 1 | 3a=1 | wrong links: 0 | - |
4: 1 1 | 4a=1 4b=1 | wrong links: 0 | - |
5: 1 1 | 5a=1 5b=1 | wrong links: 0 | - | of -> "new: entity hire" taken as [2]
6: 1 1 | 6a=1 6b=1 | wrong links: 0 | - |
7: 1 1 | 7a=1 7b=1 | wrong links: 0 | - |
8: 1 1 | (none) | wrong links: 0 | - |
9: 1 0 | 9a=1 9b=0 | wrong links: 1 | unclear | binds -> new value "PayRight address"; F 0 as in A1
10: 0 0 | 10a=0 10b=0 | wrong links: 1 | misled-by: operation | "An endpoint we serve ... operation"; form in `says`, not `invoked_as`; performs -> case counted wrong
11: 1 1 | 11a=1 11b=1 | wrong links: 0 | - |
12: 1 1 | 12a=1 12b=1 | wrong links: 0 | - | type list, as column A allows
13: 0 1 | 13a=0 13b=0 | wrong links: 0 | structural | workflow with event -> transition
14: 1 1 | 14a=1 14b=1 14c=1 14d=1 | wrong links: 0 | - |
15: 1 1 | 15a=1 15b=0 | wrong links: 0 | unclear | no `by`
16: 1 1 | 16a=1 | wrong links: 0 | - |
17: 1 1 | 17a=1 | wrong links: 0 | - |
18: 1 1 | 18a=1 18b=1 | wrong links: 0 | - |
19: 1 1 | 19a=1 19b=1 | wrong links: 0 | - | both halves in `says`; see Doubts on when -> [3]
20: 1 1 | 20a=1 20b=0 | wrong links: 0 | unclear | tie to [10] only in why
21: 1 1 | 21a=1 21b=1 21c=1 | wrong links: 0 | - | credit: "(AI pick, flagged)"
22: 1 1 | 22a=1 22b=1 22c=1 22d=1 | wrong links: 0 | - |
23: 1 1 | 23a=1 | wrong links: 0 | - |
24: 0 1 | 24a=1 | wrong links: 1 | structural | main home three bike attrs; "reply shape stated as text on [10]" gives 24a; `sort -> [6]` is not a field in the map
25: 1 1 | 25a=1 25b=1 | wrong links: 0 | - |
26: 1 1 | 26a=1 | wrong links: 0 | - |
27: 1 1 | 27a=1 27b=1 | wrong links: 0 | - |
28: 1 1 | 28a=1 28b=1 28c=1 28d=1 | wrong links: 0 | - |
```

## Summary

| run | link items (of 53) | misplacements (of 27) | false friends | wrong links | name-caused | names blamed |
|---|---|---|---|---|---|---|
| A1 | 41 | 3 ([10], [13], [24]) | 3 ([9], [10], [13]) | 4 | 1 | misled-by `operation`, missed `command` ([10]) |
| A2 | 46 | 3 ([10], [13], [24]) | 2 ([9], [10]) | 3 | 1 | misled-by `operation` ([10]) |
| mean | 43.5 | 3 | 2.5 | 3.5 | 1 | |

Anchor [1]: 1 of 1 in both runs.

Misses that recur in both runs: 9b (`binds` to a new value), 10a/10b ([10] filed as `operation`), 13a/13b (the
notifier filed as a workflow), 15b (no `by`), 20b (no tie to [10]). Errors with a name blamed: only [10].

## Doubts

- [9] F: both runs bind `PAYRIGHT_URL` to a new `value` "PayRight address". I read that as a copy of the fact in
  a listed false-friend home (a decided number), so F 0, on top of 9b = 0 and one wrong link.
- [10] A2 blame: the why line maps "endpoint" to `operation` without naming `command`. I recorded
  `misled-by: operation` because the name is in the line and the reasoning is the REST sense; no `missed`.
- [12] A1 12b: the attr is a list of a new entity "tag", not free text. Column A allows "type list", but the
  neutral item says free text, so 12b = 0 and `of -> entity tag` counted as a wrong link. A2's plain list scored 1.
- [13] A1 F: the why says the notifier "is part of PayRight, covered by external [3]", read as folding it into
  [3] (a listed false friend), F 0. 13b = 0 in both runs because a workflow cannot carry it; `event -> transition`
  not counted as wrong.
- [14] A1 14a: the parent hire appears only in the attr's name and the why line, with no `of`; scored 0 under the
  "why line only" rule. K kept at 1 because the parent is not wrong.
- [5], [14] A2: `of -> new: entity hire` takes the hire entity of [2] as a new reference; scored as the right
  target, since there is only one hire entity.
- [19] A2: the deviation's parent is shown only by `when -> [3]` and by `says` naming PayRight. 19a scored 1. Not
  counted as a wrong link, because I could not tell from the key alone what `when` means in the map.
- [24] A2: 24a scored 1 because the links cell says the reply shape sits as text on [10], even though [10] is
  the wrong kind. K 0, since the key's home (on the `command`) is missing and the main entry is bike attrs.
  `sort -> [6]` counted as one wrong link (no such field).
