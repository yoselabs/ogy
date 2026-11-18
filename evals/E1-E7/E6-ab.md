# E6: edge-case hunt, ontology entries (a) vs prose sources (b)

Both Sonnet, same topic (factory core), same budget, neither saw the other.

## E6a: from E1's entries only (12 findings)
1. Attempt can be abandoned from any state, task abandon only claimed→ready; captured/verified attempts of a held task undecided.
2. hold-task waits for attempt.release, unreachable from dispatching/registered except via interrupt, which nothing triggers: a hold on a running agent waits forever.
3. Hold lifecycle has no failure state; crash after `label` leaves the comment unsent; resume ignores holds.
4. unhold fires on tracker.answered, but repeats-exhausted / main-moved / stuck holds are not questions; unhold does not reset step.repeats, so the task is re-held at once.
5. step `exhausted` and `done` terminal and keyed by (task, kind): a new implement pass after feedback cannot start.
6. Off-by-one: attempt.number max 3 vs repeats < 3 allows 4 attempts.
7. Repeat transfers the reservation; between old release and new row another admit can take the slot.
8. resume relaunch reuses the attempt id but no dispatching→dispatching transition; interrupted only releases.
9. resume `finished` vs still-exiting process; crash before register with no pid: `gone` can double-launch.
10. A refused admit and the max-new budget; round_taken unused; advance not counted against slots.
11. Lease lapses during downtime while the attempt lives → another claim → two executions on one task; no-double-run scoped per attempt/slot, not task.
12. checks-attempt unlinked to step/slot, number uncapped; max-rerun and setup-fail-limit values used by no rule.
Format note: lifecycle `from` lists and guards made exitless states and missing transitions visible fast; values with no
rule using them hid gaps.

## E6b: from prose sources (12 findings)
1. Claim lease lapses while a checked task waits at `Next: land`; reclaim could re-take or re-plan it.
2. Hold removes the approval label and adds `held`; both-labels and neither-label states undecided.
3. Hold abandons "when the slot allows"; while setup/checks run, attempt, reservation and claim stay; who ends it?
4. Land vs abandon deadlock when the push outcome is unknown (neither withdrawable nor abandonable).
5. Crash between push and close: delivered candidate, task still open and claimed with a lapsing lease; who retries?
6. Repeat cap 3, re-run cap 3 "in a row", stuck relaunch cap 2: no overall budget per task; what resets "in a row"?
7. Advances take slots before fresh admissions; fresh tasks can starve; no reserved capacity.
8. Round settle vs a person's `tl step release`/`start`/`land` racing on one slot; the loser just refuses.
9. After a factory.db discard: a live claim with no attempt, dirty slots, an existing task branch: no owner.
10. External or force push to task/<id> between publish and advance: refused with no exit but abandon.
11. A claimed mid-step task gains an open ask or a new blocker, or loses approval: invisible except through a hold.
12. Reboot: lingering or hung attempt past its deadline waits for the owner, holding a slot and an unrenewed lease.
Format note: precise per-term definitions helped; rules spread across paragraphs and documents made interactions
visible only by cross-reading; no state-transition table, so "states nobody leaves" had to be inferred.

## Comparison
- Overlap (both found): interacting limits; starvation of fresh tasks; lease lapse vs live work; crash/relaunch
  identity; a hold while the slot is busy.
- Only the ontology reader: exitless states, missing transitions, off-by-one between two limits, values no rule uses,
  reservation hand-over race. Structure made these fast to see.
- Only the prose reader: operational facts the E1 capture dropped: labels, push/close crash window, force-push to the
  task branch, discard with live claims, asks arriving mid-step, manual commands racing a round.
- Caveat: several ontology-reader findings may be capture errors in E1 (the model, not the factory); they need checking
  against code before they count.
- Reading: the ontology is better at structural gaps, prose holds more facts. The interview/capture must not drop
  operational facts, and "values used by no rule" and "states with no exit" are cheap lint checks.
