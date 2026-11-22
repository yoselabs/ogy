# Three decision groups: exact board targets

Read-only live evidence, 22 November 2026. Root: `/home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/docs/kb`. Read with `just … ogy show` and `find … -exec cat`; `impact`, `diagram` and `work` were also executed. No KB writes or Git commands. The two newest questions and the earlier answered preview decision form one discussion: show the idea, see it immediately, understand its consequences.

The tables define the exact selected targets. Options/proposal stay inside their decision card. `derived` means a recorded field, part or operation result. `agent selected` means commentary about a real entry, not an encoded dependency. No `impact` or `affected` fields occur on these decisions. `impact` below is the existing operation.

## 1. Explain a flow that does not exist — mocked group

**Subject:** `product/inspection/decision/show-what-does-not-exist-yet`, question waiting, no answers.

| Full part address | Recorded option / proposal | `sets` |
|---|---|---|
| `product/inspection/decision/show-what-does-not-exist-yet/option/both` | Server-only illustration, plus promotion to real unagreed KB entries | Absent |
| `product/inspection/decision/show-what-does-not-exist-yet/option/unagreed-entries` | Always write real entries; unagreed entries are the preview | Absent |
| `product/inspection/decision/show-what-does-not-exist-yet/option/illustration-only` | Server-only sketches; write real entries after owner says so | Absent |
| `product/inspection/decision/show-what-does-not-exist-yet/proposal` | `chose: both`; rationale: disposable sketches should not pollute the KB; useful ones become real entries | No direct `sets` |

No recorded delta, `because`, incoming `satisfies` or `constrains` is established for this decision. Direct derived impact is empty. The subject's prose is not a typed dependency.

| Role / origin | Exact board target | Commentary |
|---|---|---|
| subject / derived | `product/inspection/decision/show-what-does-not-exist-yet` | Decide how to show an invented flow and preserve it when it matters. Proposal is both; no owner answer yet. |
| impact / agent selected | `product/inspection/capability/preview-a-new-requirement` | Existing preview capability is the relevant product promise; this question records no change to it. |
| impact / agent selected | `product/inspection/workflow/preview-requirement` | Its recorded flow previews a proposed change. The mock's new three-step workflow is a separate illustration, not an expansion of this workflow. |
| needs / agent selected | `software/viewing/interface/inspection-data` | `work software/viewing` reports unbuilt; board and agent need the same validated differences. |
| needs / agent selected | `software/viewing/rule/agent-inspection-parity` | Recorded rule, unbuilt; verify that illustration differences mean the same thing to agent and owner. |
| context / agent selected | `software/viewing/decision/staged-changes-home` | Answered `kb-proposals`: durable work lives in a decision proposal; attention and disposable illustration do not. |

These six are the mock's blinking targets and six commentary cards. Its summary says: decide how to illustrate, touches preview capability/workflow, needs shared data/parity. The sketch uses temporary IDs only. Its dashed frame explicitly says “sketch, not in the knowledge base”.

Additional answered context is available in subject details, without blinking:

* `product/inspection/decision/agent-session-view` → `one-board-session-log`, 2026-11-22T04:28:42+01:00, note “For now”.
* `product/inspection/decision/preview-a-new-requirement` → `ghost-impact-advice`, 2026-11-21T22:32:21+01:00, hedge “Yes, I guess.” This is the earlier agreed direction, not an answer to the new question.

## 2. See each call immediately

**Subject:** `software/viewing/decision/board-follows-agent-calls`, question waiting, no answers.

| Full part address | Recorded option / proposal | `sets` |
|---|---|---|
| `software/viewing/decision/board-follows-agent-calls/option/push` | Push each change on call completion; file watch covers external edits | Absent |
| `software/viewing/decision/board-follows-agent-calls/option/poll` | Ask for a version every second or two | Absent |
| `software/viewing/decision/board-follows-agent-calls/option/manual` | Owner refreshes | Absent |
| `software/viewing/decision/board-follows-agent-calls/proposal` | `chose: push`; the shared process can notify immediately | No direct `sets` |

Again: no encoded delta, `because`, `satisfies` or `constrains` on the question. No derived impact is claimed.

| Role / origin | Exact board target | Commentary |
|---|---|---|
| subject / derived | `software/viewing/decision/board-follows-agent-calls` | Choose how the board follows calls; push is proposed, not answered. |
| impact / agent selected | `software/viewing/interface/board` | Needs to receive changes without reload; current contract says inspect/walk/preview but has no push contract. |
| impact / agent selected | `software/cli/interface/view-server` | Its sentence currently says each reload rereads the KB; `includes` board. An immediate-update contract is still missing. |
| needs / agent selected | `software/viewing/rule/projection-contract` | Recorded snapshot identity and exact witnesses keep each pushed state coherent; `work` reports unbuilt. |
| needs / agent selected | `software/viewing/entity/inspection-projection` | The rule `constrains` this entity. A push must carry or identify the same projection the agent reads. |
| context / agent selected | `software/cli/decision/serve-includes-mcp` | Answered `one-process`, 2026-11-22T03:27:57+01:00: API and MCP share one server. |
| context / agent selected | `product/inspection/decision/agent-session-view` | Answered one board with session log; make every update attributable. |

Exact witnesses in details: `software/viewing/interface/inspection-data.satisfies` and `software/viewing/handler/derive-inspection.satisfies` both reach `software/viewing/rule/projection-contract`; that rule `constrains → software/viewing/entity/inspection-projection`. `software/cli/interface/view-server.includes → software/viewing/interface/board`; both interfaces `satisfies → software/viewing/rule/agent-inspection-parity`. These are recorded relationships, not proof that push is implemented.

Current source `src/ogy/web/api.py` exposes `/api/inspection`, `/api/version` and `/api/entry/{address:path}`; `/` returns “The board is not built yet.” There is no SSE route there. MCP tools are generated from CLI subcommands in `src/ogy/mcp_server.py`, excluding server starters. Thus the common-server answer does not imply that spotlight/push already exists.

## 3. Understand the consequence of a proposed requirement

**Subject:** `product/inspection/decision/preview-a-new-requirement`. Latest answer: `ghost-impact-advice`, 2026-11-21T22:32:21+01:00, `where: ai:claude/f6fcc5ed`, hedged “Yes, I guess.” The proposal chooses the same option. Keep answer and proposal distinct.

| Full option address | Exact `sets` target and value |
|---|---|
| `product/inspection/decision/preview-a-new-requirement/option/none` | `product/inspection/capability/preview-a-new-requirement: null` |
| `product/inspection/decision/preview-a-new-requirement/option/ghost` | `product/inspection/capability/preview-a-new-requirement.says`: “ogy shows a proposed requirement on the map as ghosts with the links they would make, before any entry exists.” |
| `product/inspection/decision/preview-a-new-requirement/option/ghost-impact-advice` | `product/inspection/capability/preview-a-new-requirement.says`: “ogy shows a proposed requirement on the map as ghosts while the owner chats, lights what it would impact and shows what else it recommends linking it to, before any entry exists.” |

`product/inspection/decision/preview-a-new-requirement/proposal` has `chose: ghost-impact-advice` and no direct `sets`. The current capability sentence matches that option: its present sentence delta is empty. `none` would require a valid removal plan, not just deleting a card.

| Role / origin | Exact board target | Commentary / witness |
|---|---|---|
| subject / derived | `product/inspection/decision/preview-a-new-requirement` | Review the agreed preview direction, retaining its hedge. |
| impact / derived | `product/inspection/capability/preview-a-new-requirement` | All options `sets` this entry; latest chosen sentence is already present. |
| impact / derived | `product/inspection/workflow/preview-requirement` | `realizes` the capability; returned as reached-by in `impact`. |
| needs / derived | `software/viewing/interface/inspection-data` | `serves` the preview step and is unbuilt in `work`; inspect the shared data requirement. |
| needs / derived | `software/viewing/rule/agent-inspection-parity` | The data interface and preview handler `satisfies` it; recorded unbuilt obligation. No `constrains` is recorded on this rule. |
| context / derived | `product/inspection/decision/inspection-outcome` | Capability `realizes → product/inspection/goal/understand-recorded-product`, whose `because` reaches this answered decision (`understand`, 2026-11-22T03:12:47+01:00). |
| context / agent selected | `software/viewing/decision/staged-changes-home` | Answered `kb-proposals`, 2026-11-22T04:28:37+01:00. Separates durable proposed content from transient attention. No subject `because` link joins them. |

Exact workflow parts: `product/inspection/workflow/preview-requirement/step/preview`, its `choice/preview`, and `product/inspection/workflow/preview-requirement/end/done`. `diagram` prints start → preview → Done. This is one actual step, not the mock's invented three-step flow.

Rule/implementation witnesses:

* `product/inspection/workflow/preview-requirement.satisfies → product/inspection/rule/inspection-preserves-declarations`.
* `software/viewing/handler/preview-change.performs → product/inspection/workflow/preview-requirement/step/preview/choice/preview`; its `satisfies` reaches the declaration-preservation and parity rules; `because` reaches the preview decision.
* `software/viewing/interface/board.serves` and `software/viewing/interface/inspection-data.serves → product/inspection/workflow/preview-requirement/step/preview`. Their `offers` reaches that step's `choice/preview` for board; the library interface records no `offers` field.
* `software/viewing/interface/inspection-data.satisfies → software/viewing/rule/projection-contract`, which `constrains → software/viewing/entity/inspection-projection`.
* Goal `for` names `product/shared/actor/owner` and `product/shared/actor/agent`. Purpose and answer evidence remain separate from work left.

`impact` additionally returns the goal, actors, inspection-outcome option, constitution principle `constitution/principle/layers-split-business-from-technical`, workflow parts, board, view-server, inspection-data and preview-change. Keep these in expandable reach details, not all blinking. No returned entry is declared broken.

`work software/viewing` returns ten unbuilt entries: board, entry-details, inspection-data and seven rules. Exit 1 means work is left, not command failure. Lack of a built record does not prove lack of code.

## Mock evidence boundary

`graph2.json`: 830 nodes / 501 edges; `graph_tool.json`: 90 / 82. Older exports lack the newest decisions and full proposal/answer data. The self-contained mock therefore embeds the live target records read above; it borrows the tool fixture's Loan, Remind and Member as unrelated blocks. Exact kind icons from `lab29.tpl.html`, white cards, dotted board, blue workflow parts and compact controls follow lab29. The new three-step illustration and its alternatives are invented for this mock. Its promotion preview names proposed addresses explicitly; none is represented as an existing entry. All promotion and delivery feedback is explicitly simulated.

The outcome-first recommendation checkpoints surviving alternatives into a decision/proposal before the agent ends a brainstorm. This makes the week's return independent of pointer lifetime or a manual save. In the mock, Keep for later previews that proposed operation and then simulates unagreed entries; it performs no KB writes.

The older `product/inspection/decision/agent-points-owner` still proposes `focus-request` with a stored-request rationale and no `sets`. The owner's newer instruction makes the pointer transient. Its proposal needs a future explicit reconciliation; this task does not silently rewrite it.
