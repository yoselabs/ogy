# Ontology audit, 2026-11-28 (second audit)

Read at commit 6dd55dd: the 30 kind files, ontology.yml, starts.yml and agents.md. Two audits ran apart, following the
ontology-designer skill's audit branch: Fable (instances counted in ogy, pet-shop, task-loop and the tool-library fixture) and
an independent reviewer (ogy and the fixture). Both found no is-a, rigidity or identity breach. Where the findings went:

| finding | found by | now |
|---|---|---|
| agents.md and glossary restate kind facts and drifted (`from: human`, `because` without pain, term `names`, shape, area) | both | decision software/ontology/decision/agents-text-from-kinds |
| kind-file reasons sit in 30 comments; `--unreasoned` lists 128 of 128 | both | bead ogy-kr01 (kind-reasons is answered) |
| four answers changed no kind file and had no tracker item | review | beads ogy-8eqc (answer-where-ui), ogy-ous5 (harm-names), ogy-mlq3 (command-inputs-are-accepted); rules-need-a-check is ogy-ful.28; the cause is decision software/cli/decision/answered-uncited-is-work |
| effect value `transition` is a kind's name, the others verbs | Fable | decision software/ontology/decision/effect-do-words |
| workflow.realizes one, capability.realizes many | Fable | decision software/ontology/decision/workflow-realizes-many |
| dependency.realizes is a third meaning of the word | review | not asked: dependency-actor-word was answered `realizes` on 2026-11-28, and no new evidence |
| an entry's name has three homes (id, title, term.names) | Fable | decision software/ontology/decision/entry-name |
| the 17 top-level kinds are grouped by each reader | Fable | decision software/ontology/decision/kind-groups |
| values and fields with no instance; proposal.sets cannot be answered | both | decision software/ontology/decision/unused-values (Fable drop, review staged) |
| starts.yml seeds ogy's own principle; owner and human are two identities | both | decision software/ontology/decision/what-a-new-kb-starts-with |
| nothing computes an attribute nothing reads | Fable | decision software/ontology/decision/attribute-nothing-reads |
| two homes for the reason an entry exists (sets and because) | both | decision software/ontology/decision/reason-one-home |
| card, context, row, proposal, unused carry two meanings | review (card: both) | decision software/ontology/decision/one-word-each |
| command inputs are prose; a placeholder may be no product fact | both | decision software/ontology/decision/inputs-that-are-no-fact (command-inputs-are-accepted stays answered) |
| the board's read model and screen situations live in product (L7) | review | decision product/inspection/decision/board-read-model-home |
| 65 of 74 rules linked to nothing | review | ogy-ful.28 (answered proof-or-decision) |
| choice, case and timeout repeat one row shape | review | bead ogy-b2wm, a change run of its own |

Listed only, no action now: step's three types told apart by fields; `satisfies` and `constrains` hold "held to a rule" at two
ends; review policy (own_card, asked, printed_first, harms order) beside meaning in kind files (storage-is-a-projection holds);
an effect has no key (no case needs one); entities' states are not checked as one graph (defer to a real two-lifecycle case);
capability `harm: [authorization]` has no stated reason; the context of board-is-product has stale counts; bead ogy-ful.14 asks
for a pain kind that now exists.

The board (owner's question): it has actors, flow, effects, ends, the why chain and every gap as a computed status. It lacks the
five decisions above that name it (entry-name, kind-groups, inputs-that-are-no-fact, attribute-nothing-reads, reason-one-home)
and board-read-model-home. Icons, display modes, arrow rules and hats stay the viewer's (L7), so beads ogy-ful.8 and ogy-ful.17
should not land in the kind files.
