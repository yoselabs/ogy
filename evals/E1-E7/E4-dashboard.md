# E4: the read-only dashboard in spec-v3

Assumption: task, attempt, step, slot, hold and land facts are owned elsewhere (factory.db, tracker) and appear as `external/` facts.
## 1. Entries (YAML, compact)

```yaml
# --- business ---
persona/owner:      {nature: human}
persona/factory:    {nature: agent}            # rounds process; open: is it a persona or `system`?
goal/see-factory:   {states: [watching, acted]}  # open: a goal with no state change of its own
capability/watch-board: {does: "owner sees every task, where it is, what waits on them", serves: goal/see-factory}
term/board:   {means: "one card per task, one screen"}
term/quiet:   {means: "a running step with no agent line for a while"}
term/card:    {means: "the board's view of one task"}
set/column:   {members: [ready, plan, implement, checks, land, held, landed]}   # `waiting` shown as Ready: open (term/ready vs id)
set/land-status: {members: [waiting_for_you, delivering]}
value/quiet-amber:  {is: 2, unit: minutes}
value/quiet-red:    {is: 15, unit: minutes}
value/pause-shown:  {is: 2, unit: seconds}     # faint "paused" row; also "agent thought" threshold
external/factory-db: {owns_facts: [task, attempt, slot, hold, land-process], pin: schema-N}
external/tracker:    {owns_facts: [title, fields, comments, ready-tasks, questions], pin: bd-N, events: []}
external/evidence:   {owns_facts: [events.jsonl, rounds.log, check logs, answer.txt]}
entity/task:    # read-only mirror; open: whose entity? (defined by factory workflow, not here)
  attrs: {id: text, title: text, step: set/step, attempt: counter, slot: {type: set/slot, optional: true},
          hold_cause: {type: text, optional: true}, last_command_at: {type: time, optional: true}}
  lifecycle: {states: [ready, plan, implement, checks, land, held, landed], initial: ready, terminal: [landed]}
  # open: `held` is orthogonal to step (a held task still has a step); lifecycle can't say "step + held flag"
entity/card:    # a derived projection, not stored
  attrs: {id: text, column: set/column, try: counter, repeat: {type: text, optional: true},
          time_in_step: duration, quiet_for: {type: duration, optional: true}, land: {type: set/land-status, optional: true}}
derived/column:      {is: "if held then held else if landed then landed else if land-pending then land else step"}   # FEEL ok
derived/quiet-for:   {is: "now - last_command_at", scope: running steps}
derived/land-status: {is: "if land_process = running then delivering else waiting_for_you"}   # open: process liveness is not an entity state
# --- the workflow ---
workflow/watch-board:
  goal: goal/see-factory
  actors: [persona/owner]
  trigger: {actor: persona/owner}            # open: also "page already open and live"
  start: step/show-board
  ends: {closed: {result: success, means: "owner left the page"}}   # open: a view never ends; closing is not a goal outcome
  steps:
    show-board:   {actor: system, then: step/owner-looks}
    owner-looks:
      actor: persona/owner
      choices:
        switch:  {label: "Steps / By slot", then: step/show-board}
        open:    {label: "open a card", then: step/show-drawer, each: set/column}   # each is meant for sets, not for tasks: open
        logs:    {label: "Logs screen", then: step/show-logs}
        leave:   {label: "close", then: end/closed}
    refresh:   {actor: system, wait: {until: "any change"}, then: step/show-board}   # open: wait.until wants transition/, change comes from outside
rule/never-writes: {kind: holds, scope: {on: interface}, body: {statement: "no operation of a dashboard interface carries a causes"}}
rule/display-only: {kind: holds, scope: {on: entity, in: entity/card}, body: {statement: "no rule or guard reads a card or log row"}}
# --- technical ---
interface/dashboard-board: {form: screen, serves: [step/show-board], offers: [choice/switch, choice/open, choice/logs],
  says: {end/closed: "-"}, version: slice-1}   # `serves` a step of a workflow that exists only to host this screen
interface/api-board:  {form: api, serves: [step/show-board], request: "GET /api/board", response: {slots: list of set/slot, tasks: list of entity/card}}
interface/api-events: {form: api, serves: [step/show-board], response: "SSE: task|log"}   # open: stream is a push; spec has api = request/response only
operation/list-attempts: {performs: case/show-board.rows, uses: [external/factory-db]}   # shared with `tl step list`
# --- qualities ---
quality/never-stale-silently: {of: interface/dashboard-board, measure: "board shows notice when a tracker read failed", target: "open", under: "bd down"}
# --- receipts ---
interface/dashboard-board.proof: test/dash_board_columns   # built/covers written by the tool, not shown
derived/column.proof:            test/dash_board_column_table
```

Questions and held tasks (the part the owner reads most):

```yaml
entity/question: {attrs: {task: entity/task, text: text, asked_at: date, answer: {type: text, optional: true}},
  lifecycle: {states: [asked, answered], initial: asked, terminal: [answered]}}   # owned by tracker, read-only here
```

## 2. Edge cases exposed

1. Land has two truths: "waiting for you" is state, "delivering" is a live process observation. The spec has no
   `observed` fact kind; entity state vs process liveness has no home (derived with an external read).
2. `held` is a flag across steps, but entity.lifecycle is one state field. A held task has a step AND a hold.
3. Task with no attempt yet is a tracker-only fact (ready) merged with factory.db facts. One card, two owners, no merge rule.
4. Time since the agent's last command: needs `now` in an expression. Spec says the clock is never an actor, but does not
   say whether `now` is allowed in derived. FEEL has it; the tool has no clock port. open.
5. Start times are file mtimes, "approximate". A `derived` built on a non-exact source: no way to mark accuracy.
6. Tracker failure: the board keeps the last answer and sets `notice`. Stale-with-flag is an end state of a read, not an
   end of a workflow.
8. Count wording: "try" vs "attempt" (a repeat is a new try of the same step; checks tries number across the task):
   a counter per (task, step) vs per task. counter has no key scope.
9. A tail of 20 lines and a cursor: pagination state held by the client between requests; spec has no session state.
10. `replaced: true` cursor invalidation: the interface response has an in-band reset flag; no place for protocol semantics.

## 3. "Slippery slope" designs

A. **Pretend a workflow**: `watch-board` above, owner as actor, choices = screen controls, system step `show-board`. Everything
   type-checks, lint passes, reachability passes, and it says nothing. The spec's checks reward ritual: a loop step that
   returns to itself is "reachable and reaches an end" only because of the fake `leave` choice. Cost: every read-only screen
   gets a fake workflow; Quint translation then explores UI toggles. Verdict: reject unless the workflow is real.
B. **Interface with no `serves`**: allow `interface {serves: []}` plus `reads: [entity/]`. Less ritual, but then the lint
   "every step has an interface"-style check inverts to "every interface has a step" and must be waived. A new field and a
   new exemption; the spec grows `reads`, then `observes`, then `view`.
C. **A new kind `view` {reads, shows, refresh, for: persona}**: covers dashboard, report, CLI list. Honest, small. Slope:
   next come `view.filters`, `view.sort`, `view.layouts`, then it is a UI DSL. Cap: view has `shows: [derived/]`, `refresh: value/`,
   nothing else; layout/sort stay implementation.
D. **Everything as quality**: dashboard as a bundle of quality targets (freshness, drawer latency) on an unnamed screen. Gives
   receipts and targets, loses what it shows. Slope: qualities become the feature list.
E. **Query as a step with no actor effect** (system step, no causes, then: itself). Reuses the shape; every step then must
   assert "causes empty", i.e. a read-only flag per step, which rule/never-writes already says at interface scope. Prefer the rule.
F. **Persona goal without workflow**: `goal/see-factory` served by `capability/watch-board`, capability has `serves: goal/` but
   no step link, and `interface.serves` points at capability/ instead of step/. Smallest change (one more allowed target in
   `serves`); keeps lint "every capability has a proof". Best candidate.

## 4. Misfits

1. **No home for a read-only view that serves no workflow step.** `interface.serves:[step/]` forces step. The dashboard
   serves a goal (see-factory), not a step of a flow. Options A to F above; F or C is smallest. Highest-impact misfit.
2. **Derived facts built from observed state** (land process running, quiet for N minutes, idle between attempts): derived {is: expr}
   evaluates over entity states, not over process liveness, file mtimes or clocks.
3. **Foreign-owned entities.** The task, attempt, slot are owned by another workflow (factory) and another system (tracker).
   The spec has `external` for facts but not "an entity I read and never transition". Needs `entity {owner: external/}` or
   `readonly: true`, else a dashboard entry redeclares task and a second lifecycle drifts.
4. **Projection / card**: an entity that is a derived join of three sources has no kind. entity/card with derived attrs
   works only if attrs may be `derived`; spec has `derived` as standalone.
5. **Push channels** (SSE, 2 s poll): `interface.form: api` is request/response; "refresh" has no representation except an
   invented self-looping step with wait. Closest real fit: `{after: value/, since: transition/}` trigger on a system workflow,
   but nothing in the *view* transitions.
6. **Quality `under`** wants a condition; here "page connected, bd slow" are environment states without an owner.
7. **Questions on held tasks**: spec's `?open {question, asks: persona/}` is spec-level uncertainty. The dashboard shows
   product-level questions (a task's question for the owner). Same word, two meanings; `entity/question` collides with `?open`.
8. **Static front-end constants and cache TTLs** need `constant {binds, source}` for JS; "no literal numbers elsewhere" would
   bite every CSS/JS threshold (amber 2 min, red 15 min): honest, noisy.
9. **No UX words**: "calm", "newest first", "animates to place", "skeleton while loading" are the owner's decisions in
   layer decides, but the owner decided them).
10. **Persona nature `agent` for factory**: the rounds process is a program, not an agent; `system` actor exists but cannot
    be the owner of a goal.

## 5. Unused / over-engineered parts (for this exercise)

- `trigger` variants (schedule, event, after, called): the only trigger used is `{actor}`.
- `choices.each: set/`, `?conflict`, `?timeout` (a view has no timeouts; the only "timeout" is a cache TTL, not a step timeout).
- `rule.guard` and `rule.adds`: only `holds` was useful (never-writes).
- `effects` (`causes`): the screen has none by definition; the whole vocabulary exists to prove its absence.
- Layers (business/technical/implementation): a dashboard's decisions are almost all "owner decided UX" yet technical; the three-tier model
- `?open` worked well: used for the `held`-as-flag, the observed process and the push channel.
