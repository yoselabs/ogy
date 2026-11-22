# Board drawing (S3, stage 3)

The board reads the stage-2 inspection model through `model/models.js`. The
index owns children and incoming/outgoing relation occurrences. Authored nodes,
fields, relation witnesses and the inspection document remain unchanged, because
`one-owner-per-fact`: layout is a view of those facts.

`render/mentions.js` is the one path for structured names, headings and accessible
names. It uses the stage-2 identity descriptor and escapes authored text. Literal
enum members and option sets stay literal values. List parts retain their local
locator identities; the renderer never invents an address.

The renderer separates workflow steps and rows, E1 effect badges, entity
attributes and lifecycle declarations, decision answers/proposals/options, and
the remaining kinds. E1 groups effects within their exact row by target owner;
every badge retains the row and effect indices. Transition sources and targets
are declarations, and a missing firing row says “No recorded trigger”. No
conditions, effects or answers execute in the browser.

`canvas/layout.js` measures actual cards in a hidden DOM host. Steps occupy
columns derived from `start` and `then`, with cycle-safe traversal. Fixed shelves
pack top entries in source order. Layouts are cached by document and detail class
(summary below .38, structure below .8, detail otherwise). Camera, selection,
viewport size and future panels are not layout inputs. Card dimensions and hit
areas are identical on fresh phone and desktop loads. Viewport culling leaves
world positions intact. Below .15 the board displays readable layer summaries,
workflow mentions and exact kind counts instead of microscopic cards.

The lab31 palette remains in the component styles: orange workflow frames,
sticky yellow goals, amber capabilities, blue entities, and success/failure end
colours. Tailwind 4.1.11 builds the shipped stylesheet. Like a2kay's reference,
these are plain ES modules without a bundler; a2kay's npm recipe is replaced by
the standalone Tailwind executable. The current hardened server is unchanged.

Native Open and mention clicks select an entry and move its camera. Hover and
mouseup do not rebuild the DOM. Selection updates attributes without replacing
an unchanged scene. The broader interaction controls belong to stage 4.

## Browser evidence

The scratchpad `s3-draw-check.mjs` uses the existing `s3-data-serve.py` helper to
start the real `serve --port 0` command surface with an in-memory credential,
then follows its one-use exchange URL in installed headless Chromium 156.
The harness imports the shipped modules through CDP; no test handle is shipped.

The stage-3 subset of the lab30 scenes covers Fit, every workflow, five zoom
levels, narrow overview, and a mounted detail card for every kind. Kind scenes
mount the exported renderer in the browser, including parts without a separate
world block. Palette, help, dark controls, hover panels and edge checks are
stage-4 acceptance and are not claimed here. Screenshots and measurement results
are `s3-draw-*.png` and `s3-draw-results.json` in the task scratchpad. Browser
measurements are deterministic regression evidence, **untested as an agent eval**.

Stage 4 can consume `scene.layout(level)` with world rectangles and step slots,
the indexed relation occurrences and the shared renderers. It still owes edges,
walk, interactions, palette, help, dark and narrow controls. Live updates and
removing the old list page remain stages 5 and 6. Biome 2.6.8 is absent: the
coordinator must fetch `biome-linux-arm64` from the `biomejs/biome` release tagged
`@biomejs/biome@2.6.8`, install and lock the configured mise tool, format the
modules and rerun `just check`. No network fetch was attempted.
