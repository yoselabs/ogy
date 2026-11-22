import { inspectionClient, standingClient, versionClient } from "./api.js";
import { createStore } from "./state.js";
import { mountBreadcrumb } from "./shell/breadcrumb.js";
import { mountHeader } from "./shell/header.js";
import { createLive } from "./shell/live.js";
import { mountRail } from "./shell/rail.js";
import { createRouter } from "./shell/router.js";
import { followSystemTheme } from "./shell/theme.js";
import { mountStatusStrip } from "./shell/status-strip.js";
import { words } from "./ui/words.js";
import { mountCanvas } from "./views/canvas.js";
import { areaRoute } from "./views/area.js";
import { decisionRoute } from "./views/decision.js";
import { mountNotFound } from "./views/not-found.js";

export const store = createStore();
const inspection = { error: null };
const live = createLive(standingClient(), versionClient());
const board = [{ text: words.board, href: "#/" }];
// Every page of the board is one entry here; a route no entry claims is the not-found page.
const routes = [
  { test: (path) => path === "" || path === "board", layer: "product", mount: mountCanvas, crumbs: () => [{ text: words.board }] },
  decisionRoute,
  areaRoute,
];
const fallback = { layer: null, mount: mountNotFound, crumbs: () => [...board, { text: words.notFound }] };
const router = createRouter(routes, fallback);

followSystemTheme();
const part = (id) => document.getElementById(id);
const context = { router, live, store, inspection };
mountHeader(part("header"), context);
mountStatusStrip(part("strip"), context);
mountBreadcrumb(part("crumb"), context);
mountRail(part("rail"), context);

let path = null;
let unmount = null;
function show(route) {
  if (route.path === path) return;
  path = route.path;
  unmount?.();
  unmount = router.resolve(route.path).mount(part("main"), { ...context, route }) || null;
}
router.subscribe(show);
show(router.current());

// The inspection document goes first: the standing facts hold the repository lock for as long as the KB takes to count.
try {
  store.dispatch({ type: "applyDocument", document: await inspectionClient()() });
} catch (error) {
  inspection.error = error;
  path = null;
  show(router.current());
}
live.start();
