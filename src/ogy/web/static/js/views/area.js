import { authored } from "../ui/authored.js";
import { glyph, h } from "../ui/dom.js";
import { words as shell } from "../ui/words.js";
import { areaView } from "./area/data.js";
import { chainSection } from "./area/chain.js";
import { entitiesSection, othersSection } from "./area/others.js";
import { factsOf, head } from "./area/parts.js";
import { words } from "./area/words.js";

// An area, #/<layer>/<area>: why each workflow exists, then its entities, then everything else.
const PATH = /^(product|software)\/([^/]+)$/;

export const areaRoute = {
  test: (path) => PATH.test(path),
  get layer() {
    const first = location.hash.replace(/^#\/?/, "").split("/")[0];
    return first === "product" || first === "software" ? first : null;
  },
  mount: mountArea,
  crumbs: (route) => [
    { text: shell.board, href: "#/" },
    { text: shell[route.segments[0]], href: route.segments[0] === "product" ? "#/" : "#/software" },
    { text: route.segments[1] },
  ],
};

function notice(main, ...children) {
  main.replaceChildren(h("section", { class: "page notice area" }, ...children));
}

// The head of the page: the area as a header, its sentence, and the two counts that call for the owner.
function pageHead(view, facts, standing, layer, area) {
  const node = view.entry || { id: `${layer}/${area}`, address: `${layer}/${area}`, key: area, kind: "area", title: "" };
  const waiting = Object.keys(standing?.decisions || {}).filter(
    (address) => address.startsWith(`${layer}/${area}/`) && facts.waiting(address),
  );
  const owed = facts.owed(`${layer}/${area}`);
  const stats = [
    waiting.length
      ? h(
          "a",
          { class: "stat is-waiting", href: "#/waiting", "data-stat": "waiting" },
          glyph("waiting"),
          h("b", {}, String(waiting.length)),
          h("span", {}, shell.waitingCount),
        )
      : null,
    owed
      ? h("span", { class: "stat is-owed", "data-stat": "owed" }, glyph("owed"), h("b", {}, String(owed)), h("span", {}, shell.owed))
      : null,
  ];
  return h(
    "header",
    { class: "page-head" },
    head(node, facts),
    view.entry?.says ? authored(view.entry.says, "p", { class: "says" }) : null,
    stats.some(Boolean) ? h("div", { class: "stats" }, stats) : null,
  );
}

export function mountArea(main, { store, live, inspection, route }) {
  const [layer, area] = route.segments;
  const page = h("section", { class: "page area", "data-part": "area", "data-address": `${layer}/${area}` });
  let signature = null;

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
    const view = areaView(model, layer, area);
    if (!view) return notice(main, h("h1", {}, shell.notFound), h("p", {}, `${words.noArea} `, h("code", {}, `#/${layer}/${area}`), "."));
    // Standing that belongs to another snapshot than the document on screen is not shown.
    const standing = live.state.data?.version === model.snapshot.version ? live.state.data : null;
    const facts = factsOf(standing);
    const next = JSON.stringify([model.snapshot.version, standing?.version ?? null]);
    if (next === signature && page.querySelector("[data-part=chain], [data-part=others], .page-head")) return;
    signature = next;
    const sections = [chainSection(view, facts), entitiesSection(view, facts), othersSection(view, facts)].filter(Boolean);
    page.replaceChildren(
      pageHead(view, facts, standing, layer, area),
      ...(sections.length ? sections : [h("p", { class: "empty" }, words.nothing)]),
    );
  }

  const offLive = live.subscribe(render);
  const offStore = store.subscribe(render);
  render();
  return () => {
    offLive();
    offStore();
  };
}
