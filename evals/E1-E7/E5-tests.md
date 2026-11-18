# E5 - tests as proofs of E1 entries, and a limit change (exercise, 2026-11-17)

Sources: spec-v3 RECEIPTS, E1-core, `grep "def test_"` over tests/ (1205 test functions, 320 `parametrize` uses).
Test id = `tests/<path>.py::test_<name>`; below `steps/x.py::name` abbreviates it. Ids matched by name only, not run.

## 1. Entry -> proof (36 of 42 proof-bearing items have a test, 6 gaps)
Items counted: every rule, workflow, quality, interface, constant, dependency, value, derived, entity, external-group
and set of E1. Personas, goals and terms carry no proof by nature (vocabulary), so they are not counted.

| E1 entry | test id(s) |
|---|---|
| rule one-reservation-per-slot | steps/test_admit.py::a_slot_taken_between_observe_and_commit_moves_to_the_next_or_refuses; steps/test_attempt_store.py::stale_reservation_expired_or_missing_attempt_is_refused |
| rule one-execution-per-attempt | steps/test_attempt.py::bad_answer_has_one_execution; ::two_connections_contend_for_one_dispatch; ::dispatch_is_consumed_and_wrong_key_cannot_capture |
| rule repeat-cap | steps/test_repeat.py::the_third_attempt_is_not_repeated; steps/test_repeat_dispatch.py::three_attempts_then_the_owner |
| rule crash-not-an-attempt | steps/test_launch.py::an_observed_dead_entry_is_replaced; steps/test_attempt_store.py::a_replacement_from_another_boot_renews_the_deadline_once_per_reboot; steps/test_advance.py::a_restart_after_the_advance_was_admitted_but_never_launched_continues_it |
| rule no-competitor-launch | steps/test_launch.py::a_live_or_unobservable_entry_is_not_started_again; steps/test_attempt_store.py::first_registration_wins_and_a_second_is_a_conflict |
| rule held-blocks-admission | steps/test_round_holds.py::a_round_under_another_label_skips_a_held_task_even_when_it_carries_that_label; ::a_start_by_hand_of_a_held_task_is_refused_on_hold_and_changes_nothing_until_answered |
| workflow round | steps/test_round.py::admission_follows_selection_and_stops_at_no_free_slot; ::a_round_starts_at_most_max_new_fresh_tasks_though_slots_are_free |
| workflow admit | steps/test_admit.py::no_free_slot_refuses_before_any_effect; ::claim_refusal_and_unknown_claim; ::store_failure_after_the_claim_is_compensated |
| workflow attempt-run | steps/test_attempt.py::execute_and_independent_collection_preserve_facts_and_reservation; steps/test_dispatch_slot.py::a_deadline_crossed_during_the_slot_read_never_dispatches |
| workflow verify | steps/test_answer_contract.py::collected_always_names_its_outcome_and_only_a_verified_plan_succeeds; steps/test_attempt.py::failed_execution_valid_answer_is_not_success |
| workflow repeat | steps/test_repeat.py::a_repeat_takes_the_reservation_over_and_freezes_the_previous_attempt |
| workflow hold-task | steps/test_hold.py::a_hold_records_moves_the_labels_abandons_then_comments_once; ::a_crash_after_the_labels_resumes_at_the_abandon |
| workflow unhold | steps/test_round_holds.py::the_person_s_answer_takes_the_task_again_at_plan_on_its_branch_and_held_is_removed |
| workflow resume | steps/test_round.py::each_existing_attempt_by_its_next_word; steps/test_check_entry.py::a_live_or_unknown_orphan_is_reconciled_before_any_slot_read_and_counted |
| workflow stop | steps/test_round.py::a_stop_after_the_first_settle_move_performs_no_further_move; steps/test_round_holds.py::a_graceful_stop_skips_the_clear_and_the_next_round_does_it |
| workflow ask-owner | steps/test_round_holds.py::show_of_a_hand_started_needs_owner_prints_the_agent_s_question_and_a_next_action_of_the_step (weak) |
| workflow parallel-tasks | steps/test_advance.py::two_done_tasks_and_one_slot_advance_oldest_release_first_and_new_work_waits; steps/test_round.py::a_refusal_about_one_task_moves_on_to_the_next |
| quality restart-continuity | **no test** (no ratio is measured; only single-case restart tests exist) |
| interface tl-step | cli/test_step_cli.py::rounds_require_every_choice_and_the_help_names_the_stop (weak: says-words `refused`/`held` untested for tl-step) |
| constant MAX_REPEATS | **no test** (source name is `ATTEMPTS`, attempt_types.py:49) |
| dependency bd | steps/test_admit.py::composition_claims_through_bd_and_unclaim_is_fenced_never_forced |
| value max-repeats | same ids as repeat-cap |
| value max-rerun | steps/test_checks_round.py::a_third_main_moved_in_a_row_holds_the_task_naming_the_cause |
| value max-new | steps/test_round.py::a_round_starts_at_most_max_new_fresh_tasks_though_slots_are_free |
| value attempt-minutes | **no test** (open in E1 too) |
| value lease-renew | steps/test_claim_lease.py::the_first_renewal_then_the_loop_record_one_word (weak: 100s not pinned) |
| value reclaim-grace | cli/test_task_inspection.py::a_discarded_factory_leaves_in_progress_rows_with_an_expired_lease_that_a_round_takes_again (weak) |
| value setup-fail-limit | steps/test_advance.py::a_setup_failing_twice_after_the_advance_was_admitted_is_stuck_and_never_relaunched_again |
| entity task (6 transitions) | admit: test_admit.py::admitted_rows_are_what_the_body_loads_and_stay_unregistered; hold: test_hold.py (above); unhold: test_round_holds.py (above); abandon: test_admit_chain.py::an_abandoned_implement_restarts_the_task_at_plan; land: test_land.py::a_moved_main_validates_s_in_a_slot_releases_it_then_pushes; close: test_land_close.py::a_refused_close_leaves_the_task_open_and_claimed_and_the_rerun_closes_it |
| entity attempt (8 transitions, 6 attrs) | dispatch: test_dispatch_slot.py::the_dispatch_records_the_slot_head_as_base_and_keeps_the_fenced_admission; register: test_attempt_store.py::first_registration_wins...; capture: test_attempt.py::the_answer_is_stored_with_its_effect; reject: test_repeat_dispatch.py::planned_with_nothing_new_in_a_later_attempt_is_rejected_for_good; interrupt: test_checks.py::the_deadline_without_survivors_interrupts_and_expires_the_attempt; release/abandon: test_slot_release.py::abandon_a_prepared_admitted_attempt_parks_it_at_d; attrs: ::the_schema_numbers_attempts_and_links_each_to_the_one_it_repeats |
| entity checks-attempt | steps/test_check_entry.py::a_passing_block_concludes_passed_releases_the_slot_at_d_and_exits_0; steps/test_check_admit.py::a_failed_released_checks_attempt_is_re_run_as_number_2_and_the_first_is_kept |
| entity slot | steps/test_slot_release.py::after_a_release_every_other_writer_meets_the_fence_and_the_slot_is_free_again; ::a_held_slot_lock_is_slot_busy |
| entity reservation | steps/test_attempt_store.py::stale_reservation_expired_or_missing_attempt_is_refused; steps/test_repeat.py::a_repeat_takes_the_reservation_over... |
| entity session | steps/test_attempt.py::capture_upgrades_pending_session_state_once_and_rejects_different_evidence; ::recorded_session_conflict_is_visible_without_a_result_and_blocks_complete |
| entity step | **no test**: the code has no step table (a step is derived from its attempts), so pending/running/done/exhausted are never transitions |
| entity hold (phases) | steps/test_hold_store.py::the_label_step_is_recorded_once_on_the_read_rev; ::the_comment_is_recorded_only_under_a_lease; ::a_hold_is_cleared_only_after_the_task_was_taken_again |
| derived slot-free | steps/test_admit.py::no_free_slot_refuses_before_any_effect |
| derived live-execution | steps/test_launch.py::a_live_or_unobservable_entry_is_not_started_again |
| externals (tracker, harness, origin) | steps/test_admit.py::claim_refusal_and_unknown_claim; steps/test_publish.py::a_diverged_remote_is_refused_and_kept_and_an_unknown_tip_is_remote_moved |
| set disposition | steps/test_answer_contract.py::the_schema_has_the_five_keys_and_the_unchanged_disposition |
| set hold-reason | **no test** (open: full list lives in code; no test enumerates it) |
| set step-kind | **no test** (members' attribute `agent: true/false` is not tested; test_access.py only touches plan/implement) |

Coverage: 42 items, 36 with a test (6 of them weak, one test id that only touches the entry), 6 without
(restart-continuity, MAX_REPEATS, attempt-minutes, step entity, hold-reason, step-kind). 86%.
Opposite direction: about 377 of 1205 test functions sit in land, publish, checks, check-*, dashboard files, which E1
excluded; plus test_policy (one-signal-owner), test_credentials, test_access, test_activity_file, test_git_read_bound,
test_profile, test_prepare, test_environment have no E1 entry. Rough guess: under a third of the tests prove an E1 entry.

## 2. Simulation: "the repeat limit goes from 3 to 4"
Source facts: E1 `value/max-repeats` is 3, used by `step.repeats max:`, `attempt.number max:`, `rule/repeat-cap` and
`workflow/repeat.cap`, `constant/MAX_REPEATS`. Real code: `ATTEMPTS: Final = 3` (attempts of one step, "2 repeats").
Value edit:
```yaml
- {kind: value, id: max-repeats, is: 4, unit: count}      # was 3
```
`ogy work-left` under RECEIPTS (fingerprint = meaning + proof id + proof hash; deps hash):
```
changed       value/max-repeats            fingerprint differs; has no proof -> nothing to re-run, delivery commit only
re-verify via value/max-repeats:
              rule/repeat-cap              dep hash differs (guard `step.repeats < value/max-repeats`)
              workflow/repeat              dep hash differs (case `room`)
              entity/step                  attr repeats max:
              entity/attempt               attr number max:
              constant/MAX_REPEATS         binds value/max-repeats
unchanged     everything else (references are by target, so entry text of dependents does not change)
new           none
```
Tests that must rerun (proofs of the five re-verify entries):
- tests/steps/test_repeat.py::test_the_third_attempt_is_not_repeated (calls `renumber(registered, 3)`: **will fail, edit to 4**)
- tests/steps/test_repeat_dispatch.py::test_three_attempts_then_the_owner (3 attempts hardcoded: fails, edit)
- tests/steps/test_repeat.py::test_a_repeat_takes_the_reservation_over_and_freezes_the_previous_attempt (passes)
- tests/steps/test_attempt_store.py::test_stale_reservation_expired_or_missing_attempt_is_refused (cheap dep, passes)
- tests/steps/test_hold.py::test_a_hold_records_moves_the_labels_abandons_then_comments_once (reached via repeats_exhausted)
Not re-run: test_checks_round main_moved test (`max-rerun` is a separate value, still 3). Once the two tests are edited,
their content hash changes, so their own entries (repeat-cap, repeat) become "changed" too: edited proof => changed, not only
re-verify. The final work-left after the edit is therefore `changed` on the value + repeat-cap + workflow/repeat,
`re-verify` on step, attempt, MAX_REPEATS.
Delivery commit must touch: the value file (docs/kb/.../values), `src/taskloop/attempt_types.py:49` (ATTEMPTS = 4; and
its comment "2 repeats" -> 3), the two tests above, and the `built:` hashes the tool rewrites on the five entries
(the tool commits those, not the agent). Docs/glossary text "numbered 1 to 3" and CLI help strings that say three
(`three_attempts_then_the_owner`, the `repeats_exhausted` feedback) must be grepped; not found without reading bodies.

## 3. Where the receipts model was unclear or wrong
1. **One test proves many entries.** `test_three_attempts_then_the_owner` proves repeat-cap, max-repeats, repeat workflow,
   the exhausted end and the feedback text. `proof:` is a single test id per entry, and `built.deps` is per entry, so one
   edit to that test makes all of them "changed" at once. Needs `proof: [ids]` plus a per-entry assertion marker, else
   work-left over-reports. Conversely `test_attempt.py` has ~50 tests all weakly tied to attempt-run: which one is "the" proof?
2. **Entries with several proofs.** Every entity here (attempt: 8 transitions) needs a test per part; the spec gives parts
   an address (`<kind>/<id>.<part>`), but a transition is a part only under entity.lifecycle; attrs/limits are not parts.
   `ATTEMPTS` is declared in code and enforced by SQL CHECKs in two stores; no test says which.
3. **Tests with no entry (about two thirds).** Land, publish, dashboards, sandbox, credentials, policy AST tests have no
   E1 entry. RECEIPTS is "on every entry that has a proof": test -> entry is not reverse-checked, so orphan tests are
   invisible and stale tests never raise work. A lint "every test maps to an entry or is marked tool-only" is missing.
4. **Parametrized tests (320 uses).** A proof id is a function name, but `parametrize` yields N cases; whether the
   proof covers all cases or one is undefined, and the content hash of the function does not include the parameter
   table when it lives in a decorator/fixture. Hash must cover decorator + fixtures (conftest, `round_bench.py`, doubles).
   Shared benches like tests/steps/round_bench.py mean one edit invalidates most proofs; `covers:` is the only way out.
5. **Value without a proof.** `value/max-repeats` has no proof so it never gets a `built`; "changed" is then defined
   against what? Spec says built is written when a proof passes. Values need to be `changed` against the last delivery.
6. **"No literal numbers elsewhere" is false in tests.** Tests hardcode 3 (`renumber(.., 3)`, `[1, 2, 3]`). A value
   change then fails tests instead of flowing through the constant; tests need to import/read the value, or the
   receipts model must accept test edits as part of any value change (a cost the owner sees).
7. **Value meaning mismatch.** E1 says max-repeats is 3 "numbered 1 to 3" while `rule/repeat-cap` allows a repeat while
   `repeats < 3`, which yields 4 attempts; the code means 3 attempts total. Receipts did not catch it because the proof
   (`the_third_attempt_is_not_repeated`) is not a statement about the value, only about number 3.
8. **Absent-by-design entries.** `entity/step` has no table and no test: the model proves transitions that code never
   performs. A "derived entity" kind (no lifecycle, proved through its parts) would stop this gap from being a false positive.
