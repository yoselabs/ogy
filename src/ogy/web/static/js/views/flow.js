import { authored } from "../ui/authored.js";
import { cardHeader } from "../ui/card-header.js";
import { h } from "../ui/dom.js";
import { words as shell } from "../ui/words.js";
import { factsOf } from "./area/parts.js";
import { format } from "../shell/router.js";
import { DEFAULT_LEVEL, levelControl, levelOf, touchedStrip } from "./flow/controls.js";
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

export function mountFlow(main, { store, live, inspection, route, router }) {
  const address = route.path;
  const page = h("section", { class: "page flow", "data-part": "flow", "data-address": address });
  const canvas = h("div", { class: "flow-canvas", "data-part": "flow-graph" });
  const scroll = h("div", { class: "flow-scroll", role: "group", "aria-label": words.graph, tabindex: "0" }, canvas);
  const phone = matchMedia(PHONE);
  let signature = null;
  let drawing = 0;

  const query = () => router.current().query;
  const hrefOf = (id) => format(address, { ...query(), sel: id });
  const select = (id) => router.setQuery("sel", id);

  // The selected step or end is highlighted in place; nothing is laid out again.
  function markSelected() {
    const chosen = query().sel;
    for (const node of canvas.querySelectorAll("[data-node]")) {
      const on = node.dataset.node === chosen;
      node.classList.toggle("is-selected", on);
      if (on) node.setAttribute("aria-current", "true");
      else node.removeAttribute("aria-current");
    }
  }

  async function paint(view, facts, level) {
    const turn = ++drawing;
    page.dataset.state = "laying";
    page.dataset.level = String(level);
    canvas.dataset.direction = phone.matches ? "down" : "right";
    canvas.dataset.level = String(level);
    try {
      const laid = await drawFlow(canvas, view, phone.matches ? "DOWN" : "RIGHT", { level, marks: facts.marks, hrefOf, select });
      markSelected();
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
    const level = levelOf(query());
    const next = JSON.stringify([model.snapshot.version, standing?.version ?? null, phone.matches, level]);
    if (next === signature && canvas.parentNode) return;
    signature = next;
    const head = h(
      "header",
      { class: "page-head" },
      cardHeader(view.workflow, facts.marks(address)),
      view.workflow.says ? authored(view.workflow.says, "p", { class: "says" }) : null,
      levelControl(level, (chosen) => router.setQuery("level", chosen === DEFAULT_LEVEL ? "" : String(chosen))),
    );
    page.replaceChildren(...[head, scroll, touchedStrip(view.touched)].filter(Boolean));
    paint(view, facts, level);
  }

  const offRoute = router.subscribe(() => {
    render();
    markSelected();
  });
  const offLive = live.subscribe(render);
  const offStore = store.subscribe(render);
  phone.addEventListener("change", render);
  render();
  return () => {
    drawing++;
    offRoute();
    offLive();
    offStore();
    phone.removeEventListener("change", render);
  };
}
