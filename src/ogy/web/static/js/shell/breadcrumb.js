import { authored } from "../ui/authored.js";
import { identity, text } from "../model/descriptor.js";
import { h } from "../ui/dom.js";
import { words } from "../ui/words.js";
import { words as owedWords } from "../views/owed/words.js";

// Fixed crumbs are the viewer's words; any other crumb is an area's or an entry's name, so it is marked as authored.
const fixed = new Set(
  [...Object.values(words), owedWords.owed].filter((value) => typeof value === "string").map((value) => value.toLowerCase()),
);
const said = (item) => (!item.entry && fixed.has(String(item.text).toLowerCase()) ? item.text : authored(item.text));

// An entry's name in the trail: its title, else the question or label it asks or answers by, else its sentence; its key only when it has none.
function nameOf(node) {
  const said = text(node.title) || text(node.question) || text(node.label) || text(node.word) || text(node.says);
  if (!said) return identity(node).title;
  return said.length > 70 ? `${said.slice(0, 69)}…` : said;
}

// Where this page sits: the route's own trail, the last item being the page itself.
export function mountBreadcrumb(root, { router, store }) {
  root.setAttribute("aria-label", words.breadcrumb);
  const paint = (route) => {
    const entry = store.getState().model?.byId.get(route.segments.slice(0, 4).join("/"));
    const trail = router
      .resolve(route.path)
      .crumbs(route)
      .map((item) =>
        entry && route.segments.length === 4 && item.text === route.segments[3] ? { ...item, text: nameOf(entry), entry: true } : item,
      );
    root.replaceChildren(
      h(
        "ol",
        {},
        trail.map((item, index) =>
          index === trail.length - 1
            ? h("li", { "aria-current": "page" }, said(item))
            : h("li", {}, h("a", { href: item.href }, said(item))),
        ),
      ),
    );
  };
  router.subscribe(paint);
  store.subscribe(() => paint(router.current()));
  paint(router.current());
}
