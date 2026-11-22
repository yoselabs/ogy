import { h } from "../../ui/dom.js";
import { linked } from "../../ui/path.js";
import { words } from "./words.js";

export const LEVELS = [1, 2, 3];
export const DEFAULT_LEVEL = 1;

export function levelOf(query) {
  const level = Number(query.level);
  return LEVELS.includes(level) ? level : DEFAULT_LEVEL;
}

// The level control: three buttons, one pressed. Level 1 draws steps and ends, 2 adds what each step does, 3 why each way on.
export function levelControl(current, choose) {
  return h(
    "div",
    { class: "flow-levels", role: "group", "aria-label": words.level, "data-part": "levels" },
    h("span", { class: "flow-label" }, words.level),
    LEVELS.map((level) =>
      h(
        "button",
        {
          type: "button",
          class: "level-button",
          "data-level": level,
          "aria-pressed": String(level === current),
          title: words.levels[level - 1],
          onclick: () => choose(level),
        },
        String(level),
      ),
    ),
  );
}

// Under the graph: everything the workflow touches, once, with what is done to it.
export function touchedStrip(touched) {
  if (!touched.length) return null;
  return h(
    "section",
    { class: "flow-touched", "data-part": "touched" },
    h("span", { class: "flow-label" }, words.touches),
    h(
      "ul",
      { class: "flow-touched-list" },
      touched.map(({ owner, ops }) =>
        h("li", { class: "touched", "data-owner": owner.id }, linked(owner), h("span", { class: "touched-ops" }, [...ops].join(" · "))),
      ),
    ),
  );
}
