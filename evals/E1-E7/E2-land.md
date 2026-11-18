# E2: LAND in ontology spec v3
Sources: spec-v3, land*.py docstrings, glossary. O = origin main tip, X = checked branch tip, S = squash of X onto O.

## 1. Entries
```yaml
- {id: persona/person, nature: human}             # only trigger; rounds never land
- {id: goal/delivered, states: [work on target, task closed]}
- {id: term/land, means: "squash checked X onto target as S, validate if needed, push S never forced, close task"}
- {id: value/max-again, is: 1, unit: count}       # one new candidate per invocation after main moves
- {id: value/validation-minutes, is: 30, unit: minutes}
  ?open: {question: "default validation deadline", assumed: 30, asks: persona/person}   # source: --minutes, no default
- {id: set/validation-kind, members: [same_tree, no_change, passed, failed]}
- {id: set/super-reason, members: [moved, withdrawn, gone, abandoned]}
- id: entity/land-candidate                       # one S for one checks attempt
  attrs: {task: {type: text}, x: {type: text}, o: {type: text}, s: {type: text}, remote_head: {type: text, optional: true},
          validation: {type: set/validation-kind}, super_reason: {type: set/super-reason, optional: true},
          closed_how: {type: text, optional: true}}
  key: [task, x, o]
  lifecycle:
    states: [pending, pushable, delivered, closed, superseded, failed]
    initial: pending            # misfit: really pending | pushable (same_tree) | delivered (no_change at insert)
    terminal: [closed, superseded]   # failed: open, source lets a rerun make a new candidate
    transitions:
      validate_pass: {from: pending, to: pushable}
      validate_fail: {from: pending, to: failed}
      push_ok:       {from: pushable, to: delivered}
      found_on_origin: {from: pushable, to: delivered}     # R is S, or S in fetched tip
      close_task:    {from: delivered, to: closed}
      supersede:     {from: [pending, pushable, failed], to: superseded}   # pending only by abandon; pushable by moved/withdrawn/gone
- {id: entity/land-run, attrs: {again: {type: counter}}}   # invented only for the per-invocation counter
- {id: derived/needs-validation, is: "s_tree != x_tree or required_at_o != required_at_checks"}
- {id: external/git-origin, owns_facts: [main tip R, objects, fast-forward rule], pin: "person's Git config, trusted as configured",
   events: [main_moved, push_race_lost, push_policy_refused, unreachable, s_pruned]}
- {id: external/tracker, owns_facts: [task status, assignee, children, blockers], pin: "bd, as actor taskloop",
   events: [closed_by_person, claim_lost, blocked, unavailable, task_deleted]}
- {id: external/factory-db, owns_facts: [candidate rows, slot reservation, checks attempts], events: [fault]}
- {id: interface/tl-step-land, form: command, serves: [step/preflight], version: 1,
   says: {end/landed: "closed locally, not synced", end/unavailable: "a rerun is safe"}}   # flags withdraw/summary: no choices to offer
- {id: operation/land, performs: workflow/land, uses: [external/git-origin, external/tracker, external/factory-db]}
- {id: rule/never-force, kind: holds, scope: {on: step, tag: pushes}, body: {statement: "push is never forced"}}   # untestable
- {id: rule/push-before-close, kind: guard, scope: {on: step, tag: closes}, body: {when: "{state/land-candidate} = delivered", else: end/refused}}
- {id: rule/delivery-by-reading, kind: holds, scope: {on: transition, in: entity/land-candidate},
   body: {statement: "delivered only from a Pushed answer or origin read live, never a log or stale ref"}}
- {id: rule/one-new-candidate, kind: guard, scope: {on: step, tag: again}, body: {when: "land-run.again <= value/max-again", else: end/target_moved}}
- id: workflow/land
  goal: goal/delivered
  actors: [persona/person, external/git-origin, external/tracker, system]
  trigger: {actor: persona/person}
  inputs: {task: text, accept_gate: bool, no_change: bool, minutes: duration}
  start: step/preflight
  ends:
    landed:         {result: success, means: "S (or no-change) on origin main and task closed", gives: "closed locally, not synced"}
    already_landed: {result: success, means: "closed before this call; nothing called"}
    refused:        {result: failure, means: "word: not_done not_checked branch_moved commit_missing no_remote target target_profile no_required conflict gate_changed claim_lost closed blocked landing remote_rejected"}
    unavailable:    {result: failure, means: "tracker|git|slot_busy|store|interrupted; rerun safe; earlier effects remain"}
    target_moved:   {result: failure, means: "main moved twice in one invocation"}
  steps:
    preflight:      # ~12 ordered reads, all before any effect
      actor: system
      cases:
        closed: {order: 1, when: "{state/land-candidate} = closed", then: end/already_landed}
        notdone: {order: 2, when: "current attempt not a done implement, or checks not passed+released", then: end/refused}  # text fallback
        branch: {order: 3, when: "task/<id> local, tracking or origin != X and not no_change", then: end/refused}
        deliv:  {order: 4, when: "{state/land-candidate} = delivered", then: step/close}
        pend:   {order: 5, when: "{state/land-candidate} = pending", then: step/validate}
      otherwise: step/read-tracker
    read-tracker:   # reply is an event of external/tracker (request step elided)
      actor: external/tracker
      choices: {open_mine: {label: open and ours, then: step/fetch}, closed: {label: closed, then: end/refused},
                claim_lost: {label: other actor, then: end/refused}, unavailable: {label: down, then: end/unavailable}}
    fetch:
      actor: system
      ?timeout: {after: value/fetch-timeout, then: end/unavailable}    # value not stated in sources: open
      causes: [{write: land-candidate.o, from: "fetched R"}]
      then: step/squash
    squash:
      actor: system
      cases:
        conflict: {order: 1, when: "squash of X onto O conflicts", then: end/refused}
        gate:     {order: 2, when: "gate facts not empty and not accept_gate", then: end/refused}
        same_o:   {order: 3, when: "s_tree = o_tree and not no_change", then: end/refused}    # source: delivered as no_change disposition: open
      otherwise: step/insert
    insert:         # one transaction with slot reservation (second store)
      actor: system
      cases:
        fast:  {order: 1, when: "not {derived/needs-validation}", then: step/deliver, causes: [{create: entity/land-candidate}, {transition: land-candidate.validate_pass}]}
        lost:  {order: 2, when: "another land won the fence", then: end/refused}
      otherwise: step/validate
    validate:
      calls: workflow/checks-block       # shared with check step; not defined here
      with: {at: S, minutes: minutes}
      ?timeout: {after: value/validation-minutes, then: end/unavailable}
      cases: {passed: {then: step/deliver}, failed: {then: end/refused}}
      otherwise: end/unavailable
    deliver:
      actor: system
      tags: [pushes]
      cases:
        is_s: {order: 1, when: "R = S", then: step/close, causes: [{transition: land-candidate.found_on_origin}]}
        is_o: {order: 2, when: "R = O", then: step/push-reply}
      otherwise: step/refetch
    push-reply:
      actor: external/git-origin
      choices: {pushed: {label: accepted, then: step/close, causes: [{transition: land-candidate.push_ok}]},
                race: {label: rejected, main moved, then: step/refetch}, policy: {label: rejected, main unchanged, then: end/refused},
                unreachable: {label: unavailable, then: end/unavailable}}
    refetch:
      actor: system
      tags: [again]
      causes: [{count: land-run.again, op: inc}]
      cases:
        in_tip: {order: 1, when: "S ancestor of fetched F", then: step/close, causes: [{transition: land-candidate.found_on_origin}]}
        again:  {order: 2, when: "otherwise a new S is possible", then: step/squash, causes: [{transition: land-candidate.supersede}]}  # reason moved: not settable here
      otherwise: end/target_moved
    close:
      actor: system
      tags: [closes]
      then: step/close-reply
    close-reply:
      actor: external/tracker
      choices: {closed: {label: ok, then: end/landed, causes: [{transition: land-candidate.close_task}, {write: land-candidate.closed_how}]},
                found_closed: {label: already closed, then: end/landed, causes: [{transition: land-candidate.close_task}]},
                claim_lost: {label: held by another, then: end/refused}, blocked: {label: open children, then: end/refused},
                unavailable: {label: down, then: end/unavailable}}
```

## 2. Edge cases exposed
1. **Pushed, not closed**: crash between push-reply.pushed and close-reply. Candidate stays `delivered`; rerun hits preflight `deliv`
   and goes straight to close. Recovery works only because the lifecycle state is the resume point.
2. **Closed in tracker, record write lost**: state `delivered`, tracker closed. Rerun reads tracker -> found_closed -> `closed`. Two stores, no atomicity.
3. **Pushed, answer lost, not recorded**: rerun finds R = S -> found_on_origin. Two transitions to `delivered` for one meaning.
4. **Push rejected because our other land won**: reread by same rule, S in F -> delivered. A rejection must route to a read, not to an end.
5. **Main moved during validation**: pushable candidate superseded `moved`; at most one new candidate; second time `target_moved`. Counter per invocation.
6. **Moved main now already holds X**: new S equals O -> `no_change`, delivered at insert, no push, then close.
7. **Branch diverged** (local, tracking or origin task/<id> != X): refused `branch_moved`; `--no-change` skips this check (flag disables a precondition).
8. **Merge conflict**: refused `conflict` naming first paths (output text, not an end value).
9. **Gate change** (checks, setup, required names, config files, weakened tests): refused until `--accept-gate-changes`; same person triggers and approves.
10. **Required names differ at O**: validate even if tree is X's (derived from two sources).
11. **Concurrent land of same task / slot busy**: `landing` / `unavailable slot_busy`.
12. **Task deleted mid-land / S pruned (`gone`)**: source silent or unlikely: `?open`.
13. **Close refused (claim_lost)**: task stays open, person closes by hand (`bd close --force`), rerun records `already_closed`. A human act on an external changes the path.
14. **Abandon while landing**: refused `landing`/`landed`; needs `--withdraw` first. A rule on another workflow keyed on candidate state.
15. **Ctrl-C in validation**: `unavailable:interrupted`, exit 130; next run's reconcile marks the check `interrupted`.
16. **Tracker not synced**: close is local; `bd dolt push` is the person's chore. "Closed in tracker" has two meanings.

## 3. Slippery slope
- **Request/reply pairs.** Every external call is a system step plus an external-actor step with choices. Four external calls give ~12 steps before any failure branching.
- **States by reason.** `superseded` has 4 reasons, `delivered` 3 entries: flat states push toward `superseded_moved`.
- **Preflight is a priority table of ~12 refusals.** `order` carries what source says in prose ("every read before any effect"); lint checks overlap only.
- **Resume by state.** Each new lifecycle state adds a case in preflight. Idempotence ("a rerun does only what is missing") is a whole-workflow property nothing checks.
- **Quint**: nondeterministic externals (5 git x 5 tracker events x crash anywhere) explode unless events are scoped to steps; not expressible.

## 4. Misfits
1. **Crash or interrupt between two effects** (the central failure). Neither the clock nor the process is an actor; there is no "process dies after step X" event. Used: rerun as new instance keyed on state. Exploration will not inject it.
2. **Facts read from externals as step results** (R, O, F, tree listings). `owns_facts` is names only; no way to store an answer and compare it later. Used raw text in `when` (untracked fallback).
3. **"Never forced", "never claims/unclaims/syncs"**: negatives over an external's operations. `holds` without `check` is untestable; `value` cannot hold `never`. Needs a `forbids`.
4. **Two stores, one transition**: tracker close + row record + recovery. `causes` are atomic per row only.
5. **Refusal families** (~25 words under `refused`): one end per name, one result. Callers cannot branch on the word; used prose in `means`.
6. **Initial state is one**; a candidate starts pending, pushable or delivered.
7. **Setting an attr during a transition** (super_reason) needs a separate `{write}` effect; the supersede case has no way to say which reason.
8. **Set with runtime members** (required checks from `.task-loop.json` at O) is repo data, not KB.
9. **Per-invocation counter** forced an invented `land-run` entity; shared validation's slot custody is invisible to `calls`.
10. **Timeouts per external call** (fetch, push) are not per step; `?timeout` re-arms per step entry. Source gives no number for them: `?open`.

## 5. Unused / over-engineered
- Unused: `capability`, `quality`, `dependency`, `schedule`/`after`/`event` triggers (land is manual; rounds only report `Next: land`), `?each`, `?for_each`, `adds` rules, `{add|remove|clear}` effects, `built`/`covers`/receipts, `layers` (sources do not split owner vs agent decisions), `?conflict`, `?wait`, `{tell:}` (the answer text "not synced" is interface.says).
- Fit well: externals as actors with choices (git race, tracker refusal), `?open`+`assumed`, lifecycle with from-lists, `calls` for shared validation, `guard` for push-before-close, `{state/..}` in cases for resume.
- Over-engineered here: FEEL (nothing numeric but one counter), `value/` indirection for `1`, `constant` + `value` + `interface.says` repeating `ends`, `derived` for one use.
