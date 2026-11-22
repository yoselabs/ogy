import { marksFor, cardHeader } from "../ui/card-header.js";
import { h } from "../ui/dom.js";
import { words } from "../ui/words.js";
import { bindWaiting } from "../views/waiting.js";

const TABS = [
  ["details", words.details],
  ["waiting", words.waiting],
  ["agent", words.agent],
];

// The one right rail: three tabs, one panel. Below 720px it sits under the page and a tab opens it in place.
export function mountRail(root, { router, live, store }) {
  let open = false;
  let unbind = null;
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
  buttons.find((button) => button.dataset.tab === "waiting").append(counts.get("waiting"));
  const paint = (route = router.current()) => {
    const active = ["details", "waiting", "agent"].includes(route.query.rail) ? route.query.rail : "details";
    for (const button of buttons) {
      button.setAttribute("aria-selected", String(button.dataset.tab === active));
      button.tabIndex = button.dataset.tab === active ? 0 : -1;
    }
    root.dataset.open = String(open);
    panel.setAttribute("aria-labelledby", `tab-${active}`);
    if (active === "waiting") {
      if (unbind) return;
      const host = h("div", { class: "rail-waiting" });
      panel.replaceChildren(host);
      unbind = bindWaiting(host, { live, store }, { compact: true });
      return;
    }
    unbind?.();
    unbind = null;
    const node = active === "details" && route.query.sel ? store.getState().model?.byId.get(route.query.sel) : null;
    const entry = node && live.state.data?.entries[node.address];
    panel.replaceChildren(node ? cardHeader(node, marksFor(entry)) : h("p", { class: "empty" }, words.emptyRail));
  };
  router.subscribe(paint);
  let seen = null;
  store.subscribe((state) => state.model !== seen && ((seen = state.model), paint()));
  live.subscribe(({ data }) => {
    counts.get("waiting").textContent = data ? ` ${data.totals.waiting}` : "";
    paint();
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
