import { glyph, h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { head, says, stateStrip } from "./parts.js";
import { words } from "./words.js";

// Entities, each with its states in lifecycle order.
export function entitiesSection(view, facts) {
  if (!view.entities.length) return null;
  return h(
    "section",
    { class: "block", "data-part": "entities" },
    h("h2", {}, words.entities),
    h(
      "ul",
      { class: "entity-list" },
      view.entities.map(({ entity, states }) =>
        h(
          "li",
          { class: "entity", "data-part": "entity", "data-address": entity.address },
          head(entity, facts),
          says(entity),
          states.length ? stateStrip(states) : null,
        ),
      ),
    ),
  );
}

// Every other kind of the area as one collapsed row: icon, the kind word and how many; a decision row says how many wait.
function kindRow(group, facts) {
  const waiting = group.nodes.filter((node) => facts.waiting(node.address)).length;
  return h(
    "details",
    { class: "kind-row", "data-part": "kind-row", "data-kind": group.kind },
    h(
      "summary",
      {},
      glyph(group.kind),
      h("span", { class: "kind-name" }, group.kind),
      h("span", { class: "pill", "data-part": "count" }, String(group.nodes.length)),
      waiting ? h("span", { class: "pill pill-waiting" }, glyph("waiting"), `${waiting} ${words.waiting}`) : null,
    ),
    h(
      "ul",
      { class: "mention-list" },
      group.nodes.map((node) =>
        h("li", {}, mention(node), facts.waiting(node.address) ? h("span", { class: "pill pill-waiting" }, words.waiting) : null),
      ),
    ),
  );
}

export function othersSection(view, facts) {
  if (!view.others.length) return null;
  return h(
    "section",
    { class: "block", "data-part": "others" },
    h("h2", {}, words.others),
    h(
      "div",
      { class: "kind-rows" },
      view.others.map((group) => kindRow(group, facts)),
    ),
  );
}
