# Guidance for the software ontology

How to think about a project with ogy: what goes into the ontology, what stays a plain task, and how work follows
from the ontology.

## The ontology describes what should be true

The knowledge base holds the state the product should be in: its goals, capabilities, workflows, rules, entities,
quantities and the software that builds them. It does not hold the work.

Work is the difference between what should be true and what is true. When the ontology changes, the difference
between the old and the new version is the work to do. When reality drifts from the ontology, restoring it is the
work to do.

So every task either changes what should be true, or acts on the running world without changing it.

## The one question

**Does this task change what should be true?**

- Yes: change the ontology first. The task follows from the change.
- No: it is a plain task. The task tracker owns it, and the ontology does not mention it.

## Kinds of tasks

| Kind | Example | Where it goes |
|---|---|---|
| Changes what should be true | a new feature; a new limit or rule | an ontology change; the work follows from the difference between the two versions |
| Something the system does again and again | a nightly database vacuum; a cache clean-up every hour | the ontology, as a workflow with a `schedule` |
| A one-off act on the running world | "vacuum the database tomorrow"; "flush memcached now" | a plain task, outside the ontology |
| Reality drifted from the ontology | an outage; a bug | a task to restore what the ontology says; perhaps a rule or a proof was missing, and adding it is an ontology change |
| Finding out | research, a spike, a consult | a decision: the question, its options and, once found, the answer |
| How the team works | CI, tooling, restructuring the knowledge base | the repository's constitution or rules when it should stay true, else a plain task |

## Four questions for any task

1. Does it change what should be true?
2. Does it repeat?
3. Who does it: the system or a person?
4. Does it leave a lasting result?

## The test for "outside the ontology"

Imagine the task done and forgotten. If nothing in the ontology becomes false, it is a plain task.

## Examples

- **Deploy to a new environment.** The ontology has no environment kind yet: environments are deferred. For now, an
  environment the product must keep running in is a decision (where it runs, and why) plus the `setting`s and `quantity`s
  it sets; a one-off deploy to it is a plain task.
- **Vacuum the database tomorrow, once.** Nothing in the ontology becomes false if it is forgotten: a plain task.
- **Vacuum the database again and again.** A repeated manual task is a sign that a scheduled workflow is missing.
  Add the workflow; the system then does it.
- **A bug.** The ontology already says what should happen; the code does not do it. Fix the code. If nothing caught
  the bug, add the missing rule or proof.
- **Which database to use.** A question with options: a decision. Its answer changes what should be true.

## Rigid where checked

Principle `rigid-where-checked` (decision `software/ontology/decision/rigid-where-checked`): a fact a check, the work
(the fingerprint derivation) or impact reads is a field or a link; everything else is a sentence on its entry. `ogy
init` ships this principle and this section to every repository.

| The fact | Where it goes |
|---|---|
| read by a check, the work derivation or impact | a field or a link |
| read only by a person or an agent | text (`says`) on its entry |
| text that names another entry | that part becomes a link |
| a decided number | a quantity |
| no kind fits | a rule with links and a proof, never a new kind |
| a new kind or field | only when it names the check that reads it |

Two ways this fails:

- **All rigid.** The model grows as detailed as the code and lags behind it, like a UML round-trip.
- **Hybrid.** The text becomes a second, unchecked spec. The guards: text lives only on entries; a sentence that
  names an entry must be a link; a rule that constrains nothing is an error; a new field comes only when several
  rules repeat one sentence shape.

Example, a store. Choosing Postgres is a decision plus a dependency. How fields are stored (a JSON column, a compound
index, a DynamoDB GSI or LSI) is text on that decision, or code, unless a check must read it. What should be true is
the requirement: a latency quantity plus a rule with a timing proof. Moving to DynamoDB then changes the decision and the
dependency; the requirement and its proof stay, and the work is what the proof finds no longer true.
