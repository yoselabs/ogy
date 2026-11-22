import { h } from "./dom.js";
import { landing } from "./landing.js";
import { mention } from "./mention.js";

// A name that leads to the page of the row it names (a workflow, an entity, a decision), drawn by the one mention function.
export function linked(node) {
  const link = mention(node);
  link.setAttribute("href", landing(node.address || node.id));
  return link;
}

// The owners of a row up to its top entry, outermost first, the row itself last: workflow, step, case.
export function ownersOf(model, row) {
  const path = [];
  for (let node = row; node; node = node.parent ? model.byId.get(node.parent) : null) path.unshift(node);
  return path;
}

// workflow › step › case: each name a link, the last one the row the path is about.
export function pathStrip(path, props = {}) {
  return h(
    "ol",
    { class: "strip-flow lc-path", "data-part": "path", ...props },
    path.map((node) => h("li", { class: "strip-item" }, linked(node))),
  );
}
