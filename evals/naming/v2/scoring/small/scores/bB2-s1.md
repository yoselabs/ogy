## R285

1: - - | 1a=1 | wrong links: 0 | rider and mechanic, both nature human
2: 1 1 | 2a=1 2b=1 | wrong links: 0 | extra rule "no going backwards" constrains the states; no false friend
3: 1 1 | 3a=1 | wrong links: 0 |
4: 1 1 | 4a=1 4b=0 | wrong links: 0 | no attr.max, case.when, choice.when, timeout.after or derived reads the 12; only a rule of [17] constrains it
5: 1 1 | 5a=1 5b=1 | wrong links: 0 | parent stated as "attr hire duration ... of -> [2] entity hire" (see Doubts)
6: 1 1 | 6a=1 6b=1 | wrong links: 0 |
7: 1 1 | 7a=1 7b=1 | wrong links: 0 |
8: 1 1 | - | wrong links: 0 |
9: 1 1 | 9a=1 9b=1 | wrong links: 0 | "binds: none"; extra rule constrains the key, no false friend
10: 1 1 | 10a=1 10b=1 | wrong links: 1 | serves -> new step; shows -> [24] points at a rule, not at the bike or its facts (wrong target); accepts not scored
11: 1 1 | 11a=1 11b=1 | wrong links: 0 |
12: 1 1 | 12a=1 12b=1 | wrong links: 0 | type text, many; extra interface add-remark (accepts/allows not scored)
13: 1 1 | 13a=1 13b=0 | wrong links: 0 | the move to paid is tied through "workflow event ->", not through step.actor or an effect; the notifier is not tied to the workflow in the links
14: 1 1 | 14a=1 14b=1 14c=1 14d=1 | wrong links: 0 | derived -> value late-fee-rate, which is an entry of [17]
15: 1 1 | 15a=1 15b=1 | wrong links: 0 | constrains -> state out of the hire
16: 1 1 | 16a=1 | wrong links: 0 | not scored: an operation distance-between-stations uses geolib
17: 1 1 | 17a=1 | wrong links: 0 | rule late fee + value late-fee-rate (5 EUR/hour); rule has no 5 in its text
18: 1 1 | 18a=1 18b=1 | wrong links: 0 | one interface, serves both steps
19: 1 1 | 19a=1 19b=1 | wrong links: 0 |
20: 1 1 | 20a=1 20b=1 | wrong links: 0 | "allows-from [10]" stated
21: 1 1 | 21a=1 21b=1 21c=1 | wrong links: 0 | not scored: reason on the guess
22: 1 1 | 22a=1 22b=1 22c=1 22d=1 | wrong links: 0 |
23: 1 1 | 23a=1 | wrong links: 0 |
24: 0 1 | - | wrong links: 0 | own rule entry, not on the entry of [10]; [10] shows the rule rather than the bike's facts
25: 1 1 | 25a=1 25b=1 | wrong links: 0 |
26: 1 1 | 26a=1 | wrong links: 0 |
27: 1 1 | 27a=1 27b=1 | wrong links: 0 | not scored: written by an effect in the return workflow
28: 1 1 | 28a=1 28b=1 28c=1 28d=1 | wrong links: 0 |

## R445

1: - - | 1a=1 | wrong links: 0 |
2: 1 1 | 2a=1 2b=1 | wrong links: 0 | extra rule over the states
3: 1 1 | 3a=1 | wrong links: 0 | not scored: realizes -> [13]
4: 1 1 | 4a=1 4b=1 | wrong links: 0 | [14] derived -> [4]
5: 1 1 | 5a=1 5b=1 | wrong links: 0 |
6: 1 1 | 6a=1 6b=1 | wrong links: 0 |
7: 1 1 | 7a=1 7b=1 | wrong links: 0 | satisfies -> [25] not scored
8: 1 1 | - | wrong links: 0 |
9: 1 1 | 9a=1 9b=1 | wrong links: 0 |
10: 1 1 | 10a=1 10b=1 | wrong links: 0 | serves -> new step; satisfies -> [24] not scored; extra read-only rule
11: 1 1 | 11a=1 11b=1 | wrong links: 0 |
12: 1 1 | 12a=1 12b=1 | wrong links: 0 |
13: 1 1 | 13a=1 13b=0 | wrong links: 0 | case/interface for the move named only in "why"; not scored: realized by [3]
14: 1 1 | 14a=1 14b=1 14c=1 14d=1 | wrong links: 0 | also derived -> [4]
15: 1 1 | 15a=1 15b=1 | wrong links: 0 | constrains -> entity bike
16: 1 1 | 16a=1 | wrong links: 0 |
17: 1 1 | 17a=1 | wrong links: 0 |
18: 1 1 | 18a=1 18b=1 | wrong links: 0 |
19: 1 1 | 19a=1 19b=1 | wrong links: 0 |
20: 1 1 | 20a=1 20b=1 | wrong links: 0 | actor of the step [10] serves
21: 1 1 | 21a=1 21b=1 21c=1 | wrong links: 0 | not scored: reason on the guess
22: 1 1 | 22a=1 22b=1 22c=1 22d=0 | wrong links: 0 | no timeout reads the value
23: 1 1 | 23a=1 | wrong links: 0 |
24: 0 1 | - | wrong links: 0 | own rule entry, not on the entry of [10]
25: 1 1 | 25a=1 25b=1 | wrong links: 0 | proof: pending (see Doubts)
26: 1 1 | 26a=1 | wrong links: 0 |
27: 1 1 | 27a=1 27b=1 | wrong links: 0 |
28: 1 1 | 28a=1 28b=1 28c=1 28d=1 | wrong links: 0 |

## R184

1: - - | 1a=1 | wrong links: 0 |
2: 1 1 | 2a=1 2b=1 | wrong links: 0 | transitions written as entity > state > transition (see Doubts); extra rule
3: 1 1 | 3a=1 | wrong links: 0 |
4: 1 0 | 4a=1 4b=0 | wrong links: 0 | nothing reads the 12 through a reading field; rule of [17] "late fee applies beyond 12 hours" leaves 12 in its text (false friend)
5: 1 1 | 5a=1 5b=1 | wrong links: 0 |
6: 1 1 | 6a=1 6b=1 | wrong links: 0 |
7: 1 1 | 7a=1 7b=1 | wrong links: 0 |
8: 1 1 | - | wrong links: 0 |
9: 1 1 | 9a=1 9b=1 | wrong links: 0 |
10: 1 1 | 10a=1 10b=1 | wrong links: 0 | 10b through [24]'s "interface [10] shows -> these attrs"; allows -> other companies' apps
11: 1 1 | 11a=1 11b=1 | wrong links: 0 |
12: 1 1 | 12a=1 12b=0 | wrong links: 0 | bike attr remark has no type; the text lives in a new entity remark (no stages, so not the listed false friend)
13: 1 1 | 13a=1 13b=1 | wrong links: 0 | effect does the transition returned->paid
14: 1 1 | 14a=1 14b=1 14c=1 14d=1 | wrong links: 0 |
15: 1 1 | 15a=1 15b=1 | wrong links: 0 | constrains -> state out and entity bike
16: 1 1 | 16a=1 | wrong links: 0 |
17: 1 1 | 17a=1 | wrong links: 0 | extra rule has no 5 in its text
18: 1 1 | 18a=0 18b=0 | wrong links: 0 | one interface, but serves no step; allows -> rider not scored here
19: 1 1 | 19a=1 19b=1 | wrong links: 0 |
20: 1 1 | 20a=1 20b=0 | wrong links: 0 | "calls us via [10]" is no field; [10] allows another actor
21: 1 1 | 21a=1 21b=0 21c=1 | wrong links: 1 | guess written with "sets ->" (the option field), not "chose"; not scored: reason on the guess
22: 1 1 | 22a=1 22b=1 22c=1 22d=0 | wrong links: 0 | no timeout reads the value
23: 1 1 | 23a=1 | wrong links: 0 | extra value walk limit through "threshold" (unknown word), not alone
24: 1 1 | - | wrong links: 0 | [10] shows -> new bike attrs; extra rule
25: 1 1 | 25a=1 25b=1 | wrong links: 0 |
26: 1 1 | 26a=1 | wrong links: 0 |
27: 1 1 | 27a=1 27b=1 | wrong links: 0 |
28: 1 1 | 28a=1 28b=1 28c=1 28d=1 | wrong links: 0 |

| run | link items (of 51) | 1a | 15b | misplacements (of 27) | false friends | wrong links |
|---|---|---|---|---|---|---|
| R285 | 49 | 1 | 1 | 1 | 0 | 1 |
| R445 | 49 | 1 | 1 | 1 | 0 | 0 |
| R184 | 44 | 1 | 1 | 0 | 1 | 1 |

## Doubts

- R285 states the parent of each attr only as "of -> <entity>" ([5], [6], [12], [14], [27]); I read it as the attr being written inside that entity. I counted no wrong link, and R184/R445 got the same treatment where they add "of -> [2]".
- R184 [2] writes transitions as entity > state > transition. They are still inside the hire, so I gave K=1.
- R445 [25] has only "proof: pending" in the field; I gave 25a=1 because the field is filled and the run gives the same proof as [15].
- R184 [4]: the 12 appears only in the text of the extra rule filed under [17]; I counted it as the [4] false friend "must-hold statement with 12 left in its text".
