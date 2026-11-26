# Pet shop

An invented storefront, to find structural problems in the ontology early (decision
`software/ontology/decision/reference-cases`, option `start-small`). Its owner and the owner's answers are invented
(`where: ai:example/pet-shop#owner`). Only the product layer is written; the software layer is the next stage.

Read it with `just ogy --repo examples/pet-shop status`, `... work product`, `... work software`, or `... show <address>`.

## What is in it

Every area starts from a pain written as a decision (decision `product/capture/decision/from-pain-to-built`, decision-first);
the answer writes the goal or the value, and the rest cites that decision with `because`. Since decision
`product/capture/decision/pain-kind` (2026-11-26) each pain is also its own entry: `catalog/pain/phone-calls`,
`catalog/pain/wasted-drive` (cited by the goal `know-before-visit` and by the decision `hold-online`) and
`sales/pain/leave-for-cash`; none is agreed yet.

| area | pain (decision) | what the answer wrote | what follows |
|---|---|---|---|
| catalog | customers phone to ask if a pet is still there (`stock-goal`) | goal `know-before-visit` | the pet with states available, held, sold; the pet list; stocking the shop; rule `held-is-not-available` |
| reservations | a customer drives over and the pet is gone (`hold-online`) | quantity `hold-days` = 2 | holding a pet; releasing a hold that ran out, every `release-check`; rule `one-hold-per-pet` |
| sales | buyers leave to find cash (`card-payments`); no delivery van (`take-home`) | actor `payment-provider`; goal `take-home-today` | ringing up and charging a card, with a no-answer case after `card-wait`; rule `charge-once` |

## The twelve questions (2026-11-26)

1. **Why a workflow exists.** Holds. Each workflow realizes a capability, each capability a goal, and each goal was written by
   the answer to a decision whose context holds the owner's pain. `ogy work` groups each row under its decision (finding 1).
2. **Outside parties and their interfaces.** Holds. The customer and the assistant (human) reach the shop through four web
   interfaces: the pet list, the hold button, the stock form and the till. The payment provider (program) reaches it through
   none: we call it.
3. **Outside systems called, and no answer.** Holds. The charge step tells the payment provider; the ontology required a
   failure case and a rule that says whether a repeat is safe (`charge-once`). How long the reader waits is a case that reads
   `card-wait` (first written as a quantity nothing read; `ogy work` listed it).
4. **What starts each workflow.** Holds. Four start at an actor step; `release-expired` starts on the clock `release-check`.
5. **AI steps, and what an actor may not do.** Partly exercised. No step is an AI's. Who may do what is computed from the actor
   of each served step: the stock form serves only the assistant's step, so a customer cannot stock the shop. No "may not" was
   needed beyond that.
6. **Several interfaces on one step.** Not exercised: each step has one interface. The unoffered check fired once (the hold
   button left out "back"), which is the same check.
7. **A product made of parts.** Not exercised: one storefront.
8. **A fact from code with no reason.** Not exercised: there is no code.
9. **Entries no person confirmed.** Holds. `ogy status` shows 44 entries "decided by AI": every entry the owner did not agree
   to in a review, even those that cite an answered decision with `because`. An answer agrees to what its option sets, not to
   what cites it.
10. **Planned, not built, and what each layer owes.** Holds. `ogy work product`: 20 build rows, nothing to discover or design.
    `ogy work software`: 4 rows with effects that need a handler, one that tells the payment provider through a dependency.
11. **Layer from kind and links.** Holds. Every entry is a product kind; actor and interface are product only.
12. **A swapped dependency.** Not exercised yet: no software layer. The provider is an actor named by its role, so a swap would
    touch only the dependency that realizes it.

## Findings

1. **`ogy work` says "by no decision" for entries that cite one.** Its grouping reads only the decision that sets an entry; this
   case sets few entries and cites decisions with `because`, so every row read "by no decision". Decided
   (`software/cli/decision/work-cause-reads-because`, because-too) and built: a row now goes under the decision it cites.
2. **A proposal in force writes its entries before the answer.** A pain-only decision wrote the goal at once, before the
   owner answered; the goal read "decided by AI" until then. That is how a proposal works (built until answered); no change.
3. **`realizes` takes a list on a capability and one link on a workflow.** A writer used one form for both and was refused.
   The difference has a reason (a capability may serve several goals; a workflow reaches one result); no change.
