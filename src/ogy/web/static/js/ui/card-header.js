import { glyph, h } from "./dom.js";
import { mention } from "./mention.js";
import { words } from "./words.js";

// Standing marks a header can carry, in a fixed order; a mark is drawn only where its fact holds.
const MARKS = ["unagreed", "changed"];

export function marksFor(entry) {
  if (!entry) return [];
  return [entry.source === "ai" && "unagreed", entry.changed && "changed"].filter(Boolean);
}

// Header of every card, row and rail panel: icon, title, corner kind word, status marks.
export function cardHeader(node, marks = []) {
  const shown = MARKS.filter((name) => marks.includes(name));
  return h(
    "header",
    { class: "card-header" },
    mention(node, { self: true }),
    h(
      "span",
      { class: "card-header-side" },
      shown.map((name) =>
        h("span", { class: `mark mark-${name}`, title: words[name] }, glyph(name), h("span", { class: "sr-only" }, words[name])),
      ),
      h("small", { class: "kind-word" }, node.kind),
    ),
  );
}
