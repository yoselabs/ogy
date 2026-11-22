import { cardHeader } from "../../ui/card-header.js";
import { glyph, h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { linked } from "../../ui/path.js";
import { owedTag, pathStrip } from "./diagram.js";
import { words } from "./words.js";

// The transitions as a list under the graph: the whole of who fires each one, and the readable form on a narrow screen.
function stateNames(states) {
  return h(
    "span",
    { class: "lc-states" },
    states.map((state) => mention(state, { self: true })),
  );
}

function fact(label, ...content) {
  return h("div", { class: "lc-fact" }, h("dt", {}, label), h("dd", {}, ...content));
}

function rowHead(node, owed, facts) {
  const header = cardHeader(node, facts.marks(node.address));
  header.classList.add("lc-row-head");
  if (owed) header.querySelector(".card-header-side").prepend(owedTag());
  return header;
}

function row(transition, facts) {
  const { node, from, to, firedBy, events, owed } = transition;
  return h(
    "li",
    {
      class: `lc-row${owed ? " is-owed" : ""}`,
      "data-part": "transition",
      "data-address": node.address,
      "data-owed": owed ? "true" : "false",
    },
    rowHead(node, owed, facts),
    h(
      "dl",
      { class: "lc-facts" },
      from.length ? fact(words.from, stateNames(from)) : null,
      to ? fact(words.to, stateNames([to])) : null,
      firedBy.length ? fact(words.firedBy, h("div", { class: "lc-paths" }, firedBy.map(pathStrip))) : null,
      events.length ? fact(words.eventOf, events.map(linked)) : null,
    ),
    owed ? h("p", { class: "gap", "data-part": "gap" }, glyph("owed"), h("span", {}, words.nothingFires)) : null,
  );
}

export function transitionList(transitions, facts) {
  return h(
    "ul",
    { class: "lc-rows", "data-part": "transitions" },
    transitions.map((transition) => row(transition, facts)),
  );
}
