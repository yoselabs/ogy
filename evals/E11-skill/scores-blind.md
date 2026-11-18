# Scores g1

## R449
1. P-surfaced: P2 (RB10), P3 (Q4), P4 (Q2), P5 (Q2 "how long keep"), P6 (Q1), P7 (RB7), P8 (Q5), P9 (Q6, RB15), P10 (RB9), P11 (RB19 driver sees only own route) = 10/11. Missing P1.
2. Z-surfaced: Z1 (Q3, hazard, RB20), Z2 (hazard driver-phone-no-signal), Z4 (RB12), Z5 (donate unknown end, RB13/14), Z9 (Q7 backup fail), Z10 (RB7 once per drop) = 6/12.
3. settled-by-7: P6, P4, P5, Z1, P3, P8, P9, Z9 = 8.
4. must-ask-7: P3, P4, Z1 = 3/7.
5. invisible: none = 0.
6. wasted: RB8 part (lapsed cannot order = D4), RB22 (Priya is coordinator, stated in [8]).
7. citations: ~60; mis-cited 1 (family key: phone cited to [2][4][11][19] with no mark). Rate 1/60.
8. derive: D1-D6 all = 6.
9. notes: Strong product coverage incl. a weak P11 via driver-visibility read-back. Hazard questions limited to warehouse offline and backup; driver offline only as a hazard entry. Twilio "retry 3 times" is in read-back, so not invisible.

## R408
1. P-surfaced: P3 (Q2), P4 (Q3), P5 (Q3, RB17), P6 (Q5, food_groups open), P7 (Q7), P8 (Q4), P9 (currency open, RB5), P10 (open, RB9) = 8/11. Missing P1, P2 (only after-cutoff addressed), P11.
2. Z-surfaced: Z1 (Q1, hazard), Z2 (Q1, hazard), Z3 (sum_and_send rerun: checks, RB13), Z4 (Q6, text_unknown hazard), Z9 (RB23 failed backup), Z10 (RB19) = 6/12.
3. settled-by-7: Z1, Z2, P3, P4, P5, P8, P6, Z4, P7 = 9.
4. must-ask-7: P3, P4, Z1, Z2 = 4/7.
5. invisible: Z5 (Stripe unknown routed to end/failed as fact; comment points to a hazard note that does not exist) = 1.
6. wasted: RB10 (second order refused = D2), RB11 part (window = D1), RB15 (coordinator assigns, stated in [8]), RB8 part (D4).
7. citations: ~65; mis-cited 2 (stock_in_out packer scans cited [14]; donate unknown->failed under src [17]). Rate 2/65.
8. derive: D1-D6 all = 6.
9. notes: Good must-ask hit on both offline holes. Payment-unknown handled wrongly and silently. No permission/data question (P10, P11 not asked).

## R747
1. P-surfaced: P2 (Q7), P3 (Q5), P4 (Q2), P5 (Q2), P6 (Q6, food-group open), P7 (open, RB), P8 (Q4), P9 (Q1, currency RB, director-how open), P10 (open, RB) = 9/11. Missing P1, P11.
2. Z-surfaced: Z1 (network-drop hazard, RB reliability, double tick), Z2 (network-drop on driver app), Z3 (restart: missed cutoff job runs once; close-orders failed end), Z4 (send-text failed/unknown, Q3), Z5 (donate unknown -> pending-check, RB), Z7 (exact-12:00 boundary open, double place, timezone), Z9 (backup failure open, missed job, backup halfway), Z10 (low-stock failed case, once per drop), Z11 (wrong tap undo) = 9/12.
3. settled-by-7: P9, P4, P5, Z4, Z5 (receipt half), Z10, P8, P3, P6, P2 = 10.
4. must-ask-7: P3, P4, Z5 = 3/7.
5. invisible: none = 0 (all retry/hold values carry open marks or read-back).
6. wasted: Q5 part (who assigns: [8] already says drivers sign up, coordinator assigns), RB "place order twice refused by one-box guard" (D2).
7. citations: ~72; mis-cited 1 (family address because [8]). Rate 1/72.
8. derive: D1-D6 all = 6.
9. notes: Widest hazard coverage, but none of the 7 questions covers offline (Z1, Z2 only in read-back). No permission question (P10/P11). Recommended defaults in every question.

## R953
1. P-surfaced: P2 (open, RB), P3 (Q6), P4 (Q2), P5 (Q2, RB), P6 (Q5, food-group open), P8 (Q4), P9 (Q3 currency/exactly 500, director-how open), P10 (Q4) = 8/11. Missing P1, P7 (weekly_use given as an unmarked formula), P11.
2. Z-surfaced: Z1 (Q1, hazard), Z2 (Q1), Z3 (send rerun mark: tablet unreachable), Z4 (Q2 text fails, RB Friday text), Z5 (pay-wait recheck, Q3 receipt fails/twice), Z9 (Q7, nightly-missed hazard), Z10 (low-stock rerun open, RB) = 7/12.
3. settled-by-7: Z1, Z2, P4, P5, Z4, Z5, P9, P8, P10, P6, P3, Z9 = 12.
4. must-ask-7: P3, P4, P10, Z1, Z2, Z5 = 6/7.
5. invisible: none counted = 0 (borderline: cover_weeks = on_hand/weekly_use stated without mark, but no window given).
6. wasted: Q3 part ("exactly 500" answered by "over"), RB strictly-less/over/>4 (D3), RB one-a-week per family (D2), RB no orders after cutoff (D1), RB Priya is a role holder ([8]).
7. citations: ~72; mis-cited 3 (goal/board-informed "weekly figures" cited [s21] which says nightly; set/box-kind "standard" cited [s4]; family.name cited [s2]). Rate 3/72.
8. derive: D1-D6 all = 6.
9. notes: Best question set: 6 of 7 must-ask, 12 holes settled. Misses P7 and P11; spends some read-back on derivable facts.

| run | P-surfaced | Z-surfaced | settled-by-7 | must-ask-7 | invisible | wasted | citations | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|---|
| R449 | 10 | 6 | 8 | 3 | 0 | 2 | ~60 | 1 (1/60) | 6 |
| R408 | 8 | 6 | 9 | 4 | 1 (Z5) | 4 | ~65 | 2 (2/65) | 6 |
| R747 | 9 | 9 | 10 | 3 | 0 | 2 | ~72 | 1 (1/72) | 6 |
| R953 | 8 | 7 | 12 | 6 | 0 | 5 | ~72 | 3 (3/72) | 6 |
# E11 scores (scorer g2)

## R815
1. P-surfaced: P2, P3, P4, P5, P6, P7, P8, P9, P10 (9/11). P1 (family size source/change) and P11 (data access) missing.
2. Z-surfaced: Z1, Z2 (Q2 offline packing ticks / driver taps), Z4 (Q6), Z9 (backup failure open + RB8), Z10 (rule + RB6) (5/12).
3. settled-by-7: P3, P4, P5, P6, P8, P9, Z1, Z2, Z4 (9).
4. must-ask-7: P3, P4, Z1, Z2 (4/7). P10 only in read-back; P11, Z5 absent.
5. invisible: none (0). Durations (3 days, 30 days, 4-week average) all sit in read-back as assumed.
6. wasted: RB16 late orders refused (D1); RB4 more than twelve stops (D6); RB14 families who never ordered get nothing (trivially derivable).
7. citations: 61; mis-cited: 2 (route_week ?timeout -> end/assigned cited to [8]; order.cancelled state "because sentence 2"). Rate 2/61.
8. derive: 6/6.
9. notes: Strong product pass, all fabrication traps marked assumed. Weak hazard pass: no Stripe unknown outcome, no double submit/race/stale stock, no data-privacy question.

## R506
1. P-surfaced: P3, P4, P5, P6, P7, P8, P9, P10 (8/11). P1, P2 (change/cancel), P11 missing.
2. Z-surfaced: Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8, Z9, Z10, Z11 (11/12). Z12 missing ("only the board receives it" does not address personal data).
3. settled-by-7: Z4, Z1, P4, P5, P6, P3, Z5, P9, Z9, P10 (10; Q7 is an either/or, counted both halves).
4. must-ask-7: P3, P4, P10, Z1, Z5 (5/7). Z2 only in read-back (Q2 is iPad only); P11 absent.
5. invisible: none (0). Retry 3x, 2 weeks, next Saturday all in read-back.
6. wasted: Q6 "is exactly 500 a big donor" (said: over 500) plus RB same; RB large box 5+ (D3); RB second order refused (D2); RB late orders refused (D1); RB 12 stops max (D6); RB orders open Monday 00:00 (D1).
7. citations: 60; mis-cited: 3 (quality/simple_for_older_drivers src s23 for "one tap" under "patchy phone signal"; order_week end closed_empty because s5 used for lapsed/duplicate refusals; goal states family_declined_or_lapsed src s1,s2). Rate 3/60.
8. derive: 6/6.
9. notes: Best hazard coverage, much of it via a long read-back. Questions mix in a derivable sub-question; Q7 is two questions joined by "Or". Long read-back repeats several derivable facts.

## R649
1. P-surfaced: P2, P3, P4, P5, P6, P7, P8, P9, P10 (9/11). P1, P11 missing.
2. Z-surfaced: Z1, Z2 (RB), Z4 (RB), Z5 (weak: RB receipt once per donation), Z7 (RB duplicate click), Z9, Z10 (7/12).
3. settled-by-7: Z1, P8, P4, P5, P3, P6 (6). Q6 (worst failure) and Q7 (clock times, ETA) settle no key hole.
4. must-ask-7: P3, P4, Z1 (3/7).
5. invisible: none (0).
6. wasted: RB "more than four means five or more" (D3); RB order window Monday-Wednesday 12:00 (D1); RB Priya is coordinator (said in [8]); RB "over" means more than (said).
7. citations: 73; mis-cited: 1 (receive-delivery assigns scanning to packer with src [14], while its own persona entry marks that open). Rate 1/73.
8. derive: 6/6.
9. notes: Clean entries and good product holes, but two of seven questions go to vague or low-value matters. Hazards mostly pushed to read-back; Stripe unknown outcome, races, stale stock and data privacy not raised.

## R576
1. P-surfaced: P1 (RB family size on account), P2, P3, P4, P5, P6, P7, P8, P9, P10, P11 (RB driver sees own route only) (11/11).
2. Z-surfaced: Z1, Z2, Z3 (send step retry/timeout open), Z4, Z5, Z6, Z8, Z11 (left-open grid cells in RB), Z9, Z10 (10/12). Z7 (double order / exact cutoff) and Z12 missing.
3. settled-by-7: P4, P5, Z4, Z5, Z1, Z2, P9, P6, P3, P2, P8 (11).
4. must-ask-7: P3, P4, Z1, Z2, Z5 (5/7). P10 and P11 only in read-back.
5. invisible: none (0). The 5-minute retry and the 1-hour retry window carry open/assumed marks and are in read-back. (Rerun never on texts is covered by Q2.)
6. wasted: RB order window Monday 00:00 to Wednesday 12:00 (D1); RB after cutoff orders refused (D1); RB large box 5+ (D3); RB Priya is coordinator (said); RB stock taken out at packing (said in [14]).
7. citations: 55; mis-cited: 1 (renew-eligibility check step causes family.renew on both accept and reject, src [19]). Rate 1/55.
8. derive: 6/6.
9. notes: Broadest coverage. Questions pack two decisions each and settle 11 holes. P11 surfaces only weakly, and Z12 is missing.

| run | P-surfaced | Z-surfaced | settled-by-7 | must-ask-7 | invisible | wasted | citations | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|---|
| R815 | 9 | 5 | 9 | 4 | 0 | 3 | 61 | 2 (3%) | 6 |
| R506 | 8 | 11 | 10 | 5 | 0 | 7 | 60 | 3 (5%) | 6 |
| R649 | 9 | 7 | 6 | 3 | 0 | 4 | 73 | 1 (1%) | 6 |
| R576 | 11 | 10 | 11 | 5 | 0 | 5 | 55 | 1 (2%) | 6 |
# Scores (scorer g3)

## R819
1. P-surfaced: P1 (household size source, read-back; mid-week change not), P3, P4, P5, P6, P7 (four-week average, read-back), P8, P9, P10 (read-back) = 9/11. Missing P2, P11.
2. Z-surfaced: Z1, Z2, Z3 (send_list open, restart no double send), Z4, Z5 (unknown row, webhook twice), Z6 (grid: two coordinators), Z7 (time zone read-back), Z9, Z10 = 9/12. Missing Z8, Z11, Z12.
3. settled-by-7: P3, P4, P5, P6, P8, P9, Z1, Z2, Z4, Z5, Z10 = 11.
4. must-ask-7: P3, P4, Z1, Z2, Z5 = 5/7 (P10 only in read-back, P11 absent).
5. invisible: none = 0 (every invented value carries ?open/?assumed or is in read-back).
6. wasted: read-back "outside Mon-Wed noon refused; second box refused" (D1, D2); "large box when 5 or more" (D3); "tick-offs take items out of stock" ([14]); "packing list built once at cutoff, later orders wait" (D1/[5]) = 4.
7. citations: ~60; mis-cited 2 (hazard restart because [22]; route driver ?optional because [8]). Rate 2/60.
8. derive: D1-D6 all captured = 6.
9. notes: Broadest hazard coverage via the read-back grid; questions bundle hazard clusters well (Q2, Q3). Misses personal-data access and order change/cancel; spends read-back lines on derivable facts.

## R788
1. P-surfaced: P2, P3, P4, P5, P6, P7 (read-back weekly use), P8, P9 = 8/11. Missing P1, P10, P11.
2. Z-surfaced: Z1, Z2 (read-back offline taps), Z3 (build_list rerun checks, list cached), Z4 (hazard text_lost), Z5 (rerun never / check first, read-back), Z9 (backup failure tells board, restart hazard), Z10 = 7/12. Missing Z6, Z7, Z8, Z11, Z12.
3. settled-by-7: P2, P3, P4, P5, P6, P8, P9, Z1 = 8.
4. must-ask-7: P3, P4, Z1 = 3/7.
5. invisible: P10 (rejected proof -> "family stays as is", unmarked); Z8 (rule stock_never_negative stated as fact, no policy or mark) = 2.
6. wasted: Q7 second half "what if they miss ordering altogether" (answered by D1/D2); read-back "Priya is the usual coordinator" ([8]) = 2.
7. citations: ~63; mis-cited 3 (persona supplier src [14], suppliers do not use the app; hazard restart because [22]; stock_never_negative because [14]). Rate 3/63.
8. derive: D1-D6 = 6.
9. notes: Product-side questions are good, but all seven questions are product holes except offline tablet; Stripe, driver offline and text failures appear only in read-back. Rejected proof is settled silently.

## R471
1. P-surfaced: P2 (read-back 8, no edit), P3, P4, P5, P6, P7 (weekly_need open), P8, P9 (currency only), P10 = 9/11. Missing P1, P11.
2. Z-surfaced: Z1, Z2, Z3 (send-list rerun, grid), Z4, Z5, Z6 (grid: two drivers cannot take one route), Z8 (grid: stock re-read when list built), Z9, Z10 = 9/12. Missing Z7, Z11, Z12.
3. settled-by-7: P3, P4, P5, P8, P10, P6, Z1, Z2, Z4, Z5, Z9 = 11.
4. must-ask-7: P3, P4, P10, Z1, Z2, Z5 = 6/7 (P11 missing).
5. invisible: none = 0 (text-retries 2, pickup wait, reminder 14 days all ?open with decision).
6. wasted: read-back 8 first half "orders after Wednesday noon are refused" (D1); read-back 5 "route never more than stop limit" (D6); read-back 2 "strictly over" ([18]) = 3.
7. citations: ~59; mis-cited 1 (workflow catch-up because [23], invented replay mechanism cited as owner's). Rate 1/59.
8. derive: D1-D6 = 6.
9. notes: Best must-ask coverage; each question is a cluster decision with options. Only P11 (personal data) and Z7/Z11/Z12 missed. Low-stock email fail and Z8 surfaced only via open/grid.

## R161
1. P-surfaced: P2, P3, P4, P5, P6, P8, P9 (currency, director channel), P10 = 8/11. Missing P1, P7, P11.
2. Z-surfaced: Z1, Z3 (wifi-loss unsent list, not_delivered open), Z4 (ask rerun never, assumed; duplication only), Z5 (otherwise check_payment open, read-back 8), Z9, Z10 = 6/12. Missing Z2, Z6, Z7, Z8, Z11, Z12.
3. settled-by-7: Z1, Z3, P4, P5, P8, P3, P6, P2 = 8 (Q2 "what does reliable mean" settles no specific hole).
4. must-ask-7: P3, P4, Z1 = 3/7.
5. invisible: none = 0.
6. wasted: read-back 4 "more than 500" strictness ([18]); read-back 5 "under two weeks, not exactly 2" ([16]); read-back 16 "Priya is coordinator and gets stock emails" ([8], [16]); read-back 21 "every family with an order gets the Friday text" ([13]) = 4.
7. citations: ~55; mis-cited 1 (hazard restart because [s22]). Rate 1/55.
8. derive: D1-D6 = 6.
9. notes: Driver-phone-offline hazard never surfaced (Q5 asks about app skill instead). Q2 is a vague reliability question that settles nothing concrete. No forecast basis for "two weeks of boxes".

## Final table
| run | P-surfaced | Z-surfaced | settled-by-7 | must-ask-7 | invisible | wasted | citations | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|---|
| R819 | 9 | 9 | 11 | 5 | 0 | 4 | 60 | 2 (3%) | 6 |
| R788 | 8 | 7 | 8 | 3 | 2 | 2 | 63 | 3 (5%) | 6 |
| R471 | 9 | 9 | 11 | 6 | 0 | 3 | 59 | 1 (2%) | 6 |
| R161 | 8 | 6 | 8 | 3 | 0 | 4 | 55 | 1 (2%) | 6 |
# Scores (scorer g4)

## R392
1. P-surfaced: P1 (Q7 household change), P2, P3, P4, P5, P6, P7 (RB8), P8, P9, P10 (?open + RB16), P11 (RB15, weak: drivers see own route only) = 11/11
2. Z-surfaced: Z1, Z2, Z3 (send_list ?open tablet unreachable, RB14), Z4 (RB4), Z5 (donate ?open, RB5, RB6), Z6 (RB20), Z7 (RB20 double order; noon clock not covered), Z9 (backup fail ?open, RB11), Z10 (RB7) = 9/12. Missing Z8, Z11, Z12.
3. settled-by-7: P1, P2, P3, P4, P5, P6, P8, P9, Z1, Z2 = 10
4. must-ask-7: P3, P4, Z1, Z2 = 4/7 (P10, P11, Z5 only in entries/read-back)
5. invisible: none = 0 (all invented values carry ?open/?assumed and appear in read-back)
6. wasted: RB14 partial ("later orders wait for next week" is D1) = 1
7. citations: 56; mis-cited: 2 (hazard/restart because [22]; hazard/text_unsure because [12] claims Twilio uncertainty) ; rate 2/56
8. derive: D1-D6 all captured = 6
9. notes: Broadest hazard coverage; hazard grid read-back item (RB20) gives proposed answers for races. Questions spend no slot on Stripe/proof/permissions despite capturing them.

## R690
1. P-surfaced: P1 (RB size at order time), P2 (RB), P3 (rule ?open, RB), P4, P5, P6, P7 (?open, RB), P8, P9, P10 (RB) = 10/11. Missing P11.
2. Z-surfaced: Z1, Z2, Z4 (Q1), Z5 (Q3), Z7 (RB cutoff local time; weak), Z9 (Q7), Z10 (?open, RB) = 7/12. Z3 only an unhandled failure end; missing Z3, Z6, Z8, Z11, Z12.
3. settled-by-7: Z4, P4, P5, Z5, P9, Z1, Z2, P8, P6, Z9 = 10
4. must-ask-7: P4, Z1, Z2, Z5 = 4/7
5. invisible: none = 0
6. wasted: RB "stops is a cap" (D6), RB "nobody can order outside window" (D1), RB "lapsed cannot place an order" (D4), RB "ticking takes items out of stock / scan adds" ([6][14]) = 4 (all partial, with a non-derivable tail)
7. citations: 65; mis-cited: 3 (hazard restart because [22]; hazard text-unknown [12][22]; quality easy-for-drivers "one tap" because [23]); rate 3/65
8. derive: 6
9. notes: Good question packing (Q1/Q3 bundle hazard + product). Long read-back padded with restatements of the scenario. No permission/personal-data hole.

## R570
1. P-surfaced: P2 (RB), P3 (Q4), P4, P5, P6, P7 (?open, RB), P8, P9, P10 (RB rejected proof told by text), P11 (RB volunteer sees name/address only; weak) = 10/11. Missing P1.
2. Z-surfaced: Z1, Z2, Z4 (RB retry 3x then coordinator), Z5 (RB unknown Stripe; thank-you once), Z9 (Q6), Z10 (RB once per low spell), Z12 (RB summary counts only, no names) = 7/12. Missing Z3, Z6, Z7, Z8, Z11.
3. settled-by-7: Z1, Z2, P4, P5, P8, P3, P6, Z9, P9 = 9
4. must-ask-7: Z1, Z2, P4, P3 = 4/7
5. invisible: none = 0
6. wasted: RB "families > 4 always get large box" (D3), RB "stop limit checked on assign" (D6 partial), RB "packing a box removes its items" ([14] partial) = 3
7. citations: 72; mis-cited: 1 (stock_item.low_alert_sent because [16] for "email once", acknowledged as own reading); rate 1/72
8. derive: 6
9. notes: Only run to surface Z12. Options with defaults per decision are well-formed. Hazards cite qualities, not sentences; Z3/races absent.

## R907
1. P-surfaced: P2 (RB11), P3 (Q5), P4, P5 (Q2 wait, RB15), P6, P7 (Q3), P8 (Q6), P9 (Q7), P10 (?open, RB7) = 9/11. Missing P1, P11.
2. Z-surfaced: Z1, Z2, Z3 (send ?open tablet unreachable), Z4 (Q2 text fails, hazard), Z9 (?open, RB14), Z10 (Q3) = 6/12. Z5 not surfaced: unknown Stripe outcome routed to thank-you as fact (email-unknown hazard only partial). Missing Z5, Z6, Z7, Z8, Z11, Z12.
3. settled-by-7: Z1, Z2, P4, P5, Z4, P7, Z10, P6, P3, P8, P9 = 11
4. must-ask-7: Z1, Z2, P4, P3 = 4/7
5. invisible: Z5 (donate.pay unknown -> step/thank, no mark, not in read-back) = 1
6. wasted: RB11 partial (one order only while open: D1, D2), RB14 partial (backup at 02:00: [21]) = 2
7. citations: 72; mis-cited: 3 (donate.pay unknown->thank because [17]; donate actor persona/family for donors [17]; quality easy-for-older-drivers "large taps, no typing" src [23]); rate 3/72
8. derive: 6
9. notes: Questions settle the most holes (11). Unknown Stripe payment silently treated as paid is a real money hazard. No permission/personal-data coverage.

## Table
| run | P-surfaced | Z-surfaced | settled-by-7 | must-ask-7 | invisible | wasted | citations | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|---|
| R392 | 11 | 9 | 10 | 4 | 0 | 1 | 56 | 2 (2/56) | 6 |
| R690 | 10 | 7 | 10 | 4 | 0 | 4 | 65 | 3 (3/65) | 6 |
| R570 | 10 | 7 | 9 | 4 | 0 | 3 | 72 | 1 (1/72) | 6 |
| R907 | 9 | 6 | 11 | 4 | 1 | 2 | 72 | 3 (3/72) | 6 |
