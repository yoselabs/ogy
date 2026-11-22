import { glyph, h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { words } from "./words.js";

export const PAGE = 20;

// Matched letters of the title are marked; the name itself stays one authored element.
function lit(row, query) {
  const holder = row.querySelector("[data-identity-text]");
  const needle = query.trim().toLowerCase();
  const text = holder.textContent;
  const at = needle ? text.toLowerCase().indexOf(needle) : -1;
  if (at < 0) return;
  holder.replaceChildren(text.slice(0, at), h("mark", {}, text.slice(at, at + needle.length)), text.slice(at + needle.length));
}

function row(item, id, query) {
  const link = h(
    "a",
    { class: "result", role: "option", id, href: `#/${item.goes}`, "data-address": item.goes, "data-kind": item.kind, tabindex: "-1" },
    h(
      "span",
      { class: "result-name" },
      mention(item.node, { self: true }),
      item.context ? h("span", { class: "result-context" }, item.context) : null,
    ),
    h("small", { class: "kind-word" }, item.kind),
  );
  lit(link, query);
  return link;
}

// The list: one group per kind with its count, PAGE rows each, then a button for the rest. `open` holds the kinds shown in full.
// Returns the rows and buttons in the order the arrow keys walk them.
export function renderResults(list, groups, query, open) {
  const walk = [];
  list.replaceChildren(
    ...groups.map((group, g) => {
      const shown = open.has(group.kind) ? group.items : group.items.slice(0, PAGE);
      const heading = h(
        "h2",
        { class: "group-head", id: `group-${g}` },
        glyph(group.kind),
        h("span", {}, group.kind),
        h("b", {}, String(group.items.length)),
      );
      const rows = shown.map((item, i) => {
        const link = row(item, `result-${g}-${i}`, query);
        walk.push(link);
        return link;
      });
      if (shown.length < group.items.length) {
        const more = h(
          "button",
          { type: "button", class: "more", role: "option", id: `more-${g}`, "data-more": group.kind, tabindex: "-1" },
          `${group.items.length - shown.length} ${words.more}`,
        );
        rows.push(more);
        walk.push(more);
      }
      return h("div", { role: "group", "aria-labelledby": `group-${g}`, class: "group" }, heading, rows);
    }),
  );
  return walk;
}
