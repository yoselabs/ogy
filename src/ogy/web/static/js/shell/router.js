// Hash routes are the whole view state: #/<path>?<query>. Every view is a URL and the browser's Back works.
export function parse(hash) {
  const [path, query = ""] = hash.replace(/^#\/?/, "").split("?");
  const clean = path.replace(/\/+$/, "");
  return { path: clean, segments: clean ? clean.split("/") : [], query: Object.fromEntries(new URLSearchParams(query)) };
}

export function format(path, query) {
  const text = new URLSearchParams(Object.entries(query).filter(([, value]) => value)).toString();
  return `#/${path}${text ? `?${text}` : ""}`;
}

export function createRouter(routes, fallback) {
  const listeners = new Set();
  let index = 0;
  const find = (path) => routes.find((route) => route.test(path));
  const router = {
    current: () => ({ ...parse(location.hash), index }),
    has: (path) => Boolean(find(path)),
    resolve: (path) => find(path) || fallback,
    canGoBack: () => index > 0,
    back: () => history.back(),
    subscribe: (listener) => (listeners.add(listener), () => listeners.delete(listener)),
    // Panel choices replace the entry instead of stacking one per click.
    setQuery(name, value) {
      const route = parse(location.hash);
      history.replaceState(history.state, "", format(route.path, { ...route.query, [name]: value }));
      emit();
    },
  };
  function emit() {
    for (const listener of listeners) listener(router.current());
  }
  function settle() {
    // A navigation the browser added has no state yet: number it so Back knows where the start is.
    if (history.state?.index == null) history.replaceState({ index: index + 1 }, "");
    index = history.state.index;
    emit();
  }
  addEventListener("hashchange", settle);
  addEventListener("popstate", () => {
    index = history.state?.index ?? index;
  });
  if (history.state?.index == null) history.replaceState({ index: 0 }, "");
  index = history.state.index;
  return router;
}
