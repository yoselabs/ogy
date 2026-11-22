import { authored } from "../../ui/authored.js";
import { glyph, h } from "../../ui/dom.js";
import { linked } from "../../ui/path.js";

// One effect of a row as a badge: the operation's glyph and word, what it is done to, and for a transition `from → to`.
// create has a green edge and delete a red one (class fx-create, fx-delete); a write names the attribute it writes.
export function effectBadge(effect) {
  const states = (list) => list.flatMap((state, index) => [index ? " · " : "", linked(state)]);
  return h(
    "li",
    { class: `fx fx-${effect.do}`, "data-effect": effect.do, title: effect.row ? effect.row.key : null },
    glyph(effect.do, true),
    h("span", { class: "fx-do" }, effect.do),
    effect.target ? linked(effect.target.kind === "transition" ? effect.owner : effect.target) : null,
    effect.target?.kind === "transition"
      ? h("span", { class: "fx-tag", "data-part": "transition-tag" }, states(effect.from), " → ", effect.to.map(linked))
      : null,
  );
}

// Who acts on a step and which interfaces serve it, as chips with the one mention function.
export function chips(facts) {
  const items = [
    facts.actor && h("span", { class: "chip chip-actor", "data-chip": "actor" }, linked(facts.actor)),
    ...facts.interfaces.map((one) => h("span", { class: "chip chip-interface", "data-chip": "interface" }, linked(one))),
  ].filter(Boolean);
  return items.length ? h("div", { class: "flow-chips" }, items) : null;
}

export function condition(row) {
  return row.when ? authored(row.when, "span", { class: "flow-when" }) : null;
}
