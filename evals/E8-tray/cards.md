# Kind cards

Every slot holds one of: an answer | `na: <reason>` | `?open {question, assumed}`. Never leave a slot out.
"implies" lists companions a lint requires; each must exist or be answered `na: <reason>`.

| kind | slots | implies |
|---|---|---|
| persona | nature: human/agent | acts as the actor of at least one step |
| goal | states | at least one capability serves it |
| capability | does, serves: goal/ | at least one workflow has this goal |
| term | means | |
| value | is, unit | used by a rule, case or timeout; no literal numbers anywhere else |
| set | members | |
| entity | attrs, key, lifecycle | |
| entity attr | type, ?max: value/ | at least one writer (an effect) and one reader (a when, check or from) |
| lifecycle | states, initial, terminal, transitions {from, to} | every non-terminal state has a way out |
| workflow | goal, actors, trigger, inputs, start, ends, steps | |
| workflow input | type | a guard or case reads it (its limits) |
| workflow ends | {name: {result: success/failure, means}} | at least one success and one failure end; each end has a message in every interface serving the workflow |
| actor step | actor, choices {label, then} | timeout {after: value/, then} |
| system step | cases {order, when, then}, otherwise | |
| calling step | calls: workflow/, cases over the callee's ends, otherwise | |
| effect (causes) | transition, create, write, count, tell | inward = our own facts; outward = a tell, or a change to a fact an external owns |
| outward effect | | rerun: same/checks/never; a case for "no answer" (unknown); answers to "done twice" and "silently not done" |
| external | owns_facts, events | answers to: down, slow, wrong answer, answers twice, changes facts behind us |
| rule | kind: holds/guard/adds, scope, body | |
| interface | form, serves: step/, says {end/: text} | |
