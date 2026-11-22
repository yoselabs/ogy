import { glyph, h } from "../ui/dom.js";
import { words } from "../ui/words.js";

const apple = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
const LAYERS = [
  ["product", words.product, ""],
  ["software", words.software, "software"],
];

function time(date) {
  return date ? date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "";
}

// The header line: Back, which knowledge base and revision, when it last changed, layer tabs, search.
// Its elements are built once; a route or data change only edits their text, so nothing here moves.
export function mountHeader(root, { router, live }) {
  const back = h(
    "button",
    { type: "button", class: "btn icon-only", "aria-label": words.back, title: words.back, onclick: router.back },
    glyph("back"),
  );
  const name = h("strong", { class: "hdr-name" });
  const meta = h("span", { class: "hdr-meta" });
  const tabs = LAYERS.map(([layer, label, path]) =>
    router.has(path)
      ? h("a", { class: "tab", href: `#/${path}`, "data-layer": layer }, label)
      : h("span", { class: "tab", "aria-disabled": "true", "data-layer": layer }, label),
  );
  const search = h(
    "button",
    { type: "button", class: "btn search", "aria-label": words.search },
    glyph("search"),
    h("span", {}, words.search),
    h("kbd", {}, apple ? "⌘K" : "Ctrl K"),
  );
  root.append(back, h("div", { class: "hdr-id" }, name, meta), h("nav", { class: "layers", "aria-label": words.layers }, tabs), search);
  const paint = (route = router.current()) => {
    back.disabled = !router.canGoBack();
    const layer = router.resolve(route.path).layer;
    for (const tab of tabs) {
      if (tab.dataset.layer === layer) tab.setAttribute("aria-current", "page");
      else tab.removeAttribute("aria-current");
    }
  };
  router.subscribe(paint);
  live.subscribe(({ data, error, updated }) => {
    name.textContent = data?.repository ?? "";
    meta.textContent =
      !data && !error
        ? words.loading
        : data
          ? `${data.revision === "worktree" ? words.worktree : data.revision} · ${words.loaded} ${time(updated)}`
          : "";
  });
  paint();
}
