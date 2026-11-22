# The ogy board: design critique

22 November 2026. Reviewed: **lab31** (`lab31-tool.html`, 90 entries; `lab31.html`, the ogy KB, 845 entries), the newest prototype that exists; `spotlight-mock.html` (`?v=A`, `?v=B`); `design-views.md` (findings and terminology audit), `spotlight-design.md` (outcomes and section 1), `view-architecture.md` (section 1 only); the qa30 screenshots and the lab28 reference sheet; 21 KB decisions about the board; and the production start in `src/ogy/web/` (`api.py`, `inspect.py`, `index.html`, `main.js` read; the `js/canvas` and `js/render` files only listed: 14 files, 542 lines).

**Verdict in one line:** wipe the front end and restart from the questions the owner asks, not from a canvas. Keep the server, the inspection document, the real-input harness and the lab28 palette. Details in "Verdict" at the end; the build plan is in `action-plan.md` next to this file.

## How this was checked

- About 90 views captured into this folder; 45 of them looked at one by one, the rest read through the harness's text output. Every interactive one was driven with real mouse and keyboard through the DevTools protocol (the qa30 harness, output redirected here). Sizes: 1440×1000, 390×844, 820×1100. One dark-mode pass.
- Two measurements ran in the page: an edge-crossing count (edges of the edge layer only, icons excluded, against text runs and block interiors) and a contrast calculation. The edge script is reproduced verbatim in `action-plan.md`, section (d).
- File names below are in this folder unless a path says otherwise.

**Not verified** (marked again where it matters):

- Touch gestures (pinch, two-finger pan): no touch input was sent.
- The contrast of the faint arrows: estimated from the screenshots, not computed.
- Whether actors, entities and goals can be reached on a phone by zooming: after four wheel steps in at 390 px the DOM held workflow and step blocks only; other blocks may have been off screen (finding 51).
- 5,000 entries: no data set of that size exists; statements about it are extrapolation from 845.
- Screen-reader output: only the DOM was inspected.
- The Open button of the Record step in Borrow: my click landed outside the viewport, so finding 44 says "unreachable without panning", not "dead".
- The E1 effect badges (green create edge, red delete, field list): I never reached a view that shows them. Finding 13 says "not visible at any level I reached".
- Whether the URL updates on navigation: not tested.
- Loading and error states of the lab files (they are static files; the production `index.html` has one "Loading…" line).

## What the owner must know at a glance: shown, hidden or wrong

Ranked by importance. `ogy status` on the same KB prints most of these today in one screen of text, which is the bar the board has to beat.

| # | Question | The board | Evidence |
|---|---|---|---|
| 1 | What waits for me? | **Hidden.** The KB has 3 open questions; no view lists them, no count, no badge. | `02-ogy-default.png`, `69-ogy-wheel-out.png` |
| 2 | What would my decision change? | **Hidden.** The decision card says "Option effects and answer history are unavailable in this export." | `90-tool-decision.png` |
| 3 | Is this decision answered, and how? | **Wrong by omission.** Fee rounding is answered ("chose: up" is in the data); the card lists two options with no mark. | `90-tool-decision.png`, `99-relation-bundle.png` |
| 4 | What is only a sketch? | **Wrong.** The chat draft "Reserve a tool" renders as a solid card identical to real workflows. | `51-chat.png` |
| 5 | What does this product do and why? | **Hidden.** The home view is 32 unlabelled boxes; the goal → capability → workflow chain is never drawn as a chain. | `02-ogy-default.png`, `66-ogy-tab-why.png` |
| 6 | What is unbuilt, unfired, owed? | **Whispered.** "No recorded trigger" in 10px grey; `ogy status` says 253 items of work left and the board shows none. | `33-open-loan.png` |
| 7 | Which entries did the AI decide and I have not agreed? | **Hidden.** 37 entries decided by AI, 7 changed since agreed; no mark on any card. | all |
| 8 | What state is each workflow in? | **Hidden.** No status on a workflow card: only "3 steps · 2 ends". | `01-tool-default.png` |
| 9 | What is the agent pointing at? | **Only in a separate mock** with a different look; nothing in lab31. | `21-spot-A.png` |
| 10 | Did a path fail? | **Wrong.** Remind's failed Notify runs into a green "Done · result: success" on green arrows. | `93-open-remind-call.png` |
| 11 | What was removed or dropped? | **Hidden.** 85 dropped items; no trace. | all |
| 12 | Which revision am I looking at (worktree or commit), and is it live? | **Hidden.** | all |

Signals that exist: kind icon and kind word; area colour of a workflow (unlabelled); counts of steps and ends; success/failure tint on end cards; "No recorded trigger"; a relation count; selection outline. That is the whole list.

## Findings

Format: **severity** · where · what is wrong · why it matters · fix. Evidence in brackets.

### A. Purpose fit

1. **blocker** · every view · Nothing shows what waits for the owner. The KB has three open questions (`product/inspection` 2, `software/viewing` 1) and the board has no list, count or badge. · Deciding is the second of the board's three jobs and the owner already answered `answer-drawer` with "a drawer listing what waits, grouped by area". · Build the waiting list first, before any drawing. [`02-ogy-default.png`]
2. **blocker** · ogy KB, home · 116 decisions exist; zero are on the board. They appear only as "Decision: 21" and "Decision: 95" in 10px grey at the furthest zoom. · The most numerous and most important kind for the owner is invisible. · Decisions get their own primary view. [`69-ogy-wheel-out.png`, harness: `onboard=0`]
3. **blocker** · decision card · The card cannot show options' effects, the proposal's reason, answers, paraphrases or notes: "unavailable in this export". · The owner cannot decide from it; he must go back to the terminal. · The inspection document already carries the authored fields; render them. [`90-tool-decision.png`]
4. **blocker** · decision card · An answered decision looks the same as an open one. Fee rounding has `chose → up` (`ogy show` on the fixture: "answered …", given under a delegation); the card shows "Rounded up / Whole days only" unmarked and says nothing of the delegation. · He will answer twice or doubt the record; and an answer given for him is exactly what he must be able to veto. · Status line first: "Answered by you, 22 Nov: Rounded up", "Answered for you under delegation: …" or "Waiting for you". [`90-tool-decision.png`, `99-relation-bundle.png`]
5. **blocker** · chat draft · A sketched workflow and entity ("Reserve a tool", "Reservation") are drawn exactly like recorded ones: solid border, same colours, no word. lab28 drew them dashed. · The owner can no longer tell what exists. This is the one thing the brainstorm job must never get wrong. · One sketch treatment everywhere: dashed border, hatched fill, corner word "sketch", never success or area colours. [`51-chat.png`]
6. **blocker** · home, ogy KB · The first screen does not say what the product does. 13 workflow boxes in a grid ordered by nothing visible, entities and goals mixed into the same grid, no area names, no sentences. · "See and understand the product" is job one. · Home is a map of areas with each area's sentence, goals and counts. [`02-ogy-default.png`]
7. **major** · Purpose tab · "Purpose" re-sorts the same boxes into rows; it does not draw goal → capability → workflow. Arrows are faint and run through other cards. · The why-chain was an answered decision (`why-chain-on-board`). · Draw the chain as three aligned columns with one row per goal. [`66-ogy-tab-why.png`, `40-tab-why.png`]
8. **major** · By area, By actor tabs · On the tool library these two and Purpose give nearly the same picture: same rows, no group headings, no area or actor label. · Three tabs that change nothing teach the owner the tabs are noise. · A grouping must show its groups: a heading and a boundary per group. [`39-tab-area.png`, `40-tab-why.png`, `41-tab-actor.png`]
9. **major** · software layer · "Software: 4 workflows · 559 entries". 21 interfaces, 8 handlers, 50 rules, 5 dependencies and 95 decisions have no home on the board. · Two layer views with limits were answered (`map-layers`); the software view does not exist. · A layer switch at the top; each layer has its own area map. [`69-ogy-wheel-out.png`]
10. **major** · workflow card · No state on a workflow: not "complete", "has work owed", "has open question", "changed since agreed". · He cannot scan for trouble. · One status dot row per card: waiting, owed, unagreed, each a count that opens the list. [`01-tool-default.png`]
11. **major** · entity card, lifecycle · An unfired transition reads "No recorded trigger" in the smallest, palest type on the card. lab28 at least tagged it "unused". · Work owed is the signal with the most value per pixel. The tool library has a Close loan workflow and a Return transition that nothing fires; whether the fixture leaves that open on purpose or not, the board gives it the least weight on the card. · Owed work gets the warning colour, an icon and a place in a work list. [`33-open-loan.png`]
12. **major** · lifecycle · "Transitions in: Otherwise" names a case with no step and no workflow. · "Who changes it" is the point of the lifecycle view; "Otherwise" answers nothing. · Always the path: Borrow › Record › otherwise. [`33-open-loan.png`]
13. **major** · effects · The agreed E1 badges (create with green edge, delete red, each written field listed, state change as an arrow tag) are not visible at any level I reached. Steps show "Reads: 1 Effects: 2 Creates: 1 Transitions: 1". · Counts say that something happens, not what. · Replace every count row with the badge row. [`30-open-borrow.png`, `60-ogy-open-remove.png`; not verified deeper]
14. **major** · call step · lab28's "RUNS" and "THEN, BY HOW IT ENDED" became "Calls" and "Cases / Choices" and exist only in the side card, not on the board. · The owner asked for exactly those words. · Restore them on the step itself. [`93-open-remind-call.png`, `qa30/lab28-ref-sheet.png`]
15. **major** · agent attention · lab31 has no spotlight at all; the mock is a separate page with its own layout, colours and card shapes. · The owner will meet two products. · Spotlight is a state of the one board, drawn with the same components. [`21-spot-A.png` vs `01-tool-default.png`]
16. **major** · provenance · No card says whether it was decided by the owner, by the AI, or read from code or docs, nor whether it changed since agreed. · That is the trust boundary of the whole KB. · A small standing mark on every card and row: agreed / unagreed / changed. [all]
17. **minor** · home · No KB name, no revision, no "live" indicator, no time of last change. · He cannot tell a stale page from the truth. · A quiet header line: repository, worktree or commit, updated when. [all]
18. **minor** · findings and dropped · `ogy check` findings and `ogy dropped` (85) have no place. · They are part of every hand-over. · Two counts in the header that open lists. [all]

### B. Information design

19. **blocker** · the paradigm · A free pan-and-zoom whiteboard holding every kind is the wrong home for this data. Evidence: at fit, the real KB's text is 5 to 7px (`02-ogy-default.png`); zoomed to read one workflow, everything else is gone (`68-ogy-wheel-in.png`); every relation between distant blocks must cross other blocks (`66-ogy-tab-why.png`). · A canvas gives position a meaning the data does not have. Areas, layers, the why-chain and "what waits" are hierarchies and lists; only the inside of one workflow and one lifecycle are graphs. · Lists and a map for hierarchy; a laid-out graph only for one workflow or one entity at a time.
**The alternatives, judged for this data** (belongs to finding 19):

| Paradigm | Fits | Fails | Use it for |
|---|---|---|---|
| Free whiteboard (today) | Brainstorm sketches of a few things | Hierarchy, lists, 800 entries, any stable reading order; needs hand-made routing | Nothing as a home |
| Map of areas with drill-down | Layer → area → entry is the KB's own folder structure; status rolls up naturally | Relations across areas (show them as links, not lines) | **Home** |
| Flow-first layout | One workflow: steps, cases, ends, calls | Many workflows at once; entities and decisions have no place in it | **The workflow page** |
| Matrix | Goal × capability × workflow; entity × workflow (who changes what); actor × workflow | Sequence | **The area page** (why-chain table) and an effects table per entity |
| Timeline | Answer history of one decision; Git history replay (deferred by `map-modes`) | Structure | The history block of a decision |
| Notebook / document | A decision with its context; an agent's explanation in order | Overview, comparison | **The decision page and the spotlight** |
| Graph with focus + context | "What touches this entry" at one hop | More than about 15 nodes; it re-lays out on every focus, so it jumps | The "potentially affects" block, as a list first |
| Small multiples | Comparing 13 workflows by shape and status | Detail | **Flow strips in the area table** |

20. **major** · 14 workflows on one canvas · It cannot work. With steps open, one workflow is about 1,700×900 px at readable size (`30-open-borrow.png`); 13 of them are 22,000 px wide. Closed, they are title boxes, which a list shows better with a sentence each. · The canvas pays for pan and zoom and returns a grid of titles. · Small multiples: one compact flow strip per workflow in a list, full flow on its own page.
21. **major** · zoom levels · Zoom is three unrelated things: a text index (scale 0.03 to 0.1), boxes (0.2 to 0.8), and geometric magnification with no added detail (above 1). At scale 3 one word fills the screen. · "Zoom changes what is shown" is met at one threshold only; past it, zoom is a magnifying glass. · Three named detail levels chosen by a control, not by scale; cap magnification at readable size. [`45-wheel-out.png`, `01-tool-default.png`, `44-wheel-in-more.png`]
22. **major** · furthest zoom · The outer level is the most useful view in lab31 (a layer summary with workflow list) and it is hidden behind zooming out three times. · The best overview is undiscoverable. · Make that the home. [`69-ogy-wheel-out.png`]
23. **major** · roll-up · Hidden parts are summarised as counts ("8 internal relations", "Cases: 6") and arrows between hidden things do not roll up into one labelled arrow; they either vanish or all draw. · C4-style levels need "Borrow → Loan: creates, transitions" as one arrow. · Roll up by (source block, target block), label with the verbs. [`01-tool-default.png`, `42-arrows-all.png`]
24. **major** · density · The opened step card is 470 px wide and mostly empty; the opened workflow summary card repeats what the steps beside it show. Three steps do not fit in 1,440 px: Record is cut off. · Low density forces panning for a three-step flow. · Step node 200 to 240 px, title plus one line; details in the side card. [`30-open-borrow.png`]
25. **major** · noise · Count rows: "Steps: 3 Ends: 3 / Result · success: 1 Result · failure: 2 / Reads: 3 Effects: 3 / Tells: 1 Creates: 1 Transitions: 1 / More steps and ends: 3". · Five lines of numbers with no decision value; "More steps and ends: 3" is unexplainable. · Delete all of it; show the things themselves or nothing. [`30-open-borrow.png`]
26. **major** · noise · Every block carries a pin button and an open button: 22 buttons for 11 blocks, 64 on the ogy home. · They are the most repeated mark on the screen and carry no information. · Click selects and opens the side card; one "keep open" control lives in the side card. [`02-ogy-default.png`]
27. **major** · what gets pixels · On the home view the largest coloured areas are workflow headers coloured by area; goals (the reason for everything) are the same size as actors. · Size and colour should follow importance: what waits, then goals, then flows. · Give the largest type to area names and goal sentences. [`02-ogy-default.png`]
28. **major** · redundancy · Selecting a step in walk shows it three times: on the canvas, in the side card, in the walk bar. The spotlight mock shows each target twice (canvas and rail). · Each fact once (the constitution's `one-owner-per-fact` applies to the screen too). · Canvas shows where, rail shows why; never the same text in both. [`54-walk.png`, `21-spot-A.png`]
29. **minor** · empty space · At tool-library fit the board uses about a quarter of the viewport; at ogy fit 300 px margins stay empty while text is unreadable. · Fit does not fit. · Fit to content with a minimum readable scale; if it cannot fit, do not pretend. [`01-tool-default.png`, `02-ogy-default.png`]
30. **minor** · entity card on the board · "Attributes: 3 States: 2 Transitions: 2" instead of the lifecycle. · The lifecycle is small enough to draw (two states, one arrow). · Draw the state strip on the card. [`01-tool-default.png`]
31. **minor** · search results · Parts appear without their owner: "Open · STATE", "Start · TRANSITION", "Out · ATTRIBUTE", two rows named "Loan". · He cannot pick the right row. · Show the owner path in grey after the name. [`46a-search-typed.png`]

### C. Visual design

32. **blocker** · colour system · One hue has several meanings. Orange: the Lending area, the "then" line, the capability note. Green: success, the Checks area, the software layer (in "Colour: by layer"). Red: failure, the Pre-commit check workflow's area. · He cannot learn a colour. A red workflow header reads as failing. · Reserve green, red and amber for status only; areas get a neutral family or a small swatch, never the header fill. [`02-ogy-default.png`, `70-ogy-colour-layer.png`, `49-legend.png`]
33. **major** · contrast · White on the orange header is 3.58:1 (measured), used at 10px for the kind word; grey kind words on capability notes are 3.38:1 and on goal notes 4.14:1; faint arrows are far below 3:1 (estimated near 1.3:1 from the screenshot, not computed). · Below WCAG AA (4.5:1) for small text; the arrows are invisible on a projector. · Darken the header or use dark text; minimum 4.5:1 for all text, 3:1 for lines. [harness scene 111]
34. **major** · type size at default · On the ogy home the kind word and "internal relations" render at about 5px, counts at 6px, titles at 11px. · The first screen of the real KB is unreadable. · Never render text below 11px; if a level cannot fit text, drop the text. [`02-ogy-default.png`]
35. **major** · type scale · 16 distinct font sizes in the DOM (10, 11, 11.5, 12, 12.5, 13, 13.33, 14, 15, 15.21, 16, 17, 18, 19.5, 21, 31.4). · No hierarchy can be read from 16 steps. · Five sizes: 11, 13, 15, 18, 24. [harness scene 103]
36. **major** · word breaks · Titles break mid-word: "Reservatio/n", "Requirem/ents", "Answere/d", "Stor/e wor/ds", "Writ/e entr/ies". · Looks broken; the owner complained about label collisions before. · Cards size to their title; break only at spaces; never `overflow-wrap:anywhere` on titles. [`51-chat.png`, `62-ogy-pin-decision-entity.png`, `61-ogy-open-review.png`]
37. **major** · card sizes · In one row: actor 140×105, capability 140×105, goal 140×155, entity 140×210, "Reminder bot" 140×130. Bottom edges are ragged; the row has no baseline. · Reads as accident. · One grid: fixed card heights per level, width in grid units. [`01-tool-default.png`]
38. **major** · kind word placement · Under the title at overview, top-right corner when opened, lower-case in the workflow and entity side cards ("workflow", "entity"), upper-case in the actor and decision side cards. · The owner asked for "corner kind word" once, everywhere. · One component for the header of every card. [`01-tool-default.png`, `30-open-borrow.png`, `33-open-loan.png`, `34-pin-member.png`]
39. **major** · icons · The help lists "exactly one icon per kind", but several kinds share a glyph: capability and proposal (bolt), and the chat button is the same bolt; area, rule and enum (three lines), and "How to read" and the legend button use it too; step and setting (sun); dependency and workaround (plug). · An icon that means three things means nothing. · One distinct glyph per kind; controls never reuse a kind's glyph. [`48-help.png`]
40. **minor** · icon size · Kind icons are 8 to 12px next to 17px titles; on the ogy home about 5px. · They cannot be recognised, so they do not do their job as the identity mark. · Icon at cap height of the title, minimum 14px. [`02-ogy-default.png`]
41. **minor** · workflow card · A pink band hangs under each workflow card and a second orange outline surrounds it (the collapsed frame showing through). · A 16px artefact on every workflow. · Draw one shape per block. [`01-tool-default.png`]
42. **minor** · button chrome · Pin and open sit in white squares on goal, capability and entity cards, bare on workflow and actor cards. · Inconsistent. · Moot once finding 26 is done. [`01-tool-default.png`]
43. **minor** · native controls · The relation panel uses unstyled browser buttons ("Close", "Show endpoints"); the top bar mixes a segmented control, two native selects, three text buttons, one bordered button ("Reset positions", the least important) and a bare "Back". · The loudest control is the least useful. · One button style, one select style; order by frequency of use. [`98-internal-relations.png`, `01-tool-default.png`]
44. **minor** · opened workflow · The third step is cut by the viewport edge and its buttons are outside it. · A three-step flow should fit a laptop. · Fit the frame when it opens. [`30-open-borrow.png`]
45. **minor** · dark mode · lab31 has one and it holds up; the orange header and yellow notes keep full brightness and glare. The spotlight mock has none. · He works at night. · Tokens for both themes from the start; test both every time. [`115-tool-dark.png`, harness scene 119]
46. **minor** · lab28 fidelity · Kept: background, dot grid, orange header, note colours. Lost: sentences on goal and capability notes, curved coloured arrows with readable labels, the "AUTOMATIC · Lending" corner, RUNS / THEN BY HOW IT ENDED, the "unused" tag. · The parts the owner liked were the expressive ones. · Carry the palette and the three lost elements into the rebuild. [`qa30/lab28-ref-sheet.png` vs `31-open-remind.png`]
47. **nit** · focus ring · The close button's focus ring is a 40px blue square, larger than the icon and detached from it. · Sloppy. · 2px ring on the control's own radius. [`46-search.png`]
48. **nit** · search rows · The description column starts at a different x in each row (687, 690, 700, 705). · Ragged. · Fixed column grid. [`46a-search-typed.png`]
49. **nit** · legend · The Lending row has two swatches, an orange square and a small grey one, with no explanation. · Noise. · One swatch. [`49-legend.png`]

### D. Interaction

50. **blocker** · phone, menu · Opening Menu draws the controls on top of the content: "Colour: by area" over "Product", "Fit" over "Workflows", "Arrows" over "Software", "By actor" cut off. · Unusable; and "blocks on top of each other" is the owner's first complaint. · A real sheet that covers the page, with its own background. [`81-phone-menu.png`]
51. **major** · phone · The phone home lists workflows only; actors, entities, goals and capabilities are not on it. Zooming in four steps showed workflow blocks only (not verified further; they may be reachable by panning). · Half the product is not where a phone user starts. · The same area map as desktop, one column. [`80-phone-tool.png`; harness scenes 83 and 123]
52. **major** · pinning · Pinning a card clips the board at x=1060 with a hard edge: cards are cut in half ("Owner", "Remind"). · It looks like a rendering fault every time he selects something. · The side card is a column of the layout; the main area reflows, nothing is clipped. [`34-pin-member.png`, `33-open-loan.png`]
53. **major** · layout jump · Opening the Relations list shifts the whole board 300 px right; switching to "Focus on workflow" inserts a "direct / + one more hop" control and shifts every top-bar control. "Back" disappears in that mode. · "A layout that jumps when you click" is on his list. · Reserve space for panels; top-bar controls never move. [`50-relations.png` vs `01-tool-default.png`; `38-tab-focus.png`]
54. **major** · floating surfaces · Six independent overlays: side card, relation detail, relations list, legend, chat, walk bar. Each has its own position, style and close rule; several can overlap (walk bar over the step, toast over cards in the mock). · He manages windows instead of reading. · One right rail with tabs (Details, Waiting, Agent); one bottom strip at most. [`54-walk.png`, `98-internal-relations.png`, `116-spot-sim.png`]
55. **major** · scroll inside cards · The walk side card nests choice cards in a scrolling card; the chat list scrolls inside its panel with its first line cut ("one to see it on the board."); the help dialog scrolls and cuts its last line. · "Scroll areas inside cards" is on his list. · The rail scrolls as a whole; cards never scroll. [`54-walk.png`, `51-chat.png`, `48-help.png`]
56. **major** · hover card · It covers the block it describes and its neighbours, and after a drag it stays open over other cards. It repeats the side card's content exactly. · It hides the context it should explain. · Hover shows a 2-line tooltip (name, sentence, status) beside the pointer; the full card is the rail. [`94-hover-mention.png`, `96-drag-block.png`, `101-ogy-open-capture-z.png`]
57. **major** · Focus on workflow · With nothing selected it silently opens Borrow (the first one). · An arbitrary choice presented as an answer. · Disabled until something is selected, or ask which. [`38-tab-focus.png`]
58. **major** · open versus pin · Two icons per block: an arrow ("Open details") and a pin ("Pin details"). On a workflow, open expands steps on the canvas; on an actor, open and pin both show the side card. · Same control, different results; neither name says what happens. · One action per block: select. Expanding a flow is navigation to its page. [`30-open-borrow.png`, `34-pin-member.png`]
59. **major** · zoom limits · Wheel zoom runs to scale 3 (one word on screen) and down to 0.002. · Easy to get lost; no reason to go there. · Clamp between "fits" and "readable"; no free zoom on list views at all. [`44-wheel-in-more.png`]
60. **major** · state lost on zoom · Open a workflow, wheel out twice: the open state is dropped and a hover card is left hanging over the grid. · Position and state should survive zoom. · Open state belongs to the route, not the scale. [`101-ogy-open-capture-z.png`]
61. **major** · keyboard · 195 tab stops on the tool library; Tab walks every pin and open button. No arrow-key movement between blocks, no skip link, no shortcut list. · Keyboard use is impractical; at 845 entries it is hopeless. · Roving focus per region; `j/k` through lists, `Enter` opens, `Esc` back, `g w` waiting, `/` search; show them in help. [harness scene 53]
62. **major** · search coverage · A decision cannot be found by its title: "decision mode for humans" and "topology" return nothing on the ogy KB. The lab export is stale (those entries are missing) and it does not carry `title` for decisions at all. · Search is the only door to 116 decisions and it is shut. · Search title, question, key and address; test on the live inspection document. [`110-ogy-pin-decision.png`, `63-ogy-search-decision.png`]
63. **major** · search result action · Enter on "Loan" opens the side card and clips the board; the found block is not centred or marked beyond a thin outline. · "Where is it?" stays unanswered. · Navigate to the entry's page; highlight it for two seconds. [`46-search.png`]
64. **minor** · search volume · "decision" returns 549 flat rows on the ogy KB. · Unusable list. · Group by kind with counts; filter chips; 20 rows then "more". [harness scene 102]
65. **minor** · drag · Blocks can be dragged; the new place is kept only until "Reset positions", which resets all of them. No undo of one move. · A manual layout he will lose. · Remove dragging; a derived layout needs no hand repair. [`96-drag-block.png`]
66. **minor** · Back · Shown at rest when there is nothing to go back to; hidden in Focus and Walk. The browser's Back is not used (not verified whether the URL changes). · History he cannot trust. · Every view is a URL; browser Back works; the button mirrors it and disables at the start. [`01-tool-default.png`, `38-tab-focus.png`]
67. **minor** · target size · Pin and open are about 10×10 px on the ogy home. · Below the 24px minimum; mis-clicks. · Moot after finding 26; otherwise 28px minimum. [`02-ogy-default.png`]
68. **minor** · walk · The walk bar covers the canvas bottom and the step is magnified until its text is 22px and cut. · The walk shows less than the plain view. · Walk is the flow page with one step highlighted and its choices as buttons in the rail. [`54-walk.png`]
69. **minor** · spotlight tour path · In "B · Guided tour" a dashed purple polyline wraps arbitrary groups of cards and runs through the caption "Recorded links above; role selection is agent commentary." · A decoration that strikes out text. · Number badges already give the order; delete the path. [`22-spot-B.png`]
70. **minor** · spotlight, phone · The mock lays out at 1,020 px on a 390 px screen. · No phone story for the agent's part. · Rail becomes a bottom sheet with Back / Next. [harness scene 118: `vp=1020x2208`]
71. **minor** · empty, loading, error · The lab pages have none. Production `index.html` has "Loading…" and one error sentence. An area with no workflows, a KB with no decisions, a lost connection: no design. · First run and bad days are when trust is set. · Design all three for each primary view. [not verified beyond the files]
72. **minor** · scale · A full redraw takes 197 ms at 845 entries with 32 blocks on screen (measured), and interactions redraw fully. 5,000 entries would be well over a second per click (extrapolated, not measured). · Lag on every click. · Render only the current view's entries; lists are virtualised; no global redraw. [harness scene 104]
73. **minor** · motion · No `prefers-reduced-motion` rule found in lab31. · Camera moves are large. · Honour it; with lists there is little to animate anyway. [harness scene 103]

### E. Language

74. **blocker** · debug strings in the UI · "Option effects and answer history are unavailable in this export."; "Display representatives · original assertions below"; "0 filtered · 0 offscreen"; "direction: forward"; "edge:19 → product/lending/workflow/borrow/step/standing/case/owes → …"; "offscreen · product / product/lending · down"; "relation group · offscreen"; "Source · not exported"; "Walk · declaration inspection". · He named debug strings as a complaint; these are the worst yet. · A grep gate on viewer text only (authored KB text is exempt, since an entry may rightly say "export"): none of `export|offscreen|edge:\d|representatives|assertions|direction:|not exported|declaration` may appear. [`90-tool-decision.png`, `98-internal-relations.png`, `99-relation-bundle.png`, `54-walk.png`]
75. **major** · one thing, many names · A relation is "internal relations", "Relations", "relation group", "link" (legend) and "Typed relations" (help). Start is "Start", "Started by", "Started", "Schedule". The side card is opened by "Open details" and "Pin details". · His complaint, repeated: member / Mail relay, serves goal / realizes. · One term per thing, taken from the ontology; a test that fails on a second spelling. [`50-relations.png`, `49-legend.png`, `101-ogy-open-capture-z.png`, `31-open-remind.png`]
76. **major** · invented relation words · The side card says "For", "Read by", "Effects from", "Actor in"; the relations list says "Chose", "Delegated", "Max", "To", "From", "After", "Constrains", "Satisfies" as bare capitalised field names. · Neither the ontology's words in context nor plain sentences. "Max ×1" and "To ×2" mean nothing. · A sentence per relation from the kind file: "Borrow › Record creates Loan". [`34-pin-member.png`, `50-relations.png`]
77. **major** · keys shown as titles · "Ask", "Standing", "Record", "Call", "Ok", "Otherwise", "Full", "Two", "Up", "Yes". · A step called "Call" that "Calls Notify"; an option called "Two". They are ids with a capital letter. · Show the sentence (`says`, `label`) as the name where no title exists; the key only as a grey suffix. [`31-open-remind.png`, `99-relation-bundle.png`]
78. **major** · proposal · "Recorded proposal" is the link text for every proposal. · A link named after its kind. · "Proposed: Rounded up, because …". [`90-tool-decision.png`]
79. **major** · help text · "Inspect exact field paths and their evidence with Vocabulary. Search includes every exported identity and scoped effect." "A capability realizes a goal. … These fields have different meanings." A section lists renderer modes: "mention", "board", "card", "row". · Written for the builder. A newcomer learns nothing. · Six lines: what the page is, the three things to do, the status marks, the keys. [`48-help.png`]
80. **minor** · plurals · "1 steps · 1 ends", "1 steps · 2 ends". · Sloppy on the most repeated line. · Pluralise. [`01-tool-default.png`]
81. **minor** · typo · "24 relation groupd". [`50-relations.png`]
82. **minor** · duplicates · "Borrow cli  cli", "Borrow page  web": the form repeated after a name that contains it. "steps / ends" as a label above "4 steps · 2 ends". [`30-open-borrow.png`, `101-ogy-open-capture-z.png`]
83. **minor** · raw field names in prose · The chat suggestion reads "Tell the first person in line when a tool ← covers_ends". The legend reads "← Ends · result: success". · Machine notation in a sentence. · Plain words; the arrow notation only in a schema view. [`51-chat.png`, `49-legend.png`]
84. **minor** · casing · WORKFLOW / workflow, ACTOR / actor, "Cases / Choices" / "Choices Timeout" as stacked headings. · Three casings for kind words. · Small caps style from one component, source text lower-case. [`54-walk.png`]
85. **minor** · placeholder · Search placeholder says "Jump to a workflow, thing, goal…". · "thing" is not an ontology word (it means entity). · "Search entries". [template line 74]
86. **minor** · spotlight mock copy · "A · SIMULTANEOUS SET", "B · ORDERED EXPLANATION", "sets: absent", "answers: none · question waiting", "work: unbuilt", "agent selected · no recorded sets", "Local mock · delivery simulated", "spotlight.show — 6 targets", slogans "Let me show you the idea." and "Show now. Keep what matters." · Half protocol trace, half advertising. · The agent's own sentence as the title; status words from the status set; the call log behind a disclosure. [`21-spot-A.png`]
87. **nit** · "Search Ctrl K" · On a Mac it is ⌘K. [`01-tool-default.png`]
88. **nit** · "Reset positions" · Names an implementation detail. Gone with finding 65.

### F. Arrows and relations

89. **blocker** · arrows over cards and text · Edges run through cards and strike text. Measured on the edge layer only: on the tool library home an edge enters the interior of 7 of 11 blocks and crosses 3 of 48 text runs ("1 steps" struck through, the "Member" and "Loan" titles crossed); on the ogy home 4 of 32 blocks and 4 of 146 text runs ("Owner", "2 steps · 2 ends"); in the Purpose layout 2 blocks and 1 text run. It should be zero. · Label collision is his oldest complaint and it is in the default view. · No edge may cross a node box: a layout engine with obstacle-aware orthogonal routing, or no edges at that level. [`01-tool-default.png`, `42-arrows-all.png`, `64-ogy-arrows-all.png`; harness scenes 120, 121]
90. **major** · bundles · Borrow to Member and Loan is a knot of seven parallel lines with shared corners; in Remove entry six red and green case lines merge at one edge and split again. · "Arrows joining and splitting confusingly", verbatim. · One arrow per (source, target, meaning) at each level; distinct ports; never share a segment between different meanings. [`01-tool-default.png`, `60-ogy-open-remove.png`]
91. **major** · arrows to nowhere · A dashed line leaves Member to the left, turns and ends in empty space; in Remind a dotted line drops from the route and stops; on the ogy home a dotted line ends below Owner at the viewport edge. · A relation with a missing end is false. · If the target is not in view, end in a labelled stub ("→ Notify"). [`01-tool-default.png`, `31-open-remind.png`, `02-ogy-default.png`]
92. **major** · default arrows are invisible · "Arrows: faint links" draws them at very low contrast (estimated 1.3:1) with 4px heads. · Either they matter or they do not; drawn but unreadable is the worst of both. · Off by default at overview; on and readable on a flow page. [`01-tool-default.png`]
93. **major** · labels · "Arrows: all, labelled" puts four chips ("Actor", "Tells", "Reads", "Creates") in a row at the knot; no chip can be matched to its line. "Transitions" floats alone at the left. · Labels that cannot be attached are noise. · Label on the segment it names, mid-way, with a background; one label per rolled-up arrow. [`42-arrows-all.png`]
94. **major** · direction · Lend tools → Tools reach members is a 20px hook between two cards; Notify ↔ Remind is two overlapping 40px lines with opposite heads. · Direction, the one thing an arrow adds, cannot be read. · Minimum edge length; flow direction fixed (left to right for sequence, upward for "realizes"). [`01-tool-default.png`]
95. **minor** · line styles · Five styles (orange solid, grey thin, purple dashed, green dotted, red dotted) at 1px; dotted green and dotted red differ only in hue. · Red/green colour-blind users lose the success/failure difference. · Add a mark: a cross on the failure arrowhead, a tick on success. [`49-legend.png`]
96. **minor** · the Relations list · 82 relations (501 on ogy) summarised as "Then ×7", "Reads ×1" three separate times, "Constrains ×2" twice. · A table of field names with counts answers no question. · Delete it; relations belong on the entry they touch. [`50-relations.png`]

### G. Trust and honesty

97. **blocker** · success colour on a failure path · In Remind, the case "Otherwise · Ends: Failed · The message did not go out" continues on a green arrow into "Done · END · result: success", tinted green. All routes in that frame are green. · The picture says reminders always succeed. The owner raised this exact case. · A case that covers a failure end is drawn red up to the join and carries the label "after failure"; the end that swallows a failure gets a mark "also reached after: Notify failed". [`31-open-remind.png`, `93-open-remind-call.png`]
98. **major** · derived shown as recorded · Counts, "Start", the roll-ups and "No recorded trigger" are computed; the card gives them the same type as authored sentences. The mock, to its credit, writes "agent selected". · He cannot tell the KB's words from the viewer's. · Authored text in the text colour; computed facts in a second, consistent style with one legend line. [`30-open-borrow.png`]
99. **major** · agent-chosen versus agreed · In the mock, role borders (subject, impact, needs, context) colour real entries; the only notice is one grey line "Recorded links above; role selection is agent commentary." · The agent's framing looks like structure. · Roles live in the rail only; on the canvas the agent's targets get one neutral highlight and a number. [`21-spot-A.png`]
100. **major** · options look selected · In the mock's subject decision all three options carry a ticked-box icon (it is the option kind's glyph). · Reads as "all three chosen". · Radio shapes for options; a tick only on the chosen one. [`21-spot-A.png`]
101. **major** · simulated promotion · "Kept as unagreed (simulation)", "Simulate promotion", a toast "candidate alternatives kept as a decision proposal". · In the real thing this is a KB write on the owner's word; the mock makes it one click with no read-back. · Any write shows exactly what will be recorded, in the owner's words, before it happens. [`116-spot-sim.png`]
102. **minor** · the sketch · "Sketch a new workflow and show its impact" is, in the mock, three numbered text lists side by side. No steps drawn, nothing it touches marked. · The impact, the whole reason to sketch, is absent. · Draw the sketch with the flow renderer; list "would touch" entries with what changes. [`116-spot-sim.png`]
103. **minor** · dimmed context · "3 unrelated blocks dimmed" are at about 10% opacity and partly under the toast. · Neither context nor absence. · Dim to 45% or hide; never cover. [`21-spot-A.png`]
104. **minor** · stale picture · The lab export lacks entries the KB has (`view-topology`, `answer-drawer`: zero matches in the file). · A board that lags the KB by a day is wrong about what waits. · Live data only; show the snapshot's time. [grep of `lab31.html`]

### H. The decision experience

105. **blocker** · no way to answer · There is no answer control anywhere: not on the lab card, not in the mock (whose subject is a waiting question). · Job two cannot be done. · The decision page: options as choices, a paraphrase field, a note field, Record; then the read-back. [`90-tool-decision.png`, `21-spot-A.png`]
106. **major** · layout of a decision · Today: title, question, "Answers" (an apology), "Proposals" (a link), "Options" (two words). The order hides what matters. · To decide he needs, in order: the question; why it is asked (context); the options, each with what it sets; the proposal and its reason; what he said before. · Build that order; see the wireframe. [`90-tool-decision.png`]
107. **major** · option impact · No option shows what it would set, add or remove, or which entries it potentially reaches. · `human-decision-mode` was answered with exactly this. · Per option: "sets" as a short diff list; "potentially affects" as mentions, labelled as reachability. [`90-tool-decision.png`]
108. **major** · paraphrase and hedge · The KB stores `said` and `note` ("Hedged: 'Yes, I guess.'"). Nothing shows them. Four of the board's own answered decisions are hedged. · A hedged yes is the thing he most needs to see again. · Answer history as lines: date, option, "You said (paraphrased): …", note in the warning colour. [`just ogy show product/inspection/decision/map-layers`]
109. **major** · "You said … read as B" · A proposal that rests on his words (`proposal.heard`) should read "You said (paraphrased): …. Read as B." with one yes. Not present. · That one-click confirm is the fastest path in the whole tool. · A distinct card state with a single Confirm. [not present in any view]
110. **minor** · options are not links · Option names are plain text; "every mention is a link" is broken on the decision card. [`90-tool-decision.png`]
111. **minor** · decision block on the board · "Fee rounding · DECISION · 2 internal relations". · No status, no question. · Status mark and the question's first line. [`90-tool-decision.png`]
112. **minor** · review rounds · `ogy reply` grammar ("yes all", per-item) has no board form. · A round of ten cards needs "yes to all" and per-card answers. · The waiting list supports multi-select and one Record. [not present]

### I. Technical foundations

113. **blocker** · one generated file · 2.68 MB of HTML with the data inlined; a 108 KB template on one line of script; layout, routing, rendering and state as global functions (`draw()`, `sel`, `scale`). · Every fix so far has caused a regression elsewhere (lab31's own defect list counts 50 of 153 checks passing on lab30). The architecture is why. · Modules with one job each; the production tree already starts this (`js/model`, `js/render`, `js/state.js`): keep that, drop `js/canvas`.
114. **major** · hand-written layout and routing · `lab31-layout.js` (35 KB) and `lab31-edges.js` (19 KB) pack shelves and route orthogonal lines without knowing about obstacles. · Findings 89 to 94 are all consequences. · For the one place that needs a graph (a flow, a lifecycle): ELK layered with orthogonal routing and ports (`elkjs`, in a worker), compound nodes for steps with cases. Never lay out more than one workflow at a time.
115. **major** · HTML inside SVG · Cards are `foreignObject` HTML inside a scaled SVG group (confirmed: 11 of 11 blocks on the tool library home). · Text scales with zoom (finding 34), focus order follows DOM not position, text selection and find-in-page misbehave. · DOM for everything with text; one SVG layer under it for edges only.
116. **major** · full redraw · Every interaction calls a global draw. · Finding 72; also the cause of hover cards replacing click targets (lab31 defect 1). · A small reactive view layer; update what changed.
117. **major** · accessibility tree · Blocks are divs without roles or names; 188 aria attributes, most on buttons. · A screen reader gets a flat list of "Pin details" buttons (not verified with a reader). · Lists are `ul`/`li`, the flow is a list of steps with described edges, the rail is a `complementary` region.
118. **major** · testability · The lab is tested by screenshot and by reading globals. · Layout regressions were found by the owner, not the tests. · The measures in `action-plan.md` (d) as tests: no overlap, no route through a node, no text under 11px, no forbidden words, one name per term.
119. **minor** · framework · The answer to `view-frontend-build` is "reuse the a2kay setup: builds Tailwind CSS, bundles, ships static files"; `docs/board-data.md` says the shipped assets are plain ES modules without a bundler and Tailwind is the standalone binary. The two do not say the same thing. · Workable for lists and a rail. The risk is hand-rolled DOM updates. · Stay with it and add one tiny rendering helper (a vendored tagged-template library such as `lit-html`, or `preact` + `htm`, both usable without a bundler). Owner question 3 in the action plan.
120. **minor** · no URL state · View, selection and level live in memory. · No link to share with the agent, no Back, no reload. · The route is the state: `#/product/review/workflow/review-and-reply?level=2`.
121. **minor** · the agent's side · Spotlight needs a push channel from server to page; `docs/board-data.md` says there is "no streaming connection". · Without it "live" means polling. · Server-sent events on the existing server; the page shows connection state.

## Verdict

**Wipe and restart the front end. Keep the back.**

Reasons, in order:

1. The three jobs are see, decide, share. The current thing does a weak version of the first and none of the second or third. Twelve of the twelve glance questions fail.
2. The faults the owner keeps reporting (overlap, label collisions, arrows merging, jumps, too many words) are produced by the paradigm: a free canvas with hand-written packing and routing, scaled text, and every kind as a box. Four generations have patched symptoms; lab31 fixed clicks and positions and lost lab28's expressiveness on the way.
3. The data is mostly hierarchy and lists. Only two things are graphs: the inside of one workflow, and one entity's lifecycle.

**Keep:** `ogy serve`, `/api/inspection` (schema 2), `js/api.js`, `js/model/adapt.js`, `js/model/descriptor.js`, `js/state.js`, the icon paths (after de-duplication), the lab28 neutral palette and note colours as tokens, the real-input harness, the spotlight's roles and its "agent selected" honesty, the furthest-zoom layer summary as the seed of the home view.

**Drop:** the pan-zoom canvas as the home, `js/canvas/*`, lab layout and edge code, pin/open buttons, drag, the Relations list, the five layout tabs, the colour and arrow selects, hover cards that duplicate the rail, the chat mock.

**One conflict to settle with the owner first:** `product/inspection/decision/product-map` is answered "canvas" (hedged: "Yes, I guess."). This restart keeps a drawn flow but removes the canvas as the home. That is a proposal on that decision, not something to act on silently. It is owner question 1 in the action plan. The plan's stages 0 to 6 (the QA gate, the status facts, the shell, the waiting list, the decision page, answering, what an option reaches) are valid whichever way he answers; removing the canvas (stage 7) waits for his word.

## The alternative

**Information architecture.** Layer → area → entry → part. Three kinds of page, one rail.

**Views.**

1. **Map (home).** Two tabs: Product, Software. A grid of area tiles. Each tile: area name, its one sentence, its goals as lines, then counts that are links: workflows, entities, and status marks (waiting, owed, unagreed). A header strip totals the status marks for the whole KB.
2. **Area.** The why-chain as a table: one row per goal; columns goal, capability, workflow. Each workflow cell is a compact flow strip (step dots, ends coloured by result, status marks). Below: entities with their state strips, then actors, rules and the rest as rows.
3. **Flow** (one workflow) and **Lifecycle** (one entity). The only graphs, laid out by ELK, left to right. Steps are small nodes; cases and choices are labelled edges; ends sit at the right, success above failure; a call step shows RUNS and THEN, BY HOW IT ENDED. Under the flow: a strip of the entities it touches with effect badges.
4. **Decide.** The waiting list grouped by area, and the decision page.

**Navigation.** Every view is a URL. Breadcrumb at the top. Any mention (icon + name) is a link to that entry's page; hover shows two lines. Search (`/`) covers title, question, key, address. Browser Back works.

**Levels instead of zoom.** A three-step control: 1 names only, 2 adds actor, interface and effect badges, 3 adds sentences and conditions. The level changes content, never text size. What a level hides becomes a count that opens it; edges between hidden parts become one labelled edge.

**The rail.** One right column, three tabs. *Details*: the selected entry. *Waiting*: what waits, always one click away, with its count on the tab. *Agent*: the spotlight.

**Spotlight.** The agent sends an ordered list of targets with a sentence each. The page navigates to the view that holds target 1, numbers the targets, dims the rest, and the Agent tab shows the sentences with Back / Next. A sketch is drawn by the same flow renderer in the sketch treatment, with "would touch" rows. Dismiss restores the view.

**Visual language.** lab28's neutrals and note colours. Kind = icon + corner word, never colour. Colour is reserved: green success, red failure, amber waiting or owed, violet agent, dashed and hatched for sketch. One card header component. Five type sizes. 8px grid.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ogy · tool-library · worktree · updated 16:02    [Product|Software]  / Search │
│ ● 3 waiting   ▲ 253 owed   ◌ 37 unagreed   ✎ 7 changed   ⌫ 85 dropped         │
├───────────────────────────────────────────────────────┬──────────────────────┤
│ Product › Review                              level 1 2 3 │ Details Waiting(3) Agent│
│                                                       │                      │
│ GOAL                 CAPABILITY        WORKFLOW        │ ◇ How the agent shows│
│ ◎ Requirements   ←   ϟ Apply a reply ← ⤳ Review and    │   something that does│
│   agreed                                reply  ●1      │   not exist yet      │
│                                        ○─○─○─┬✓        │   Waiting for you    │
│                                              └✗        │                      │
│                      ϟ Answer under  ← ⤳ Hand over     │ Why asked: …         │
│                        delegation      ○─○─✓   ▲2      │                      │
│                                                       │ ( ) Both   proposed  │
│ ENTITIES                                              │     sets: + 2 entries│
│ ▢ Decision   ◦ waiting ─▶ ◦ answered                  │ ( ) Unagreed entries │
│ ▢ Review round   (no states)                          │ ( ) Illustration only│
│                                                       │                      │
│ ACTORS  ♙ Owner  ♙ Agent     RULES 16 ›   TERMS 29 ›  │ Your words: [______] │
│                                                       │ Note:       [______] │
│                                                       │ [Record answer]      │
└───────────────────────────────────────────────────────┴──────────────────────┘
```

**First two weeks.** Week 1: the status facts in the inspection document; the shell (header strip, breadcrumb, rail, routes); the Waiting list and the decision page, read-only then with Record; the Map. Week 2: the Area page with flow strips and state strips; the Flow page with ELK, levels and effect badges; the failure-path rule; search; phone layout; the QA gate running on three data sizes in both themes. Spotlight and sketch follow in week 3 on the same components. The Map and everything after it in this list wait for the owner's answer on the canvas; if it is slow, week 1 still delivers deciding on the board. Stage-by-stage detail: `action-plan.md`.
