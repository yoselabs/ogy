import { authored } from "../ui/authored.js";
import { marksFor } from "../ui/card-header.js";
import { glyph, h } from "../ui/dom.js";
import { linked, ownersOf, pathStrip } from "../ui/path.js";
import { words as shell } from "../ui/words.js";
import { words } from "./owed/words.js";

// The owed list, #/owed: every item of work `ogy work` lists, one row each, grouped by layer and then by cause.
const LAYERS = [
  ["product", shell.product],
  ["software", shell.software],
  ["constitution", words.constitution],
];
// Causes in the order they call for the owner; any other cause follows, alphabetically.
const CAUSES = ["unused", "unbuilt", "changed", "no-answer-path", "removed", "code changed since captured"];

const KINDS = new Set(["state", "transition", "case", "choice", "timeout", "step", "end", "effect", "option", "answer", "attribute"]);

// Before the inspection document arrives a row is named from its address: the last segment, with the kind before it.
function stub(address) {
  const parts = address.split("/");
  const last = parts.at(-1);
  const kind = KINDS.has(last) ? last : parts.at(-2) || "entry";
  return { id: address, address, key: last, kind, title: "" };
}

function order(list, name) {
  const at = list.indexOf(name);
  return at < 0 ? list.length : at;
}

function groups(work) {
  const byLayer = new Map();
  for (const item of work) {
    const layer = item.address.split("/")[0];
    const causes = byLayer.get(layer) || new Map();
    causes.set(item.cause, [...(causes.get(item.cause) || []), item]);
    byLayer.set(layer, causes);
  }
  const layers = LAYERS.map(([name]) => name);
  return [...byLayer]
    .sort(([a], [b]) => order(layers, a) - order(layers, b))
    .map(([layer, causes]) => ({
      layer,
      label: LAYERS.find(([name]) => name === layer)?.[1] || layer,
      causes: [...causes]
        .sort(([a], [b]) => order(CAUSES, a) - order(CAUSES, b) || a.localeCompare(b))
        .map(([cause, items]) => ({ cause, items: items.toSorted((a, b) => a.address.localeCompare(b.address)) })),
    }));
}

function row(item, model, standing) {
  const node = model?.byId.get(item.address) || stub(item.address);
  // A part is named by its owners, so "Otherwise" says which workflow and step it belongs to.
  const link = node.parent && model ? pathStrip(ownersOf(model, node), { "data-part": "owed-path" }) : linked(node);
  const area = item.address.split("/").slice(0, 2).join("/");
  const marks = marksFor(standing.entries?.[item.address]);
  return h(
    "li",
    { class: "owed-row", "data-part": "owed-row", "data-address": item.address, "data-cause": item.cause },
    h(
      "div",
      { class: "owed-head" },
      link,
      h(
        "span",
        { class: "card-header-side" },
        marks.map((name) =>
          h("span", { class: `mark mark-${name}`, title: shell[name] }, glyph(name), h("span", { class: "sr-only" }, shell[name])),
        ),
        h("small", { class: "kind-word" }, node.kind),
      ),
    ),
    h(
      "p",
      { class: "owed-detail" },
      authored(area, "small", { class: "owed-where" }),
      item.text ? authored(item.text, "span", { class: "owed-text" }) : null,
    ),
  );
}

function list(state, model) {
  if (!state.data)
    return h(
      "p",
      { role: "status", class: "waiting-note is-loading", "data-part": "loading" },
      state.error ? shell.countsUnavailable : words.loading,
    );
  const found = groups(state.data.work);
  if (!found.length) return h("p", { class: "waiting-note", "data-empty": true }, words.none);
  return h(
    "div",
    { class: "owed-list" },
    found.map((layer) =>
      h(
        "section",
        { class: "owed-layer", "aria-label": layer.label, "data-layer": layer.layer },
        h("h2", { class: "owed-layer-name" }, layer.label),
        layer.causes.map(({ cause, items }) =>
          h(
            "section",
            { class: "owed-cause", "data-cause": cause },
            h("h3", { class: "owed-cause-name" }, words.causes[cause] ?? cause, h("span", { class: "count" }, ` ${items.length}`)),
            h(
              "ul",
              { class: "owed-rows" },
              items.map((item) => row(item, model, state.data)),
            ),
          ),
        ),
      ),
    ),
  );
}

export function mountOwed(main, { store, live }) {
  const count = h("span", { class: "count", "data-part": "count" });
  const body = h("div", { "data-part": "owed-body" });
  main.replaceChildren(h("section", { class: "page waiting-page owed-page", "data-part": "owed" }, h("h1", {}, words.owed, count), body));
  let seen = null;
  const paint = () => {
    const model = store.getState().model;
    const next = [live.state.data, live.state.error, model];
    if (seen?.every((value, index) => value === next[index])) return;
    seen = next;
    count.textContent = live.state.data ? ` ${live.state.data.totals.owed}` : "";
    body.replaceChildren(list(live.state, model));
  };
  const offLive = live.subscribe(paint);
  const offStore = store.subscribe(paint);
  paint();
  return () => {
    offLive();
    offStore();
  };
}

export const owedRoute = {
  test: (path) => path === "owed",
  layer: null,
  mount: mountOwed,
  crumbs: () => [{ text: shell.board, href: "#/" }, { text: words.owed }],
};
