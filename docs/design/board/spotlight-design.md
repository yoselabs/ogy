## 0 Outcomes

1. **Explain a decision.** Within five seconds of “let me show you”, the owner sees the decision, what its options change and what needs checking, with everything else dimmed or hidden. Success: the owner can identify the question, one consequence and one missing requirement from the board alone.
2. **Explain a new flow.** In the same exchange, the agent draws a new workflow with new parts before any entry exists. Within 250 ms of call completion on a connected local board, the owner sees its steps and can distinguish illustration from KB entries. Verify timestamps and unchanged KB content.
3. **Compare alternatives.** In one exchange, the owner inspects two or three alternatives side by side against shared existing context. Success: alternatives retain separate parts and differences; switching writes nothing.
4. **Concentrate.** In one click, the owner removes unrelated blocks and lines, then restores them without losing position. Verify hidden counts, unchanged target coordinates and restored navigation.
5. **See each call.** Without refresh, the owner sees every agent call's completion, session and result on the next available paint; local p95 target: 250 ms. Verify a read, illustration, write and refusal, with continuous sequence numbers. Network transit cannot literally take zero time.
6. **Settle a sketch.** In the current exchange or later, the owner names an alternative to keep; the agent previews exact differences and records only the answer given. By the next paint, the board distinguishes proposed, unagreed and agreed entries. Verify fingerprints and answers independently of drawing style.
7. **Return after a week.** Within two seconds of loading the KB, the owner and a new agent see pending proposals, unagreed entries and latest answers. Verify after server restart: saved work returns; yesterday's pointer and dismissed illustration do not.

These are acceptance targets, not measured server performance. [Three exact decision groups](spotlight-examples.md) distinguish recorded links from agent-selected commentary, using live KB reads on 22 November 2026. Composition follows [view architecture](view-architecture.md) and [view design](design-views.md). Proposed mechanisms below remain proposals.

## 1. Outcomes 1 and 4 require attention without losing meaning

A **spotlight** carries a title, subjects, summary and per-target commentary, `set` or ordered `tour`, lifetime until dismissal/replacement, and authenticated session identity with a display label. These are transient interaction data, never ontology kinds or links.

Roles explain inclusion: **subject** is what is being decided; **impact** is what an option changes or potentially reaches; **needs** is a recorded requirement or work left to check; **context** explains why it arises. Preserve multiple roles and witnesses per identity. Role words and coloured borders supplement canonical kind icons. Pulse borders gently three times, then hold steady; reduced motion stays steady throughout.

Default to the simultaneous set so the owner sees the whole argument. Back/Next optionally follows the same targets with a numbered path and commentary per stop. This orders an explanation, never executes a workflow. Fit once at readable scale; use details for overflow.

**Dim** preserves other blocks, links and navigation as spatial context. **Hide distractions** removes unrelated blocks, lines and hit targets; retain target ancestors needed to understand parts and boundary counts for omitted relations. Keep coordinates and offer Restore. Neither changes KB data. The toggle is local; the agent may suggest it.

## 2. Outcome 1 requires derived facts and authored commentary

At one KB version, the server reads subjects, options, proposal and latest answers. Option `sets` derives direct impact, including creation and `null` removal. Compare alternatives separately against the current KB: an applied sentence has no new difference. Run `impact` on changed entries, preserving reaches/reached-by and typed witnesses; reach proves no breakage.

Use `diagram` for `start`, `then`, `calls`, `covers_ends`; `work` supplies recorded obligations. Follow `workflow.realizes → capability.realizes → goal.for` for purpose, separately from `because`, answers, `src` and `proof`. Preserve `satisfies` and `constrains` direction. “Unbuilt” describes the built record. Never infer requirements from prose or invent absent `impact`/`affected` links.

Normally the agent names subjects and writes commentary; the server supplies identities, role candidates and witnesses. Missing commentary gets a deterministic witness sentence. The agent may choose a bounded subset, order it, or add an existing address with role and explanation. Label these **agent selected**. The newest decisions have no `sets` or typed dependencies: their related entries cannot honestly be derived impact.

Reuse one semantic model and linked identity rendering path for board and agent. Illustrations reuse workflow/step/choice/end recipes with temporary identities; layout adds no meaning.

## 3. Outcomes 2, 3, 6 and 7 require two small MCP tools

Keep existing KB tools; add two tools. Arguments/results below are transport data:

* `spotlight({action:show|dismiss, expected_version, subjects?, title?, commentary?:{summary,by_address}, references?:[{address,role,commentary}], presentation?:set|tour, path?, hide_distractions?})` → `{version,kb_version,targets:[address,roles,witnesses,commentary,availability],gaps,session,sequence}`. Dismiss changes attention only.
* `illustrate({action:show|promote|dismiss, expected_version, id?, title?, alternatives?:[{id,records,commentary}], selected?, decision?, kb_version?})` → `{version,temporary_to_address,validation,differences,sequence}`. Show validates complete workflows and parts in memory; up to three alternatives share existing context. Dismiss removes illustration. Promote revalidates and atomically uses the checked write path to save a decision/proposal with option `sets` and any intended real unagreed entries. Return canonical addresses; replace temporary identities after success. Grant no agreement. An obsolete preview returns new differences for inspection.

Before ending a brainstorm, the agent promotes surviving alternatives into a KB decision/proposal; the owner needs no save gesture. “Keep for later” can request this sooner. Only deliberately disposable illustrations remain server-only and disappear on restart. Reconstruct saved alternatives from option `sets`; compute waiting work from proposals and sentence agreements, never pointers or session logs. An answered decision does not prove every changed entry's current sentence agreed. “Commit it” settles the specified decision with displayed paraphrase; it means no Git operation.

## 4. Outcome 5 requires one server and immediate delivery

Add sequenced SSE `/api/events` for **every MCP completion**, including reads and refusals. Publish status and changed inspection/spotlight/illustration data or versions before returning the MCP result. Reads update the log without moving the camera. External file changes enter the same stream. Paint acknowledgement distinguishes “sent” from “seen”.

Connect using a versioned state snapshot and subscription cursor; reconnect gaps trigger resynchronization. Existing `/api/version` polling is a visibly degraded fallback, not fulfilment of immediacy. Extend its KB-only version with attention/illustration versions. Show disconnection.

Two sessions replace attention using compare-and-swap: one succeeds; the other receives current session/title/version and must explicitly replace it. One board, bounded session/time log; Back/Next stays local. KB changes rederive the active targets against the new version. Removed targets retain address/commentary as unavailable; skip camera movement, never substitute by title. Restart clears attention and illustrations.

Chat discussion records no answer. Explicit chat answers and deliberate board option confirmation use the same `answer`/`reply` path, displayed paraphrase and version check inside the write lock. Promotion, pointing and dismissal are never assent.

## 5. What I can do today

Use `find` and `show` on the three decisions, options, proposals, answers and referenced entries; `impact` on the preview capability; `diagram` on its workflow; `work software/viewing`. Explain those groups in chat. `review` prepares owner cards but **saves a review round**: it was not run for this read-only task.

Current MCP has no spotlight, hide filter, illustration publication or board push. Current API exposes inspection/version/entry reads and a placeholder board. Those tools cannot make lab29 blink, navigate or hide. The smallest first addition is `spotlight(show|dismiss)` plus event stream and board consumer; nonexistent workflows additionally need `illustrate`. The mock simulates these proposed interactions locally without MCP, SSE or KB writes.

## 6. Recommendation and owner questions

**Recommend one shared board with a simultaneous spotlight, optional tour, and disposable illustrations that can become KB proposals.** The whole argument stays visible and lasting work is recoverable.

* **Problem:** another session interrupts. **Options:** queue or explicit replacement. **Recommended:** versioned replacement. **Why:** attributable interruption without hidden overwrites.
* **Problem:** sketches must survive a week. **Options:** automatic brainstorm checkpoint or manual Keep for later. **Recommended:** agent saves surviving alternatives before ending the exchange. **Why:** returning works without remembering a save gesture; transient experiments can still be dismissed.
* **Problem:** related entries lack links. **Options:** derived targets only or labelled agent references. **Recommended:** labelled references. **Why:** useful explanation without manufactured evidence.
