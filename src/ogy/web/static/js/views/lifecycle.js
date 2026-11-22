import { authored } from "../ui/authored.js";
import { glyph, h } from "../ui/dom.js";
import { words as shell } from "../ui/words.js";
import { factsOf, head } from "./area/parts.js";
import { drawLifecycle } from "./lifecycle/diagram.js";
import { lifecycleView } from "./lifecycle/data.js";
import { transitionList } from "./lifecycle/rows.js";
import { words } from "./lifecycle/words.js";

// An entity's lifecycle, #/<layer>/<area>/entity/<id>: its states and transitions drawn, then who fires each transition.
const PATH = /^(product|software)\/([^/]+)\/entity\/([^/]+)$/;

export const lifecycleRoute = {
  test: (path) => PATH.test(path),
  get layer() {
    const first = location.hash.replace(/^#\/?/, "").split("/")[0];
    return first === "product" || first === "software" ? first : null;
  },
  mount: mountLifecycle,
  crumbs: (route) => [
    { text: shell.board, href: "#/" },
    { text: shell[route.segments[0]], href: route.segments[0] === "product" ? "#/" : "#/software" },
    { text: route.segments[1], href: `#/${route.segments[0]}/${route.segments[1]}` },
    { text: route.segments[3] },
  ],
};

function notice(main, ...children) {
  main.replaceChildren(h("section", { class: "page notice area" }, ...children));
}

function pageHead(view, facts) {
  const owed = facts.owed(view.entity.address);
  return h(
    "header",
    { class: "page-head" },
    head(view.entity, facts),
    view.entity.says ? authored(view.entity.says, "p", { class: "says" }) : null,
    owed
      ? h(
          "div",
          { class: "stats" },
          h("span", { class: "stat is-owed", "data-stat": "owed" }, glyph("owed"), h("b", {}, String(owed)), h("span", {}, shell.owed)),
        )
      : null,
  );
}

export function mountLifecycle(main, { store, live, inspection, route }) {
  const [layer, area, , key] = route.segments;
  const page = h("section", { class: "page area lifecycle", "data-part": "lifecycle", "data-address": `${layer}/${area}/entity/${key}` });
  let signature = null;
  let drawing = 0;

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
    const view = lifecycleView(model, layer, area, key);
    if (!view) return notice(main, h("h1", {}, shell.notFound), h("p", {}, `${words.noEntity} `, h("code", {}, `#/${route.path}`), "."));
    // Standing that belongs to another snapshot than the document on screen is not shown.
    const standing = live.state.data?.version === model.snapshot.version ? live.state.data : null;
    const next = JSON.stringify([model.snapshot.version, standing?.version ?? null]);
    if (next === signature) return;
    signature = next;
    const facts = factsOf(standing);
    const host = h("div", { class: "lc-host", role: "img", "aria-label": words.diagram });
    page.replaceChildren(
      ...[
        pageHead(view, facts),
        view.states.length
          ? h(
              "section",
              { class: "block", "data-part": "diagram-block" },
              h("h2", {}, words.lifecycle),
              h("p", { class: "note" }, words.moves),
              host,
            )
          : h("p", { class: "empty", "data-part": "no-states" }, words.noStates),
        view.transitions.length
          ? h("section", { class: "block" }, h("h2", {}, words.transitions), transitionList(view.transitions, facts))
          : null,
      ].filter(Boolean),
    );
    if (!view.states.length) return;
    const mine = ++drawing;
    drawLifecycle(host, view, facts).then(
      (summary) => mine === drawing && (host.dataset.edges = String(summary.edges)),
      (error) =>
        mine === drawing && host.replaceChildren(h("p", { role: "status", class: "empty" }, `${words.layoutFailed} ${error.message}`)),
    );
  }

  const offLive = live.subscribe(render);
  const offStore = store.subscribe(render);
  render();
  return () => {
    drawing++;
    offLive();
    offStore();
  };
}
