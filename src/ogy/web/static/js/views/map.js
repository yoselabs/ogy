import { authored } from "../ui/authored.js";
import { glyph, h } from "../ui/dom.js";
import { mention } from "../ui/mention.js";
import { words as shell } from "../ui/words.js";
import { factsOf } from "./area/parts.js";
import { mapView } from "./map/data.js";
import { words } from "./map/words.js";

// The Map, #/ (product) and #/software: one tile per area, what it is for, what it holds, and where trouble is.
const GOALS_SHOWN = 3;
const layerOf = (path) => (path === "software" ? "software" : "product");

export const mapRoutes = ["", "software"].map((path) => ({
  test: (candidate) => candidate === path,
  layer: layerOf(path),
  mount: mountMap,
  crumbs: () => (path === "" ? [{ text: shell.board }] : [{ text: shell.board, href: "#/" }, { text: shell.software }]),
}));

// Standing marks of one area, only where the fact holds. Waiting links to the list; the rest are plain counts.
function marks(standing, facts, scope) {
  const row = standing?.areas?.[scope];
  if (!row) return null;
  const pieces = [
    ["waiting", row.questions, "is-waiting", "#/waiting"],
    ["owed", facts.owed(scope), "is-owed", null],
    ["unagreed", row.ai, "", null],
    ["changed", row.changed, "", null],
  ].filter(([, count]) => count > 0);
  if (!pieces.length) return null;
  return h(
    "div",
    { class: "stats", "data-part": "marks", "aria-label": words.marks },
    pieces.map(([name, count, status, href]) => {
      const props = { class: `stat ${status}`.trim(), "data-stat": name };
      const body = [glyph(name), h("b", {}, String(count)), h("span", {}, words[name])];
      return href ? h("a", { ...props, href }, body) : h("span", props, body);
    }),
  );
}

function goalLines(tile, link) {
  if (!tile.goals.length)
    return tile.wantsGoal ? h("p", { class: "gap", "data-part": "gap" }, glyph("owed"), h("span", {}, words.noGoal)) : null;
  const shown = tile.goals.slice(0, GOALS_SHOWN);
  const rest = tile.goals.length - shown.length;
  return h(
    "ul",
    { class: "goal-lines", "data-part": "goals" },
    shown.map((goal) => h("li", { class: "goal-line" }, mention(goal), goal.says ? authored(goal.says, "span", { class: "says" }) : null)),
    rest > 0 ? h("li", {}, h("a", { class: "more", href: link }, `+${rest} ${words.more}`)) : null,
  );
}

function countLinks(tile, link) {
  return h(
    "ul",
    { class: "counts", "data-part": "counts", "aria-label": words.entries },
    tile.kinds.map(({ kind, count }) =>
      h(
        "li",
        {},
        h(
          "a",
          { class: "count", href: `${link}?kind=${kind}`, "data-kind": kind },
          glyph(kind),
          h("span", { class: "kind-name" }, kind),
          h("b", { "data-part": "count" }, String(count)),
        ),
      ),
    ),
  );
}

function tileOf(tile, layer, standing, facts) {
  const link = `#/${layer}/${tile.area}`;
  const node = tile.entry || { id: tile.scope, address: tile.scope, key: tile.area, kind: "area", title: "" };
  return h(
    "li",
    { class: "tile", "data-part": "tile", "data-address": tile.scope },
    h(
      "header",
      { class: "card-header" },
      h("h2", {}, mention(node, { href: link })),
      h("span", { class: "card-header-side" }, h("small", { class: "kind-word" }, "area")),
    ),
    tile.says ? authored(tile.says, "p", { class: "says" }) : null,
    goalLines(tile, link),
    marks(standing, facts, tile.scope),
    countLinks(tile, link),
  );
}

export function mountMap(main, { store, live, inspection, route }) {
  const layer = layerOf(route.path);
  const page = h("section", { class: "page map", "data-part": "map", "data-layer": layer });
  let signature = null;

  function render() {
    page.removeAttribute("aria-busy");
    if (page.parentNode !== main) main.replaceChildren(page);
    if (inspection.error)
      return page.replaceChildren(h("p", { role: "status", class: "empty" }, words.couldNotRead, " ", inspection.error.message));
    const { model } = store.getState();
    if (!model) {
      page.setAttribute("aria-busy", "true");
      return page.replaceChildren(h("p", { role: "status", class: "loading", "data-part": "loading" }, words.loading));
    }
    // Standing that belongs to another snapshot than the document on screen is not shown.
    const standing = live.state.data?.version === model.snapshot.version ? live.state.data : null;
    const next = JSON.stringify([model.snapshot.version, standing?.version ?? null]);
    if (next === signature && page.querySelector("[data-part=tiles], .empty")) return;
    signature = next;
    performance.mark("map-start");
    const tiles = mapView(model, layer);
    const facts = factsOf(standing);
    page.replaceChildren(
      h("h1", {}, shell[layer]),
      tiles.length
        ? h(
            "ul",
            { class: "tiles", "data-part": "tiles" },
            tiles.map((tile) => tileOf(tile, layer, standing, facts)),
          )
        : h("p", { class: "empty" }, words.nothing),
    );
    performance.measure("map-render", "map-start");
  }

  const offLive = live.subscribe(render);
  const offStore = store.subscribe(render);
  render();
  return () => {
    offLive();
    offStore();
  };
}
