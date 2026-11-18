# Scores (blind scorer x)

## R449
1. P-surfaced: P2 (RB10), P3 (open+Q4), P4 (open+Q2), P5 (Q2 "how long keep"; pickup place/time not asked), P6 (open+Q1), P7 (RB7), P8 (Q5), P9 (Q6 + RB15), P10 (RB9), P11 (RB19 driver sees only own route; weak) = 10/11. Missing P1.
2. Z-surfaced: Z1 (hazard+Q3+RB20), Z2 (hazard driver-phone-no-signal), Z4 (RB12), Z5 (unknown case + RB13/14), Z7 (RB25 timezone only), Z9 (open+Q7), Z10 (RB7 once per drop) = 7/12. Missing Z3, Z6, Z8, Z11, Z12.
3. settled-by-7: P3, P4, P5, P6, P8, P9, Z1, Z9 = 8.
4. must-ask-7: P3, P4, Z1 = 3/7 (Z2 hazard captured but not asked; Z5, P10, P11 only in read-back).
5. invisible: none = 0 (retry 3, 30-day backup etc. all in read-back).
6. wasted: RB8 (lapsed blocks ordering = D4), RB22 (Priya is coordinator, [8]) = 2.
7. citations: 60; mis-cited: 1 (entity.family key [phone] cited to [2][4][11][19], not supported) = 1/60.
8. derive: D1-D6 all captured = 6.
9. notes: Questions spend slots on P6/P8/P9/Z9 while P10, P11, Z2, Z5 are only read-back. Hazard section only covers the two offline holes; message/job/race hazards come via read-back.

## R815
1. P-surfaced: P2 (open+RB1), P3 (open+Q5), P4 (open+Q1), P5 (Q1 how long kept), P6 (open+Q3), P7 (RB9), P8 (open+Q4), P9 (open+Q7), P10 (RB10) = 9/11. Missing P1, P11.
2. Z-surfaced: Z1 (Q2+open offline), Z2 (Q2 driver tapping), Z4 (Q6), Z9 (open+RB8), Z10 (rule + open + RB6) = 5/12. Missing Z3, Z5, Z6, Z7, Z8, Z11, Z12.
3. settled-by-7: P3, P4, P5, P6, P8, P9, Z1, Z2, Z4 = 9.
4. must-ask-7: P3, P4, Z1, Z2 = 4/7.
5. invisible: Z5 (donate.charged "rerun: checks" stated as fact, no unknown outcome, no mark, not in read-back) = 1.
6. wasted: RB16 (late orders refused = D1), RB4 (route over twelve stops = D6) = 2.
7. citations: 61; mis-cited: 2 (rule.low_stock_email_once body "once per drop" cited to [16]; quality.patchy_wifi extends to driver phones from [22][23], which only name warehouse wifi) = 2/61.
8. derive: D1-D6 = 6.
9. notes: Best must-ask coverage per question slot among offline/returns, but no Stripe-unknown handling at all. Q6 (text failure) is a non-must-ask hazard question. No personal-data/permission hole.

## R819
1. P-surfaced: P1 (RB household size entered at signup; source only), P3 (Q6), P4 (Q1), P5 (Q1 how long kept + RB pickup), P6 (open+Q7), P7 (RB four-week average), P8 (Q5), P9 (open+Q4+RB director task), P10 (RB rejected proof) = 9/11. Missing P2, P11.
2. Z-surfaced: Z1 (Q2+hazard+RB tick twice), Z2 (Q2), Z3 (open tablet offline at send, list_not_seen end, RB restart no double send), Z4 (Q3+open), Z5 (unknown case + Q3 + RB), Z6 (RB hazard grid two coordinators), Z7 (RB time zone), Z9 (open backup failure + RB rerun after restart / run twice), Z10 (open + Q3 + RB) = 9/12. Missing Z8, Z11, Z12.
3. settled-by-7: P3, P4, P5, P6, P8, P9, Z1, Z2, Z4, Z5, Z10 = 11.
4. must-ask-7: P3, P4, Z1, Z2, Z5 = 5/7.
5. invisible: none = 0 (pickup_hold_days 3 marked open; Friday-text "rerun: same" contradicted but covered by RB/Q3).
6. wasted: RB orders outside window / second box refused (D1, D2), RB large box at 5+ (D3), RB ticks take stock out ([14]), Q6 "route has more than twelve stops" part (D6) = 4.
7. citations: 60; mis-cited: 1 (quality/reliable "under: restart, external service failure" cited to [22] only) = 1/60.
8. derive: D1-D6 = 6.
9. notes: Q3 bundles four message/payment failures into one question, which buys wide hazard coverage. Several read-back lines restate derivable facts. No personal-data hole; pickup_hold_days value 3 conflicts with its own assumed "until Monday".

## R392
1. P-surfaced: P1 (Q7 household change), P2 (open+Q7), P3 (open+Q1), P4 (open+Q2), P5 (Q2 + RB10), P6 (open+Q6), P7 (RB8), P8 (open+Q5), P9 (Q3 + currency open + RB13), P10 (open+RB16), P11 (RB15 drivers see only own route; weak) = 11/11.
2. Z-surfaced: Z1 (hazard+Q4+RB9), Z2 (Q4), Z3 (open tablet unreachable at send + RB14), Z4 (hazard text_unsure + RB4), Z5 (unknown case + open + RB5), Z6 (RB20 two coordinators), Z7 (RB20 family ordering twice at same moment), Z9 (backup failed/unknown open + RB11), Z10 (open + RB7) = 9/12. Missing Z8, Z11, Z12.
3. settled-by-7: P1, P2, P3, P4, P5, P6, P8, P9, Z1, Z2 = 10.
4. must-ask-7: P3, P4, Z1, Z2 = 4/7 (Z5, P10 in read-back only; P11 weak read-back).
5. invisible: none = 0 (offline_sync_retry 5 min and pickup_reply_wait 2 days both ?open and in read-back).
6. wasted: RB12 (Priya is coordinator, [8]) = 1.
7. citations: 59; mis-cited: 1 (route transition "assigned from [open, signed_up]" cited to [8], which describes assigning after sign-up) = 1/59.
8. derive: D1-D6 = 6.
9. notes: Widest coverage of the four; Q7 uses a slot on a non-must-ask cluster (P1/P2) while Z5 stays read-back only. RB6 "retried" contradicts thank step "rerun: never". Retry interval/hold days invented but properly marked.

## Final table

| run | P-surfaced | Z-surfaced | settled-by-7 | must-ask-7 | invisible | wasted | citations | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|---|
| R449 | 10 | 7 | 8 | 3 | 0 | 2 | 60 | 1 (1/60) | 6 |
| R815 | 9 | 5 | 9 | 4 | 1 (Z5) | 2 | 61 | 2 (2/61) | 6 |
| R819 | 9 | 9 | 11 | 5 | 0 | 4 | 60 | 1 (1/60) | 6 |
| R392 | 11 | 9 | 10 | 4 | 0 | 1 | 59 | 1 (1/59) | 6 |
