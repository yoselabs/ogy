# The ogy board: action plan

For the coordinator. Companion to `critique.md` in this folder; "F12" means finding 12 there. Paths without a root are in the worktree `/home/iorlas/Workspaces/ogy-e7ef37fafaf0a2b7/ontology-graph-visualization-87d2a9`.

**Decision: wipe the front end and restart; keep the server and the inspection document.** One answered KB decision stands in the way (`product-map`: canvas) and is owner question 1 below. Stages 0 to 6 do not depend on his answer, so work starts now; stage 7 (the Map replaces the canvas) waits for it.

## (a) How to think about this UI

Twelve principles in priority order. When two conflict, the lower number wins.

| # | Principle | The test that says it is met | What it cuts |
|---|---|---|---|
| 1 | **What waits is never more than one glance away.** | On every view, at 1440 and 390 px, the header shows the waiting count and it equals the number of decisions whose computed status is "question waiting". One click or `g w` lists them. | Any home view that does not show the count. |
| 2 | **The picture never says more than the KB.** | A sketch has the sketch treatment and the word "sketch"; a computed fact has the computed style; an agent's framing appears only in the Agent tab; no success colour on any path that covers a failure end (DOM check: an edge whose case covers an end with `result: failure` has class `after-failure`). | Role-coloured borders on real entries; green everything. |
| 3 | **Questions first, graph second.** | Each primary view answers one question written in its spec: Map "what is this product and where is trouble", Area "why does each flow exist", Flow "what happens and how can it end", Decide "what do I choose and what does it change". A reviewer can answer that question from a screenshot in ten seconds. | The everything-canvas, the five layout tabs. |
| 4 | **One name, one icon, one component per thing.** | A test collects every rendered kind word and relation word and fails on any word not in the ontology or the viewer's fixed command list; every kind has a glyph no other kind or control uses; every entry mention in the DOM is produced by one function (`data-renderer="mention"` on all of them, and no entry name outside one). | "internal relations / relation group / link"; bolt for three things. |
| 5 | **Compact: icon, title, corner kind word. The rest on demand.** | At level 1 a card or row has at most: icon, title, kind word, status marks. No count-only text ("Reads: 3") anywhere. | Count rows, sentence walls, "More steps and ends". |
| 6 | **Nothing overlaps, nothing is struck through, nothing jumps.** | The overlap script in (d) returns `blockOverlaps=0 textRunsCrossedByEdge=0 blocksEnteredByEdge=0 labelsOnBlocks=0` on all three data sizes; selecting anything leaves every other element's rectangle unchanged (compare rects before and after a click). | Hand-written routing; panels that push the board. |
| 7 | **Levels change content, not size.** | Text is never rendered below 11px or above 24px at any level (computed-style scan). Switching level changes which fields render; hidden parts leave a count that opens them; edges between hidden parts appear as one labelled edge. | Free zoom, scaled text. |
| 8 | **Colour is for status only.** | Green, red, amber appear only on elements with a status class (success, failure, waiting/owed). Area and kind are told by label and icon. Every text pair is at least 4.5:1, lines 3:1, in both themes. | Area-coloured headers, "Colour: by…" select. |
| 9 | **Every click lands where it looks like it will, with a real mouse.** | All acceptance checks use `Input.dispatchMouseEvent` / `dispatchKeyEvent`; no `element.click()`. Every control has one result; no control is shown that does nothing. | Pin vs open; dead Back. |
| 10 | **The phone is the same product in one column.** | At 390×844: no horizontal scroll, no element over another, every kind reachable from the home without search, the rail is a bottom sheet. | A separate phone index. |
| 11 | **The agent points with the same pieces.** | A spotlight renders with the same card and flow components (no spotlight-only card markup); targets get a number and one neutral highlight; the owner can dismiss and the view returns to the exact prior route. | The mock's separate page and look. |
| 12 | **A write shows its exact record before and after.** | Before Record: the option, the paraphrase and the note are visible as they will be stored. After: the read-back line "Recorded: … You said (paraphrased): …" with Undo offered as a new answer, never an edit. | One-click "keep", silent promotion. |

## (b) The decision and the information architecture

**Wipe and restart the front end.** Reasons are in the critique's verdict. The right-hand column is removed in stage 7, after the owner answers question 1; until then the existing canvas stays reachable at `#/board`. I listed `js/canvas` and `js/render` (14 files, 542 lines) but did not read them; the worker of stage 2 reads them before touching anything. What stays and what goes:

| Keep | Drop |
|---|---|
| `src/ogy/web/serve.py`, `api.py`, `cache.py`, `boundary.py`, `token.py` | `src/ogy/web/static/js/canvas/*` (camera, layout, levels, pack, scene) |
| `/api/inspection` schema 2, `/api/entry/{address}`, `/api/version` | `render/cards-*.js` as written (port ideas, not code) |
| `js/api.js`, `js/model/adapt.js`, `js/model/descriptor.js`, `js/state.js` | lab layout and edge code, drag, pin/open buttons, Relations list |
| `scratchpad/s3-data-check.mjs` (its server helper does the token exchange) | |
| Icon paths (after de-duplication), lab28 neutrals and note colours as tokens | Colour and arrow selects, the five layout tabs, the chat mock |
| The CDP real-input harness (`scratchpad/qa30/cdp.mjs`) | Hover cards that repeat the rail |

**Information architecture.** Layer → area → entry → part.

- **Routes** (hash routes, the whole view state):
  - `#/` Map, product layer. `#/software` Map, software layer.
  - `#/<layer>/<area>` Area page.
  - `#/<layer>/<area>/workflow/<id>` Flow page. `#/<layer>/<area>/entity/<id>` Lifecycle page.
  - `#/<address>` for any other entry: an entry page (header, sentence, relations as sentences).
  - `#/waiting` the waiting list. `#/<decision address>` the decision page.
  - Query: `?level=1|2|3`, `?sel=<address>` (what the rail shows), `?rail=details|waiting|agent`.
- **Shell.** Header line (KB name, worktree or commit, updated time, layer tabs, search). Status strip (waiting, owed, unagreed, changed, dropped: each a count and a link). Breadcrumb. Main column. Right rail with three tabs.
- **Map.** Grid of area tiles: name, sentence, goals as lines, counts as links, status marks.
- **Area.** Why-chain table (goal | capability | workflow with a flow strip). Then entities with state strips, then the other kinds as collapsed rows with counts.
- **Flow.** ELK layered, left to right. Step node: icon, name, corner word, actor chip, effect badges at level 2. Edges: `then` plain; case and choice edges labelled with their condition; edges after a failure end red and labelled. Ends at the right, success above failure. Call step: "RUNS ⤳ Notify" and "THEN, BY HOW IT ENDED" with one edge per covered end. Under the graph: the entities this flow touches, each with the effect badges that touch it.
- **Lifecycle.** States as nodes, transitions as edges, each edge labelled with who fires it as a path (Borrow › Record › otherwise). A transition nobody fires is amber, dashed, tagged "owed", and listed in the owed list.
- **Decide.** Waiting list grouped by area with multi-select. Decision page order: status line; question; why it is asked (context); options as radio choices, each with "sets" and "potentially affects"; proposal with its reason and, if present, "You said (paraphrased): … Read as B."; answer history with paraphrase and note; the answer form.
- **Rail.** Details (selected entry, same order as its page, shorter). Waiting (same list, compact). Agent (spotlight title, numbered targets with the agent's sentence, Back / Next / Dismiss, connection state).
- **Sketch treatment.** Dashed 1.5px border, 45° hatch at 6% ink, corner word "sketch", violet agent mark. Never green, red or amber.

## (c) Build plan

Sixteen stages, each one Codex run. Each lists what a machine checks, what a person looks at, the findings it closes and what it leaves. Rules that bind every stage: `just check` and `just test` green; no `subprocess` in `src/` or `tests/`; 400 lines per source file, 80 per function; no commit without the owner's word; every change names its eval in `evals/ledger.md` or says it is untested; read `docs/agents/python.md`, `testing.md`, `architecture.md` before the matching work.

Order and gates: 0 → 1 → 2 → 3 → 4 → 5 → 6, then **owner question 1**, then 7 to 15. Stages 8 and 13 can run beside their neighbours.

### Stage 0. The QA gate

**Goal:** one command that later stages run, so that "it looks fine" is never the evidence.

**Brief for the worker (complete; S = the session scratchpad that holds `qa30/`):**

1. Create `S/board-qa/` (outside the repository). Copy `S/qa30/cdp.mjs` to `board-qa/cdp.mjs`. Change it so that: the output folder comes from `process.env.OUT`; a scene's `url` is used as given (today it builds a `file://` URL from `src`); a new action `{"media":"dark"|"light"}` calls `Emulation.setEmulatedMedia` with feature `prefers-color-scheme`; the profile folder is removed with `{recursive:true, force:true, maxRetries:5}`.
2. The board is served by `ogy serve`, which prints a one-use exchange URL. Read `S/s3-data-check.mjs`: its server helper starts the server for a given KB and returns that URL. Reuse that helper unchanged (import it or copy the function); do not open any credential file.
3. Create `board-qa/measures.js` exporting strings for `Runtime.evaluate`:
   - `OVERLAP`: the script in section (d), verbatim, with its two selector constants.
   - `TEXT`: over every element that has its own text node, return the minimum and maximum computed `font-size` and the number of distinct sizes.
   - `VIEWER_WORDS`: the page's text with authored KB text removed: clone `document.body`, delete every element matching `[data-authored]`, return `innerText`. (From stage 2 on, every piece of text that comes from a KB field is rendered inside an element with `data-authored`. On today's page nothing is marked, so the baseline run reports authored words too; that is expected.)
4. Create `board-qa/forbidden.txt`, one regular expression per line: `\bexport`, `offscreen`, `edge:\d`, `representatives`, `assertions`, `direction:`, `not exported`, `declaration`, `\bundefined\b`, `\bnull\b`, `\bNaN\b`, `\[object`, `relation group`, `internal relations`, `\b1 (steps|ends|cases|choices|options)\b`, `\bmock\b`, `simulat`.
5. Three data sets, each a folder that `ogy --repo <folder> serve` accepts: (a) `tests/fixtures/tool-library` in the worktree; (b) the worktree itself; (c) a synthetic KB of about 5,000 entries in a temporary folder: start from a copy of (a) made with ordinary file copy, then add areas `lending-02` … `lending-55` by reading each entry of `product/lending` with `ogy show --rev .` (or the library call behind it) and writing it under the new area with `ogy --repo <tmp> put` batches, one batch per area. Never write KB YAML by hand. If one area takes longer than 20 seconds or `put` refuses, stop and report the refusal text; do not work around it.
6. Create `board-qa/scenes.json` with one scene per data set for now: the home URL, wait 3 s.
7. Create `board-qa/run.mjs`: for each data set × {1440×1000, 390×844 with `mobile:true`} × {light, dark}: start the server, run the scenes, save a screenshot per scene as `<set>-<width>-<theme>-<scene>.png`, evaluate the three measures, test `VIEWER_WORDS` against `forbidden.txt`, stop the server. Write `results.json` and print one line per run. Exit 1 if any run has: `blockOverlaps>0`, `textRunsCrossedByEdge>0`, `blocksEnteredByEdge>0`, `labelsOnBlocks>0`, minimum font size under 11, more than 5 distinct sizes, or a forbidden word.
8. Run it against today's page and save the output as `board-qa/baseline.txt`.

**Machine acceptance:** `node board-qa/run.mjs` exits 1 on today's board and the output names at least one concrete failure per data set; pointed at a blank page with one 16px heading it exits 0.
**Look at:** `baseline.txt` and the twelve screenshots.
**Closes:** F118. **Provides the checks for:** F33 to F36, F74, F89.
**Deferred:** the contrast measure (stage 2, when tokens exist).

### Stage 1. Standing facts over the API

**Goal:** the page can know what waits, what is owed, what is unagreed and what was dropped without re-deriving it in JavaScript.

**Why a separate route and not a key in the inspection document:** `inspect()` in `src/ogy/inspect.py` promises "without I/O, guessed labels, graph derivation"; dropped items need the removed ledger and work needs built records. So: a new route.

**Brief for the worker (complete):**

1. Read `src/ogy/web/api.py`, `src/ogy/web/cache.py`, `src/ogy/commands.py` lines 36 to 95, `src/ogy/ops.py` (`run_status`, `run_work`, `run_dropped`, `run_show`), `src/ogy/wire.py` (`status`, `work`, `dropped`: how the agent's lines are built from the values), `src/ogy/terms.py` (`waiting`), and `docs/board-data.md`. Import contracts in `pyproject.toml` allow `ogy.web` to import `ogy.ops`; nothing below `ogy.web` may import starlette.
2. Add `src/ogy/web/standing.py` with one function `standing(target) -> dict` that calls `ops.run_status(target, None, with_coverage=False)`, `ops.run_work(target, None)` and `ops.run_dropped(target)` and returns plain JSON:
   - `totals`: `{waiting, owed, unagreed, changed, dropped, findings}` (waiting = questions open summed over areas; owed = number of work items; unagreed = entries decided by AI; changed = entries changed since agreed; dropped = number of dropped items; findings = number of check findings).
   - `areas`: one object per `<layer>/<area>` with the same numbers the status line prints for it.
   - `decisions`: a map from decision address to `{status: "waiting"|"answered", chose, at, delegated}` where `delegated` is the address of the delegating decision or null. Take the status from the same code that prints "status (computed)" in `ogy show` (find it from `ops.run_show` and `src/ogy/show.py`); do not write a second rule.
   - `entries`: a map from address to `{source: "owner"|"ai"|"docs"|"code", changed: bool}` for every entry the status overview classifies. If the overview holds only counts, extend the function that computes it to also return the addresses (one owner per fact), and keep the CLI output byte-identical.
   - `work`: `[{address, cause, text}]`; `dropped`: `[{address, text}]`.
   - `computed: true` and `version`: the inspection snapshot version it was computed for.
3. Add `Route("/api/standing", …)` in `api.py` using the same `response(...)` helper (ETag from the version) and the same repository lock path as `inspection`. Cache it in `InspectionCache` keyed by the same input signature if that is a small change; otherwise compute per request and say so in the doc.
4. Tests (pytest functions, in `tests/test_web.py` or a new `tests/test_web_standing.py`, under 800 lines): on the tool library fixture, `totals` equal the numbers obtained from the three `ops` calls; `product/lending/decision/fee-rounding` is `answered`, `chose` ends with `/option/up`, `delegated` is `product/lending/decision/fee-details`; every decision entry has a row; the route answers 304 to a matching `If-None-Match`; a second request after adding an answer in a temporary copy returns a different version.
5. Update `docs/board-data.md` (a short section "Standing"). Add the eval line to `evals/ledger.md` or write "untested" with the reason.
6. Do not touch `src/ogy/web/static/`.

**Machine acceptance:** `just check && just test` green. On this KB, `GET /api/standing` gives `totals.waiting` equal to the sum of "questions open" in `just ogy status` (3 on 22 November: re-read at run time), `totals.owed` equal to its "work left" line, `totals.dropped` equal to its "dropped" line.
**Look at:** the JSON rows for `product/inspection/decision/show-what-does-not-exist-yet` (waiting), `software/cli/decision/view-topology` (answered), the tool library's `fee-rounding` (answered, delegated).
**Closes (data side):** F1, F4, F10, F11, F16, F18, F98, F104.
**Deferred:** option reach (stage 6).

### Stage 2. Shell and tokens

**Scope:** new `static/index.html`; `js/shell/router.js` (hash routes from section (b)), `header.js`, `status-strip.js` (reads `/api/standing`), `breadcrumb.js`, `rail.js` (three tabs, empty for now); `js/ui/mention.js` (the one function that renders an entry mention, `data-renderer="mention"`), `js/ui/card-header.js` (icon, title, corner kind word, status marks), `js/ui/authored.js` (wraps KB text in `data-authored`); `assets/board/tokens.css` (five type sizes 11/13/15/18/24, 8px grid, lab28 neutrals, status colours, light and dark). De-duplicate `js/model/icons.js`: no two kinds and no control share a glyph. The existing canvas scene is mounted unchanged at `#/board` and stays the default route. Add the contrast measure to `board-qa`.
**Machine acceptance:** gate from stage 0 green for the shell elements (the canvas route is excluded until stage 7); header counts equal `/api/standing` totals; the rects of all header controls are identical on every route; contrast ≥ 4.5:1 for all shell text in both themes; no horizontal scroll at 390 px; Tab reaches header, main, rail in that order with a visible 2px focus ring.
**Look at:** the shell on `#/board` and on an unknown route (the "not found" state), 1440 and 390, light and dark.
**Closes:** F17, F18, F35, F38, F39, F40, F43, F45, F47, F53, F54, F66, F73, F87, F113, F116, F120.
**Deferred:** content of the rail tabs.

### Stage 3. The Waiting list

**Scope:** `js/views/waiting.js` at `#/waiting` and the same list, compact, in the rail's Waiting tab. Grouped by layer and area; each row: decision icon, title, first line of the question, age. Keyboard: `g w` opens it, `j`/`k` move, `Enter` opens. Empty state: "Nothing waits for you."
**Machine acceptance:** rows equal the decisions with `status: waiting` in `/api/standing`, on all three data sets; real-mouse click on a row changes the route to that decision's address; browser Back returns with the same row focused; at 390 px the list is one column and the rail is a bottom sheet that does not overlap content (overlap script zero).
**Look at:** this KB (3 rows), the tool library, the empty state, the 5,000 set, both themes.
**Closes:** F1, F50, F55, F61, F71 (this view), F117 (lists).
**Deferred:** multi-select answers (stage 5).

### Stage 4. The decision page, read-only

**Scope:** `js/views/decision.js`. Order: status line; question; "Why this is asked" (context); options as a radio group, each with its label, sentence and "sets" (authored); the proposal with its reason and, if `heard` is present, "You said (paraphrased): … Read as <option>."; answer history, newest first: date, option, "You said (paraphrased): …", the note in amber, "given for you under delegation" where `delegated` is set. Every option and every address is a mention.
**Machine acceptance:** for every decision of the three data sets the page renders without a forbidden word; an answered decision's first line contains the chosen option's label and the date; exactly one option has the chosen mark when answered, none when waiting; `product/inspection/decision/map-layers` shows the note containing "Yes, I guess"; the tool library's `fee-rounding` shows the delegation line.
**Look at:** a waiting one, an answered one, a hedged one, a delegated one, one with ten options (find the largest in `software/ontology`), at both sizes.
**Closes:** F2, F3, F4, F78, F100, F106, F108, F109 (display), F110, F111.
**Deferred:** answering (stage 5), reach (stage 6).

### Stage 5. Answering on the board

**Scope:** one write route, `POST /api/answer`, that calls the same operation `ogy answer` uses (find it from `commands._answer` → `ops`), under the repository lock, with the inspection version as a precondition (refuse when stale). Fields: decision, option, `said` (required), `note` (optional), `where` (form per owner question 4). The form on the decision page; "yes to all proposals" and per-row answers on the Waiting list for a review round, through the reply operation. After Record: the read-back line and a link "Not what I meant" that opens the form again (a new answer, never an edit).
**Machine acceptance:** on a temporary copy of the tool library with one waiting decision: real-mouse choose, type, Record → `ogy show` prints that answer and `said`; the waiting count drops by one without reload; a second page holding the old version gets the refusal text and writes nothing (compare inspection version); a request without `said` is refused with 4xx; `just check && just test` green with tests for the route.
**Look at:** the form before Record, the read-back after, the refusal.
**Closes:** F101, F105, F109, F112.
**Deferred:** none.

### Stage 6. What an option reaches

**Scope:** `/api/standing` (or a sibling route) gains, per option, `reach`: the addresses `ogy impact` returns for what the option sets. Rendered under each option as "potentially affects", in the computed style, collapsed above five.
**Machine acceptance:** for a fixture decision whose options set different addresses the two lists differ and equal the `ops` impact call.
**Look at:** two options side by side at 1440, stacked at 390.
**Closes:** F107.

### — Owner question 1 is answered here. Stages 7 to 15 assume (b). —

### Stage 7. The Map replaces the canvas

**Scope:** `js/views/map.js` at `#/` and `#/software`: area tiles (name, sentence, goals as lines, counts as links, status marks from `/api/standing`). Delete `js/canvas/`, the `#/board` route and the lab-derived card renderers that nothing imports.
**Machine acceptance:** tile count equals the number of areas per layer; each tile's counts equal the entries of that area; every kind is reachable from the home in at most two clicks at 390 px; gate green on all twelve runs; first render under 300 ms on the 5,000 set (`performance.now()` around the view's render).
**Look at:** both layers, both themes, phone; an area with no goals.
**Closes:** F6, F9, F19, F22, F26, F27, F29, F34, F36, F37, F41, F42, F51, F52, F57, F58, F59, F60, F65, F67, F72, F88, F96, F115.

### Stage 8. Search

**Scope:** overlay on `/`: matches title, question, key, address, sentence; grouped by kind with counts; parts show their owner path; 20 rows per group then "more"; Enter navigates to the entry's route.
**Machine acceptance:** `topology` finds `software/cli/decision/view-topology`; `decision mode` finds `human-decision-mode`; a state name shows its entity; under 50 ms per keystroke on the 5,000 set.
**Closes:** F31, F48, F62, F63, F64, F85.

### Stage 9. The Area page

**Scope:** `js/views/area.js`: the why-chain table (goal | capability | workflow); a flow strip per workflow (step dots, end marks by result, status marks); entity state strips; the other kinds as collapsed rows with counts.
**Machine acceptance:** every workflow of the area appears exactly once and in the row of the goal its capability realizes; one without a capability is under "No goal recorded" in amber; overlap script zero; no text under 11px.
**Look at:** `product/review`, `software/cli`, the tool library's `product/lending`.
**Closes:** F7, F8, F10, F20, F30.

### Stage 10. Flow page: layout and edges

**Scope:** vendor `elkjs` (worker build) under `static/vendor/` (owner question 3); `js/graph/elk-layout.js` (layered, direction right, orthogonal routing, one port per outgoing case or choice), `js/graph/edges.js` (one SVG layer under DOM nodes, selector `.edge-layer path`), `js/views/flow.js` at level 1: step and end nodes with the card header only; `then` edges; case and choice edges labelled.
**Machine acceptance:** on every workflow of the three data sets: `blockOverlaps=0`, `textRunsCrossedByEdge=0`, `blocksEnteredByEdge=0`, `labelsOnBlocks=0`; every edge's two end points lie on a node border or on a labelled stub; a three-step workflow fits 1,440 px without scrolling.
**Look at:** Borrow, Remove entry (six cases), Review and reply, Capture entries; phone (direction down).
**Closes:** F24, F44, F89, F90, F91, F92, F93, F94, F114.
**Stop rule:** if ELK cannot route a real workflow without entering a node, stop and report with the screenshot. Do not patch the router by hand.

### Stage 11. Flow page: levels, effects, calls, failure

**Scope:** the level control (1, 2, 3); effect badges (create: green edge on the badge; delete: red; write: each field named; transition: `from → to` tag); actor and interface chips; the call step with "RUNS" and "THEN, BY HOW IT ENDED"; the failure-path rule (an edge from a case that covers an end with `result: failure` gets class `after-failure`, the failure colour and a cross mark on its head; the end it reaches shows "also reached after <workflow> failed"); roll-up of edges between hidden parts into one labelled edge; the strip of touched entities under the graph; walk as a highlighted step with its choices as buttons in the rail.
**Machine acceptance:** in tool-library Remind the edge from case `otherwise` to end `done` has class `after-failure` and the failure token as computed stroke; switching level changes no computed font size; at level 1 no text other than header text is in a node; every count shown opens the things it counts; gate green.
**Look at:** Remind and Notify at the three levels; Borrow's Record step badges; lab28's reference sheet beside it.
**Closes:** F13, F14, F21, F23, F25, F46, F68, F95, F97.

### Stage 12. Lifecycle page and owed work

**Scope:** `js/views/lifecycle.js`: states as nodes, transitions as edges labelled with who fires them as a path (workflow › step › case); a transition nothing fires is amber, dashed, tagged "owed"; `#/owed` lists `standing.work` grouped by layer and cause; unagreed and changed marks on every card header and row.
**Machine acceptance:** the tool library's Loan `return` transition has class `owed` and appears in `#/owed`; every "fired by" is a mention path of at least two segments; the number of rows in `#/owed` equals `totals.owed`.
**Look at:** Loan, Entry, Decision (the entity), the owed list on this KB.
**Closes:** F11, F12, F16.

### Stage 13. Language pass

**Scope:** every rendered word comes from the ontology (kind and field words), from the entry (authored, marked), or from `js/ui/words.js` (the viewer's fixed list, under 60 entries). Relation lines are sentences built from kind files ("Borrow › Record creates Loan"). A key is never shown as a title when a sentence or label exists. Plurals. Help: six lines and the key list.
**Machine acceptance:** a test collects all viewer text on every route of the tool library and fails on any word outside `words.js` and the ontology's words; forbidden gate green; no "1 steps".
**Look at:** help; an actor page; a decision whose options are named by key.
**Closes:** F74, F75, F76, F77, F79, F80, F81, F82, F83, F84, F86.

### Stage 14. Spotlight

**Scope:** per the answers to owner questions 6 and 9: a push channel (server-sent events) from `ogy serve`; one MCP tool that sets a spotlight (title, ordered targets with one sentence each); the Agent tab (title, numbered targets, Back / Next / Dismiss, connection state); on the page the targets get a number and one neutral highlight, the rest dims to 45%.
**Machine acceptance:** an MCP call changes an open page within 250 ms locally without reload; no element carries a spotlight-only card class (targets are the same components); Dismiss returns the exact prior route and scroll position; the inspection version is unchanged after show and dismiss.
**Look at:** a decision spotlight with four targets on desktop and phone.
**Closes:** F15, F28, F56, F69, F70, F99, F103, F121.

### Stage 15. Sketch

**Scope:** per the answer to owner question 5: one MCP tool that shows a sketch (entries in the `put` format, never written); drawn by the flow renderer in the sketch treatment; "would touch" rows from the impact operation; "Keep" opens the stage 5 form for a proposal on a decision.
**Machine acceptance:** sketch nodes have the sketch class and none of the status colours; after show and dismiss the inspection version is unchanged; after Keep, `ogy show` on the decision shows the proposal and nothing else changed.
**Look at:** a sketched three-step workflow with what it would touch.
**Closes:** F5, F102.
**Deferred:** three alternatives side by side, until the owner has used one sketch.

### Check: every finding has a home

All of F1 to F121 are named in a stage above except these, which are closed as follows:
- F32 (colour system): stage 2 tokens and principle 8's check (status colours only on status classes); also owner question 7.
- F33 (contrast): the contrast measure added in stage 2, run in every later stage.
- F49: the legend is gone with stage 7; status marks are explained in help (stage 13).
- F71 (empty, loading, error): each stage's "look at" list must include them; stage 3 shows the pattern.
- F119 (rendering helper and build): owner question 3.

## (d) Standing QA protocol

Run all of it before the owner sees anything. One command: `node board-qa/run.mjs`.

1. **Real input only.** Mouse and keys through `Input.dispatch*`. Move before every press. Never `element.click()`, never calling app functions.
2. **Sizes:** 1440×1000 and 390×844 (mobile emulation on). **Themes:** light and dark. **Data:** tool library (about 90 entries), this KB (about 850), synthetic (about 5,000). That is 12 runs.
3. **Forbidden words:** the viewer's text of every scene (authored KB text removed by its `data-authored` mark) against `forbidden.txt`. Zero hits.
4. **Overlap measure** (run in the page; the four counts must be 0). This is the script that produced the lab31 baseline; only the two constants change with the build:

```js
(()=>{const BLOCK="[data-local-id]";            // the build's top-level node selector
const EDGE="#vp path, #vp polyline, #vp line";  // the build's edge layer; must not match icons
const R=e=>e.getBoundingClientRect();
const vis=r=>r.width>2&&r.height>2&&r.right>0&&r.bottom>0&&r.left<innerWidth&&r.top<innerHeight;
const hit=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>2&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>2;
const blocks=[...document.querySelectorAll(BLOCK)].filter(e=>!e.parentElement.closest(BLOCK)).map(e=>[e,R(e)]).filter(x=>vis(x[1]));
let bb=0;for(let i=0;i<blocks.length;i++)for(let j=i+1;j<blocks.length;j++){if(hit(blocks[i][1],blocks[j][1]))bb++}
const texts=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
for(let n;(n=w.nextNode());){if(!n.nodeValue.trim()||!n.parentElement.closest(BLOCK))continue;const g=document.createRange();g.selectNodeContents(n);for(const r of g.getClientRects())if(vis(r))texts.push(r)}
const edges=[...document.querySelectorAll(EDGE)].filter(p=>!p.closest(BLOCK)&&!p.closest("defs")&&!p.closest("svg svg"));
const pts=[];for(const p of edges){const L=p.getTotalLength?p.getTotalLength():0;if(!L)continue;const m=p.getScreenCTM();
 for(let d=0;d<=L;d+=3){const q=p.getPointAtLength(d);pts.push([q.x*m.a+q.y*m.c+m.e,q.x*m.b+q.y*m.d+m.f])}}
let rt=0;for(const t of texts){if(pts.some(s=>s[0]>t.left&&s[0]<t.right&&s[1]>t.top+1&&s[1]<t.bottom-1))rt++}
let rb=0;for(const b of blocks){const r=b[1];if(pts.some(s=>s[0]>r.left+6&&s[0]<r.right-6&&s[1]>r.top+6&&s[1]<r.bottom-6))rb++}
const labels=[...document.querySelectorAll(".route-label")].map(R).filter(vis);
let lb=0;for(const l of labels)if(blocks.some(b=>hit(l,b[1])))lb++;
return "blocks="+blocks.length+" edges="+edges.length+" blockOverlaps="+bb+" textRunsCrossedByEdge="+rt+"/"+texts.length+" blocksEnteredByEdge="+rb+"/"+blocks.length+" labelsOnBlocks="+lb+"/"+labels.length})()
```

   lab31 baseline: tool library home `blockOverlaps=0 textRunsCrossedByEdge=3/48 blocksEnteredByEdge=7/11`; this KB's home `0, 4/146, 4/32`; this KB's Purpose layout `0, 1/146, 2/32`; an opened workflow `0, 0/64, 0/4`. Known limit: it sees only what is in the viewport, so run it per view after Fit, and it does not detect an edge lying exactly on a block border.
5. **Type:** minimum computed font size ≥ 11px, maximum ≤ 24px, distinct sizes ≤ 5; no title broken inside a word.
6. **Contrast:** every text element against its effective background ≥ 4.5:1; edge strokes ≥ 3:1; both themes.
7. **Stability:** record every visible element's rect, perform a selection, compare: only the rail's content may differ.
8. **One name:** the word test from stage 8.
9. **Signals checklist** (a person looks, on this KB, and ticks each; any blank is a stop):
   - The waiting count is visible and matches `just ogy status`.
   - Each waiting decision is one click away, with its question.
   - An answered decision says so first, with the option and the date; a hedge is visible.
   - Work owed is visible as a count and on the entries that owe it.
   - Unagreed and changed-since-agreed entries carry their mark.
   - A sketch cannot be mistaken for a recorded entry.
   - No failure path ends in a success colour.
   - The home says what the product does: area sentences and goals.
   - The agent's targets are numbered and its words are in the Agent tab only.
   - The header says which revision and when it was updated.
   - Dropped count is visible.
10. **Look.** Open every screenshot of the run. A gate that passes on an ugly page has a missing check: add the check, then fix the page.

## (e) Questions only the owner can answer

Each becomes a decision entry (or a new option on the existing one) through ogy before anyone acts on it; he is asked from `ogy review`, not from this list.

**1. Does the board stay a canvas?**
- Problem: `product/inspection/decision/product-map` is answered "canvas" (hedged). Four canvas generations produced overlap, struck-through text and merged arrows; the critique finds the cause in the paradigm (F19, F20).
- Options: (a) keep one pan-zoom canvas as the home; (b) Map and Area pages as lists and tables, with a drawn graph only for one workflow or one entity at a time; (c) both, canvas as an extra view.
- Recommended: (b).
- Why: position on a free canvas has no meaning in this data; the two real graphs are small enough to lay out without crossings; (c) doubles the work and keeps the faults.

**2. What is the home view?**
- Problem: the first screen must serve "what waits" and "what is this product".
- Options: (a) the Map with a status strip; (b) the Waiting list when anything waits, else the Map; (c) always the Waiting list.
- Recommended: (a), with the waiting count in the header and the Waiting tab one click away.
- Why: most visits are to look, and a home that changes by state is disorienting; the count keeps deciding in sight.

**3. May the front end vendor one small rendering library and elkjs?**
- Problem: the answer to `view-frontend-build` says "builds Tailwind CSS, bundles, ships static files" (reuse the a2kay setup, location unconfirmed); `docs/board-data.md` says plain ES modules, no bundler, standalone Tailwind. The two differ, and neither says whether third-party code may be vendored. Hand-written DOM updates and hand-written graph layout are where the faults came from (F113, F114, F119).
- Options: (a) no dependencies at all; (b) vendor `elkjs` only; (c) vendor `elkjs` and one rendering helper (`lit-html`, about 7 KB, no build step).
- Recommended: (c).
- Why: both are single files served as static assets, so it works with or without a bundler; layout is the one thing that must not be home-made again. Settle the bundler wording in the same answer.

**4. Is a click on the board the owner speaking?**
- Problem: `human-decision-mode`'s context says a deliberate Choose click can count; ogy requires a paraphrase (`said`) for every answer.
- Options: (a) option click plus a required paraphrase typed by him; (b) option click only, `said` filled with the option's label; (c) option click, paraphrase optional.
- Recommended: (a) with the field pre-filled by the option's label, editable.
- Why: the record keeps his words when he has any, and one Enter records the plain case.

**5. What does the agent's sketch become when he says "keep"?**
- Problem: `product/inspection/decision/show-what-does-not-exist-yet` waits (one of the three open questions). `staged-changes-home` says a staged change lives as a proposal on a decision.
- Options: (a) illustration only, nothing kept; (b) keep creates a decision with the sketch as its proposal; (c) both, keep is his explicit act.
- Recommended: (c).
- Why: showing must be free and write nothing; keeping must go through the same answer path with a read-back.

**6. How does the agent point?**
- Problem: `product/inspection/decision/agent-points-owner` waits (one of the three open questions).
- Options: (a) the page follows the agent at once (navigates and highlights); (b) the Agent tab shows a request "Look at …" and he clicks to go; (c) follow when the tab is idle, ask when he is typing or reading a decision.
- Recommended: (c).
- Why: being moved while answering a decision is how wrong answers get recorded.

**7. Do areas have colours?**
- Problem: area colour collides with status colour (F32).
- Options: (a) no area colour, name only; (b) a small swatch beside the area name, never a fill; (c) keep coloured headers.
- Recommended: (a).
- Why: he reads the name anyway; every extra hue weakens red, green and amber.

**8. Is dragging blocks wanted?**
- Problem: drag exists to "read under" overlapping blocks (F65).
- Options: (a) remove it; (b) keep it on the Flow page.
- Recommended: (a).
- Why: with no overlap there is nothing to read under, and a hand-placed layout is lost at the next change.

**9. How fast does the board follow the agent?**
- Problem: `software/viewing/decision/board-follows-agent-calls` waits (the third open question). `docs/board-data.md` says there is no streaming connection today; the spotlight needs one (F121).
- Options: (a) the page polls `/api/version` every few seconds; (b) the server pushes over server-sent events and the page shows the connection state; (c) push for spotlight and sketch, polling for KB changes.
- Recommended: (b).
- Why: one mechanism; "live" is the owner's word for the brainstorm, and a visible connection state is what makes a still page trustworthy.

**10. May the status overview return addresses, not only counts?**
- Problem: marks for "decided by AI" and "changed since agreed" need the entries, and today's status prints counts per area (stage 1, item 2).
- Options: (a) extend the one function that computes the overview so the CLI and the board read the same result; (b) compute it again in the web layer.
- Recommended: (a).
- Why: `one-owner-per-fact`; a second rule would drift.
