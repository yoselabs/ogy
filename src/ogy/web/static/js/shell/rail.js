import { marksFor, cardHeader } from "../ui/card-header.js";
import { h } from "../ui/dom.js";
import { words } from "../ui/words.js";
import { walkPanel } from "../views/flow/rail.js";
import { bindAgent } from "../spotlight/agent-tab.js";
import { bindWaiting } from "../views/waiting.js";

const TABS = [
  ["details", words.details],
  ["waiting", words.waiting],
  ["agent", words.agent],
];

// The one right rail: three tabs, one panel. Below 720px it sits under the page and a tab opens it in place.
export function mountRail(root, { router, live, store, spotlight }) {
  let open = false;
  let unbind = null;
  let bound = null;
  const buttons = TABS.map(([name, label]) =>
    h(
      "button",
      {
        type: "button",
        role: "tab",
        id: `tab-${name}`,
        "aria-controls": "rail-panel",
        "data-tab": name,
        onclick: () => {
          const active = router.current().query.rail || "details";
          open = name === active ? !open : true;
          router.setQuery("rail", name === "details" ? "" : name);
        },
      },
      label,
    ),
  );
  const counts = new Map(buttons.map((button) => [button.dataset.tab, h("span", { class: "tab-count" })]));
  const panel = h("div", { role: "tabpanel", id: "rail-panel", class: "rail-panel" });
  root.append(h("div", { role: "tablist", class: "rail-tabs", "aria-label": words.tabs }, buttons), panel);
  for (const name of ["waiting", "agent"]) buttons.find((button) => button.dataset.tab === name).append(counts.get(name));
  const paint = (route = router.current()) => {
    const active = ["details", "waiting", "agent"].includes(route.query.rail) ? route.query.rail : "details";
    for (const button of buttons) {
      button.setAttribute("aria-selected", String(button.dataset.tab === active));
      button.tabIndex = button.dataset.tab === active ? 0 : -1;
    }
    root.dataset.open = String(open);
    panel.setAttribute("aria-labelledby", `tab-${active}`);
    if (active === "waiting" || active === "agent") {
      if (unbind && bound === active) return;
      unbind?.();
      bound = active;
      const host = h("div", { class: `rail-${active}` });
      panel.replaceChildren(host);
      unbind = active === "agent" ? bindAgent(host, { spotlight, store }) : bindWaiting(host, { live, store }, { compact: true });
      return;
    }
    bound = null;
    unbind?.();
    unbind = null;
    const node = active === "details" && route.query.sel ? store.getState().model?.byId.get(route.query.sel) : null;
    const entry = node && live.state.data?.entries[node.address];
    const marks = marksFor(entry);
    const walk = node && walkPanel(node, { model: store.getState().model, router, marks });
    panel.replaceChildren(walk || (node ? cardHeader(node, marks) : h("p", { class: "empty" }, words.emptyRail)));
  };
  router.subscribe(paint);
  let seen = null;
  store.subscribe((state) => state.model !== seen && ((seen = state.model), paint()));
  live.subscribe(({ data }) => {
    counts.get("waiting").textContent = data ? ` ${data.totals.waiting}` : "";
    paint();
  });
  // A new spotlight opens the panel under the page on a phone; the tab itself carries its target count on every size.
  let shown = 0;
  spotlight.subscribe(({ fresh, spotlight: active, request }) => {
    counts.get("agent").textContent = active ? ` ${active.targets.length}` : "";
    buttons.find((button) => button.dataset.tab === "agent").toggleAttribute("data-request", Boolean(request));
    if (fresh !== shown) {
      shown = fresh;
      open = !request;
      paint();
    }
  });
  root.addEventListener("keydown", (event) => {
    const keys = { ArrowRight: 1, ArrowLeft: -1 };
    if (!keys[event.key] || !event.target.matches("[role=tab]")) return;
    const next = buttons[(buttons.indexOf(event.target) + keys[event.key] + buttons.length) % buttons.length];
    next.focus();
    next.click();
  });
  paint();
}
