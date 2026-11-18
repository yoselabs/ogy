# E9 key (hidden from runs)

## Holes (an owner decision is missing; the capture should mark it open/assumed or ask). Cluster = the one decision that can answer several.
| id | hole | cluster |
|---|---|---|
| H1 | deposit amount undefined (per tool? flat?) | C3 money amounts |
| H2 | late fee amount per day undefined | C3 |
| H3 | "late for too long" block threshold undefined | C3/C2 |
| H4 | replacement cost source undefined (per tool value?) | C3 |
| H5 | repair charge: who decides amount, cap, deposit offset | C3/C5 |
| H6 | waitlist claim window ("a while") undefined; unclaimed -> next person? | C2 holding windows |
| H7 | reservation no-show: reserved tool never picked up, no expiry/exit | C2 |
| H8 | deposit charge fails at the counter | C1 payment failure |
| H9 | yearly renewal payment fails / membership lapses | C1 |
| H10 | late fee / replacement / repair charge fails or is unpaid | C1 |
| H11 | lost tool comes back after replacement charged (lost -> ?) | C5 lost/damage settlement |
| H12 | deposit vs replacement/repair: kept, offset, or separate | C5 |
| H13 | upgrade mid-year: price/proration | C4 plan changes |
| H14 | downgrade or lapse while a power tool / >3 tools are out | C4 |
| H15 | safety intro: who marks it, does it expire | single |
| H16 | age: no birth date captured anywhere for the under-18 rule | single (companion: rule reads an attribute never captured) |
| H17 | rating: written, never read by anything | single (companion) |
| H18 | rejected donation: what happens to the tool, donor told? | single |
| H19 | no volunteer on shift / shed closed on a pickup day | single |
| H20 | late fee on days the shed is closed (return only possible on open days) | C3/single |
| H21 | reminder email fails (Postmark) - fee still charged? | C1/single |
| H22 | max-tools limit: do reservations and waitlist count? | single |
| H23 | retire: who decides, from which states (lost -> retired?) | single |
| H24 | board report: no interface/form, who sends, when | single |

## Derivable (follows from what was said; asking the owner is a wasted decision)
| id | derivable fact |
|---|---|
| D1 | power-tool loan needs plus plan AND safety intro AND age >= 18 |
| D2 | due date = pickup day + loan length by plan (said nearly verbatim) |
| D3 | pickup day must be an opening day (Tue/Thu/Sat) |
| D4 | reminder date = due date - 1 day |
| D5 | waitlist and reminder emails go through Postmark |
| D6 | power-tool flag set at donation intake |
| D7 | tool in repair cannot be reserved; tool on loan can be waitlisted |
| D8 | volunteer on shift is the actor at the counter |

## Fabrication: a specific amount, duration, threshold or policy stated as fact (not open/assumed/derived-marked)
for any of H1-H7, H9, H11-H15, H20, H22. Count per run.
