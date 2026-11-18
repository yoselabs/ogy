# Scores g1 (R399, R750, R109, R592)

## R399
1. settled-by-7: H1, H2, H3, H4, H5, H6, H8, H9, H12, H13, H15 (partial: who marks, not expiry) = 11
2. must-ask-7: 6/6 (H1, H2, H4, H5, H8, H15)
3. read-back: H7, H10 (late fee/replacement unpaid -> stays blocked; repair charge failure left as `gives: ?`), H11, H14 (downgrade only), H16, H17, H18, H22, H23, H24 = 10
4. missed: H19, H20, H21
5. invisible: 1 (H20: derived/days_late counts every calendar day as fact, closed days never considered)
6. wasted: RB16 (all emails via Postmark = D5), RB20 (deposit refunded on fine return, said in [17]/[27]) = 2
7. mis-cited: 2. rule/in_repair_not_reservable: "repair, lost or retired never reserved" cited src [29] (only repair); workflow/return_tool because [31] for "late fee taken at return" ([31] does not say when the fee is taken)
8. derive: 7 (D1, D2, D3, D4, D6, D7, D8; D5 sent to read-back)
9. notes: Questions grouped by decision cluster; every must-ask hit. Decision files with defaults make read-back proposals concrete. Misses the operational holes (no volunteer, closed-day fees, email failure).

## R750
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12 (partial: "deposit used first?"), H14 (partial: lapse with tools out), H22 = 11
2. must-ask-7: 4/6 (H1, H2, H4, H5; H8 only in read-back, H15 only in read-back)
3. read-back: H8, H10 (unblock when fees paid; unpaid keeps block), H11, H13, H15, H16, H17, H18, H23, H24 = 10
4. missed: H19, H20, H21
5. invisible: 1 (H20: workflow/lateness adds a fee every day as fact)
6. wasted: RB6 (reminder day before via Postmark = D4/D5), RB8 (part: power tool needs plus+intro+18 = D1), RB13 (part: pickup on an opening day = D3), RB20 (renewal automatic yearly on Stripe, said in [11]) = 4
7. mis-cited: 0 (no citations used)
8. derive: 4 (D2, D6, D7, D8; D1, D3, D4, D5 restated as read-back assumptions)
9. notes: Spent two questions on H7 and H22 (lower-stakes) while H8 and H15 dropped to read-back. Entries carry many concrete assumed values, all under ?open. No source traceability.

## R109
1. settled-by-7: H1, H2, H3, H4 (partial: full replacement price asked, per-tool source not), H5, H6, H7, H9, H11, H12, H13, H15 (partial: who marks) = 12
2. must-ask-7: 5/6 (H1, H2, H4 partial, H5, H15 partial; H8 absent)
3. read-back: H10 (unblock on payment), H14 (no downgrade; lapsed keep nothing out), H16, H17, H18, H22, H23, H24 = 8
4. missed: H8 (pickup declined -> end/refused, no open mark, not asked or read back), H19, H20, H21
5. invisible: 1 (H20: late_days counted per calendar day as fact)
6. wasted: RB "reservation only for an open day" (D3), RB "reminder day before... through Postmark" (D4/D5) = 2
7. mis-cited: 2. rule tool_is_free "in repair, lost or retired" cited src [29]; rate skipped end because [34] ("people like doing that" does not support skipping)
8. derive: 5 (D1, D2, D6, D7, D8; D3, D4, D5 restated in read-back; remind trigger also wrongly computed)
9. notes: Densest question coverage (questions bundle several holes each). Deposit-failure path silently decided. Read-back includes concrete placeholder prices, fine as marked.

## R592
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12, H13 = 10
2. must-ask-7: 4/6 (H1, H2, H4, H5; H8 absent, H15 only in read-back)
3. read-back: H10 (lost charge/owed keeps block), H11, H14 (partial: lapse with tools out, cancel by not renewing), H15, H16, H17, H18, H22, H23, H24 (partial: day/time, not delivery) = 10
4. missed: H8 (end/no_deposit with no open mark), H19, H20, H21
5. invisible: 1 (H20: charge_late_one adds a fee every calendar day as fact)
6. wasted: RB15 (power-tool eligibility = D1), RB16 (deposit released on fine return, said [27]), RB27 (reminder day before = D4), RB28 (emails via Postmark = D5) = 4
7. mis-cited: 4. value/lost_after "30 days" src [32] (owner said "a month"); rule repair_not_reservable "repair, lost or retired" src [29]; persona/board "decides money amounts" src [43]; (also rule waitlist_hold "only offered member may reserve" src [22])
8. derive: 5 (D2, D3, D6, D7, D8; D1, D4, D5 restated in read-back)
9. notes: Q7 half-spent on loan length of tools already out (not a key hole). Long read-back (31 items) with several derivable restatements. Citations frequently widen the owner's words.

| run | settled-by-7 | must-ask-7 | read-back | missed | invisible | wasted | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|
| R399 | 11 | 6 | 10 | H19, H20, H21 (3) | 1 (H20) | 2 | 2 | 7 |
| R750 | 11 | 4 | 10 | H19, H20, H21 (3) | 1 (H20) | 4 | 0 | 4 |
| R109 | 12 | 5 | 8 | H8, H19, H20, H21 (4) | 1 (H20) | 2 | 2 | 5 |
| R592 | 10 | 4 | 10 | H8, H19, H20, H21 (4) | 1 (H20) | 4 | 4 | 5 |
# E10 scores (scorer g2)

## R882
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H8, H9, H12, H13, H15 (who marks only), H22 (reservations only) = 13
2. must-ask-7: 6/6 (H1, H2, H4, H5, H8, H15)
3. read-back: H11, H16, H18, H20, H24 = 5
4. missed: H14, H17, H19, H21, H23 (H10 only partly open via return.late-unpaid)
5. invisible: 0
6. wasted: 1 (read-back 22 "hand tools need no deposit and no safety intro", stated by [17]/[18])
7. mis-cited: 3; e.g. rule.not-blocked scoped to waitlist-join with src [31] (owner said "borrowing"); waitlist timeout-passes-to-next because [22] ([22] does not say next person); rule.claim-held because [21,22] (holding not said)
8. derive: 8
9. notes: Best question set: price-list, payment-failure and who-may clusters cover all six must-asks. Decision options embed proposed numbers, but always under an open decision. Misses the email-failure, no-volunteer, downgrade and retire holes.

## R537
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12, H13, H22 = 11
2. must-ask-7: 4/6 (H1, H2, H4, H5; H8 and H15 only via read-back or not at all)
3. read-back: H11, H15, H16, H17, H23, H24 = 6
4. missed: H8, H10, H14, H18, H19, H20, H21
5. invisible: 0 (H8 deposit failure is handled as fact, "Do not hand over the tool", but H8 is not a trap hole)
6. wasted: 3 (plus loan length applies to hand tools [9]; basic borrows only hand tools [7]; returns only at the counter during opening hours [25])
7. mis-cited: 0 (no citations)
8. derive: 8
9. notes: Strong read-back (rating unused, retire authority), but H8 (must-ask) is silently decided in the entries. Read-back repeats every question's fallback. Also misses donation-decline and closed-day late fees.

## R196
1. settled-by-7: H1, H2, H3, H5, H6, H7, H9, H12, H13 = 9
2. must-ask-7: 3/6 (H1, H2, H5; H4 and H15 pushed to read-back, H8 not at all)
3. read-back: H4, H10, H14 (partial: no downgrade), H15, H16, H17 (partial: only shown to member), H20, H22, H23 (partial: Marta decides retire), H24 = 10
4. missed: H8, H19, H21 (H11, H18 marked open in Entries only)
5. invisible: 0
6. wasted: 2 (hand tools for basic and plus, power only plus [7][8]; due date = pickup day + loan length (D2))
7. mis-cited: 0 (no citations)
8. derive: 8
9. notes: Widest read-back coverage, but uses questions on lower-value items while pushing must-asks H4 and H15 into read-back. H8 is decided as fact (deposit fail -> refused) with no mark.

## R204
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12, H13, H15 (who marks; expiry in read-back), H23 = 12
2. must-ask-7: 5/6 (H1, H2, H4, H5, H15; H8 marked open in Entries only)
3. read-back: H10, H11, H16, H17 (partial), H18, H20 (partial: due stays on closed day, fee keeps counting), H21, H22, H24 = 9
4. missed: H14, H19 (H8 open in Entries only, not asked and not in read-back)
5. invisible: 0
6. wasted: 3 (hand tools need no deposit [17]; plus loan length applies to hand tools [9]; basic cannot reserve power tools [7][8])
7. mis-cited: 5; e.g. entity.tool transitions (found lost->available, retire from available) because [28,32]; workflow.join because [9] (loan lengths, unrelated); late_fee deposit.keep on lost because [17] ([17] only says the deposit is returned)
8. derive: 8
9. notes: Best total coverage: only H14 and H19 missed, and it is the only run to catch H21 (email failure). Q4 who-may adds the retire authority. Citation discipline is the weakest: several "because" references do not support the claim.

| run | settled-by-7 | must-ask-7 | read-back | missed | invisible | wasted | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|
| R882 | 13 | 6 | 5 | 5 (H14,H17,H19,H21,H23) | 0 | 1 | 3 | 8 |
| R537 | 11 | 4 | 6 | 7 (H8,H10,H14,H18,H19,H20,H21) | 0 | 3 | 0 | 8 |
| R196 | 9 | 3 | 10 | 3 (H8,H19,H21) | 0 | 2 | 0 | 8 |
| R204 | 12 | 5 | 9 | 2 (H14,H19) | 0 | 3 | 5 | 8 |
# Scores g3

Scoring convention: a derivable fact counts for "derive" only when captured as fact and not re-asked in questions or
read-back. A hole asked partly counts as settled when its main point is asked.

## R780
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12, H13, H15 (who marks; expiry is in read-back) = 11
2. must-ask-7: 5/6 (H8 only in read-back)
3. read-back: H8, H11, H18, H22, H24 = 5
4. missed: H10, H14, H16 (birthdate added silently to member/join, never surfaced), H17, H19, H20, H21, H23
5. invisible: 0
6. wasted: read-back "collect only on the reserved pickup day, due = that day + loan length" (D2); read-back pickup among opening slots (D3, partial, bundled with the new 14-day horizon); read-back "shift sign-up stays in Sam's sheet" ([41], partial); read-back "about 400 members is context" ([3])
7. mis-cited: 3. workflow/waive-charge because [28] (nothing about waiving); workflow/expire-reservations because [14,15,29] ([29] is repair, nothing on no-show); workflow/join-membership src [11] with a birthdate input [11] never mentions
8. derive: 6 (D1, D4, D5, D6, D7, D8; D2 and D3 re-asked in read-back)
9. notes: Clean decision clustering; all trap amounts open with assumed values. Weak on companions (age capture, rating read) and on failure branches other than deposit/renewal.

## R295
1. settled-by-7: H1, H2, H3, H5, H6, H7, H9, H12, H13, H14 (Q5 tools still out + Q7 downgrade) = 10
2. must-ask-7: 3/6 (H4, H8, H15 only in read-back)
3. read-back: H4, H8, H15, H16, H17, H18, H22, H23, H24 = 9
4. missed: H10, H11, H19, H20, H21
5. invisible: 1. H11: entity.tool transition found lost -> available stated as fact, no open mark, not in read-back
6. wasted: Q2 "what lifts the block (tool back, fees paid, both)" (answered in [31]); read-back 17 reminder by Postmark the day before (D4, D5); read-back 24 pickup is an open day (D3, partial); read-back 26 about 400 members ([3]); read-back 3 lost = 30 days (partial, [32]); read-back 16 sheet outside the system ([41], partial)
7. mis-cited: 0 (no sentence citations used)
8. derive: 5 (D1, D2, D6, D7, D8; D3, D4, D5 re-asked in read-back)
9. notes: Broadest read-back coverage of companions (age, rating, retire, report). Spent questions on block lift instead of must-ask H4/H8/H15. One silent policy (lost found).

## R909
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12, H13, H15, H23 (Q5 who may retire) = 12
2. must-ask-7: 5/6 (H8 only in read-back)
3. read-back: H8, H10 (lost charge fails -> stays blocked and owes), H11, H14 (partial: no downgrade offered; lapse with tools out not covered), H16, H17, H18, H22, H24 = 9
4. missed: H19, H20, H21
5. invisible: 0
6. wasted: Q5 "can any volunteer at the counter do all loans and returns" (D8); read-back "tool in repair or lost cannot be reserved" (D7, says so itself); read-back pickup must be an opening day (D3, partial); read-back one reminder the day before due (D4, partial); read-back deposit charged at pickup, refunded on fine return ([17], partial)
7. mis-cited: 4. tool found because [39] ([39] lists states, says nothing about lost tools returning); reservation cancel because [14]; waitlist leave because [21]; rate skip because [33] (none of these mention cancel/leave/skip)
8. derive: 4 (D1, D2, D5, D6; D3, D4, D7 re-asked in read-back, D8 re-asked in Q5)
9. notes: Best coverage: only H19/H20/H21 missed and no invisible policy. Cost: several derivables re-asked and loose because-citations.

## R419
1. settled-by-7: H1, H2, H3, H5, H6, H7, H9, H12, H13, H14 (Q5 keep current loans, partial), H22 = 11
2. must-ask-7: 3/6 (H4 and H8 nowhere; H15 only in read-back)
3. read-back: H11, H15, H17, H18, H24 = 5 (H23 marked open in entries only)
4. missed: H4, H8, H10, H16 (birth_date added silently; only "may under-18s join" asked), H19, H20, H21
5. invisible: 0 (deposit_failed -> no loan stated as fact, but H8 is not a trap hole)
6. wasted: Q2 second half "same 30 days for lost" ([32], partial); read-back 5 loans start only on opening days (D3, partial); read-back 10 only a tool that is out can be waitlisted (D7/[21]); read-back 13 block lifts when tool back and owed is zero ([31]); read-back 21 shift sheet outside the app ([41])
7. mis-cited: 3. rule reservable_only_when_available note [29] (generalised from repair to lost/retired); join note "[20]" for under-18s allowed to join; waitlist note "[21] only for a tool that is out" (generalises a conditional into "only")
8. derive: 6 (D1, D2, D4, D5, D6, D8; D3 and D7 re-asked in read-back)
9. notes: Missed must-ask H4 (replacement source) and H8 (deposit fails) entirely. Otherwise solid open marking; no invisible policies.

| run | settled-by-7 | must-ask-7 | read-back | missed | invisible | wasted | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|
| R780 | 11 | 5 | 5 | 8 | 0 | 4 | 3 | 6 |
| R295 | 10 | 3 | 9 | 5 | 1 | 6 | 0 | 5 |
| R909 | 12 | 5 | 9 | 3 | 0 | 5 | 4 | 4 |
| R419 | 11 | 3 | 5 | 7 | 0 | 5 | 3 | 6 |
# Scores g4

## R378
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12 (repair/deposit half via Q2), H13, H15 (who marks; not expiry), H16 = 12
2. must-ask-7: 5/6 (H1, H2, H4, H5, H15; H8 only in read-back)
3. read-back: H8, H10, H11, H17, H18, H22, H24 = 7
4. missed: H14, H19, H20, H21, H23
5. invisible: 0 (every placeholder amount/duration carries ?open and is in read-back)
6. wasted: 0
7. mis-cited: 3. e.g. rule reserved-tool-not-offered "in repair, lost, retired, on loan or reserved cannot be reserved" src [29] (29 only says in repair); tool.retire from [available, in_repair] src [40] (40 gives no from-available); upgrade end "stays on basic" because [12] (12 says nothing about failure). Borderline 4th: tool.shelve from lost cited [22,27,28].
8. derive: 8/8
9. notes: Clusters questions well (price list, damage, renewal+upgrade, age+intro). Read-back explicitly labels amounts as placeholders. Misses intro expiry, closed-day late fees, reminder email failure, no-volunteer days.

## R461
1. settled-by-7: H1, H2, H3, H5, H6, H7, H9, H12 (repair/deposit via Q5), H16 = 9
2. must-ask-7: 3/6 (H1, H2, H5; H4 and H15 only read-back, H8 nowhere)
3. read-back: H4, H13, H14 (downgrade not supported), H15, H17, H22, H24 = 7
4. missed: H8, H10, H11, H18, H19, H20, H21, H23
5. invisible: 1 (H11: tool transition found lost->available stated as fact, no open, not in read-back)
6. wasted: 3 - "reserve only on an opening day" (D3), "Emails all via Postmark" (D5), "opening hours Tue/Thu eve, Sat morning are fixed" (scenario [5]); reminder item also leans on D4 (Entries put an ?open on due-minus-one)
7. mis-cited: 0 (no citations)
8. derive: 7/8 (D4 marked open)
9. notes: Questions spent on money amounts but skips deposit-failure and replacement source; spends Q7 on age only. Entries model deposit-fail, lost-found, rejected donation as silent fact. at-limit derived counts only out_now while read-back says reservations count (inconsistent).

## R931
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12, H13 = 10
2. must-ask-7: 4/6 (H1, H2, H4, H5; H8 and H15 in read-back)
3. read-back: H8, H10 (replacement unpaid -> stays blocked), H11, H14 (no downgrade), H15 (who marks; not expiry), H16, H17, H18, H20 (late days are calendar days), H22, H23 (Marta alone decides retiring), H24 = 12
4. missed: H19, H21
5. invisible: 0
6. wasted: 0 (Q6 notifications is not in the key but is not answered by the scenario)
7. mis-cited: 1. tool part "retire is reachable from repair only" src [40] / because [28,40] (owner never restricts retire to repair). Minor: loan cancel because [14].
8. derive: 8/8 (D5 for reminder only implied via [23] and the postmark external)
9. notes: Widest coverage; nearly every hole is either asked or put up for confirmation. Q6 (notifications) spends a slot on a non-key decision while H8/H15/H16 go to read-back. Guard bodies are written inverted (when "state != active" else refused), not scored.

## R920
1. settled-by-7: H2, H3, H4, H5, H6, H7, H9, H12, H16, H22 = 10
2. must-ask-7: 3/6 (H2, H4, H5; H1 and H15 in read-back, H8 nowhere)
3. read-back: H1 (fixed vs per tool; amount left open), H11, H13, H14 (no downgrade), H15, H17, H23 (retire is volunteer's call), H24 = 8
4. missed: H8, H10, H18, H19, H20, H21
5. invisible: 0 (amounts are 0 placeholders with ?open; claim window 48h marked assumed)
6. wasted: 3 - read-back confirming loan lengths/limits/age/reminder/lost-after "as the owner said" (scenario [9],[10],[20],[30],[32]); "Emails all go through Postmark" (D5); "Both plans pay by card via Stripe" (scenario [11])
7. mis-cited: 0 (no citations)
8. derive: 7/8 (D4 reminder carries an ?open on the trigger)
9. notes: Good question bundling (Q5 pairs no-show with reservation limit). Deposit amount itself never asked; deposit-failure modeled as silent fact. Repair charge failure, rejected donation, reminder failure absent.

| run | settled-by-7 | must-ask-7 | read-back | missed | invisible | wasted | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|
| R378 | 12 | 5 | 7 | 5 (H14, H19, H20, H21, H23) | 0 | 0 | 3 | 8 |
| R461 | 9 | 3 | 7 | 8 (H8, H10, H11, H18, H19, H20, H21, H23) | 1 (H11) | 3 | 0 | 7 |
| R931 | 10 | 4 | 12 | 2 (H19, H21) | 0 | 0 | 1 | 8 |
| R920 | 10 | 3 | 8 | 6 (H8, H10, H18, H19, H20, H21) | 0 | 3 | 0 | 7 |
