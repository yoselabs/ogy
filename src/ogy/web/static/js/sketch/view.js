import { cardHeader } from "../ui/card-header.js";
import { authored } from "../ui/authored.js";
import { h } from "../ui/dom.js";
import { words as shell } from "../ui/words.js";
import { levelControl } from "../views/flow/controls.js";
import { flowView } from "../views/flow/data.js";
import { drawFlow } from "../views/flow/draw.js";
import { words as flow } from "../views/flow/words.js";
import { sketched, sketchModel } from "./model.js";
import { touchBlock } from "./touch.js";
import { words } from "./words.js";

// The sketch, #/sketch: what the agent drew, in the one sketch treatment, and what it would touch. It is a state of the page that
// holds the agent's records only in memory: nothing here reads or writes the knowledge base beyond the document already on screen.
export const sketchRoute = {
  test: (path) => path === "sketch",
  layer: null,
  mount: mountSketch,
  crumbs: () => [{ text: shell.board, href: "#/" }, { text: words.sketch }],
};

const PHONE = "(max-width: 720px)";
const LEVEL = 2;

// Every edge that starts or ends at a drawn node is drawn as part of the sketch, whatever the failure it would cover.
function treated(view) {
  const drawn = new Set(view.nodes.filter((item) => item.stub || item.node?.sketch).map((item) => item.id));
  for (const item of view.nodes) if (item.stub) item.sketch = true;
  for (const edge of view.edges) if (drawn.has(edge.from) || drawn.has(edge.to)) edge.class = "is-sketch";
  return view;
}

function actions(sketch, { keep, dismiss }) {
  return h(
    "div",
    { class: "sketch-actions", "data-part": "sketch-actions" },
    sketch.decision
      ? h("button", { type: "button", class: "btn pri", "data-action": "keep", title: words.keepHint, onclick: keep }, words.keep)
      : null,
    h("button", { type: "button", class: "btn", "data-action": "dismiss-sketch", onclick: dismiss }, words.dismiss),
  );
}

function head(sketch, model, controls) {
  return h(
    "header",
    { class: "page-head sketch-head" },
    h("p", { class: "sketch-tag is-sketch", "data-part": "sketch-tag" }, words.sketch),
    authored(sketch.title, "h1", { class: "sketch-title", "data-part": "sketch-title" }),
    h("p", { class: "says", "data-part": "not-kept" }, words.notKept, ` ${words.by} `, authored(sketch.session)),
    actions(sketch, controls),
  );
}

// A sketched entry that is not a workflow: its header and sentence, in the same treatment as a sketched step.
function card(node) {
  const header = cardHeader(node, []);
  header.querySelector(".card-header-side").prepend(h("small", { class: "sketch-word", "data-part": "sketch-word" }, words.sketch));
  return h(
    "li",
    { class: "sketch-card is-sketch", "data-sketch": node.address, "data-address": node.address },
    header,
    node.says ? authored(node.says, "p", { class: "says" }) : null,
  );
}

export function mountSketch(main, { store, spotlight }) {
  const page = h("section", { class: "page sketch", "data-part": "sketch" });
  const phone = matchMedia(PHONE);
  let level = LEVEL;
  let signature = null;
  let drawing = 0;

  const keep = () => {
    const { decision, option } = spotlight.state.sketch;
    location.hash = `#/${decision}/option/${option}?keep=1`;
  };

  async function paint(canvas, model, workflow) {
    const view = treated(flowView(model, workflow.address));
    canvas.dataset.direction = phone.matches ? "down" : "right";
    canvas.dataset.level = String(level);
    try {
      await drawFlow(canvas, view, phone.matches ? "DOWN" : "RIGHT", { level, marks: () => [], hrefOf: () => null, select: () => {} });
    } catch (error) {
      page.dataset.state = "failed";
      canvas.replaceChildren(h("p", { role: "status", class: "empty" }, `${words.couldNotDraw} ${error.message}`));
    }
  }

  function render() {
    const { sketch } = spotlight.state;
    const { doc } = store.getState();
    if (page.parentNode !== main) main.replaceChildren(page);
    if (!sketch) return page.replaceChildren(h("p", { role: "status", class: "empty", "data-part": "no-sketch" }, words.nothing));
    if (!doc) return page.replaceChildren(h("p", { role: "status", class: "loading" }, words.loading));
    const next = JSON.stringify([sketch.since, doc.snapshot.version, phone.matches, level]);
    if (next === signature && page.querySelector("[data-part=sketch-actions]")) return;
    signature = next;
    const model = sketchModel(doc, sketch);
    const { workflows, others } = sketched(model);
    const flows = workflows.map((workflow) => {
      const canvas = h("div", { class: "flow-canvas", "data-part": "flow-graph" });
      return {
        workflow,
        canvas,
        scroll: h("div", { class: "flow-scroll", role: "group", "aria-label": words.graph, tabindex: "0" }, canvas),
      };
    });
    page.dataset.state = "laying";
    page.replaceChildren(
      head(sketch, model, { keep, dismiss: () => spotlight.dismissSketch() }),
      workflows.length ? levelControl(level, (chosen) => ((level = chosen), render())) : null,
      ...flows.flatMap(({ workflow, scroll }) => [
        h("h2", { class: "sketch-flow-name" }, authored(workflow.title || workflow.key), ` · ${flow.graph}`),
        scroll,
      ]),
      others.length
        ? h(
            "section",
            { class: "block", "data-part": "also-sketched" },
            h("h2", {}, words.alsoDrawn),
            h("ul", { class: "sketch-cards" }, others.map(card)),
          )
        : null,
      touchBlock(model, sketch),
    );
    const turn = ++drawing;
    Promise.all(flows.map(({ workflow, canvas }) => paint(canvas, model, workflow))).then(() => {
      if (turn === drawing && page.dataset.state !== "failed") page.dataset.state = "ready";
    });
  }

  const offSpot = spotlight.subscribe(render);
  const offStore = store.subscribe(render);
  phone.addEventListener("change", render);
  render();
  return () => {
    drawing++;
    offSpot();
    offStore();
    phone.removeEventListener("change", render);
  };
}
