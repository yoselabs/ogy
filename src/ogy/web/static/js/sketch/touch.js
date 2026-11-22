import { authored } from "../ui/authored.js";
import { h } from "../ui/dom.js";
import { linked } from "../ui/path.js";
import { words } from "./words.js";

// One row of what the sketch would touch: the existing entry, its sentence, and the way the sketch reaches it.
function row(model, item) {
  const how = [
    words.how[item.how] || item.how,
    item.via.length ? ` ${item.via.map((field) => (field === "of" ? words.partOf : field)).join(", ")}` : "",
  ].join("");
  const node = model.byId.get(item.address);
  return h(
    "li",
    { class: "touch-row", "data-touch": item.address, "data-how": item.how },
    node ? linked(node) : h("code", {}, item.address),
    h("span", { class: "touch-how" }, how),
    item.says ? authored(item.says, "p", { class: "says" }) : null,
  );
}

// "Would touch": the existing entries the sketch changes or links to, from the impact operation, nearest first.
export function touchBlock(model, sketch) {
  const rows = sketch.touching.map((item) => row(model, item));
  return h(
    "section",
    { class: "block sketch-touch", "data-part": "would-touch" },
    h("h2", {}, words.wouldTouch),
    rows.length ? h("ul", { class: "touch-list" }, rows) : h("p", { class: "empty" }, words.touchesNothing),
    sketch.more ? h("p", { class: "says" }, words.more(sketch.more)) : null,
  );
}
