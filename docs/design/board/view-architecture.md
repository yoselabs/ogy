# View architecture, described in ogy

Design and prepared records, 2026-11-22. Nothing was put into the KB, no answers were recorded, no repository or ontology was edited, and no git command was run. The only created files are scratchpad artifacts. The JSON is a proposed capture, not an assertion that the proposed interfaces or commands are built.

**Recommendation: derive inspection models from the ontology and the recorded graph; compose them with kind recipes and shared context adapters.** Every entry gets an appropriate representation in supported situations, but it does not get an independently authored implementation for every situation. Keep the context matrix as a coverage report. Keep one identity/mention path. Keep presentation hints optional and separate from executable rendering.

## 1. Authority and the choice

I read all of [design-views.md](design-views.md) and [decisions-verdict.md](decisions-verdict.md), the live main-checkout KB including its uncommitted entries, the worktree instructions and kind definitions, and the read-only glossary/kinds/search commands. The verdict was advisory when written. The later answers now select [◇ shared-hints][d-hints], [◇ entries-and-viewer-tokens][d-style], [◇ canvas][d-map], [◇ walk][d-modes], [◇ declared interfaces][d-interface] and [◇ derived-chain][d-why]. Their hedges remain part of the answers. In particular, the old `walk-and-history` proposal does not override the later `walk` answer.

Three existing boundaries still matter:

- [◇ no-views][d-no-views] still has `none` as its latest answer; `one-board` is only its proposal. The canvas and declared-interface answers establish the intended board, but do not silently rewrite this answer. Obtain an explicit `one-board` answer before implementing the new web-interface scope. Preserve printed review cards as terminal output.
- [◇ view-command-contract][d-command] proposes `serve-default`; neither delivery default is answered. Both options exclude the delivery command from MCP. This design recommends that exclusion and does not claim it is implemented.
- [◇ board-answers-in-v1][d-first] proposes a read-only first board. [◇ human-decision-mode][d-human] records the eventual decision interaction. Inspection, walking and pure previews can be built before answer endpoints; the first-version boundary still needs its own answer.

The following comparison is an architectural judgement about these requirements, not a claim that each alternative has been implemented.

| Candidate | Useful part | Why it should not own this architecture |
|---|---|---|
| Independent `kind × context × detail × mode` renderers, as the literal registry reading in design §3 | Explicit dispatch and coverage | A new context repeats identity, field selection, inverse links and availability handling across kinds; adding detail/mode multiplies those obligations. Similar tooltip/pinned implementations drift. |
| One generic card with kind-driven slots | A safe inspector and unknown-kind fallback; shared headings and sections | A workflow's flow, an entity's parts, a decision's answer history and an effect's operation have distinct structures. Forcing them into one card produces conditionals or loses meaning. |
| **Graph projection/query, followed by kind recipes and context composition** | **One owner of facts, derivation, availability and reasons; reusable results for agents and the board** | **Chosen. Requires explicit typed queries, stable fact identities, versioned output and disciplined renderer boundaries. An arbitrary-neighbour query would manufacture meaning.** |
| Atomic design | Shared identity token, field row, section, badge, frame and controls | Component sizes do not define ontology semantics or answer which facts belong in a situation. Use this as renderer composition only. |
| Presentation hints in the ontology | Shared symbolic defaults available to every consumer | Does not describe the application, interaction or a graph query. A binding rendering language would couple ontology releases to one canvas. |
| Viewer-only presentation | Owns concrete tokens, geometry and interaction | Correct for pixels; insufficient for the answered shared-hints direction or for inspectable software requirements. |

This refines design §3: dispatch remains deterministic, while a matrix cell resolves to a composition of shared pieces. It need not name a unique renderer function. A kind recipe owns primary sentence/sections and its structural family; a context adapter owns placement, clipping, navigation and bounded presentation. Tooltip and pinned use the same details; pinned adds controls. Search and relation endpoints use the same identity token. Specialized flow, lifecycle, decision and effect compositions are explicit overrides of shared families, rather than copies of all contexts.

Failure modes and boundaries:

| Failure | Prevention and observable evidence |
|---|---|
| Matrix explosion or generic-card conditionals | Generate coverage from descriptors plus registered families/overrides; no independently maintained Cartesian list of functions. Show unsupported combinations explicitly. |
| Drift from ontology vocabulary | Export real kind, sentence, field, `part_of`, `flow` and settling descriptors; validate recipe paths against them. Never relabel `realizes` as `serves`. |
| Projection becomes a second KB | Treat every model as disposable output of a content-identified snapshot and request. Store no model facts as new source entries and never write through a model. |
| Connectivity becomes invented justification | Typed, cycle-safe witness paths; distinguish purpose, rationale, evidence and work left. No utility, progress or runtime-state inference from topology. |
| Context omission hides meaning | Consume fact IDs, not strings; preserve all facts in the model and restore ownership in detached details. Never merge a read and a tell merely because their target matches. |
| Hints become executable rendering | Symbolic data only, checked paths, explicit fallback; no executable markup or layout in kind definitions. |

## 2. The layers and their contracts

```text
   KB snapshot + ontology descriptors (authoritative inputs)
                  |
                  v
   [DATA EXPORT / viewdata snapshot adapter]
   exact entries, parts, typed links, expressions, effects, answers, sources
                  |
                  v
   [INSPECTION MODELS / pure viewdata derivation]
   canonical identity + facts + typed queries + witnesses + local detail profiles
                  |                      |
                  |                      +--> show --view-model --> MCP show
                  v
   [RENDERERS / view_assets]
   kind recipe -> composition family -> context adapter -> HTML or SVG
   ONE MENTION PATH: identity token -> icon + linked title + accessible identity
                  |
                  v
   [INTERACTION / canvas]
   camera, local reveal, selection, tooltip/pin, search, walk, draft overlay
                  |
                  +-- new request / selected detail profile --> derivation

   DELIVERY SHELL: file export or loopback HTTP server around the same core
   No renderer, canvas or delivery shell reads KB files independently.
```

Each layer has one contract:

1. **Export:** represent the resolved snapshot and ontology without loss or invented absence, including source identities and availability.
2. **Inspection models:** deterministically derive identity, typed facts, parts, summaries and witness paths from those inputs and the request, without DOM, pixels, transport or writes.
3. **Renderers:** compose supplied facts for the requested kind/context/detail, using the shared identity token for every structured entry mention and never deriving new graph meaning.
4. **Interaction:** choose focus, visible representations and local detail from the supplied structural metadata, and turn inspection actions into requests without executing the inspected workflow.
5. **Delivery:** resolve input, call the same operations and serialize/serve their results, without adding semantics or answering a decision during browsing.

Dependencies point toward the data/model contract. There is no core import of the canvas, HTTP framework or MCP transport. `viewdata`, `view_assets` and an HTTP adapter such as `view_server` are proposed code stages; they were not present under those names in the inspected worktree. Its existing implementation is `view.py`/`viewpage.py`, and its `mcp_server.py` is a different, stdio adapter. Update the enforced import map with any new modules; see [architecture.md:1][architecture].

### Data and model contract

The serialized result is the proposed `software/viewing/entity/inspection-projection`, not a new ontology kind named `view`. Its minimum transport envelope is:

```text
snapshot: {kbContentId, ontologyContentId, contractVersion, resolvedRevision}
models[]:
  identity: {address, kind, title, titleSource, iconToken, destination}
  sentence: {field, exactText}
  fields/parts: exact values and owning addresses from descriptors
  facts[]: {factId, source, fieldPath, target, direction, operation?, witnesses[]}
  facets/summary: selected fact IDs, counts, owning part paths, detail profile
  availability: known | none | not-exported | filtered | unsupported
  reasons: {purposePaths[], becausePaths[], src[], proof[], answers[], proposal?}
relations[]: typed original facts, never geometrical ancestor assertions
diagnostics[]: explicit gaps and unsupported input
```

These are proposed serialized member names, not fields added to the ontology. KB attributes describe their serialized values as `type: text`, with `many` where appropriate. Application code validates the structured payload, including target-address existence. The contract stores no new copy of the definition of `goal`, `workflow`, `decision` or their fields. The source snapshot supplies those records.

Resolve `.` to one content identity for each response; resolve the ontology separately and include its identity. A source change invalidates the model cache. Cache keys include the snapshot/ontology/contract identities, target, layer filter, context, detail and draft digest. A whole-board overview composes the models requested for the selected areas' actual `area` entry addresses. Consumed fact IDs and visibility are transient composition inputs, not KB fields. A draft is validated against the exact identified snapshot; overlay IDs never masquerade as live addresses.

Use `(source address, field path, target)` for ordinary facts, `(owning row address, effect index)` for unaddressed effects, and ordered witness tuples for derived paths. Do not invent an address for an inline effect. Record empty/absent data only when the exporter establishes that the relevant fields were completely exported. A flattened `chose` edge cannot establish an answer; preserve `answers.at/said/where/note` separately from the proposal.

The normal server may derive requested models lazily. A standalone export carries the normalized facts, descriptors and required model facets so browsing it needs no KB reader. Both adapters consume the same exported semantics. Screen-dependent edge bundling is scene presentation: it groups supplied fact IDs using supplied structural owners; it cannot add purpose paths or evaluate conditions. The agent gets the same semantic models, rather than the browser's camera coordinates.

### Detail is derived from several ontology projections

The ontology provides a set of graphs, not a unique C4-like tree. Borrow the discipline of asking a distinct question at each detail profile. Do not call a `goal` a container or make `software` a zoom level.

| Local detail | Question and authority | Reveal and summary contract |
|---|---|---|
| `area` | Which area? Actual layer and area addresses | Area identity and distinct counts by kind; boundary mentions for filtered layers. |
| `purpose` | Which result? `workflow.realizes → capability.realizes → goal`, then `goal.for` | Exact typed paths, shared references for many-to-many links, and explicit missing-purpose gaps. |
| `work` | Which workflow, entity or supporting entry? | Entry identity, primary contract and part/relation counts. Every kind stays searchable and inspectable. |
| `parts` | Which declared parts? Descriptor `shape/part_of/key/holds` | Workflow steps/ends, entity attributes/states/transitions, decision options/proposal/answers, dependency workarounds. |
| `contract` | Which condition, effect or implementation? `flow` metadata and actual fields | Full row conditions, operations, covered ends, interface/handler contracts and sources; no further canvas microtext. |

Authority: [workflow.yml:9][k-flow] declares flow roles; [attribute.yml:7][k-attribute-parts] and [decision.yml:10][k-decision] describe different parts/settling structures. [capability.yml:16][k-capability-realizes] permits multiple goals. `realizes` does not establish ownership. Call depth and layout rank are independent of these profiles. Layer selection follows [ontology.yml:7][o-layers] and remains orthogonal to detail.

Each representation declares its current profile and next reveal boundary. Screen capacity chooses among these semantic profiles locally; an explicit navigation action can use the inspector when a frame cannot fit. Keep design §2.3's pixel gates as provisional asset tokens, with enter/leave hysteresis, rather than new ontology facts. Remove hidden child geometry, edges and hit targets together. A large workflow can reveal a readable region while siblings stay summarized. Opening an inspector never requires making every canvas child fit.

Roll edges to the nearest visible structural owner or an explicit filtered/offscreen boundary. Bundle by representatives, actual field/path, direction, operation and overlay status; count distinct source facts. Collapsed internal relations become an inspectable count, not a fake self-link. True recursive `calls` retains its own fact. `when.reads` and `effects.on [do=tell]` stay separate even for the same actor. Return-shaped geometry still denotes `← covers_ends`; it does not add a return field.

### One mention path

`address → canonical identity → mention token → HTML/SVG serializer` owns every structured identity in headings, cards, rows, tooltips, pinned details, search, edge inspectors, breadcrumbs, walk events and legend instances. The result includes the icon, linked title, full destination and accessible name; callers supply bounds and an adjacent field/operation annotation. Context cannot provide a replacement title or a `code` bypass. Even a self heading retains the navigation link, matching the owner's standing rule more strictly than design §3.3's self-heading exemption.

Use explicit common `title`, `term.word` for a term, otherwise the humanized key; retain the address for copying. Literal enum members, setting names, commands and authored sentences remain exact literals. Do not guess links by replacing matching words in prose. For generated prose, structured references are mention tokens from the start. In this document, literal kind/field/address spellings are technical notation; the example entry mentions below demonstrate the rendered rule:

> [▧ inspect-kb][e-inspect] `realizes` [◆ inspect][e-cap-inspect]. Its `actor` is [♙ agent][e-agent].

Glyphs here are symbolic stand-ins, not a new icon vocabulary. The viewer resolves each canonical icon once. Meaningful obligations live in rules; actual SVG paths, contrast, spacing, hysteresis and hit-target sizes live in assets. Tooltip visibility depends on the readable representation of that exact identity, including clipping and hidden parts; a pin remains available explicitly. Tooltip and pinned details have one content owner.

## 3. Model the application with existing kinds

The product layer says what an actor gets. The software layer says how these capabilities are delivered. Constitution principles apply to both; this design adds no constitution entry. Links may stay in their layer or point earlier: software can name product, product cannot name software ([ontology.yml:8][o-layers]).

| Concern | Product entry or reuse | Software realization |
|---|---|---|
| Who inspects | Reuse [♙ owner][e-owner] and [♙ agent][e-agent]; no new actor per tooltip or input device | Web interfaces serve owner steps; command/MCP interfaces serve the agent inspection step. |
| Result | Proposed inspection goal `understand-recorded-product`, with `for` owner and agent | No software goal: `goal` and `capability` are product-only ([goal.yml:9][k-goal], [capability.yml:10][k-capability]). |
| Inspect the product and see why | Reuse map/inspect capabilities and existing agent [▧ inspect-kb][e-inspect]; add owner `inspect-map` workflow | Shared `inspection-data` library interface and board; typed-reasons rule. |
| Walk | Reuse `walk-the-product`; add `walk-product` workflow | Walk handler follows supplied declarations and a call stack; no evaluator or effect executor. |
| Preview | Reuse `preview-a-new-requirement`; add `preview-requirement` workflow | Pure preview handler validates temporary records, uses the change planner and derives impact/advice separately. |
| Transient request/result | No product entity named after a widget or renderer | Software entities `inspection-request` and `inspection-projection`; these describe actual input/output data, not every KB kind again. |
| Canvas and details | No workflow per tooltip/search/legend | Existing `view-server` includes the proposed board; board includes one details interface. Contexts are enum members, not separate screens by default. |
| Obligations | Product inspection-preserves-declarations rule | Software rules for projection, mentions, detail, relation conservation, reasons, composition and parity, linked through `satisfies`. |

The proposed product workflows intentionally describe inspection outcomes at a coarse level. Their parts are not a wizard screen or one step per zoom/context. Each new owner step has an unconditional choice and a reachable success end. The software batch serves those steps and offers their choices. The existing agent workflow and its agreements stay intact.

### What `interface` can actually say

[interface.yml:20][k-interface] is decisive:

| Field | Allowed targets / restriction | This capture |
|---|---|---|
| `form` | Required: `web/cli/http/mcp/library/file/message` | Board/details `web`, shared data boundary `library`, existing delivery/show `cli`, agent surface `mcp`. |
| `serves` | `step` only | Actual inspection steps, never capabilities or kinds. |
| `offers` | `choice` only; requires `serves` | The declared inspection/walk/preview choices, never `decision.option` or toolbar strings. |
| `shows` | **`entity` or `attribute` only** | `inspection-projection`, or its `models` attribute for details. It cannot point straight to a goal, workflow, rule, kind definition or renderer. |
| `accepts` | `entity` or `attribute` only; requires `serves` | Transient `inspection-request`, not a new field such as `context` on an interface. |
| `includes` | `interface` only; acyclic | Delivery includes board; board includes details. A composition component is an interface only if it has an independently meaningful display contract. |
| `allows` | `actor`; only on an interface serving no step | Read-only details use owner/agent; the board takes its actors from its served steps and does not also set `allows`. |
| `satisfies` | `rule` | Cross-cutting obligations, not copies of the display inventory already in `shows`. |

This avoids both invalid `shows: [goal/...]` links and a misleading new ontology `view` kind. `interface.yml:2` explicitly records that the old `view` and `command` kinds merged into `interface`. Do not reverse that migration just to name rendering functions.

`handler.performs` can name only `choice/case/timeout`, while `uses` names external dependencies ([handler.yml:10][k-handler]). The three proposed handlers perform actual inspection choices. `viewdata`, recipes, renderers and the server are owned code, so they are not fake `dependency` entries. No new external library is selected by this design; existing MCP dependencies stay in their own area. A future external layout library requires a dependency choice, a declared pin where known, and a handler's `uses`; do not invent a pin now ([dependency.yml:3][k-dependency]).

`rule.constrains` can name data kinds, not interfaces; interfaces/handlers/workflows name the rule using `satisfies` ([rule.yml:3][k-rule]). The payload follows that direction. Missing implementations/proofs remain work left; it does not cite tests that do not exist.

### Facts current kinds cannot express directly

| Fact / exact limitation | Honest representation now | Ontology action |
|---|---|---|
| A renderer covers a kind definition in a particular context; kinds are not addressable KB entries and `shows` has no selector syntax | Rule `context-composition`; a checked recipe map in assets keyed by exported kind IDs; generated coverage checks every known kind and supported context | None. The obligation is testable using the existing descriptors and code map. Do not pretend `shows` links to kind files. |
| A display shows arbitrary graph entries, while `shows` targets only entities/attributes | Show the actual transient projection entity; serialize typed graph facts without making copied product entities for each kind | None. This captures the application's actual output contract. Widening `shows` is unnecessary for this design. |
| Structured arbitrary-kind address references or object-valued attributes in the projection | `type: text` for serialized payloads, `many` where appropriate; `derived` for computed output; runtime contract validation proves the contents | None. The KB checker validates the declared entity/attribute contracts, not links embedded in text. No claim of static per-entry reverse impact through those strings. |
| Full derivation/query language, path witnesses, cycle policy and counts | Rules with proofs over actual typed links/part metadata; implementation is one pure query owner | None. Do not embed executable queries in `says` or add a field merely to restate code. `derived.text` explains, and `reads` names its declared input entity. |
| A `derived.reads` link to all possible source entries or kind definitions | The projection attributes read the declared request; its derivation resolves the selected external snapshot. Source/content identities and runtime witnesses expose the other inputs | None now. The current KB cannot statically enumerate this dynamic source set. This is a documented limitation, not hidden all-entry dependency coverage. |
| Presentation contexts and local detail | The two proposed enums plus rules; enum members are closed application inputs, not kind names | None. Do not duplicate ontology layer names into another enum. |
| A true configurable default detail profile or numeric threshold | Use a `setting` only after a real file/environment name exists, with `default` to a quantity/enum; a fixed decided number is a `quantity` | No speculative setting/quantity records. Current pixel gates remain provisional viewer tokens, consistent with the answered style split. A handler parameter or camera state is not a setting. |
| Optional symbolic kind/link defaults | Versioned viewer descriptor adapter with fallback today | **Proposed structural decision `view-hint-fields`**: exact optional fields require a later ontology change, not this spike. |
| Canonical icon paths, concrete colors, CSS sizes, hover/pin placement | Assets satisfy mention/composition/detail rules | None. A new style/token kind adds no necessary meaning. |
| Form-specific parity of served steps | Rule and computed coverage over existing `interface.form/serves` links | No new semantic relation. Existing generic step coverage accepts any interface; form-specific work must be implemented explicitly. |
| Answering from the board | Existing review/answer operations behind future protected endpoints | Existing first-board/human-mode decisions own this question. No new answer kind or decision-override field. |

For the settings distinction see [setting.yml:3][k-setting] and [quantity.yml:3][k-quantity]. Enums and derived attributes already support the needed closed inputs and computed outputs ([enum.yml:14][k-enum], [attribute.yml:11][k-attribute]). A glossary term cannot encode a query or UI contract; no glossary term is proposed here and no owner's glossary agreement is fabricated.

The only proposed ontology extension is a separately evaluated optional hint vocabulary: kind `view.icon/tone/attention/compact_fields/family`, link `view.labels.forward/inverse` and `view.explanation`. Validate symbolic names and existing paths, reject executable values, keep structural metadata authoritative, and put the contract version in the descriptor envelope. Absent/unsupported optional hints fall back; an invalid field path is rejected. The new decision includes **no fields now** and binding-language alternatives. Its proposal follows shared-hints, but exact spellings remain unapproved. The current loader forbids unknown kind keys ([kinds.py:286][kind-loader]); this task changes none. A selected navigation action must still use the single navigation path; hints cannot run arbitrary code.

## 4. Prepared records and batching

[view-architecture.put.json](view-architecture.put.json) is an **array of 38 strings**. Decode the outer JSON, then give each selected string as a record argument to a future `ogy put`, or decode its records into a JSON array for that command's file input. Do **not** pass the outer array-of-strings directly as an array of records. `put.read_records` accepts mappings, not string elements ([put.py:24][put-reader]). No command in this task performed a put.

The records are contiguous by owning area. Each batch is checked against the live KB plus all preceding batches. Cross-batch links therefore resolve before use; B1's later-layer interface coverage is work left until B2. Existing required fields survive partial updates; they are not accidentally omitted from a replacement entry. New entries include required fields, and all new inline parts were checked recursively.

| Dependency order / 1-based decoded records | Area and content | Owner boundary |
|---|---|---|
| **B1: 1–10** | `product/inspection`: one proposed decision and goal, `realizes` extensions to four existing capabilities, one rule, three owner workflows | Plain capture for already answered inspection/canvas/walk/preview direction; the newly inferred common goal needs the owner's answer to `inspection-outcome`. Its proposal can be captured without answering. |
| **B2: 11–29** | `software/viewing`: area, architecture decision, two enums, two entities, seven rules, three interfaces, three handlers | New structural architecture is proposed, not accepted. Put its decision with the requirements as one proposed capture. Reconcile existing `no-views` before implementing the web scope. |
| **B3: 30–35** | `software/cli`: agent-parity decision; new `view-board` option and updated proposal on the existing command-name decision; partial updates to `view`, `view-server`, `show` | Owner chooses `agent-view-projection`; existing command-name decision must choose `view-board` before its old description changes. Delivery defaults remain owned by `view-command-contract`. |
| **B4: 36–37** | `software/mcp`: extend existing MCP-exclusion rule, declare the existing `show` tool's inspection contract | Conditional on B3 and the existing delivery-contract decision. This adds no tool named `view` or `show-inspection`; the latter is the contract entry ID for the existing `show` tool. |
| **B5: 38** | `software/ontology`: exact hint-fields decision with alternatives and proposal | Put the question for review now. Only the owner selects the structural option. No ontology implementation or glossary write is bundled. This batch is independently capturable after the live KB. |

There are **29 new addressed records and nine partial updates**, including the existing command proposal. Four new root decisions are proposed: inspection outcome, contextual composition, agent projection access and exact hint fields. The fifth review change extends an existing decision rather than creating another owner of the command description. Existing actors, capabilities, workflows, delivery interfaces and MCP rule are reused. Searches covered the broad words separately (the CLI matches all supplied words), the proposed IDs and removed entries; no removed ID is reused.

No direct record removes an entry, part or field. The JSON's `null` is inside the inspection goal's alternative **no** option, expressing that hypothetical absence, and is not an instruction executed by this capture. If that alternative is chosen later, first plan a consistent delta detaching the proposed capability links; do not leave dangling links or remove the goal to reorganize. Nothing in these artifacts authorizes executing that alternative now. If any future batch drops a part, `ogy put --why <decision-or-reason>` is required; see [put.py:152][put-drop]. This capture does not require `--why` because it drops nothing.

Avoid whole-map replacement of an existing entry's `options`, `steps`, `choices`, `includes` or `satisfies`. The command revision uses a separately addressed option and proposal so its older options and all answers survive. Existing list fields changed by this payload were absent in the inspected source; re-read and merge if they have since been populated. The existing `view.says` remains deliberately unchanged in the put batch because its current value is settled by [◇ product-map-command][d-name]; only the newly proposed option supplies the revised sentence on a future answer. Its current `invoked_as`, `form`, `serves`, proof and agreement are preserved.

Plain requirements and their proposals may be put now by an authorized coordinator; this runner has no KB-write authorization. Owner approval is required for selecting proposals and for implementation that crosses the unresolved existing boundaries. **Glossary approvals needed: none.** New principles, new kinds and synthetic evidence are unnecessary.

### Validation actually performed

Run from this scratchpad:

```text
/home/iorlas/Workspaces/ogy/.venv/bin/python -B validate-view-architecture.py
```

[validate-view-architecture.py](validate-view-architecture.py) uses the live ogy record parser and preflight validator, loads the main checkout's KB through a filesystem-only source, and runs the actual checker against the worktree ontology after applying each area batch entirely in memory. It never calls `put`, `commit`, `Editor`, a git adapter, a subprocess or a repository writer. Proposed physical KB files are serialized only to memory strings. It checks unique addresses, field contracts, kinds/layers, links, expressions, flow, decisions, evidence, terms, removed ledgers and lints through the checker, and verifies no original address, answer or agreement disappeared.

Result: **all five batches introduce zero additional findings; all 925 existing entries/parts and their answers/agreements are preserved.** The validation source cannot resolve historical `doc:` revisions without git, so its baseline contains three `missing-doc` findings. They remain unchanged; this is not a claim that the live repository passes a full git-backed check. Missing proofs/implementation remain work left rather than fabricated proof references. No official `ogy check`, landing/base comparison, write lock, browser test or source-code gate was run. The eventual coordinator must revalidate against current state before writing and run the repository's required checks after implementation.

## 5. Agent parity and MCP

Recommend `ogy show <address> --view-model --context pinned --detail contract` as a new mode on the existing entry read. It returns the semantic inspection envelope above, without HTML, output files or a server process. The existing `show` MCP tool gets corresponding arguments through the same CLI parser/operation. Context/detail options select semantic facets; output is machine-readable. Optional `--change <json>` supplies the same serialized draft records accepted by the board preview; it implies inspection mode and performs no write. `--context`, `--detail` and `--layer` also imply inspection mode; reject conflicting or unknown inputs. The request's revision comes from the existing global `--rev`; `--layer` is validated against the descriptor. This command mode is **proposed**: the inspected [cli.py:69][show-parser] currently accepts only the address for `show`.

No new `view` MCP tool. The inspected [mcp_server.py:29][mcp-no-tool] currently excludes only `mcp/init/hook`, so its automatic tool generation still needs an explicit `view` exclusion, annotation/tool-library updates and the B4 rule revision. This is a concrete discrepancy with the proposed [◇ delivery contract][d-command], not a completed implementation.

Before that mode is built, existing reads provide factual parity: `find` discovers addresses, `show` returns exact records/parts/links, `diagram` exposes declared workflow flow, and `impact` returns forward/reverse reach. They do not yet promise the same contextual model or preview envelope. Do not describe ordinary impact as a validated hypothetical change plan. The preview handler must share the pure option/record planning engine with any later answer delta, rather than asking an AI to invent authoritative links.

Parity acceptance is equality of stable semantic fields, fact IDs, availability and witnesses for the same snapshot/request, ignoring transport serialization and screen geometry. Expose the same contract/ontology identities so the agent can reproduce the board's view. A browser adapter and the `show` mode call `inspection-data`; neither owns a second purpose/flow algorithm. All-kind search includes nested parts even when they have no canvas block. Walk observations record selected paths and assumptions, not execution success.

Coverage is over product step addresses and `interface.form/serves/offers`, rather than a count of screens. Read-only first-board scope covers inspection/walk/preview. Missing review/answer web coverage stays visible as work with the first-board decision as its reason; it is not silently exempted or treated as delivered. Server startup, file export and hook/bootstrap commands are transport/lifecycle operations, with deliberate exemptions owned by the existing command/first-board decisions. A details interface serving no step uses `allows`; that is not evidence that a product workflow was delivered.

## 6. Ordered work to schedule in beads

These are proposed bead inputs requested by the owner, not issues created by this task. The coordinator should create actual beads with these dependencies and scenario text, rather than treating this document as the tracker.

| Order / category | Proposed work item | Acceptance to carry into the bead |
|---|---|---|
| 1 — KB capture | Put the B1–B5 proposals and requirements in area order, using the normal checked writer | Given the current KB, when each batch is checked and put, then no existing entry/part/answer disappears, no duplicate fact owner is introduced, all links resolve and unresolved decisions remain proposals. Re-read changed entries; report work left accurately. |
| 2 — Owner decisions | Review the common goal and composition, choose agent access, explicitly reconcile `no-views`, choose delivery defaults and the first-version write boundary, and review the command-description option | Given these decision entries, when the owner answers, then each selection and hedge is recorded by the normal answer/reply path with a paraphrase. No new design is called accepted before that answer. Exact hint fields may be deferred without blocking the adapter. |
| 3 — Code: `src/ogy/viewdata` export | Replace lossy board export with a versioned snapshot/descriptor adapter | Given quantity/setting/dependency/decision data and nested effects, when exported, then exact scalar names, full sentences, answer/proposal provenance, part addresses and availability survive; unknown fields are explicit, never guessed. Include ontology and KB content identities. |
| 4 — Code: pure `viewdata` models and existing reads | Implement typed query/model derivation and the chosen `show` mode using one core operation | Given the same request through board-data and CLI/MCP show, then semantic results match. Given multiple goals, recursive calls, missing purpose and read/tell on one actor, then witnesses and distinctions survive without invented paths. Given a draft, preview is validated in memory and does not change the KB. |
| 5 — Code: `src/ogy/view_assets` composition | Port the scratchpad prototype into kind recipes, shared families/context adapters and the mention path | Given every exported kind and supported context, then dispatch is defined or explicitly unsupported; tooltip/pinned share details, all structured names have the canonical linked icon/title, enums/literals stay exact, and a nested search result navigates to its part. Reuse lab29 findings as evidence, not a blanket proof. |
| 6 — Code: local reveal, canvas and walk | Connect readable local detail, typed relation accounting, history of camera/selection, and inspection-only walk | Given hidden/filtered/recursive parts, when detail changes, then every original fact remains inspectable exactly once in relation accounting, hidden hit targets disappear, Back restores focus, and a call continues only through the selected covered end. Narrow view can use the inspector. |
| 7 — Code: server and delivery | Wire a loopback HTTP adapter and standalone export around the same engine after delivery/no-views answers | Given reload after a KB change, then the content identity/model updates together. Given `--help`, then no server/file/write starts. Given MCP tool discovery, then `view` is absent and `show` inspection is present. First read-only board has no answer endpoints. Later deliberate-answer endpoints get their own bead and stale-preview checks. |
| 8 — Checks / gate | Implement scenario proofs, form-specific coverage and descriptor/recipe coverage; update import-map enforcement | Given a deliberately wrong label, bypassed mention, unsupported kind fallback, duplicated/dropped fact or forbidden import, then the relevant check fails before the defect is removed. Run the project gate, KB check and required dropped/waiting handoff in the authorized implementation session. Do not add a test for every CSS value. |
| Separate, after exact approval — Ontology | Implement optional hint fields and validation | Given absent hints, old descriptors still render; given invalid paths/executable values, validation refuses them. Extend the tool-library fixture and loader tests and name the eval in the ledger, or explicitly mark the ontology proposal untested. No ontology edit belongs to the viewer spike. |

The proof scenarios follow the actual data/interaction risks rather than mirroring function structure. No bead, built record or proof was created here. The source [README:293][where] assigns shape to the ontology, agent procedure to the skill and machine checks to the checker; [AGENTS.md:6][agents] requires an eval or explicit untested status for ontology/checker/skill changes. The hint extension remains **untested and proposed**.

## Sources

All ontology citations below name the authorized worktree. KB citations name the live main checkout. File-line links are evidence, not new KB references or generated `src` values.

[o-layers]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/ontology.yml:7
[k-interface]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/interface.yml:20
[k-flow]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/workflow.yml:9
[k-attribute]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/attribute.yml:11
[k-attribute-parts]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/attribute.yml:7
[k-decision]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/decision.yml:10
[k-capability]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/capability.yml:10
[k-capability-realizes]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/capability.yml:16
[k-goal]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/goal.yml:9
[k-rule]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/rule.yml:3
[k-handler]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/handler.yml:10
[k-dependency]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/dependency.yml:3
[k-setting]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/setting.yml:3
[k-quantity]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/quantity.yml:3
[k-enum]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/ontologies/software/kinds/enum.yml:14
[kind-loader]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/kinds.py:286
[d-hints]: /home/iorlas/Workspaces/ogy/docs/kb/software/ontology/decision/view-contract.yml:16
[d-style]: /home/iorlas/Workspaces/ogy/docs/kb/software/ontology/decision/style-book-home.yml:16
[d-map]: /home/iorlas/Workspaces/ogy/docs/kb/product/inspection/decision/product-map.yml:34
[d-modes]: /home/iorlas/Workspaces/ogy/docs/kb/product/inspection/decision/map-modes.yml:23
[d-interface]: /home/iorlas/Workspaces/ogy/docs/kb/software/cli/decision/viewer-is-an-interface.yml:13
[d-why]: /home/iorlas/Workspaces/ogy/docs/kb/software/ontology/decision/derive-justification.yml:16
[d-no-views]: /home/iorlas/Workspaces/ogy/docs/kb/software/cli/decision/no-views.yml:19
[d-command]: /home/iorlas/Workspaces/ogy/docs/kb/software/cli/decision/view-command-contract.yml:4
[d-name]: /home/iorlas/Workspaces/ogy/docs/kb/software/cli/decision/product-map-command.yml:4
[d-first]: /home/iorlas/Workspaces/ogy/docs/kb/product/inspection/decision/board-answers-in-v1.yml:4
[d-human]: /home/iorlas/Workspaces/ogy/docs/kb/product/inspection/decision/human-decision-mode.yml:1
[e-inspect]: /home/iorlas/Workspaces/ogy/docs/kb/product/inspection/workflow/inspect-kb.yml:1
[e-cap-inspect]: /home/iorlas/Workspaces/ogy/docs/kb/product/inspection/capabilities.yml:1
[e-owner]: /home/iorlas/Workspaces/ogy/docs/kb/product/shared/actors.yml:1
[e-agent]: /home/iorlas/Workspaces/ogy/docs/kb/product/shared/actors.yml:11
[show-parser]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/cli.py:69
[mcp-no-tool]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/src/ogy/mcp_server.py:29
[put-reader]: /home/iorlas/Workspaces/ogy/src/ogy/put.py:24
[put-drop]: /home/iorlas/Workspaces/ogy/src/ogy/put.py:152
[architecture]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/docs/agents/architecture.md:1
[where]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/README.md:293
[agents]: /home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9/AGENTS.md:6
