# Lab 28 redraw: the board as a canvas (throwaway prototype, tool library data)
Owner said: the canvas was more interesting than the page-per-kind board; workflows were clear and familiar, like screens in Figma or Sketch; he wants Figma for product people.
Owner said: Product and Software are not connected; an interface page shows nothing; a decision page does not say what it impacts or where.
Owner said (lab 28 era): too many words on a state change, wants a compact mark; show titles, not keys; kind as a small corner word; one word per relation ("serves goal" vs "realizes" was wrong), ontology words only.
Owner said (lab 28 era): keep sent and failed, and the call then how it ended; one look for an actor everywhere; effects list each field and value, no commas; liked animated dashes and one-edge highlights.
Open `index.html` by file: no server, no build; the data is the inline `snapshot.json`. Drag pans, wheel or pinch zooms, Fit or `0` resets, Esc deselects, the header switches level.
Semantic zoom: under 50% areas are labelled regions (counts, goal, capability, waiting decision, workflow summaries) and one bundle per pair of areas (Product lending to Software lending: serves 3, performs 4 ...).
50% to 95%: workflow frames with step and end names. Above 95%: lab 28 cards, orange frames, rows with arrows leaving the row that causes them (green success, red failure), effect badges, "Calls", "Then, by how it ended".
Software is drawn under Product: interfaces as screens, handlers with "performed by" marks on the rows, blue lines from each to the step it serves or performs.
Click a decision: the canvas dims, impacted cards and rows are outlined and named, amber lines run from it, the panel groups the impact by area. Late fee has `ogy impact` data (8 entries); the waiting Reply wait has none, so it is derived from links to what it sets and says so.
Changed from lab 28: pan and zoom canvas with semantic zoom; areas as regions; Product and Software drawn together; decision impact in place; interface as screen; titles humanized; layout measured, never hand-packed.
Not built: sketch cards, entity lifecycle graph, search, writing answers.
`qa/check.mjs` drives real mouse, wheel and ctrl+wheel over CDP (`CHROME=... OUT=... node qa/check.mjs`, `THEME=dark` too); `shots/` holds its screenshots.
Source: lab 28 itself is gone from disk; rebuilt from the session transcript, critique.md and design-views.md; palette and rows follow the old canvas (git `4f0469a^`).
Data: tool-library inspection (91 entries) and standing option reach from a snapshot; the worktree predates `ogy inspect`, so it is not regenerated here. Unrecovered: lab 28's exact pixels and reference sheet.
