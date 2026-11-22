// A spotlight is a state of the page, not a layer over it: the targets are the components the page already draws. This marks them
// with a number (`data-spot`) and dims everything beside them (`data-dim`); no element is added and none gets a class of its own.
const MARKS = "[data-spot], [data-dim], [data-spot-current]";

const escape = (address) => CSS.escape(address);

// The element that stands for an address on this page: a page, a row or option that carries it, else the entry's own mention.
export function elementFor(main, address) {
  const named = main.querySelector(`[data-address="${escape(address)}"], [data-option="${escape(address)}"]`);
  if (named?.matches(".page")) return named.querySelector(".page-head, .card-header") || named;
  return named || main.querySelector(`[data-entry-id="${escape(address)}"]`);
}

function clear(main) {
  for (const element of main.querySelectorAll(MARKS)) {
    element.removeAttribute("data-spot");
    element.removeAttribute("data-dim");
    element.removeAttribute("data-spot-current");
  }
  delete main.dataset.spotlight;
}

// What a page-addressed target also owns: a decision's own question reads with it, whatever else is dimmed around it.
function ownedBy(main, address) {
  const page = main.querySelector(`.page[data-address="${escape(address)}"]`);
  return page?.querySelector("[data-part=question]")?.closest(".block") ?? null;
}

// Numbers the targets that are on the page and dims what is neither a target nor holds one. Returns the current target's element
// and the addresses that are on the page.
export function paintSpotlight(main, spotlight, index) {
  clear(main);
  const present = new Set();
  if (!spotlight) return { current: null, present };
  const marked = new Map();
  const owned = new Set();
  spotlight.targets.forEach((target, position) => {
    const element = elementFor(main, target.address);
    if (!element || marked.has(element)) return;
    marked.set(element, position);
    present.add(target.address);
    const own = ownedBy(main, target.address);
    if (own) owned.add(own);
  });
  const kept = [...marked.keys(), ...owned];
  const keep = new Set(kept);
  for (const element of kept) for (let up = element.parentElement; up && up !== main.parentElement; up = up.parentElement) keep.add(up);
  const inside = (element) => kept.some((target) => target.contains(element));
  for (const element of keep) {
    if (inside(element)) continue; // what a target holds is the target
    for (const child of element.children) {
      if (!keep.has(child) && !child.matches("script, style, template, dialog")) child.setAttribute("data-dim", "");
    }
  }
  let current = null;
  for (const [element, position] of marked) {
    element.setAttribute("data-spot", String(position + 1));
    if (position === index) {
      element.setAttribute("data-spot-current", "");
      current = element;
    }
  }
  if (marked.size) main.dataset.spotlight = "on";
  return { current, present };
}

// The page redraws its views from time to time (a snapshot moved, a form was answered): the marks follow every redraw.
export function watchMain(main, repaint) {
  let queued = false;
  const observer = new MutationObserver(() => {
    if (queued) return;
    queued = true;
    queueMicrotask(() => {
      queued = false;
      repaint();
    });
  });
  observer.observe(main, { childList: true, subtree: true });
  return () => observer.disconnect();
}
