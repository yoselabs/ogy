import { authored } from "../ui/authored.js";
import { h } from "../ui/dom.js";
import { mention } from "../ui/mention.js";
import { linked } from "../ui/path.js";
import { words } from "./words.js";

const button = (label, onclick, props = {}) => h("button", { type: "button", class: "btn", onclick, ...props }, label);

// What a target is called: the entry's own mention when the page knows it, its address otherwise (it may be gone since).
function name(model, address, reachable) {
  const node = model?.byId.get(address);
  if (!node) return h("code", { class: "agent-gone" }, address);
  return reachable ? linked(node) : mention(node, { self: true });
}

function targetRow(model, target, index, { state, reaches }) {
  const reachable = reaches(target.address);
  return h(
    "li",
    { class: "agent-target", "data-n": index + 1, "data-here": reachable, "aria-current": index === state.index ? "step" : null },
    h("span", { class: "agent-n", "aria-hidden": "true" }, String(index + 1)),
    h(
      "div",
      { class: "agent-what" },
      name(model, target.address, reachable),
      authored(target.says, "p", { class: "agent-says" }),
      reachable ? null : h("p", { class: "agent-away", "data-part": "away" }, words.away),
    ),
  );
}

function callRow(row) {
  const text = [row.action === "show" ? row.title : words.actions[row.action] || row.action, row.result !== "shown" ? row.result : ""];
  return h(
    "li",
    { class: `agent-call is-${row.action}` },
    h("b", {}, `#${row.sequence}`),
    " ",
    authored(row.session, "span", { class: "agent-session" }),
    " ",
    authored(text.filter(Boolean).join(": "), "span"),
  );
}

function log(rows) {
  if (!rows.length) return null;
  return h(
    "details",
    { class: "agent-log", "data-part": "agent-log" },
    h("summary", {}, words.calls(rows.length)),
    h("ol", {}, rows.map(callRow)),
  );
}

function nav(state, controls, last) {
  return h(
    "div",
    { class: "agent-nav", "data-part": "agent-nav" },
    button(words.back, controls.back, { "data-action": "back", disabled: state.index === 0 || state.request }),
    h("span", { class: "agent-step" }, words.step(state.index + 1, last + 1)),
    button(words.next, controls.next, { "data-action": "next", disabled: state.index === last || state.request }),
    button(words.dismiss, controls.dismiss, { "data-action": "dismiss" }),
  );
}

// Title, who, the request when the owner was busy, Back / Next / Dismiss (where a phone sees them first), then the sentences.
function body(state, model, controls) {
  const spot = state.spotlight;
  if (!spot) return [h("p", { class: "empty", "data-part": "agent-empty" }, words.nothing)];
  const request = h(
    "p",
    { class: "agent-request", role: "status" },
    words.request,
    " ",
    button(words.show, controls.show, { "data-action": "show" }),
  );
  return [
    authored(spot.title, "h2", { class: "agent-title", "data-part": "agent-title" }),
    h("p", { class: "agent-by" }, `${words.by} `, authored(spot.session)),
    state.request ? request : null,
    nav(state, controls, spot.targets.length - 1),
    h(
      "ol",
      { class: "agent-targets", "data-part": "agent-targets" },
      spot.targets.map((target, index) => targetRow(model, target, index, { state, reaches: controls.reaches })),
    ),
  ];
}

// The Agent tab: the title, the numbered targets with the agent's sentence each, Back / Next / Dismiss, the connection and the log.
export function bindAgent(host, { spotlight, store }) {
  const paint = () => {
    const { state } = spotlight;
    const model = store.getState().model;
    host.dataset.state = state.connection;
    const focused = host.contains(document.activeElement) ? document.activeElement.dataset.action : null;
    host.replaceChildren(
      h("p", { class: "agent-conn", "data-part": "agent-connection", "data-state": state.connection }, words.connection[state.connection]),
      ...[...body(state, model, spotlight), log(state.log)].filter(Boolean),
    );
    if (focused) host.querySelector(`[data-action=${focused}]:not(:disabled)`)?.focus();
  };
  const offSpot = spotlight.subscribe(paint);
  let seen = null;
  const offStore = store.subscribe((next) => next.model !== seen && ((seen = next.model), paint()));
  return () => {
    offSpot();
    offStore();
  };
}
