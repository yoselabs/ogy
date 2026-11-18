# E11 key (hidden from runs)

Two kinds of holes. P = product holes (an owner decision is missing in what the owner described).
Z = hazard holes (what happens when something outside, the environment, or timing goes wrong; the owner never talks
about these). Cluster = the decision that settles several.

## Product holes
| id | hole | cluster | must-ask |
|---|---|---|---|
| P1 | large box threshold "more than four" said; what about box contents per size / which items: fine. Hole: family size source and when it changes mid-week | single | |
| P2 | order changes or cancels before cutoff: allowed? | single | |
| P3 | route not assigned / no driver signed up for a route by Friday: what happens to those families? | C-drivers | yes |
| P4 | "nobody home" family never answers the pick-up text: what happens to the box (food waste, how long kept)? | C-returns | yes |
| P5 | pick-up instead: where, when; box kept how long | C-returns | |
| P6 | food group substitutions: who defines groups; what if a whole group is out (no substitute) | single | |
| P7 | "two weeks of boxes" needs a forecast: based on which weeks' orders? | single | |
| P8 | eligibility lapse with an order already placed for this week | single | |
| P9 | big donor threshold 500: currency, single gift or yearly total; who tells the director | single | |
| P10 | proof of address rejected by the volunteer: family told? retry? | single | yes (permission/external) |
| P11 | families' personal data: who can see addresses (drivers see all?) | single | yes (permission) |

## Hazard holes (the skill's hazard pass should surface these)
| id | hole | cluster | must-ask |
|---|---|---|---|
| Z1 | warehouse tablet offline (patchy wifi) while packers tick boxes: ticks lost or doubled when it reconnects | C-offline | yes |
| Z2 | driver phone offline or dies mid-route: "delivered" taps not recorded; family wrongly texted "nobody home" | C-offline | yes |
| Z3 | packing list sent twice or never arrives at the tablet (cutoff job fails or reruns) | C-jobs | |
| Z4 | Twilio text fails or is delayed; Friday time window text not received; nobody notices | C-messages | |
| Z5 | Stripe donation outcome unknown (payment taken, receipt email never sent; or receipt sent twice) | C-money-unknown | yes |
| Z6 | two coordinators/actions assign the same route or driver at once (race) | single | |
| Z7 | order submitted twice (double tap) or exactly at noon cutoff (clock, timezone) | single | |
| Z8 | stock count stale: a box packed while a supplier scan is in progress; counts go negative | C-offline | |
| Z9 | nightly 2 am job: runs twice, does not run, or runs during order window/packing; backup fails silently | C-jobs | |
| Z10 | low-stock email to Priya fails or repeats every night | C-messages | |
| Z11 | driver taps "delivered" at the wrong stop / undo | single | |
| Z12 | board summary contains personal data / is emailed to an outside address | single | |

## Derivable (asking is wasted)
| id | fact |
|---|---|
| D1 | order window: Monday until Wednesday 12:00; orders after are refused |
| D2 | one order per family per week |
| D3 | box size large iff household > 4 |
| D4 | lapsed eligibility blocks ordering |
| D5 | texts go through Twilio; donation through Stripe |
| D6 | max 12 stops per route |

## Must-ask set M = P3, P4, P10, P11, Z1, Z2, Z5
Fabrication traps: P4/P5 durations, P7 forecast window, P9 rules, Z-hole retry counts/timeouts stated as fact.
