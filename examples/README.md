# Reference cases

Each folder here is one product described with ogy's one ontology, written through ogy (`ogy --repo examples/<case>`), so a
design pass can test a change against products other than ogy itself (decision
`software/ontology/decision/reference-cases`). `tests/test_examples.py` checks that each one loads and that `ogy check` finds
nothing in it but terms waiting for their owner's yes.

| case | what it is | layers written |
|---|---|---|
| [pet-shop](pet-shop/README.md) | a small storefront: a pet list, holding a pet online, paying at the counter | product |
| [task-loop](../tests/fixtures/example-task-loop) | the autonomous task loop: claim and land | product, software |

A case that describes a real product says where it was read from; an invented one (the pet shop) says so, and its owner's
answers are invented too (`where: ai:example/<case>#owner`).

## The twelve questions

Every design pass answers each question for each case, and names what the ontology could not hold. A question a case does not
exercise says so; it proves no need alone.

1. Why does this workflow exist: which goal, for whom, and what goes wrong today without it?
2. Which outside parties reach the product, and through which interfaces (web, CLI, MCP, HTTP)?
3. Which outside systems does the product call, and what happens when one does not answer?
4. What starts each workflow: an actor, a clock, an outside event, or another workflow?
5. Which steps does an AI perform, and what may each actor not do?
6. When one step is served by several interfaces, does the knowledge base show they offer the same choices?
7. For a product made of parts (a front end, a back end, an MCP server; a product built on another), where does each fact live,
   and can one part be described alone?
8. Can a fact read from code be recorded with its source and no known reason, and listed as "reason unknown"?
9. Which entries did no person confirm?
10. What is planned and not built, and what does each layer still owe?
11. Is each entry's layer decidable from its kind and links alone?
12. If a dependency is swapped (one payment provider for another, one tracker for another), which entries change, and does any
    product entry?
