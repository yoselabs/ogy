# E9 scores (scorer x)

## R710
1. invisible: none. 0
2. visible: H6 (decision default 2 days, held, next person), H7 (default expire / assumed expire), H9 (renew workflow: failed -> lapsed, marked by open decision), H11 (found: lost -> available, assumed), H15 (assumed Marta marks it), H22 (default loans_only). 6. H3 has 7/14-day values only as non-default options, so it does not count.
3. coverage: H1 H2 H3 H4 H5 H6 H7 H8 H9 H11 H12 H13 H14 H15 H16 H17 H18 H22 H24. 19. Missing: H10 (the unpaid late-fee branch is stated, not marked; nothing on unpaid repair or replacement), H19, H20, H21, H23.
4. questions: 20
5. yield: 18/20 = 0.90. These questions cover 2 or more holes: Q1 (H1, H2), Q3 (H5, H12), Q4 (H9, H14), Q6 (H4, H11).
6. must-ask: 4/6 (H1, H2, H5, H4 in Q1-Q7). H15 is first asked at Q14. H8 is marked in an entry but never asked.
7. wasted: none counts in full. Q11 is half wasted: its first half (can basic borrow no power tool?) is D1. Q9 (clock times) and Q12 cover no key hole but are not derivable.
8. false-said: 0. Only a small gloss: goal/lend-tools adds "instead of buying".
9. derive: D2 D3 D4 D5 D6 D7 D8. 7. D1 fails because the plus-only part is marked open and asked (rule power-tools-need-plus, Q11).
10. notes: Decision entries carry option sets, defaults, and a ranked question budget. Money holes get no default, which is good discipline. The options invent sample values (7/14 days, 2 days, a replacement-price cap) but keep them out of force. Missed: H10 (unpaid charges), H19 (no volunteer or shed closed), H20 (late fee on closed days), H21 (reminder email fails), H23 (retire decisions).

## R978
1. invisible: none. 0. The deposit-failure refusal in start-loan is stated as fact, but that is H8, which is outside the trap list.
2. visible: H1 (flat), H2 (flat, no cap), H3 ("block never fires"), H4 (per tool at intake), H5 (fixer decides amount), H6 (48 hours), H7 (no-show frees the tool), H9 (lapsed cannot reserve), H11 (lost is final), H12 (set-off against repair), H13 (pay the difference), H14 (existing loans continue), H15 (fixer marks it, never expires), H22 (counts loans only; stated in the entry but covered by Q6). 14
3. coverage: H1 H2 H3 H4 H5 H6 H7 H9 H10 H11 H12 H13 H14 H15 H16 H17 H18 H19 H22 H23 H24. 21. Missing: H8 (stated, unmarked), H20, H21.
4. questions: 16
5. yield: 19/16 = 1.19. These questions cover 2 or more holes: Q1 (H1, H2, H4), Q4 (H5, H12), Q6 (H22, H16), Q7 (H9, H13), Q9 (H11, H23).
6. must-ask: 4/6 (H1, H2, H4, H5 in Q1-Q7). H15 is first asked at Q8. H8 is never asked.
7. wasted: none. 0
8. false-said: 0. The run uses src comments; no misattribution found.
9. derive: D1 D2 D3 D4 D5 D6 D7 D8. 8
10. notes: Every hole gets an assumed value in force, so visibility is the highest of the four runs. It asks the owner/board an invented technical value (sweep time 03:00, marked "n/a to owner"). It leaves a junk persona `stripe-user` marked `?retired`. Questions about prices are addressed to the board.

## R191
1. invisible: none. 0
2. visible: H1 (one amount), H2 (no cap), H4 (flat value per tool, deposit applied), H5 (fixer enters the amount), H6 (48 hours), H7 (cancels at end of pickup day), H9 (lapsed cannot reserve, no retry), H11 (no recovery), H12 (deposit kept when the member pays), H13 (pay the difference), H14 (lapsed keeps loans), H15 (fixer or any volunteer, never expires), H22 (on-loan only). 13. H3 is marked "unknown", with no value.
3. coverage: H1 H2 H3 H4 H5 H6 H7 H9 H11 H12 H13 H14 H15 H16 H17 H18 H19 H22 H23 H24. 20. Missing: H8 (declined card -> not_lent, stated), H10, H20, H21.
4. questions: 17
5. yield: 20/17 = 1.18. These questions cover 2 or more holes: Q1 (H5, H12), Q2 (H4, H12), Q4 (H1, H2), Q5 (H9, H13, H14), Q8 (H7, H22), Q11 (H11, H23).
6. must-ask: 4/6 (H5, H4, H1, H2 in Q1-Q7). H15 is first asked at Q10. H8 is never asked.
7. wasted: Q6 (borderline): "a month" is stated, and the question only asks 30 days versus calendar month. 1
8. false-said: 0. The run uses `source:` lists; no misattribution found.
9. derive: D1 D2 D3 D4 D5 D6 D7 D8. 8
10. notes: Shape problems: entity/loan absorbs the reservation (initial state reserved); member blocking is a bool, not a state; the repair step "beyond fixing" ends in to_repair. A lost tool also blocks the member, a policy never said (outside the key). Q16 asks the owner when reminders and fees should run (a technical detail).

## R627
1. invisible: none. 0
2. visible: H1 (per tool, set at intake), H2 (flat, no cap), H3 (7 days), H4 (per-tool cost, deposit kept first), H5 (fixer decides, card on file), H6 (48 hours), H7 (release at end of day), H9 (lapse, no borrowing), H11 (yes, the charge stays), H12 (deposit held, then kept first), H13 (pay the difference), H22 (loans only). 12
3. coverage: H1 H2 H3 H4 H5 H6 H7 H8 H9 H11 H12 H13 H14 H16 H17 H18 H19 H22. 18. Missing: H10, H15 (safety intro is never marked or asked), H20, H21, H23, H24 (only the report's content is asked, not its form, sender or timing).
4. questions: 19
5. yield: 17/19 = 0.89. These questions cover 2 or more holes: Q3 (H2, H3), Q4 (H4, H12), Q5 (H5, H12), Q9 (H9, H14).
6. must-ask: 4/6 (H1, H2, H4, H5 in Q1-Q7). H8 is first asked at Q14. H15 is never asked.
7. wasted: none counts in full. 0. Q6 is half a nit ("a month"), and Q19 (renewal anniversary) covers no key hole.
8. false-said: 2. external/shift-sheet "stays outside the system" cites [41], which does not say that. workflow/unblock cites [31] for a volunteer-triggered unblock, which [31] does not say.
9. derive: D1 D2 D3 D4 D5 D6 D7 D8. 8
10. notes: It misses the must-ask H15 entirely: the safety intro has no workflow and no open mark. The power, age and intro guards apply only at pickup, not at reserve. Several workflows are prose strings rather than steps. mark-lost counts from loan start, against [32]; the run itself notes this.

| run | invisible | visible | coverage | questions | yield | must-ask | wasted | false-said | derive |
|---|---|---|---|---|---|---|---|---|---|
| R710 | 0 | 6 | 19 | 20 | 0.90 | 4 | 0 (Q11 half) | 0 | 7 |
| R978 | 0 | 14 | 21 | 16 | 1.19 | 4 | 0 | 0 | 8 |
| R191 | 0 | 13 | 20 | 17 | 1.18 | 4 | 1 | 0 | 8 |
| R627 | 0 | 12 | 18 | 19 | 0.89 | 4 | 0 | 2 | 8 |
