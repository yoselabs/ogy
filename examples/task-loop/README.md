# Task loop

The task factory of `iorlas-task-loop` (`tl`), read from its code at commit `0e4ba39d4`: every `code:` link names a symbol in
that repository's `src/taskloop`. The repository is not held here: `tests/test_examples.py` reads each link against a stand-in
that defines its symbol, and the knowledge base was written through ogy in a scratch copy that held the real `src/`, so each
link was checked against the real code when it was written. Two planned parts are written as hypotheses, each an unanswered
decision whose proposal carries it (decision `software/ontology/decision/reference-cases`: planned parts may be hypotheses).

Read it with `just ogy --repo examples/task-loop status` (code links then report `missing-code`; the test reads them).

## What is in it

| area | layer | what it holds |
|---|---|---|
| loop | product | the round (settle, advance, admit) and the attempt (plan, implement, checks); the attempt's lifecycle; three rules; two planned parts: an MCP tool and an outside trigger |
| land | product | landing one checked task: squash, push without force, close in the tracker; five rules |
| dashboard | product | the read-only board, served from the rounds process |
| shared | product | the person, the implementing agent (AI), the tracker and the code host |
| loop, land, claim | software | the handlers, the Codex harness, bd and origin, the claim lease and the land's numbers |

## The twelve questions (2026-11-26)

1. **Why a workflow exists.** Partly. Each workflow realizes a capability and each capability a goal, but every goal here was
   read from code: no decision and no person gives the reason. The chain holds; the why is the code's.
2. **Outside parties and their interfaces.** Holds. The person (CLI: `tl rounds once`, `tl rounds start`, `tl land run`; web:
   the board), the implementing agent (the answer contract, form `message`), and, planned, an agent through MCP and an
   automation through an HTTP hook. The tracker and the code host reach the factory through no interface: it calls them.
3. **Outside systems called, and no answer.** Holds. The round tells the tracker when it claims (case `no-answer`, rule
   `claim-read-before-taken`); the land tells the code host (push) and the tracker (close), each with its failure end and the
   rule `rerun-does-what-is-missing`.
4. **What starts each workflow.** Holds. Actor steps start the round, the land and the board; the round leads to the attempt
   (a case's `then` names the workflow); the planned outside trigger leads to the round.
5. **AI steps, and what an actor may not do.** Holds. Plan and implement are the implementing agent's steps. "May not push" is
   the rule `agent-never-pushes`, satisfied by the commit choice and by the handler that launches the harness with push barred.
6. **Several interfaces on one step.** Holds. The round's first step is served by `rounds-once`, `rounds-start` and the planned
   `rounds-tool`; each lists what it offers (`once`, `repeat`, `once`), so the knowledge base shows they differ. ogy flags only a
   choice no interface offers; nothing flags two interfaces that offer different choices, and here that is intended.
7. **A product made of parts.** Partly. The dashboard is its own area in both layers and reads only the attempt, so it can be
   described alone. Every part still shares one product layer: there is no way to say "this part ships on its own".
8. **A fact from code with no reason.** Holds. 58 entries carry a `code:` source and no `because`; `ogy status` labels them
   "from code", apart from "decided by you". Its three goals cite no reason, so `ogy work product` lists each as discover
   work, `no-reason` (decision `software/ontology/decision/reason-is-owed`); what hangs below a goal takes its reason from it.
9. **Entries no person confirmed.** Holds: all of them. Nobody agreed to anything in this case; `ogy status` shows 28 "decided by
   AI" (written without a source) and 58 "from code".
10. **Planned, not built, and what each layer owes.** Partly. The planned parts are the two unanswered decisions. Everything
    else reads "unbuilt" (40 product and 12 software build rows), though the code exists: a case read from code has no
    built record, so `ogy work` cannot tell built from planned. Recorded as
    `software/ontology/decision/case-built-record`.
11. **Layer from kind and links.** Holds, with one gap: the round lands the oldest passed task first under `land: auto`, and the
    product round cannot branch on it, because `land-mode` is a setting and a setting is software only. Moving the enum
    `land-mode` (who lands) to product would let a product case read it; not done here.
12. **A swapped dependency.** Holds. Codex for Claude: the implementing agent is a product actor realized by the dependency
    `codex`; the swap changes that dependency (its `says` names the other harnesses) and nothing in product. bd for another
    tracker: `bd` realizes the product actor `tracker`; the claim's quantities and its workaround are bd's and would change with
    it, and no product entry would.

## Findings

1. **An option cannot set a workflow's steps.** The planned outside trigger first went in as one option that sets the actor,
   the hook and the workflow with its steps; `put` refused the steps and ends (`unknown-field`). The option now sets the
   workflow's own fields, and the steps come with it in the same write. Decision `from-pain-to-built` says an idea about a
   flow enters "as a decision whose option sets the workflow". Recorded as `software/ontology/decision/sets-and-parts`.
2. **A case read from code cannot say what is built** (question 10). Recorded as `software/ontology/decision/case-built-record`.
3. **Software numbers have one reader.** Five values (two quantities, a setting, an enum and the renewal limit) were unused
   until a software rule constrained each: a product row may not read a software value. That is the layer rule working; the
   rules are true of the code.
