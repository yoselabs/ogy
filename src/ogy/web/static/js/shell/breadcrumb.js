import { h } from "../ui/dom.js";
import { words } from "../ui/words.js";

// Where this page sits: the route's own trail, the last item being the page itself.
export function mountBreadcrumb(root, { router }) {
  root.setAttribute("aria-label", words.breadcrumb);
  const paint = (route) => {
    const trail = router.resolve(route.path).crumbs(route);
    root.replaceChildren(
      h(
        "ol",
        {},
        trail.map((item, index) =>
          index === trail.length - 1 ? h("li", { "aria-current": "page" }, item.text) : h("li", {}, h("a", { href: item.href }, item.text)),
        ),
      ),
    );
  };
  router.subscribe(paint);
  paint(router.current());
}
