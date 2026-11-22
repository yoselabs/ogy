import { h } from "../ui/dom.js";
import { authored } from "../ui/authored.js";
import { mention } from "../ui/mention.js";
import { words } from "../ui/words.js";

// The waiting list: every decision whose computed status is "waiting", grouped by layer and area. The page at #/waiting
// and the rail's Waiting tab are the same list (the rail one compact). Keys: `g w` opens it, `j`/`k` move, Enter opens.
const LAYERS = [
  ["product", words.product],
  ["software", words.software],
];
// The row the owner last opened: Back remounts the list and puts focus here again.
let remembered = null;

function stub(address) {
  const key = address.split("/").at(-1);
  return { id: address, address, kind: "decision", key, title: "" };
}

function groups(decisions) {
  const rows = Object.entries(decisions)
    .filter(([, row]) => row.status === "waiting")
    .map(([address, row]) => ({ address, row, layer: address.split("/")[0], area: address.split("/")[1] }));
  const order = (layer) => LAYERS.findIndex(([name]) => name === layer) + 1 || LAYERS.length + 1;
  const byArea = new Map();
  for (const item of rows.toSorted(
    (a, b) => order(a.layer) - order(b.layer) || a.area.localeCompare(b.area) || a.address.localeCompare(b.address),
  )) {
    const key = `${item.layer}/${item.area}`;
    byArea.set(key, [...(byArea.get(key) || []), item]);
  }
  return [...byArea.entries()].map(([key, items]) => ({ key, layer: items[0].layer, area: items[0].area, items }));
}

const UNITS = [
  ["year", 31536000],
  ["month", 2592000],
  ["day", 86400],
  ["hour", 3600],
];
function age(iso) {
  const seconds = (Date.parse(iso) - Date.now()) / 1000;
  if (Number.isNaN(seconds)) return "";
  const [unit, size] = UNITS.find(([, size]) => Math.abs(seconds) >= size) || ["minute", 60];
  return new Intl.RelativeTimeFormat("en", { numeric: "auto" }).format(Math.round(seconds / size), unit);
}

function row(item, model, compact) {
  const node = model?.byId.get(item.address) || stub(item.address);
  const question = node.question || node.says || "";
  const when = item.row.at ? age(item.row.at) : "";
  const open = () => {
    remembered = item.address;
    location.hash = `#/${item.address}`;
  };
  return h(
    "li",
    { class: "waiting-row", "data-address": item.address, onclick: (event) => !event.target.closest("a") && open() },
    h("div", { class: "waiting-head" }, mention(node), h("small", { class: "kind-word" }, node.kind)),
    question ? authored(question, "p", { class: "waiting-question" }) : null,
    when ? h("p", { class: "waiting-age" }, `${words.lastAnswered} ${when}`) : null,
  );
}

// One list for both places. `state` is the live standing; `model` the inspection model (titles and questions).
export function waitingList(state, model, { compact = false, retry } = {}) {
  const root = h("div", { class: `waiting-list${compact ? " is-compact" : ""}`, "data-waiting-list": true });
  root.addEventListener("focusin", (event) => {
    remembered = event.target.closest(".waiting-row")?.dataset.address ?? remembered;
  });
  if (!state.data) {
    root.append(
      state.error
        ? h(
            "div",
            { role: "status", class: "waiting-note" },
            h("p", {}, words.countsUnavailable),
            h("button", { type: "button", class: "btn", onclick: retry }, words.tryAgain),
          )
        : h("p", { role: "status", class: "waiting-note is-loading" }, words.loadingWaiting),
    );
    return root;
  }
  const found = groups(state.data.decisions);
  if (!found.length) {
    root.append(h("p", { class: "waiting-note", "data-empty": true }, words.nothingWaits));
    return root;
  }
  for (const [layer, label] of LAYERS) {
    const here = found.filter((group) => group.layer === layer);
    if (!here.length) continue;
    root.append(
      h(
        "section",
        { class: "waiting-layer", "aria-label": label },
        h("h3", { class: "waiting-layer-name" }, label),
        here.map((group) =>
          h(
            "section",
            { class: "waiting-area", "aria-label": group.area },
            authored(group.area, "h4", { class: "waiting-area-name" }),
            h(
              "ul",
              { class: "waiting-rows" },
              group.items.map((item) => row(item, model, compact)),
            ),
          ),
        ),
      ),
    );
  }
  return root;
}

function restoreFocus(root) {
  if (!remembered) return;
  const target = [...root.querySelectorAll(".waiting-row")].find((li) => li.dataset.address === remembered)?.querySelector("a");
  remembered = null;
  target?.focus();
}

// Mounts the list into `host` and repaints when the facts or the inspection model change. Returns the unmount.
export function bindWaiting(host, { live, store }, options = {}) {
  let seen = [];
  const paint = () => {
    const model = store.getState().model;
    const next = [live.state.data, live.state.error, model];
    if (seen.every((value, index) => value === next[index]) && host.firstChild) return;
    seen = next;
    const list = waitingList(live.state, model, { ...options, retry: () => live.refresh() });
    host.replaceChildren(list);
    if (live.state.data && options.restore) restoreFocus(list);
  };
  const offLive = live.subscribe(paint);
  const offStore = store.subscribe(paint);
  return () => {
    offLive();
    offStore();
  };
}

export function mountWaiting(main, context) {
  const heading = h("h1", {}, words.waiting, h("span", { class: "count" }));
  const body = h("div", { class: "waiting-body" });
  main.replaceChildren(h("section", { class: "page waiting-page", "aria-labelledby": "waiting-title" }, heading, body));
  heading.id = "waiting-title";
  const count = heading.querySelector(".count");
  const off = bindWaiting(body, context, { restore: true });
  const offCount = context.live.subscribe(({ data }) => {
    count.textContent = data ? ` ${data.totals.waiting}` : "";
  });
  return () => {
    off();
    offCount();
  };
}

export const waitingRoute = {
  test: (path) => path === "waiting",
  layer: null,
  mount: mountWaiting,
  crumbs: () => [{ text: words.board, href: "#/" }, { text: words.waiting }],
};

const typing = (target) => target?.closest?.("input, textarea, select, [contenteditable]");
let pending = 0;
// `g w` opens the list; `j` and `k` move between rows of the list that has focus (else the page's own).
addEventListener("keydown", (event) => {
  if (event.defaultPrevented || event.ctrlKey || event.metaKey || event.altKey || typing(event.target)) return;
  if (event.key === "g") {
    pending = Date.now();
    return;
  }
  if (event.key === "w" && Date.now() - pending < 1200) {
    pending = 0;
    event.preventDefault();
    location.hash = "#/waiting";
    return;
  }
  pending = 0;
  if (event.key !== "j" && event.key !== "k") return;
  const lists = [...document.querySelectorAll("[data-waiting-list]")];
  const list = lists.find((candidate) => candidate.contains(document.activeElement)) || lists[0];
  const links = [...(list?.querySelectorAll(".waiting-row a") || [])];
  if (!links.length) return;
  event.preventDefault();
  const at = links.indexOf(document.activeElement);
  const step = event.key === "j" ? 1 : -1;
  links[at < 0 ? (step > 0 ? 0 : links.length - 1) : Math.min(links.length - 1, Math.max(0, at + step))].focus();
});
