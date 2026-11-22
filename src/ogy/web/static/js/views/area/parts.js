import { authored } from "../../ui/authored.js";
import { marksFor } from "../../ui/card-header.js";
import { glyph, h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { words as shell } from "../../ui/words.js";
import { words } from "./words.js";

// What standing says about an address; empty while standing is not loaded or belongs to another snapshot.
export function factsOf(standing) {
  const work = standing?.work || [];
  return {
    loaded: Boolean(standing),
    marks: (address) => marksFor(standing?.entries?.[address]),
    owed: (address) => work.filter((item) => item.address === address || item.address.startsWith(`${address}/`)).length,
    waiting: (address) => standing?.decisions?.[address]?.status === "waiting",
  };
}

export function owedMark(count) {
  return h(
    "span",
    { class: "mark mark-owed", title: `${count} ${words.owed}`, "data-part": "owed" },
    glyph("owed"),
    h("b", {}, String(count)),
    h("span", { class: "sr-only" }, words.owed),
  );
}

// Owed work found in the chain itself: a goal nothing realizes, a capability nothing realizes. Same amber as the standing marks.
export function gap(text) {
  return h("p", { class: "gap", "data-part": "gap" }, glyph("owed"), h("span", {}, text));
}

// Icon, title, status marks and the corner kind word: the compact head of every row.
export function head(node, facts) {
  const marks = facts
    .marks(node.address)
    .map((name) =>
      h("span", { class: `mark mark-${name}`, title: shell[name] }, glyph(name), h("span", { class: "sr-only" }, shell[name])),
    );
  const owed = facts.owed(node.address);
  return h(
    "div",
    { class: "card-header", "data-address": node.address },
    mention(node),
    h("span", { class: "card-header-side" }, marks, owed ? owedMark(owed) : null, h("small", { class: "kind-word" }, node.kind)),
  );
}

export function says(node) {
  return node.says ? authored(node.says, "p", { class: "says" }) : null;
}

// Step dots in the order a reader meets them; an end carries its result, in the status colour of that result.
export function flowStrip(items) {
  return h(
    "ol",
    { class: "strip-flow", "data-part": "flow" },
    items.map((node) => {
      const end = node.kind === "end";
      return h(
        "li",
        { class: `strip-item${end ? ` end-${node.result}` : ""}`, "data-kind": node.kind },
        mention(node),
        end ? h("small", { class: "end-result" }, node.result) : null,
      );
    }),
  );
}

export function stateStrip(states) {
  return h(
    "ol",
    { class: "strip-flow strip-state", "data-part": "states" },
    states.map((node) => h("li", { class: "strip-item", "data-kind": "state" }, mention(node))),
  );
}
