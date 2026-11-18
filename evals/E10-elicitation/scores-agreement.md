# Scores (blind scorer x)

## R399
1. settled-by-7: H1, H2, H3, H4, H5, H6, H8, H9, H12, H13, H15 (who marks only, not expiry) = 11
2. must-ask-7: 6/6 (H1, H2, H4, H5, H8, H15)
3. read-back: H7, H10 (late fee/replacement unpaid -> stays blocked; repair failure open), H11, H14 (downgrade not offered; lapse with tools out not covered), H16 (birth date in profile, under-18 joins), H17, H18, H22 (reserved counted; waitlist not), H23, H24 = 10
4. missed: H19, H20, H21
5. invisible: 0
6. wasted: RB16 (all emails via Postmark = D5); RB20 (deposit refunded when returned fine, said in [17]/[27]; only "immediately" is new)
7. mis-cited: 1. rule/in_repair_not_reservable states "in repair, lost or retired is never reserved" with src [29], which only covers repair.
8. derive: 8
9. notes: Good clustering into decisions with proposed defaults. Proactively adds birth_date to fix H16. Nothing on closed-day late fees or reminder-email failure.

## R882
1. settled-by-7: H1, H2, H3, H4 (lost charge amount asked), H5, H6, H7, H8, H9, H12 (repair side), H13 (upgrade cost), H15 (who marks only), H22 (reservations count) = 13
2. must-ask-7: 6/6
3. read-back: H11, H16, H18, H20 (per calendar day), H24 = 5
4. missed: H14, H17, H19, H21, H23 (H10 is only partly covered, through the open late-unpaid end and Q4 "how pay / what lifts block")
5. invisible: 0
6. wasted: RB22 (hand tools need no deposit or intro, follows from [17]/[18]); RB21 (deposit refunded when fine, [17])
7. mis-cited: 1. rate skip cites because [34, 45] ("people like doing that", "simple"), which do not support rating being optional.
8. derive: 7 (D5 is weak: Postmark exists, but no reminder or waitlist workflow sends through it)
9. notes: Most holes settled by questions (reservation no-show and limit merged into Q7). Thin read-back: rating never read, retire and plan changes are absent. RB9 sets replacement as a single price-list amount, a defensible proposal.

## R780
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12, H13, H15 (who marks; expiry in read-back) = 11
2. must-ask-7: 5/6 (H8 only in read-back)
3. read-back: H8, H10 (unblock only when charges paid; partial), H11, H16 (under-18 joins; birthdate captured), H18, H22 (counts on-loan only), H24 = 7
4. missed: H14, H17, H19, H20, H21, H23
5. invisible: 0
6. wasted: RB "collect only on reserved day, due = that day + loan length" (due-date half is D2); RB "pickup day ... among opening slots" (slot half is D3)
7. mis-cited: 2. derived/late-loan-count counts lost loans as late with src [43]; the tool retire transition from available is commented because [..40], but [40] covers only tools beyond fixing.
8. derive: 8
9. notes: All placeholder amounts are open-marked and listed in read-back. H8 (must-ask) is pushed to read-back. Adds an organiser waive-charge workflow nobody asked for.

## R378
1. settled-by-7: H1, H2, H3, H4, H5, H6, H7, H9, H12, H13, H15 (who marks), H16 (how 18 is known) = 12
2. must-ask-7: 5/6 (H8 only in read-back)
3. read-back: H8, H10 (repair, replacement and late-fee failures), H11, H17 (nothing shows ratings), H18, H22, H24 = 7
4. missed: H14, H19, H20, H21 (handles a failed waitlist email, not a failed reminder), H23
5. invisible: 0 (placeholder amounts 30/60/50/2/14 are all ?open and repeated in read-back)
6. wasted: none
7. mis-cited: 3. tool retire from [available, in_repair] cites src [40] (only beyond fixing); rule reserved-tool-not-offered generalises to lost, retired and reserved with src [29]; the shelve transition from lost cites because [22, 27, 28].
8. derive: 8
9. notes: Only run that asks about the age data gap (H16) and flags that ratings are never read (H17). Read-back is grouped by question, which is clear. Citations are the loosest of the four.

| run | settled-by-7 | must-ask-7 | read-back | missed | invisible | wasted | mis-cited | derive |
|---|---|---|---|---|---|---|---|---|
| R399 | 11 | 6 | 10 | 3 (H19, H20, H21) | 0 | 2 | 1 | 8 |
| R882 | 13 | 6 | 5 | 5 (H14, H17, H19, H21, H23) | 0 | 2 | 1 | 7 |
| R780 | 11 | 5 | 7 | 6 (H14, H17, H19, H20, H21, H23) | 0 | 2 | 2 | 8 |
| R378 | 12 | 5 | 7 | 5 (H14, H19, H20, H21, H23) | 0 | 0 | 3 | 8 |
