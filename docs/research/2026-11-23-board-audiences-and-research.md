<!-- Fable assessment (read-only advisor), 2026-11-23, answering the owner's audience message; see docs/thoughts/owner-inputs.md -->

# Board audiences, ontology gaps, re-ranked POCs and research

Nothing was written or changed. I read `docs/thoughts/owner-inputs.md` in full and looked at four of the six redraw screenshots.

## A1. The audiences as a chain

| Hat | Receives | Must be able to do | Board must show | Must not see | What the AI asks |
|---|---|---|---|---|---|
| **Business analyst / product owner** | Stakeholder calls, huge transcripts, loose notes; later live listening | Drop raw input in; see what the AI understood; correct it; answer business questions | The product as flows and frames; what is new from this input; which passage each proposal came from; what waits | Handlers, settings, dependencies, software decisions | Business questions in the product's own words; "I don't know" is a valid answer |
| **Solution architect** | Agreed product entries | See product and software together; find product parts nothing carries; ask the AI for a design; see what it attaches to; judge balance | Uncovered steps; the proposed design as a sketch on existing software; open software decisions; "no missing decisions" | Product parts whose business decisions are still open (hidden, or greyed with the reason) | Trade-offs: complexity, reliability, proportion (proof of concept, startup, product), and the scope a rule applies to |
| **Software engineer** | A designed, decided slice | Read it as is; supervise the agent that codes; see work left and proofs | One slice: step, interface, handler, rule, proof, built or not | Open business questions; edit controls | Nothing about requirements; he sends findings back up |
| **AI-factory operator** | Many slices | See which are ready, running, blocked | Readiness and work left per area | Detail | Only what blocks |
| **One person, all hats** (Denis, now) | Everything | Switch hats without changing tools | The same surface, one hat at a time | Nothing is forbidden; the hat only filters | All of the above |
| **Business person, no software knowledge** | Own idea | Decide business; let the AI decide software | Business hat only, plus a list of what the AI decided for him | Software questions | Software questions are not asked; they are answered under a delegation and listed for veto |

Hand-offs, in order:
- **Raw input to proposed entries.** The analyst corrects them.
- **Agreed entries to the architect.** This only happens once the business decisions on that part are answered.
- **Designed slice to the engineer.** This only happens once the software decisions are answered.
- **Built to proof.** The engineer and the agent close it.

**Tuning questions to the person.** He named three ideas. Two already have a home in ogy.
- **"I don't know."** This is a third outcome beside an option and "no". Today the nearest thing is delegation: "decide on my behalf" for a scope, listed afterwards by `ogy dropped`.
- **Levels of utilisation.** How much the AI decides alone. This is delegation by scope, and a layer could be a scope.
- **A profile with values.** Values that change which option the AI proposes (reliability first, speed first). The constitution's principles already do this for the whole KB; a per-person or per-product profile does not exist.

## A2. What the ontology has, and what is missing

**Has**
- **Actors:** `owner` and `agent` in `product/shared`. No analyst, architect or engineer.
- **Decisions:** question, options, `sets`, proposal, answers, delegation.
- **Layer hand-over:** `ogy work <layer>` lists what a layer owes the next. "A row with no handler or interface yet is work the next layer owes."
- **Coverage rules:** "an actor step has an interface that serves it"; "a row with an effect has a handler".
- **Rule scope:** `satisfies` and `constrains` already let a rule bind one step, one interface or one entity.
- **Who may use an interface:** `allows`.

**Missing** (candidates for the owner; none decided)
1. **Intake.** There is no entry for a raw input, and no link from a proposed entry back to its passage. `src` takes `code:` or `doc:` only. AGENTS.md says "ogy stores no messages and no quotes". A transcript kept in the repo and cited by `doc:` may fit that; storing it in the KB would not. This needs a decision.
2. **Readiness mark.** Nothing computes "not ready for software design". It could be derived: a product entry reached by a waiting decision (through `sets` or `because`) is not ready. `ogy find` for "ready design" and "not ready" returns nothing relevant.
3. **Audience or hat.** Nothing says which kinds a hat sees. `find` for audience, stakeholder, architect, engineer returns nothing.
4. **Profile and values.** No per-person or per-product values that steer proposals. "Proportion" has no home either.
5. **"I don't know" answer.** Not distinct from delegation today.
6. **A kind for the program we ship.** `area` is a topic folder. Nothing says "the CLI is one program, the board another".
7. **Read-only role.** No concept of who may write. One person does not need it; flag it only so nothing blocks it later.
8. **A rule for a whole area or layer.** I did not check whether `satisfies` can come from an area; treat as unverified.

Candidates 1, 2, 3 and 6 shape the data, so skipping them risks a restart. Candidates 4, 5 and 7 can wait for one person.

## A3. His priority, and the new POC order

He said three things: first for himself as one person wearing all hats; analysts and product owners are the vision; he wants to taste soon. He also said "I need to use application to build some app, and then I will tell".

That changes my earlier order. I put the canvas last because it was the most expensive. The redraw now exists, so it goes first.

**The redraw against P1 to P6**

What it gets right:
- Product and software sit on one surface, with one bundle per pair of areas.
- Three zoom levels change what is shown.
- A decision click dims the canvas and lists impact by area and layer. The honest case is handled: "Reply wait" has no impact data and says so.
- The interface panel shows serves, shows, satisfies, includes. That answers "I open an interface and see nothing".
- The Borrow detail reads well: rows, red and green exits, effect badges, "performed by Lend".

What is wrong, from the screenshots:
- Lines still cross cards. The amber impact lines run through dimmed cards, and a blue dashed line strikes the "Leave button" title. This is his oldest complaint.
- The bundle label lists eleven link words with counts ("unlike 1 · when 1 · default 1"). That is the count-row noise again.
- At 32% the section labels are a few pixels high.
- Software sits far below product. Tracing one step to its interface means following a long line. Figma would put the frame next to the step.
- It runs only on the tool library: 91 entries, one product area, one software area with the same name. The ogy KB has about 850 entries, and `software/cli` serves five product areas. Scale and the mismatched areas are untested.
- It does not mark an uncovered step. That is the architect's first need.

**Re-ranked**

| New rank | POC | Why |
|---|---|---|
| 1 | **P5, as the redraw on the ogy KB** | It exists. The real test is 850 entries and areas that do not match by name. |
| 2 | **P1 blueprint**, renamed coverage view | His new words: "a new part of product not covered by software at all". The redraw does not show it. |
| 3 | **P3 frames**, folded into the redraw's detail level | Put the interface frame inside or beside its step. |
| 4 | **P2 decision in place** | Mostly done in the redraw. What remains is option-by-option difference and no crossing lines. |
| 5 | **P4 why tree** | Useful, not urgent; N6 below may replace it. |
| 6 | **P6 matrix** | Keep only as a fallback if bundles fail at scale. |

## B. Research

"Unverified" means my search returned nothing and the line is from memory.

| Thing | What it does | Joins product and software? | What to steal |
|---|---|---|---|
| **IcePanel** | Visual C4 modelling: one model, objects reused across diagrams, zoom through three levels | No product layer. Actors and "flows" are the nearest. Vendor-stated. | **Flows** drawn over the existing diagram without a new layout; **tags** that show, hide or recolour the same diagram per audience |
| **C4 / Structurizr** | One model in text, many views generated | Software only; a person is a box outside | Still current (C4 site edited into 2026; activity not confirmed from release notes). Fixed named levels; an auto legend per view |
| **ArchiMate** | Layers (motivation, strategy, business, application) with "serving" and "realization" between them; a viewpoint per stakeholder concern | Yes, this is its point | The layered viewpoint; viewpoints as "hats". Current usage: unverified |
| **Figma / FigJam / Miro** | Shared canvas of frames | Dev Mode shows build facts for a selected frame (unverified detail) | Frames in rows; sections; inspect panel; link to a frame |
| **Jama Connect** | Requirements with live trace | Yes: requirement to design to test | A red mark on an item missing a required downstream link, fixable in place |
| **Modern Requirements** | Requirements in Azure DevOps | Partly: text to diagrams and mockups, trace matrix. Vendor-stated. | Generating a mockup from requirement text |
| **Pad++ / Jazz** | Zoomable interfaces; "semantic zoom" | n/a | The redraw's three levels are this |
| **Bret Victor** | Explorable explanations; "ladder of abstraction"; Dynamicland's "no black boxes" | n/a | One control that moves between levels of abstraction |
| **Muse** | Nested boards you zoom into | n/a | Zoom in instead of flipping pages |
| **Design structure matrix** | Square matrix of dependencies, reordered to reveal modules | It is software-side, but any two sets work | Reordering to show which software clusters carry which product areas |
| **Miller columns** | Several hierarchy levels open side by side | n/a | A thread across layers in columns; weak when deep |
| **Xanadu transclusion** | The same content knowably in two places | n/a | A proposal shows the transcript passage it came from, in place |
| **tldraw / Excalidraw** | Embeddable canvas libraries | n/a | Use one instead of hand-written pan, zoom and select (capabilities beyond "drop-in whiteboard" unverified) |
| **Kumu, Tana, Obsidian/Roam graph, Gapminder, Sankey, HyperCard, Smalltalk/Self, ConceptDraw, Lucidchart, Whimsical, Mermaid, Miro+Jira** | Not searched or no results | Unverified | From memory only: graph views of everything are admired and rarely used; Gapminder's lesson is animation over one stable picture; HyperCard's is that the viewer is also the editor |

The main lesson: nobody I found joins product and software well on one canvas. IcePanel stops at software. ArchiMate joins them but is heavy and has no flows people enjoy reading. Jama joins them as tables. ogy already holds the links (`serves`, `performs`, `realizes`), so this intersection is open ground.

## New mini POCs from the research

**N1. Hats** (IcePanel tags, ArchiMate viewpoints)
- *Job:* one person switches between business, design and build without changing surface.
- *What it is:* the redraw with a three-way switch. Business hides the software band. Design shows both and hatches product parts with an open business decision. Build shows one slice with proofs and work left.
- *Two minutes:* flip the switch three times on one area.
- *Works if:* "Each hat shows me what I need and nothing I do not."

**N2. Flow overlay** (IcePanel flows)
- *Job:* walk a workflow across both layers.
- *What it is:* pick a workflow; its steps light up in order on the fixed canvas, each with its interface and handler. Nothing moves.
- *Two minutes:* play Borrow, then a workflow on the ogy KB.
- *Works if:* "I see what happens and what software does it, without losing my place."

**N3. Gaps first** (Jama's red mark)
- *Job:* the architect's "what is not covered".
- *What it is:* every actor step with no interface, and every effect row with no handler, carries one mark. A side list counts them per area. One prepared agent sketch shows a proposed handler and what it attaches to.
- *Two minutes:* find the three biggest gaps; open the sketch.
- *Works if:* "I see what is missing and where a design would connect."

**N4. Intake** (transclusion)
- *Job:* the analyst's "gigantic transcript, then what?".
- *What it is:* a static mock. Left: a real transcript (his own `owner-inputs.md` is one). Right: proposed entries in the sketch treatment. Hovering a proposal highlights its passage. Each proposal has yes, no, and "I don't know".
- *Two minutes:* read five proposals and answer them.
- *Works if:* "I trust what it understood because I see where it came from."
- *Caution:* this touches the "no quotes" rule. Mock only.

**N5. One question, three people**
- *Job:* tuning questions to the person.
- *What it is:* one real waiting decision shown three ways: business wording, architect wording with trade-offs, and "decide this for me" with what the AI would choose and why.
- *Two minutes:* read all three, pick the one he would want.
- *Works if:* "The question fits who I am right now."

**N6. Thread columns** (Miller columns, ladder of abstraction)
- *Job:* why does this exist, and what carries it. Not a canvas.
- *What it is:* six columns: goal, capability, workflow, step, interface, handler. Clicking one item filters the columns to its right and left.
- *Two minutes:* start from a handler and walk left to its goal.
- *Works if:* "I can follow one thread from why to code in one row."

## For the caller to record through ogy before anyone acts

- The eight missing concepts in A2, each as a proposal on a decision.
- `product-map` is still answered "pages". The redraw is a new option on it.

## The one question

**What is the next real thing you will build with ogy?** You said you cannot judge the board until you use it to build something. If you name it, N4 and N3 run on that product's first real input instead of on ogy's own KB, and the taste test becomes real work.

Sources:
- [IcePanel docs: modelling](https://docs.icepanel.io/features/modelling)
- [IcePanel: overlays and flows](https://dev.to/icepanel/less-maintenance-of-software-diagrams-with-overlays-1kbb)
- [IcePanel vs Structurizr (vendor)](https://icepanel.io/blog/2025-11-14-icepanel-vs-structurizr)
- [Thoughtworks Radar: IcePanel](https://thoughtworks.com/radar/platforms/icepanel)
- [Structurizr](https://structurizr.com/)
- [C4 model](https://c4model.com/llms.txt)
- [ArchiMate 3 language structure](https://pubs.opengroup.org/architecture/archimate3-doc/ch-Language-Structure.html)
- [ArchiMate example viewpoints](https://pubs.opengroup.org/architecture/archimate3-doc/ch-Example-Viewpoints.html)
- [Jama Trace View](https://help.jamasoftware.com/en/manage-content/coverage-and-traceability/trace-view.html)
- [Jama Live Trace Explorer](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/live-trace-explorer.html)
- [Modern Requirements4DevOps features](https://www.modernrequirements.com/products/modern-requirements4devops-features/)
- [Explorable Explanations](https://worrydream.com/ExplorableExplanations/)
- [Dynamicland at Harvard](https://dynamicland.org/2018/Dynamicland/)
- [Muse (Ink & Switch)](https://inkandswitch.com/muse)
- [Design structure matrix](https://en.wikipedia.org/wiki/Design_structure_matrix)
- [Miller columns](https://en.wikipedia.org/wiki/Miller_columns)
- [Project Xanadu](https://en.wikipedia.org/wiki/Project_Xanadu)
- [Pad++ paper](https://www.lri.fr/~mbl/Teach/SituatedComputing/2017/papers/ZUI/pad++-uis94-p17-bederson.pdf)
- [Cockburn et al. review](https://www.microsoft.com/en-us/research/wp-content/uploads/2008/01/cockburn-ComputingSurveys09.pdf)