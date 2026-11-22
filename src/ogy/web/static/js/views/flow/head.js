import { glyph, h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { words as shell } from "../../ui/words.js";
import { words } from "./words.js";

// The header of a node: icon, title and corner kind word like every card header. A step and an end have no page of their own, so
// the title selects the node (the side panel shows it) instead of leading to a route that does not exist.
export function nodeHeader(node, marks, { href, select, link = false } = {}) {
  const title = mention(node, { self: !href && !link });
  if (href) {
    title.setAttribute("href", href);
    title.setAttribute("title", words.selectStep);
    title.dataset.select = node.id;
    title.addEventListener("click", (event) => {
      event.preventDefault();
      select(node.id);
    });
  }
  const kind = h("small", { class: "kind-word" }, node.kind);
  if (node.kind === "end") kind.append(` · ${node.result}`);
  return h(
    "header",
    { class: "card-header" },
    title,
    h(
      "span",
      { class: "card-header-side" },
      ["unagreed", "changed"]
        .filter((name) => marks.includes(name))
        .map((name) =>
          h("span", { class: `mark mark-${name}`, title: shell[name] }, glyph(name), h("span", { class: "sr-only" }, shell[name])),
        ),
      kind,
    ),
  );
}
