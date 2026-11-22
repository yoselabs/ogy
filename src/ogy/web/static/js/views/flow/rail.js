import { identity } from "../../model/descriptor.js";
import { authored } from "../../ui/authored.js";
import { cardHeader } from "../../ui/card-header.js";
import { h } from "../../ui/dom.js";
import { landing } from "../../ui/landing.js";
import { chips, condition, effectBadge } from "./badges.js";
import { stepFacts, thenOf } from "./facts.js";
import { words } from "./words.js";

// A step or an end of a workflow selected on its page, as the side panel shows it: the step's own facts, and each of its ways on
// as a button that walks there (the selection moves to where the row leads, so the page highlights the next step).
function wayButton(step, row, { model, router }) {
  const [to] = thenOf(model, row);
  const inside = to && to.parent === step.parent;
  const go = () => (inside ? router.setQuery("sel", to.id) : (location.hash = landing(to.address || to.id)));
  return h(
    "li",
    { class: "walk-row", "data-row": row.id },
    h(
      "button",
      { type: "button", class: "walk-choice", "data-then": to?.id || null, onclick: go },
      h("span", { class: "walk-key" }, authored(identity(row).title)),
      to ? h("span", { class: "walk-to" }, " → ", authored(identity(to).title)) : null,
    ),
    condition(row),
  );
}

export function walkPanel(node, context) {
  const { model, marks } = context;
  if (!["step", "end"].includes(node.kind) || model.byId.get(node.parent)?.kind !== "workflow") return null;
  const body = [cardHeader(node, marks), node.says ? authored(node.says, "p", { class: "says" }) : null];
  if (node.kind === "end") return h("div", { class: "walk", "data-part": "walk" }, body, h("p", { class: "walk-result" }, node.result));
  const facts = stepFacts(model, node);
  body.push(chips(facts));
  if (facts.effects.length) body.push(h("ul", { class: "flow-fx" }, facts.effects.map(effectBadge)));
  if (facts.rows.length)
    body.push(
      h("h3", { class: "flow-label" }, words.rows),
      h(
        "ol",
        { class: "walk-rows" },
        facts.rows.map((row) => wayButton(node, row, context)),
      ),
    );
  return h("div", { class: "walk", "data-part": "walk" }, body);
}
