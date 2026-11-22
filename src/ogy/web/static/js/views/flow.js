import { authored } from "../ui/authored.js";
import { cardHeader } from "../ui/card-header.js";
import { h } from "../ui/dom.js";
import { words as shell } from "../ui/words.js";
import { factsOf } from "./area/parts.js";
import { flowView } from "./flow/data.js";
import { drawFlow } from "./flow/draw.js";
import { words } from "./flow/words.js";

// A workflow, #/<layer>/<area>/workflow/<id>: its steps and ends as a graph, then edges labelled by the case or choice that takes them.
const PATH = /^((?:product|software)\/[^/]+)\/workflow\/[^/]+$/;
const PHONE = "(max-width: 720px)";

export const flowRoute = {
  test: (path) => PATH.test(path),
  get layer() {
    const first = location.hash.replace(/^#\/?/, "").split("/")[0];
    return first === "product" || first === "software" ? first : null;
  },
  mount: mountFlow,
  crumbs: (route) => [
    { text: shell.board, href: "#/" },
    { text: route.segments.slice(0, 2).join("/"), href: `#/${route.segments.slice(0, 2).join("/")}` },
    { text: route.segments[3] },
  ],
};

function notice(main, ...children) {
  main.replaceChildren(h("section", { class: "page notice flow" }, ...children));
}

export function mountFlow(main, { store, live, inspection, route }) {
  const address = route.path;
  const page = h("section", { class: "page flow", "data-part": "flow", "data-address": address });
  const canvas = h("div", { class: "flow-canvas", "data-part": "flow-graph" });
  const scroll = h("div", { class: "flow-scroll", role: "group", "aria-label": words.graph, tabindex: "0" }, canvas);
  const phone = matchMedia(PHONE);
  let signature = null;
  let drawing = 0;

  async function paint(view, facts) {
    const turn = ++drawing;
    page.dataset.state = "laying";
    canvas.dataset.direction = phone.matches ? "down" : "right";
    try {
      const laid = await drawFlow(canvas, view, facts, phone.matches ? "DOWN" : "RIGHT");
      if (turn !== drawing) return;
      page.dataset.state = "ready";
      page.dataset.size = `${Math.round(laid.width)}x${Math.round(laid.height)}`;
    } catch (error) {
      if (turn !== drawing) return;
      page.dataset.state = "failed";
      canvas.replaceChildren(h("p", { role: "status", class: "empty" }, `${words.couldNotDraw} ${error.message}`));
    }
  }

  function render() {
    page.removeAttribute("aria-busy");
    if (inspection.error)
      return notice(main, h("p", { role: "status", class: "empty" }, words.couldNotRead, " ", inspection.error.message));
    const { model } = store.getState();
    if (page.parentNode !== main) main.replaceChildren(page);
    if (!model) {
      page.setAttribute("aria-busy", "true");
      return page.replaceChildren(h("p", { role: "status", class: "loading", "data-part": "loading" }, words.loading));
    }
    const view = flowView(model, address);
    if (!view) return notice(main, h("h1", {}, shell.notFound), h("p", {}, `${words.noWorkflow} `, h("code", {}, `#/${address}`), "."));
    const standing = live.state.data?.version === model.snapshot.version ? live.state.data : null;
    const facts = factsOf(standing);
    const next = JSON.stringify([model.snapshot.version, standing?.version ?? null, phone.matches]);
    if (next === signature && canvas.parentNode) return;
    signature = next;
    const head = h(
      "header",
      { class: "page-head" },
      cardHeader(view.workflow, facts.marks(address)),
      view.workflow.says ? authored(view.workflow.says, "p", { class: "says" }) : null,
    );
    page.replaceChildren(head, scroll);
    paint(view, facts);
  }

  const offLive = live.subscribe(render);
  const offStore = store.subscribe(render);
  phone.addEventListener("change", render);
  render();
  return () => {
    drawing++;
    offLive();
    offStore();
    phone.removeEventListener("change", render);
  };
}
