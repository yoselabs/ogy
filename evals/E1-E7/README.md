# Exercises E1-E7: task-loop described in spec v3 (2026-11-17)

Sonnet runs, everything on ([spec-v3](../../docs/consults/spec-v3.md)). Full outputs: [E1 core](E1-core.md), [E2 land](E2-land.md),
[E3 profile](E3-profile.md), [E4 dashboard](E4-dashboard.md), [E5 tests](E5-tests.md), [E6 A/B](E6-ab.md),
[E7 Quint](E7-quint.md).

## What pulled weight
Entity with lifecycle (`from` lists show exitless states), guards, values, externals as actors with events, `open` with
`assumed`, `{state/...}` in cases (resume points), `calls` for shared validation, ordered case tables.

## Rarely or never used (cut candidates once confirmed)
`tags` and `adds` (one audit use), `each`/`for_each`, `wait`, `conflict`, schedule/after/event triggers outside E4,
add/remove/clear effects, `quality` (one entry each in E1, E4), layer ceremony. Receipts and `covers` only in E5.

## Missing, found by several exercises
1. **Environment** (E1, E2, E4, E7): crash, restart, process liveness, lease lapse, the clock; unknown results.
   Proposed: an `environment:` block of nondeterministic events; observations as facts with "unknown".
2. **Split ownership across stores** (E1, E2): task state in the tracker and in factory.db; two stores in one
   transition; facts read from an external and compared later.
3. **Facts at a ref** (E3): the profile read from the target branch; "a fact as of commit R".
4. **Views with no step** (E4): `interface.serves` should accept capability or goal.
5. **Strings and paths** (E3): globs and templates outside the FEEL subset.
6. **Effects** (E7): `create`/`delete` with field bindings, reservation transfer, `for_each` mode.
7. **Tests** (E5): one test proves many entries; parametrized tests; tests hardcode numbers; orphan tests invisible;
   a value with no proof has no baseline.
8. **Lints** (E6a, E7): values used by no rule; rule scopes matching no row; states with no exit; off-by-one between a
   value and its use.

## Factory edge cases worth checking against the code (candidates, not verified)
- Relaunch before the process id is recorded can start a second process on the slot (E7 CE1, E6a 9).
- Repeat hands the reservation over; another admission can take the slot in between (E7 CE2, E6a 7).
- A held task re-admitted after a crash before the hold label plus a claim lapse (E7 CE3).
- Crash between push and close; who retries (E2, E6b 5). Claim lease lapsing while a task waits at `Next: land` (E6b 1).
- A task branch keeping a required check's name with argv `true` (E3) — land may already refuse a changed gate.
- Repeat cap: entry says 3 repeats, code means 3 attempts (E5, E6a 6).

## Verdicts
- Ontology vs prose (E6): the ontology reader saw structural gaps fast; the prose reader saw operational facts the
  capture dropped. Complementary: capture must keep operational facts, lints catch structure.
- Quint (E7): realistic for a bounded slice; lifecycles, cases, guards, counters map 1:1; the environment must be
  explicit or the checker explores only the happy path. All three counterexamples came from facts the YAML was silent on.
- Tests (E5): 36 of 42 core entries have a real test; two-thirds of the repo's tests match no core entry (other areas).

## Verification against `origin/main` (2026-11-17)

| Candidate | Verdict | Evidence |
|---|---|---|
| Relaunch before the process id is recorded | guarded | recovery refuses an unregistered worker (`recovery/recover.py:167-171`); the entry holds the slot's kernel lock for its whole life (`slot_lock.py:1-54`); test `test_recovery_reconcile.py:66` |
| Reservation hand-over race on repeat | guarded | insert and `transfer` in one transaction, fenced on the predecessor (`admit_chain.py:112-151`, `admit_store.py:116-124`); test `test_admit_store.py:96,125` |
| Held task re-admitted after a crash | guarded | hold row first, label redone on resume, abandon only after the label (`hold.py:104-122`); admission refuses (`admit_store.py:106-113`); residual: a claim lapsed to someone else is the designed `not_ours` path |
| Crash between push and close | guarded | rerun of land goes straight to close (`land.py:192-202, 323-330`) |
| Claim lease lapses while a checked task waits for land | **real, by design** | nothing renews the claim between steps, TTL 300 s (`claim_lease.py:3,21`); land then refuses `claim_lost` and asks for a manual close (`land.py:204-206`, `land_close.py:63`) |
| Required check renamed to argv `true` | guarded | `gate_changed` refused unless `--accept-gate-changes` (`land_target.py:77-82`, `land_gate.py:135-155`) |
| Repeat limit off by one | guarded | `ATTEMPTS = 3` attempts in total, 2 repeats (`attempt_types.py:55`, `admit_chain.py:127`) |

Lesson: five of six were false alarms because the capture (from docs) dropped guarantees that live only in code:
single-transaction transfers, kernel slot locks, registration callbacks, gate digests. Exploration is only as good as
the capture; capture must read code-level guarantees (or proofs must be attached) before a checker's counterexample
counts. The one real gap is a known design choice with a manual exit.
