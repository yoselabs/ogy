# E7 - E1 slot/reservation/attempt/hold translated to Quint (exercise, 2026-11-17)

`quint` is NOT installed (`which quint` empty), so nothing below was machine-checked. The spec is written as a
generator would emit it (only what E1 states); the counterexamples are traced by hand against that text.
Reading rule: where E1 is silent the generated action does nothing, and that silence is the finding.

## 1. Generated spec (one state record, one action per workflow row / transition, env actions at the end)
```quint
module factory {
  const TASKS: Set[str]   // Set("t1","t2")        generator: bounds are an input, not in YAML
  const SLOTS: Set[str]   // Set("s1")
  val ATT = 1.to(6)       // attempt id pool (entity attempt has no key generator)
  val MAXR = 3            // value/max-repeats
  val GUARD_TAG = false   // is tag `admits` on any step? E1: no step carries ?tags
  type S = { task: str -> str, held: bool, approved: str -> bool, hold: str -> str, repeats: str -> int,
    readmit: bool, aSt: int -> str, aTask: int -> str, aSlot: int -> str, procs: int -> int,
    pidRec: int -> bool, resv: Set[(int, str)], next: int, up: bool, due: Set[int] }
  var s: S
  def heldT(t) = s.hold.get(t) != "none" and s.hold.get(t) != "cleared"
  def holdOpen(t) = heldT(t)
  def liveExec(a) = Set("dispatching","registered").contains(s.aSt.get(a)) and s.pidRec.get(a) and s.procs.get(a) > 0
  def slotFree(sl) = not(s.resv.exists(r => r._2 == sl))        // derived/slot-free
  action init = s' = { task: TASKS.mapBy(_ => "ready"), held: false, approved: TASKS.mapBy(_ => true),
    hold: TASKS.mapBy(_ => "none"), repeats: TASKS.mapBy(_ => 0), readmit: false, aSt: ATT.mapBy(_ => "none"),
    aTask: ATT.mapBy(_ => ""), aSlot: ATT.mapBy(_ => ""), procs: ATT.mapBy(_ => 0), pidRec: ATT.mapBy(_ => false),
    resv: Set(), next: 1, up: true, due: Set() }
  // workflow/admit.claim: one row, effects_by [claim, create attempt, create reservation]
  action admit(t, sl) = all { s.up, s.next <= 6, s.task.get(t) == "ready", s.approved.get(t), slotFree(sl),
    GUARD_TAG implies not(holdOpen(t)),                          // rule/held-blocks-admission (scope: tag admits)
    s' = { ...s, task: s.task.set(t, "claimed"), aSt: s.aSt.set(s.next, "admitted"), aTask: s.aTask.set(s.next, t),
      aSlot: s.aSlot.set(s.next, sl), resv: s.resv.union(Set((s.next, sl))), next: s.next + 1,
      readmit: s.readmit or holdOpen(t) } }
  // attempt-run.dispatch (transition attempt.dispatch; guard rule/no-competitor-launch); spawn = tell agent-harness
  action dispatch(a) = all { s.up, s.aSt.get(a) == "admitted", not(liveExec(a)),
    s' = { ...s, aSt: s.aSt.set(a, "dispatching"), procs: s.procs.set(a, s.procs.get(a) + 1) } }
  action register(a) = all { s.up, s.aSt.get(a) == "dispatching",
    s' = { ...s, aSt: s.aSt.set(a, "registered"), pidRec: s.pidRec.set(a, true) } }
  action capture(a) = all { s.up, s.aSt.get(a) == "registered", s.procs.get(a) > 0,   // run.answer -> capture
    s' = { ...s, aSt: s.aSt.set(a, "captured"), procs: s.procs.set(a, 0) } }
  action reject(a) = all { s.up, s.aSt.get(a) == "captured", s' = { ...s, aSt: s.aSt.set(a, "rejected") } }  // verify.judge bad
  // workflow/repeat: cap -> take: {count step.repeats inc}, {create attempt}  (reservation: E1 says nothing)
  action repeatTake(a) = all { s.up, s.aSt.get(a) == "rejected", s.repeats.get(s.aTask.get(a)) < MAXR, s.next <= 6,
    s' = { ...s, repeats: s.repeats.set(s.aTask.get(a), s.repeats.get(s.aTask.get(a)) + 1),
      aSt: s.aSt.set(s.next, "admitted"), aTask: s.aTask.set(s.next, s.aTask.get(a)),
      aSlot: s.aSlot.set(s.next, s.aSlot.get(a)), next: s.next + 1 } }
  // repeat.cap otherwise -> workflow/hold-task, record: {create hold}, {write task.held true}
  action holdRecord(a) = all { s.up, s.aSt.get(a) == "rejected", s.repeats.get(s.aTask.get(a)) >= MAXR,
    s.hold.get(s.aTask.get(a)) == "none",
    s' = { ...s, hold: s.hold.set(s.aTask.get(a), "recorded") } }
  action releaseA(a) = all { Set("rejected","verified","interrupted").contains(s.aSt.get(a)),   // transition attempt.release
    s' = { ...s, aSt: s.aSt.set(a, "released"), resv: s.resv.exclude(Set((a, s.aSlot.get(a)))) } }
  action holdLabel(t) = all { s.hold.get(t) == "recorded", s' = { ...s, hold: s.hold.set(t, "labelled"), approved: s.approved.set(t, false) } }
  action holdComment(t) = all { s.hold.get(t) == "labelled", s.resv.forall(r => s.aTask.get(r._1) != t),  // wait until attempt.release
    s' = { ...s, hold: s.hold.set(t, "commented") } }
  action unhold(t) = all { s.hold.get(t) == "commented", s' = { ...s, hold: s.hold.set(t, "cleared") } }  // tracker.answered
  // ---- environment (nothing in YAML states these; derived from external.events / owns_facts / terms) ----
  action crash = all { s.up, s' = { ...s, up: false } }                         // M4: factory is not an actor
  action restart = all { not(s.up), s' = { ...s, up: true,
    due: ATT.filter(a => Set("admitted","dispatching","registered","captured").contains(s.aSt.get(a))) } }
  action relaunch(a) = all { s.up, s.due.contains(a), not(liveExec(a)),         // resume.reconcile case gone -> end/relaunch
    s' = { ...s, due: s.due.exclude(a), aSt: s.aSt.set(a, "dispatching"), pidRec: s.pidRec.set(a, false),
      procs: s.procs.set(a, s.procs.get(a) + 1) } }                             // "same attempt id": E1 never says a 2nd process
  action kept(a) = all { s.up, s.due.contains(a), liveExec(a), s' = { ...s, due: s.due.exclude(a) } }
  action agentDies(a) = all { s.procs.get(a) > 0, s' = { ...s, procs: s.procs.set(a, s.procs.get(a) - 1) } }
  action claimLapse(t) = all { s.task.get(t) == "claimed", s' = { ...s, task: s.task.set(t, "ready") } }  // tracker owns claim
  action step = any {
    nondet t = TASKS.oneOf()
    nondet sl = SLOTS.oneOf()
    nondet a = ATT.oneOf()
    any { admit(t, sl), dispatch(a), register(a), capture(a), reject(a), repeatTake(a), holdRecord(a), releaseA(a),
      holdLabel(t), holdComment(t), unhold(t), crash, restart, relaunch(a), kept(a), agentDies(a), claimLapse(t) } }
  val inv1 = SLOTS.forall(sl => ATT.filter(a => s.aSlot.get(a) == sl).fold(0, (n, a) => n + s.procs.get(a)) <= 1)
  val inv2 = not(s.readmit)
}
```
Run (intended): `quint run --invariant=inv1 factory.qnt`, same for inv2; `quint verify` for bounded proof.

## 2. Counterexamples (hand-derived; ids are E1 entries)
- **CE1, inv1 (two live executions on one slot).** admit.claim(t1,s1) -> attempt-run.dispatch (spawns process,
  `pid_identity` not yet stored) -> factory crash -> factory restart -> resume.reconcile: `live-execution` is false
  because it requires the recorded `pid_identity`, case `gone` -> end/relaunch spawns a second process for the same
  attempt. Guard `no-competitor-launch` is scoped to transition `attempt.dispatch`; relaunch is a workflow end, never
  that transition, so the guard never fires. (E1 edge 3 predicted the unknown; the model turns it into a trace.)
- **CE2, inv1 (slot reused under a running attempt).** admit.claim(t1,s1) -> ... -> verify.judge `bad` ->
  repeat.take (new attempt a2 on s1, repeats=1; E1's causes are `count inc` + `create attempt`, no reservation row) ->
  dispatch(a2) -> release(a1) deletes the only reservation -> round.admit_new -> admit.claim(t2,s1): `slot-free` is
  true -> t2's attempt runs while a2 runs. Needs 2 tasks; 9 steps. `repeat` text says "takes over the reservation" but
  no effect does it.
- **CE3, inv2 (held task re-admitted), with `admits` tag absent as in E1.** t1: four attempts, each admit.claim ->
  dispatch -> register -> capture -> verify.judge `bad` -> repeat.take; at repeat.cap `otherwise` -> hold-task.record
  (hold=recorded, held=true); factory crashes before hold-task.label (approval label still on); tracker claim lapses
  (env, E1 edge 4) -> task ready; release(a4); round.admit_new -> admit.claim(t1) fires with the hold open.
  `held-blocks-admission` is scoped `{on: step, tag: admits}` and no step has `?tags: [admits]`, so it constrains
  nothing; a generator with a "scope matches at least one row" lint finds this without Quint. With
  `GUARD_TAG = true` inv2 held in my reading (guard reads the DB flag; hold.clear and held=false are one atomic row).
  Even then E1 has no write that moves the task back to `ready` after a hold: hold-task.abandon has no `causes`,
  and unhold only clears the hold, so after the owner answers the task stays `claimed` (a deadlock Quint reports
  as a stuck state, not an invariant violation).
- Also noticed, not an invariant of the two asked: nothing forbids a second attempt for the same task on slot s2
  after claim lapse (admit has no "task has no non-terminal attempt" guard) -> double run per task (E1 edge 4/9).

## 3. YAML -> Quint mapping
| YAML | Quint | status |
|---|---|---|
| entity.attrs scalar type, `counter` | record field / int; `max:` -> guard on increment | enough |
| entity.lifecycle.transitions {from,to} | action guard `st == from`, update `st' = to` | enough |
| entity `key` | map domain; id pool bounded by a constant | bounds MISSING |
| entity `initial` | init record | enough; initial world variants (M5) MISSING |
| set / value | `val` constants, set members | enough |
| workflow trigger {event: transition/..} | the action is enabled when that transition just happened | needs "just happened" = a step-ordering rule; MISSING |
| step cases {order, when} + otherwise | `any` with when and `not(earlier whens)` conjuncts | enough |
| `causes` transition/write/count/create | record updates | `create`: key assignment and the mapped fields MISSING (new attempt's slot, reservation) |
| `causes` delete / remove a row | none (reservation delete is called an "effect" in E1) | `{delete: entity}` MISSING |
| `tell: external/..., what: text` | nothing computable | effect on facts of the external MISSING |
| `rule guard` | conjunct on matched rows | scope by tag/transition must be resolved; empty scope MISSING as lint |
| `rule holds` + `check` | `val inv` | enough; no-check holds (one-execution-per-attempt) unusable |
| `derived` | `def` | enough (FEEL subset maps to Quint) |
| `?timeout`, `?wait`, `after/since` | env action `tick`/deadline; urgency | durations MISSING as model time; no urgency semantics |
| external `events` | env action that sets facts | which facts it changes: MISSING |
| external `owns_facts` | state var + env writes | only names, no types/values |
| crash/restart, process death, lease lapse | env actions | no field at all: MISSING |
| `for_each` | nondet pick (loses sequential/atomic reading) | order/atomicity MISSING (M7) |
| `conflict.then` | disabled action or branch | no environment contention model |

## 4. Verdict
Realistic for a bounded slice, not as a lights-out generator. The mechanical part (lifecycles, ordered case tables,
guards, counters, derived facts, holds with a check) is a straightforward ~1:1 template; I wrote it in an hour and
every action has a YAML row behind it. What the generator cannot invent is the other half of the model: environment
actions (crash, claim lapse, process death), the effect of `tell external`, row creation/deletion with field
bindings, bounds, and what a trigger event means in time. Without those, the checker explores only the happy
admission path, and the invariants hold vacuously, as CE1-CE3 show: all three came from places where the YAML
was silent, not from clever search. Cheap rewarding middle path: make the generator emit Quint plus a coverage
lint ("rule scope matches no row", "attempt created, no reservation effect", "external event with no declared fact
change") and add an explicit `environment:` block; the lint alone catches CE3's cause and CE2's cause today.
Counterexample-to-entry mapping is easy (each action names its YAML id). Cost grows with timers (E1 section 3) and with
Quint itself (state space explodes beyond ~2 tasks x 6 attempts; verify needs bounds).

## 5. Fields the spec lacks, for the generator
1. `environment:` actions (id, guard, changes) per external/system: crash, restart, claim lapse, process death, clock tick.
2. `external.facts: {name: type}` and per event `sets: {fact: value}` instead of free-text `tell what`.
3. `causes: {delete: entity}` and `create` with field bindings (`with: {slot: from step.slot}`), plus "reservation transfer".
4. `bounds:` per entity/set for model checking; `initial:` world variants.
5. Trigger ordering semantics (event consumed once? queued?) and `for_each` mode (sequential, atomic or concurrent).
6. A `lint` rule: every rule scope matches at least one row; every `holds` has a `check` or is marked prose-only.
