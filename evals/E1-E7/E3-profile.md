# E3: repository profile and per-step settings in ontology spec v3

Sources: spec-v3, `.task-loop.json`, profile.py docstrings, plan-format sections 1-2. Facts: profile keys are `setup`,
`checks`, `required`, `target`; commands from the commit under test, `required`+`target` from the target ref. Proposed
(F1, F2, F8): `steps.<step>` block. Land mode: not in profile.py; place is `open`.

## 1. Entries (YAML, compact)
```yaml
persona/owner: {nature: human}          # layer business
persona/agent: {nature: agent}          # implementing agent; NOT the same as agent-choice below (name clash, see 4)
external/git: {owns_facts: [profile at a commit, target ref tip], pin: none, events: [landed]}
term/profile: {means: "the file .task-loop.json as read from Git at one commit"}
term/gate: {means: "the checks a commit must pass before land", replaces: "required"}
term/land-mode-wait: {means: "the task stops before land until the owner lands it"}
set/land-mode: {members: {auto: {owner_waits: false}, wait: {owner_waits: true}}}   # ?open where it is stored
set/step-name: {members: [plan, implement, land]}                 # ?open full list
set/harness: {members: [?open]}
set/placeholder: {members: [task_id, task_key, plan_path, produces, previous_produces, check_commands, setup_commands]}
value/target-branch: {is: main, unit: branch}                     # owner decides; text, but value kind is number|duration|date|time
value/check-timeout: {is: 1800, unit: seconds}
value/profile-max-bytes: {is: 65536, unit: bytes}                 # owner? probably implementation-layer; open
value/max-checks: {is: 32, unit: count}
value/hold-exit-code: {is: ?open, unit: exit code}               # F8, number not chosen anywhere
entity/command: {attrs: {argv: {type: "list of text"}}}
entity/check: {key: [name], attrs: {name: {type: text}, argv: {type: "list of text"}, timeout: {type: duration}}}
entity/agent-choice: {attrs: {harness: {type: set/harness}, model: {type: text}, effort: {type: text, optional: true}}}
entity/step-settings:
  key: [step]
  attrs: {step: {type: set/step-name}, prompt: {type: text, optional: true}, agent: {type: entity/agent-choice, optional: true},
          produces: {type: text, optional: true}, excluded: {type: "list of text"}, checks: {type: "list of entity/check"},
          hold_exit_code: {type: number, optional: true}}
entity/profile:                          # one row per commit; the "commit" is the row's identity
  key: [commit]
  attrs: {commit: {type: text}, setup: {type: "list of entity/command"}, checks: {type: "list of entity/check"},
          required: {type: "list of text"}, target: {type: text}, steps: {type: "list of entity/step-settings"},
          land_mode: {type: set/land-mode, optional: true}}      # ?open land_mode may not be profile
  lifecycle: {states: [absent, proposed, refused, in-force, superseded], initial: absent, terminal: [superseded],
              transitions: {propose: {from: absent, to: proposed}, refuse: {from: proposed, to: refused},
                            land: {from: proposed, to: in-force}, replace: {from: in-force, to: superseded}}}
entity/resolved-profile: {attrs: {setup: "list of entity/command", checks: "list of entity/check", required: "list of text",
                                   target: text, template_hash: text}}       # what one step attempt uses
entity/check-result: {attrs: {check: {type: text}, rc: {type: number}, verdict: {type: set/verdict}}}   # rc is stored (probe P10)
set/verdict: {members: [pass, fail, hold]}
derived/gate-met: {is: "every(required, r -> exists(check-result[check = r and rc = 0]))"}   # FEEL gap, see 4
constant/profile-file: {binds: value/target-branch, source: ".task-loop.json#target"}       # also per other values
constant/check-timeout-file: {binds: value/check-timeout, source: ".task-loop.json#checks[].timeout"}
rule/gate-from-target: {kind: holds, scope: {on: entity, in: entity/resolved-profile},
  statement: "required and target equal the profile at the target ref, never the commit under test",
  check: "resolved.required = profile[commit = tip(target)].required"}
rule/profile-change-waits: {kind: guard, scope: {on: workflow, in: workflow/land-task},
  when: "changed-paths contains '.task-loop.json'", else: step/wait-for-owner}     # changed-paths: no such fact kind
rule/only-owner-edits-gate: {kind: holds, scope: {on: transition, in: entity/profile.land},
  statement: "land of a profile whose required or target differs from the target ref needs persona/owner", ?by: persona/owner}
rule/unknown-key-refused: {kind: holds, scope: {on: entity, in: entity/profile}, statement: "unknown keys, duplicate names, oversize refused"}
rule/placeholder-closed: {kind: holds, scope: {on: entity, in: entity/step-settings.prompt},
  statement: "a template uses only set/placeholder members"}                      # text with {references}, tracked not evaluated
workflow/resolve-profile:
  goal: goal/gate-is-not-weakenable
  actors: [system, external/git]
  trigger: {called}
  inputs: {commit: text, target_ref: text}
  start: read-commit
  ends: {resolved: {result: success, gives: entity/resolved-profile}, refused: {result: failure, means: "reason word + key path + side"},
         unavailable: {result: failure, means: "Git unreadable; read again is safe"}}   # no_commit, not_a_file: more ends? open
  steps:
    read-commit: {actor: system, cases: {unreadable: {order: 1, when: "git.unavailable", then: end/unavailable},
                  invalid: {order: 2, when: "not valid(profile[commit])", then: end/refused}}, otherwise: step/read-target}
    read-target: {actor: system, cases: {unreadable: {order: 1, when: "git.unavailable", then: end/unavailable},
                  invalid: {order: 2, when: "not valid(profile[target])", then: end/refused}, absent: {order: 3, when: "profile[target] = null", then: step/defaults}}, otherwise: step/merge}
    defaults: {actor: system, then: step/merge, ?causes: {write: entity/resolved-profile.setup, ?from: "[[just, install]]"}}   # defaults for absent keys
    merge: {actor: system, then: end/resolved, ?causes: {write: entity/resolved-profile.required, ?from: "profile[target].required"}}
workflow/change-profile:                 # how any profile value changes
  goal: goal/owner-controls-gate
  actors: [persona/agent, persona/owner, external/git]
  trigger: {actor: persona/agent}
  steps:
    edit: {actor: persona/agent, choices: {commands: {label: "change setup/checks/steps in task branch", then: step/gate-run},
           gate: {label: "change required/target", then: step/ask-owner}}}
    ask-owner: {actor: persona/owner, choices: {approve: {label: "land it", then: step/gate-run}, no: {label: "refuse", then: end/dropped}},
                ?timeout: {after: value/owner-wait, then: end/dropped}}            # value/owner-wait not defined: open
    gate-run: {actor: system, calls: workflow/run-step-checks, then: ...}
workflow/run-step-checks:
  goal: goal/step-output-checked
  trigger: {called}
  steps:
    run: {actor: system, ?timeout: {after: value/check-timeout, then: step/rework},
          cases: {hold: {order: 1, when: "check-result.rc = value/hold-exit-code", then: end/held},
                  ok: {order: 2, when: "check-result.rc = 0", then: end/passed}}, otherwise: step/rework}
  ends: {passed: {result: success}, held: {result: failure, means: "task is held, not retried"}, reworked: {result: failure}}
interface/tl-profile: {form: command, serves: [step/read-commit], says: {end/refused: "profile refused: <reason> at <key> (<side>)"}, version: 1}   # tl profile show/check: open, not in CLAUDE.md
interface/step-override: {form: command, serves: [workflow/run-step], ?offers: [choice/agent], says: {harness_mismatch: refused}, version: 1}   # --agent flag
interface/profile-file: {form: api, serves: [step/read-commit], ?request: ".task-loop.json", version: 1}  # form fits badly, see 4
quality/gate-time: {of: workflow/run-step-checks, measure: seconds, target: value/check-timeout, under: "one check"}
rule/template-in-fingerprint: {kind: adds, scope: {on: step, in: workflow/run-step}, causes: {write: entity/resolved-profile.template_hash}}
```
Receipts: `proof` on each rule/workflow above is a test id (one test per refusal reason word). `built.deps` of a step
takes the template blob hash, so a changed template shows as "dependency hash differs: re-verify". `covers` ranks profile.py.

## 2. Edge cases exposed
1. Gate weakening is only half closed: `required` names come from target, but check `argv` come from the commit. A task can
   keep name `test` and set argv `["true"]`. Owner approval (rule/profile-change-waits) is the only guard. Open: pin commands too.
2. Bootstrap circle: `target` is read from the target ref, but which ref is read first to learn the target? `open`.
3. `required` names a check missing from the commit's `checks` (deleted or renamed): refuse or count as fail? open.
4. Adding a new required check and the check itself in one task: it cannot be required until landed, so two lands.
5. Land mode auto plus a task that edits `.task-loop.json`: forced wait (guard) vs trusting target-read. Guard needs
   "changed paths", which has no fact kind.
6. Per-step `checks` and hold exit code: same code in a required check and a per-step check; per-check or per-step? open.
7. Hold code 0 or collides with a tool's own code (2, 127, 137 after timeout kill): not rejected by anything.
8. Template blob hash is recorded at admission; template changes while an attempt is running: which hash is "built"?
9. Absent profile on target (new repo): defaults for setup/target, but `required` default is empty so the gate passes. open.
10. Per-step CLI override against a `harness` mismatch: refused, but the profile row is unchanged; the override is a
    non-profile fact on the attempt (no entity for it).
11. Timeout kills a check: `rc` is a signal artifact, not a verdict; verdict `fail` or `hold`? open.
12. Profile unavailable (Git unreadable) mid-run: no verdict, run waits; nothing says for how long (timeout absent).

## 3. "Slippery slope" designs
- Profile as a KB entity: every config key becomes an `entity/profile` attr and a `constant` binding; then each setup command
  becomes an operation, and the KB duplicates the file. Stop: profile stays a file; KB holds only the rules and values.
- Expression language for gate rules ("required unless label x"): FEEL makes it cheap; resist, the gate must stay a name list.
- Per-step block growing into a full workflow definition (cases per check result): it becomes the flow table of tl-8bh9.14.95.
- Land mode per task, per path, per label: slope from one flag to a policy engine. Keep the value two-state, per repo.
- Allowing templates with conditionals: closed placeholders are the guard; one `{if}` and it is a template language.
- Per-step `agent` fallback lists (try model B): a scheduler inside a config.

## 4. Misfits
- Branch-scoped facts: the spec has rows with state, no notion of "this value at ref R". The key fact (read from target,
  not commit) is a rule over two rows of one entity keyed by commit; clumsy and the check expression leans on tip().
- FEEL subset has no string, glob or path operations: `changed-paths contains`, `excluded` globs, `produces` templates,
  `argv` lists cannot be evaluated; they stay text and "tracked, not evaluated".
- `value` is number/duration/date/clock time only; the target branch and land mode are text and members. Used set and an
  entity attr; the owner "decides" them with no value kind.
- `interface.form` is screen|command|api; a repo file read by the factory is none of them (used api).
- Owners never write entries, but the owner (or agent) writes the JSON profile directly: a second authoring path outside
  interview, with no layer tag; the profile is config, not an entry.
- Layers are per entry; here one entity mixes owner-only attrs (required, target) with agent-proposed (setup, checks, prompt).
  Layer would have to be per attr; only `rule ?by` expresses it.
- Name clash: persona/agent (nature agent) vs step `agent` (harness, model, effort) which is a tool setting.
- Self-reference: the KB lives in the repo it describes and is itself gated by the profile; no way to say it.
- `tl` command shapes: only `tl step rounds/list/show` are known; interface says: texts for profile commands are invented.
- Check `timeout` appears as a duration attr and the spec's `?timeout {after}`; two timeout notions, one value used twice.

## 5. Unused / over-engineered parts of spec v3
Unused: `goal` states beyond naming, `capability`, `quality` (one forced entry), `counter` type, `?each`, `?wait`,
`?conflict`, `tags`, `{schedule}`, `{after,since}`, `{event}` triggers, `{count}`, `{add|remove}`, `{clear}`, `{tell}`,
`for_each`, `hand-off then`, `derived` (one entry, with an expression beyond FEEL), Quint exploration (profile has no
interleavings), `dependency` (profile is hand-validated), `constant.source` beyond one JSON pointer.
Heavy for this domain: receipts `covers`/ranking on a 300-line pure validator; separate `operation` and `interface` for a
file read; full workflow for `resolve-profile`, which is a pure function with 3 outcomes (a table of cases would do).
Used well: `rule guard/holds/adds`, system `cases` with `order`, `?open`, `ends` with `gives`, entity lifecycle,
fingerprint with template hash as a dependency, `constant` binding value to file source.
