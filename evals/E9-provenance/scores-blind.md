# Scores g1

## R710
1. invisible: H20 (loan.late_days counts every calendar day between due_on and return; late_fee formula stated with `because`, no open mark). Count 1.
2. visible: H4 (per-tool replacement_cost attr, open decision), H6 (default two_days_held), H7 (assumed expire), H9 (fail -> lapse modelled, marked open decision), H11 (found -> available assumed), H15 (assumed Marta marks), H22 (default loans_only). Count 7.
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8, H9, H11, H12, H13, H14, H15, H16, H17, H18, H22, H24. Count 19.
4. questions: 20.
5. yield: 18/20 = 0.90 (H8 marked but not asked). Multi-hole: Q1 (H1,H2), Q3 (H5,H12), Q4 (H9,H14), Q6 (H4,H11).
6. must-ask: 4 (H1, H2, H5, H4; H8 not asked, H15 is Q14).
7. wasted: Q11 first half ("basic cannot borrow any power tool?" is D1).
8. false-said: 0.
9. derive: D2, D3, D4, D5, D6, D7, D8 = 7 (D1 carries an open mark on the plus guard).
10. notes: clean decision clustering with no-default money decisions; plus-only rule needlessly marked open. Structural gap: lost wait derived as lost-after minus block-after. Extra valid holes outside key (yearly fees, currency, opening times).

## R496
1. invisible: none. Count 0.
2. visible: H2 (default 1/day), H3 (default 7 days), H4 (default per-tool cost set at donation), H5 (default Marta sets, deposit first), H6 (default 48h held), H7 (default no-show frees tool), H9 (default retry, lapse after 14 days), H11 (assumed lost stays lost), H12 (deposit kept first), H15 (default Marta, never expires), H22 (default loans only). Count 11.
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8, H9, H11, H12, H13, H14, H15, H16, H18, H19, H22, H23, H24. Count 20.
4. questions: 16.
5. yield: 20/16 = 1.25. Multi-hole: Q1 (H1,H13), Q2 (H8,H9), Q3 (H5,H12), Q4 (H2,H3,H4), Q7 (H7,H22), Q8 (H15,H16), Q12 (H11,H23).
6. must-ask: 5 (H1, H8, H5, H2, H4; H15 is Q8).
7. wasted: Q9 second half (due date on a closed day: follows from D2/D3, run admits it).
8. false-said: 1 (derived/late-loan-count `said: s43` asserts a definition by started_on month that s43 does not state).
9. derive: D1-D8 = 8.
10. notes: Money defaults in force (late fee 1/day, block 7 days) despite "placeholder" label: visible but risky. Best cluster yield; only run asking H19 (no volunteer on counter). Extra holes: booking horizon, cancel, daily job time, extra emails (Q6).

## R153
1. invisible: H22 (rule within_max_out counts member.tools_out at start_loan only, stated, no mark or question). Count 1.
2. visible: H2 (assumed uncapped), H4 (assumed per-tool replacement_cost), H5 (assumed fixer decides, taken from deposit first), H6 (timeout -> next in line, asked), H7 (assumed lapse at end of pickup day), H11 (assumed found -> available), H12 (deposit first), H13 (assumed difference), H14 (assumed no downgrade), H15 (assumed any volunteer, never expires). Count 10.
3. coverage: H1, H2, H3, H4, H5, H6, H7, H9, H11, H12, H13, H14, H15, H16, H17, H18, H23, H24. Count 18.
4. questions: 20.
5. yield: 18/20 = 0.90. Multi-hole: Q1 (H1,H2,H4), Q4 (H5,H12), Q8 (H13,H14), Q9 (H9,H14), Q15 (H11,H23).
6. must-ask: 4 (H1, H2, H4, H5; H8 unmarked, H15 is Q11).
7. wasted: Q7 last part ("can someone reserve a tool out on loan?": D7 says on-loan tools are waitlisted).
8. false-said: 2 (tool.retire from [available, in_repair, lost] cites [40]; start_loan from available cites [15]).
9. derive: D1-D8 = 8.
10. notes: H8 deposit-failure branch silently stated (refused). Invented lost = 30 days but marked. Rating optional and late fee cap raised.

## R169
1. invisible: H20 (rule late-fee-accrues-daily: "each day a loan is late adds one day of late fee", stated, no mark). Count 1.
2. visible: H1 (assumed per-tool deposit), H2 (assumed flat, no cap), H3 (14 days assumed), H4 (assumed per-tool replacement price), H5 (assumed Marta enters amount), H6 (2 days assumed), H7 (assumed expire), H9 (assumed lapse immediately), H11 (assumed found, charge stays), H12 (assumed deposit applied to replacement), H13 (assumed prorated difference), H14 (assumed lapse, loans continue), H15 (assumed Marta, never expires), H22 (assumed loans only). Count 14.
3. coverage: H1, H2, H3, H4, H5, H6, H7, H9, H11, H12, H13, H14, H15, H17, H18, H22, H24. Count 17.
4. questions: 17.
5. yield: 17/17 = 1.00. Multi-hole: Q1 (H1,H2,H4), Q4 (H3,H6), Q5 (H5,H12), Q6 (H11,H12), Q7 (H9,H14).
6. must-ask: 4 (H1, H2, H4, H5; H8 unmarked, H15 is Q10).
7. wasted: none.
8. false-said: 3 (member birth-date cites [20], which captures no birth date (H16 hidden); write-off from on-loan cites [40]; in-repair rule extended to lost/retired cites [29]).
9. derive: D1-D8 = 8.
10. notes: H16 hidden: birth-date silently added as fact. H8 and H10 fail branches stated without marks. Values filled with assumed numbers (14 d, 2 d) in the value slot itself, marked open.

| run | invisible | visible | coverage | questions | yield | must-ask | wasted | false-said | derive |
|---|---|---|---|---|---|---|---|---|---|
| R710 | 1 | 7 | 19 | 20 | 0.90 | 4 | 1 | 0 | 7 |
| R496 | 0 | 11 | 20 | 16 | 1.25 | 5 | 1 | 1 | 8 |
| R153 | 1 | 10 | 18 | 20 | 0.90 | 4 | 1 | 2 | 8 |
| R169 | 1 | 14 | 17 | 17 | 1.00 | 4 | 0 | 3 | 8 |
# E9 scores, group 2

## R547
1. invisible: none. 0
2. visible: H5, H6, H7, H9, H11, H12, H13, H15, H22 (decision defaults or assumed values). 9
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8, H9, H11, H12, H13, H15, H16, H18, H22, H24. 17
4. questions: 17
5. yield: 17/17 = 1.00. Questions covering >=2 holes: Q1 (H1,H2), Q2 (H8,H9), Q3 (H5,H12), Q7 (H4,H11)
6. must-ask: 5/6 (H1, H2, H4, H5, H8 in Q1-Q7; H15 only at Q9)
7. wasted: none (Q17 daily check time is low-value but not in the scenario)
8. false-said: 1 (tool.retire from in_repair only, cited `said: s40`; s40 does not say "only from repair", and the comment admits it is a reading)
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. 8
10. notes: Ranked decision queue, each with options and a default; this is the cleanest provenance of the four. Misses H10 (unpaid late, repair or replacement charge), H14, H17, H19, H20, H21, H23. Safety intro expiry is not asked (only who marks it).

## R978
1. invisible: H6 (on timeout the claim "passes to the next in line; re-arms" is stated in the workflow. Only the window length and the hold are open, and Q3 does not ask about next-person). 1
2. visible: H1, H2, H3, H4, H5, H6 (48h), H7, H9, H11, H12, H13, H15, H22. 13
3. coverage: H1, H2, H3, H4, H5, H6, H7, H9, H10, H11, H12, H13, H15, H16, H17, H18, H19, H22, H23, H24. 20
4. questions: 16
5. yield: 19/16 = 1.19 (H10 is marked only in entries). Questions covering >=2 holes: Q1 (H1,H2,H4), Q4 (H5,H12), Q6 (H16,H22), Q7 (H9,H13), Q9 (H11,H23)
6. must-ask: 4/6 (H1, H2, H4, H5; H8 never asked; H15 at Q8)
7. wasted: none
8. false-said: 0 (uses `src` comments; the places it reads beyond the cited sentence carry ?open)
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. 8
10. notes: Widest coverage, with the best questions-to-holes ratio. H8 (deposit charge fails) is stated as a refusal with no mark. Q15 adds concessions/families, which nobody raised.

## R858
1. invisible: none. 0
2. visible: H3 (default 7 days), H6 (default two days, held, next person), H7, H11, H15 (default Marta), H22 (default: reservations do not count). 6
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8, H9, H10, H11, H12, H13, H15, H16, H17, H18, H20, H22, H23, H24. 21
4. questions: 22
5. yield: 21/22 = 0.95. Questions covering >=2 holes: Q1 (H1,H2), Q2 (H8,H9), Q3 (H5,H12), Q7 (H7,H22), Q9 (H3,H10)
6. must-ask: 5/6 (H1, H2, H4, H5, H8; H15 at Q15)
7. wasted: no whole question. Partly wasted: Q11 second half (the power-tool flag is set at intake, D6) and Q12 second half (under-18 limited to hand tools follows from [20])
8. false-said: 0
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. 8
10. notes: The only run to catch H20 (Q19: "do closed days count as late days?"). Money decisions (pay-failure, damage, upgrade) have no defaults, so they count as covered but not as visible values. The member lifecycle has only `active`: blocked is derived and lapsed is missing, a shape gap. The 22-question tail is long.

## R766
1. invisible: none. 0
2. visible: H1 (per tool), H2 (flat, no cap), H3 (no blocking until given), H4 (tool's own price), H5, H6 (P2D, then next person), H7, H9, H11, H12, H13, H15, H22 (reservations count). 13
3. coverage: H1, H2, H3, H4, H5, H6, H7, H9, H11, H12, H13, H14, H15, H16, H17, H18, H22, H23, H24. 19
4. questions: 20
5. yield: 19/20 = 0.95. Questions covering >=2 holes: Q1 (H1,H2,H4), Q9 (H13,H14)
6. must-ask: 4/6 (H1, H2, H4, H5; H8 never asked; H15 at Q13)
7. wasted: no whole question. Partly wasted: Q18 first half (plus loans are two weeks, said in [9]) and Q12 first half (whether under-18s can be members at all, which follows from [20] gating only power tools)
8. false-said: 1 (tool.replacement_cost carries `said: [32]` as a per-tool attribute; [32] says only "we charge you the replacement")
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. 8
10. notes: H8 is stated as "no loan; tool stays reserved" with no mark. It invents a 1-day join payment timeout and a waitlist bounce branch (a partial nod to H21). The release-deposit step creates a payment on every return, hand tools included (shape error). The only run that asks about downgrade (H14, marginal).

| run | invisible | visible | coverage | questions | yield | must-ask | wasted | false-said | derive |
|---|---|---|---|---|---|---|---|---|---|
| R547 | 0 | 9 | 17 | 17 | 1.00 | 5 | 0 | 1 | 8 |
| R978 | 1 | 13 | 20 | 16 | 1.19 | 4 | 0 | 0 | 8 |
| R858 | 0 | 6 | 21 | 22 | 0.95 | 5 | 0 (2 partial) | 0 | 8 |
| R766 | 0 | 13 | 19 | 20 | 0.95 | 4 | 0 (2 partial) | 1 | 8 |
# E9 scores (g3): R483, R954, R191, R635

## R483
1. invisible: none. H1/H2/H3 are open with no value; every other trap value carries assumed or a decision default. Count 0.
2. visible: H4 (per-tool price, assumed), H5 (fixer sets cost, deposit applied first: default), H6 (2 days, assumed), H7 (end of pickup day: default), H9 (failed renewal blocks: default), H11 (stays lost, no refund: assumed), H12 (deposit covers: default), H13 (difference: default), H15 (fixer marks, never expires: assumed), H22 (from reservation: default). Count 10.
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8, H9, H10, H11, H12, H13, H15, H16, H17, H18, H22, H24. Count 19. Missing: H14, H19, H20, H21, H23.
4. questions: 18.
5. yield: 19/18 = 1.06. Questions covering 2 or more holes: Q1 (H5, H12), Q2 (H1, H2, H3, H4), Q3 (H8, H9, H10), Q5 (H6, H7).
6. must-ask: 5/6 (H1, H2, H4 in Q2; H5 in Q1; H8 in Q3; H15 only comes at Q11).
7. wasted: none.
8. false-said: 2. term/power_tool cites [17, 18, 37] for "plus plan ... age 18", which those sentences do not state. rule/reserved_or_repair_not_reservable cites [29] for lost and retired tools too, but [29] covers only repair.
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. Count 8.
10. notes: Strong decision clusters (damage/loss money, payment failure, reservation hold), each with options and a default. The derived note "No closed-day case arises" dismisses closed days but misses H20: late days count calendar days. Adds assumed values nobody asked for (06:00 sweep, report on the 1st, "3 minutes" counter-ease target), all marked.

## R954
1. invisible: none. Each trap value sits behind an open slot, a decision with no default, or a decision default. Count 0.
2. visible: H6 (2 days, held: default), H7 (lapse same day: default), H9 (stop and tell, 0-day grace: default), H11 (found again, no refund: default), H15 (Marta marks: assumed), H22 (loans only: default). H3, H5, H12 and H13 are decisions that list options but set no default, so they are not counted. Count 6.
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8, H9, H10, H11, H12, H13, H15, H16, H17, H18, H22, H24. Count 19. Missing: H14 (asks about downgrading, never about tools still out), H19, H20, H21, H23.
4. questions: 20.
5. yield: 19/20 = 0.95. Questions covering 2 or more holes: Q1 (H5, H12), Q2 (H1, H2, H4), Q3 (H8, H9, H10).
6. must-ask: 5/6 (H1, H2, H4 in Q2; H5 in Q1; H8 in Q3; H15 only comes at Q11).
7. wasted: none as whole questions. Q7's sub-part "due date from reserved day or collected day" leans on D2.
8. false-said: 1. term/power_tool cites only [37] for "needs the plus plan, the safety intro, age 18 or over, and a deposit".
9. derive: D1, D3, D4, D5, D6, D7, D8. Count 7. D2 is missing because derived/due_date is marked open (decision/no_show).
10. notes: Leaves the money decisions (damage, late policy, membership changes) with no default on purpose ("no safe default"). Adds a reservation entity apart from the loan, plus amount_owed and a settle_overdue workflow. It asks the most questions of the four runs, with the lowest yield.

## R191
1. invisible: none for key holes. Count 0. (It does state, unmarked, "lost -> member blocked", a policy that is not in the key.)
2. visible: H1 (one amount for all), H2 (no cap), H4 (flat value per tool, charged on Stripe, deposit applied), H5 (fixer enters the amount), H6 (48 hours), H7 (cancels at end of pickup day), H9 (lapses, keeps loans), H11 (no recovery), H12 (deposit kept when the member pays), H13 (difference), H14 (lapsed member keeps loans), H15 (fixer or volunteer, never expires), H22 (on-loan only). Count 13.
3. coverage: H1, H2, H3, H4, H5, H6, H7, H9, H11, H12, H13, H14, H15, H16, H17, H18, H22, H23, H24. Count 19. Missing: H8 (a declined deposit simply ends not_lent, with no mark), H10, H19, H20, H21.
4. questions: 17.
5. yield: 19/17 = 1.12. Questions covering 2 or more holes: Q1 (H5, H12), Q2 (H4, H12), Q4 (H1, H2), Q5 (H9, H13, H14), Q8 (H7, H22), Q11 (H11, H23).
6. must-ask: 4/6 (H1, H2 in Q4; H4 in Q2; H5 in Q1; H8 never asked; H15 only comes at Q10).
7. wasted: none.
8. false-said: 0. The `source: [n]` citations hold up.
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. Count 8.
10. notes: The only run among these four that covers H23 (retire: who decides, from which states). It drops almost all of the payment-failure cluster (H8, H10). The `asks:` targets vary oddly: prices go to persona/board, the claim window to the volunteer. The repair step's "charge" choice loops back to itself.

## R635
1. invisible: none. Count 0.
2. visible: H1 (per-tool deposit), H2 (flat, no cap), H4 (per-tool replacement_cost), H5 (fixer decides case by case), H6 (48 hours), H7 (no-show released at end of day), H9 (lapse after failed renewal), H11 (can be marked found), H12 (held, kept toward repair), H13 (difference), H14 (lapsed member must still return loans), H15 (never expires, fixer only), H22 (loans only). Count 13.
3. coverage: H1, H2, H3, H4, H5, H6, H7, H9, H10, H11, H12, H13, H14, H15, H16, H17, H18, H22, H24. Count 19. Missing: H8 (a failed deposit becomes end/refused with no mark), H19, H20, H21, H23.
4. questions: 15.
5. yield: 19/15 = 1.27. Questions covering 2 or more holes: Q1 (H1, H2, H4), Q3 (H5, H10, H12), Q5 (H9, H13, H14), Q7 (H7, H22).
6. must-ask: 4/6 (H1, H2, H4 in Q1; H5 in Q3; H8 never asked; H15 only comes at Q9).
7. wasted: none.
8. false-said: 1. rule/not-reservable-in-repair cites [29] for "in_repair, lost or retired", but [29] covers only repair.
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. Count 8.
10. notes: Asks the fewest questions and gets the highest yield. It clusters money amounts into Q1 and damage into Q3, with H10 (refusal to pay) in Q3. It keeps an explicit "uncaptured" list. Shape slip: loan.cancel goes reserved -> returned. renew has no failure branch, only an ?open.

| run | invisible | visible | coverage | questions | yield | must-ask | wasted | false-said | derive |
|---|---|---|---|---|---|---|---|---|---|
| R483 | 0 | 10 | 19 | 18 | 1.06 | 5 | 0 | 2 | 8 |
| R954 | 0 | 6 | 19 | 20 | 0.95 | 5 | 0 | 1 | 7 |
| R191 | 0 | 13 | 19 | 17 | 1.12 | 4 | 0 | 0 | 8 |
| R635 | 0 | 13 | 19 | 15 | 1.27 | 4 | 0 | 1 | 8 |
# E9 scores (scorer g4)

## R684
1. invisible: none. 0
2. visible: H3 (default 7 days), H6 (default 2 days, held), H9 (default grace), H13 (default pay difference), H22 (loan-limit counts active loans only, but Q9 asks). 5
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8 (assumed refused), H9, H11, H12, H13, H16, H17, H18, H19, H22, H23 (assumed), H24. 19
4. questions: 16
5. yield: 17/16 = 1.06 (H1,H2,H3,H4,H5,H6,H7,H9,H11,H12,H13,H16,H17,H18,H19,H22,H24). Multi-hole: Q1 (H1,H2,H4), Q2 (H5,H12), Q4 (H9,H13), Q9 (H7,H22)
6. must-ask: 4/6 (H1,H2,H4 in Q1, H5 in Q2; H8 only assumed in entries, H15 missing)
7. wasted: none (Q7 eligibility timing, Q13 hours, Q14, Q16 are not key holes but not derivable)
8. false-said: 1 (rule/in-repair-not-reservable generalises to every non-available state citing [29],[21-22])
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. 8
10. notes: Missed H10, H14, H15, H20, H21. Guard bodies read inverted ("when allowed-condition-false else refused"); repair workflow fires tool.return_damaged at Marta's assess step. Clean clustering of money amounts into Q1.

## R387
1. invisible: none. 0
2. visible: H4 (set at intake), H5 (Marta, from deposit), H6 (2 days held), H7 (release at close), H9 (pause), H11 (refund if found), H12 (deposit first), H15 (Marta marks), H22 (reservations do not count). 9
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8, H9, H10, H11, H12, H13, H15, H16, H17, H18, H22, H23, H24. 20
4. questions: 20
5. yield: 20/20 = 1.00. Multi-hole: Q1 (H1,H2,H3), Q3 (H8,H9,H10), Q4 (H5,H12), Q6 (H4,H11), Q8 (H16,H15)
6. must-ask: 5/6 (H1,H2 Q1; H8 Q3; H5 Q4; H4 Q6; H15 only at Q8)
7. wasted: Q10 (basic never borrows power tools is D1, from [7]-[8])
8. false-said: 2 (no-show rationale cites s29 as saying reserved tools cannot be reserved, it says in repair; only-available-reservable generalises lost/retired from s21/s29)
9. derive: D2, D3, D4, D5, D6, D7, D8. 7 (D1 left open via Q10)
10. notes: Strongest coverage; only run with one payment-failure cluster covering H8/H9/H10. Invented shed hours (18-20, 10-12) as a decision default. Missed H14, H19, H20, H21.

## R869
1. invisible: none. 0
2. visible: H1 (flat), H2 (no cap), H4 (per-tool value, deposit first), H5 (fixer per case, Stripe), H6 (held, next in order), H7 (lapse end of day), H9 (nothing automatic), H11 (lost can come back), H12 (deposit toward repair/lost), H13 (pro rata difference), H14 (no downgrade), H15 (never expires), H22 (only tools out). 13
3. coverage: H1, H2, H3, H4, H5, H6, H7, H9, H10, H11, H12, H13, H14, H15, H16, H17, H18, H22, H23, H24. 20 (H23 marked in entry only)
4. questions: 16
5. yield: 18/16 = 1.13 (H1,H2,H3,H4,H5,H6,H7,H9,H10,H11,H12,H13,H15,H16,H17,H18,H22,H24). Multi-hole: Q1 (H1,H2,H13), Q4 (H5,H10,H12), Q5 (H4,H11), Q12 (H15,H18)
6. must-ask: 4/6 (H1,H2,H13 Q1; H5 Q4; H4 Q5; H8 never covered, deposit-failed end stated as fact; H15 only at Q9)
7. wasted: none fully; Q9 partly (plus-only power tools is D1)
8. false-said: 3 (reserve-needs-available `basis: said` counts open reservations, not in [10] and contradicting its own assumption; no-reserve-in-repair adds lost/retired to [29]; counter-is-simple "one scan or one tap per decision" from [45,46])
9. derive: D2, D3, D4, D5, D6, D7, D8. 7 (D1 left open via Q9)
10. notes: Internal contradictions: guard counts reservations while the assumption says only loans; retire allowed from available while the assumption says repair only. All questions addressed to persona/board/volunteer, not the owner. H8 deposit failure stated without mark; H19-H21 missed.

## R627
1. invisible: none. 0
2. visible: H1 (per tool), H2 (flat, no cap), H3 (7 days), H4 (per-tool cost, deposit first), H5 (fixer, card on file), H6 (48 hours), H7 (release end of day), H9 (lapse), H11 (charge stays), H12 (deposit kept first), H13 (pay difference), H22 (loans only). 12
3. coverage: H1, H2, H3, H4, H5, H6, H7, H8, H9, H11, H12, H13, H14, H16, H17, H18 (entry only), H19, H22. 18
4. questions: 19
5. yield: 17/19 = 0.89 (H1,H2,H3,H4,H5,H6,H7,H8,H9,H11,H12,H13,H14,H16,H17,H19,H22). Multi-hole: Q3 (H2,H3), Q4 (H4,H12), Q5 (H5,H12), Q9 (H9,H14)
6. must-ask: 4/6 (H1 Q1, H2 Q3, H4 Q4, H5 Q5; H8 only at Q14; H15 never)
7. wasted: none (Q18, Q19 low value but not derivable)
8. false-said: 2 (no-reserve-in-repair adds lost/retired citing [29,39]; external/shift-sheet "stays outside the system" cited to [41])
9. derive: D1, D2, D3, D4, D5, D6, D7, D8. 8
10. notes: Most specific defaults (7 days, 48 hours) but all marked. Missed H10, H15, H20, H21, H23, H24 (report questions ask contents, not delivery). mark-lost trigger starts at loan start, self-flagged as needing a modelling decision.

| run | invisible | visible | coverage | questions | yield | must-ask | wasted | false-said | derive |
|---|---|---|---|---|---|---|---|---|---|
| R684 | 0 | 5 | 19 | 16 | 1.06 | 4/6 | 0 | 1 | 8 |
| R387 | 0 | 9 | 20 | 20 | 1.00 | 5/6 | 1 | 2 | 7 |
| R869 | 0 | 13 | 20 | 16 | 1.13 | 4/6 | 0 | 3 | 7 |
| R627 | 0 | 12 | 18 | 19 | 0.89 | 4/6 | 0 | 2 | 8 |
