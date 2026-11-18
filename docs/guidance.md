# Guidance for the software ontology

How to think about a project with ogy: what goes into the ontology, what stays a plain task, and how work follows
from the ontology.

## The ontology describes what should be true

The knowledge base holds the state the product should be in: its goals, capabilities, workflows, rules, entities,
values and the software that builds them. It does not hold the work.

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
| Changes what should be true | a new feature; "the app runs in environment X" | an ontology change; the work follows from the difference between the two versions |
| Something the system does again and again | a nightly database vacuum; a cache clean-up every hour | the ontology, as a workflow with `trigger: schedule` |
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

- **Deploy to a new environment.** The environment is part of what should be true (the software layer says where
  the product runs), so it is an ontology change. Deploying follows from it.
- **Vacuum the database tomorrow, once.** Nothing in the ontology becomes false if it is forgotten: a plain task.
- **Vacuum the database again and again.** A repeated manual task is a sign that a scheduled workflow is missing.
  Add the workflow; the system then does it.
- **A bug.** The ontology already says what should happen; the code does not do it. Fix the code. If nothing caught
  the bug, add the missing rule or proof.
- **Which database to use.** A question with options: a decision. Its answer changes what should be true.
