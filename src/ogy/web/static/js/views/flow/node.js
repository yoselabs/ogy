import { authored } from "../../ui/authored.js";
import { glyph, h } from "../../ui/dom.js";
import { identity } from "../../model/descriptor.js";
import { linked } from "../../ui/path.js";
import { chips, condition, effectBadge } from "./badges.js";
import { nodeHeader } from "./head.js";
import { words } from "./words.js";

// What a call step adds: the workflow it runs; at level 3 also how each way that workflow ends leads on.
function callBlock(call, level) {
  const run = h("div", { class: "flow-call", "data-part": "call" }, h("span", { class: "flow-label" }, words.runs), linked(call.callee));
  if (level < 3) return [run];
  const ways = call.ways.map((way) =>
    h(
      "li",
      { class: "flow-way", "data-row": way.row.id },
      ...way.ends.map((end) =>
        h("span", { class: `flow-end end-${end.result}`, "data-covers": end.id }, glyph("end"), authored(identity(end).title)),
      ),
      way.ends.length ? " → " : null,
      way.then ? authored(identity(way.then).title) : null,
    ),
  );
  return [run, h("div", { class: "flow-label" }, words.thenByEnd), h("ol", { class: "flow-ways" }, ways)];
}

// Level 3 for a step that does not call: each row with the condition it waits for.
function rowsBlock(rows) {
  const items = rows.map((row) =>
    h("li", { class: "step-row", "data-row": row.id }, h("span", { class: "step-row-key" }, authored(identity(row).title)), condition(row)),
  );
  return items.length ? h("ol", { class: "step-rows" }, items) : null;
}

// The reached-by-failure line of an end: it says which called workflow failed on the way here.
function afterBlock(after) {
  if (!after.length) return null;
  return h(
    "p",
    { class: "flow-after", "data-part": "after-failure" },
    words.alsoReached,
    " ",
    ...after.flatMap((callee, index) => [index ? ", " : "", linked(callee)]),
    " ",
    words.failed,
  );
}

// The body a node carries beyond its header, by level: 1 nothing; 2 who acts, what it changes, what it runs; 3 and why each way on.
function bodyOf(item, level) {
  if (level < 2) return [];
  if (item.node?.kind === "end") return [afterBlock(item.after || [])];
  const facts = item.facts;
  if (!facts) return [];
  const body = [chips(facts), facts.call ? callBlock(facts.call, level) : null];
  if (facts.effects.length) body.push(h("ul", { class: "flow-fx" }, facts.effects.map(effectBadge)));
  if (level >= 3) {
    if (item.node.says) body.unshift(authored(item.node.says, "p", { class: "says" }));
    if (!facts.call) body.push(rowsBlock(facts.rows));
  }
  return body;
}

export function nodeElement(item, { level, marks, hrefOf, select }) {
  if (item.stub) {
    return h("div", { class: `flow-node flow-start${item.sketch ? " is-sketch" : ""}`, "data-node": item.id }, h("span", {}, words.start));
  }
  const { node } = item;
  const classes = ["flow-node", `kind-${node.kind}`];
  if (node.sketch)
    classes.push("is-sketch"); // a sketched end carries no result colour: a sketch never shows a status
  else if (node.kind === "end") classes.push(`end-${node.result}`);
  if (item.external) classes.push("is-external");
  const clickable = !item.external;
  const header = nodeHeader(node, marks(node.address), clickable ? { href: hrefOf(node.id), select } : { link: true });
  if (node.sketch)
    header.querySelector(".card-header-side").prepend(h("small", { class: "sketch-word", "data-part": "sketch-word" }, "sketch"));
  return h("div", { class: classes.join(" "), "data-node": item.id, "data-address": node.address || null }, header, ...bodyOf(item, level));
}
