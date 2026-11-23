# Brief: ontology review and design session (Fable, with /ontology-designer)

Paste the block under "Prompt" into a NEW Claude Code session started in the ogy worktree
`/home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9` (branch `claude/ontology-graph-visualization-87d2a9`),
model Fable. The skill `/ontology-designer` comes from the owner's plugin `iorlas-wip`, which is NOT installed in the session that
wrote this brief: install or enable it in the new session first (the skill was not available to check).

## Prompt

Use /ontology-designer. Task: test, review and redesign the ogy ontology against everything the board work has found.
The owner (Denis) said: "make sure that all of the findings which we found where ontology needs to be adjusted will be thought
through again", and earlier: "we should not just add to ontology, we should consider changing things and adjusting things; cost of
everything is nothing".

Read first, in this order:
1. `AGENTS.md` (binding: proposals become decisions before action; never answer for the owner; never hand-write KB YAML; only `just ogy put`;
   no commit/push without the owner's word except commits on this branch, which he allowed).
2. `docs/thoughts/owner-inputs.md`: the owner's own words, kept as spoken. Append every new input of his there, at the bottom, the same day.
3. `docs/research/2026-11-23-ontology-redesign.md`: one consolidated redesign proposal (a ledger of about 100 items, the moves M0 to M9, conflicts,
   adoption stages, decisions to record) written by a read-only Fable consult. Treat it as input to challenge, not as the answer: find what it
   got wrong, what it missed, and where it was too timid. It lists what it could not verify in its section F: verify those.
4. `docs/research/2026-11-23-board-audiences-and-research.md` (audiences, hats, intake; research on IcePanel, C4, ArchiMate and others).
5. `docs/design/board/labs/lab29c/CARD-SPEC.md` (what each kind should show at each zoom level, and the nine things the ontology cannot answer yet).
6. `docs/design/board/labs/lab29b/FEEDBACK.md` (14 owner complaints; some are ontology questions: `serves` against `realizes`, a call as one step, actors not
   deciding their own drawing).
7. The KB itself: `just ogy glossary`, `just ogy kinds --map`, `just ogy status`, and the 12 new decisions waiting for the owner
   (`software/ontology/decision/{system-word,readiness-computed,derived-relations-declared,effect-value,lifecycle-grouping,close-loan-fixture,unused-actor-entity-handler,answer-where-ui}`,
   `product/language/decision/audiences`, `product/capture/decision/{dont-know-answer,intake-of-inputs}`, `product/review/decision/confirm-hedged-answers`)
   plus the new options on `context-form`, `rule-constrains`, `product-map`.
8. Open beads: `cd /home/iorlas/Workspaces/ogy && bd list --status=open` and `bd show <id>` for the `ogy-ful.*` items and `ogy-yy9`.

Method: do not stop at the existing proposals. Re-derive the ontology's shape from the owner's jobs (he is one person doing every hat now; the vision is business
analysts and product owners, then solution architects, then software engineers supervising an AI agent, then an AI-factory operator), then compare with the
current topology and with the redesign doc. Test the design on the tool-library fixture (`tests/fixtures/tool-library`) and on this KB: for each proposed
change, show a concrete example entry before and after, what `ogy check`/`ogy work` would say, and what the board would then show (cards in
`docs/design/board/labs/lab29c/CARD-SPEC.md`). Consider removing and merging existing kinds and fields, not only adding.

Done looks like:
- A written review (put it in `docs/research/` with the date) listing for every ledger item whether you confirm, change or reject its disposition, with reasons, and
  every NEW finding you made.
- Every change you propose recorded as an ogy decision with a proposal (new decisions, or new options on the decision that already asks the question);
  the owner is asked from `ogy review`, never from a pasted list. No answers recorded for him.
- `ogy check` clean, a hand-over that shows the waiting count, and a note appended to bead `ogy-ful.26` (from `/home/iorlas/Workspaces/ogy`, `bd update ogy-ful.26 --append-notes ...`).
- Nothing in `src/` or the kind files changes until the owner has answered; the adoption order follows his answers.
