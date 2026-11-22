import { landing } from "../ui/landing.js";
import { connectEvents } from "./connection.js";
import { elementFor, paintSpotlight, watchMain } from "./highlight.js";
import { createMemory } from "./memory.js";

// Something the owner is in the middle of: a text field has the cursor. The agent then asks instead of moving the page.
const TYPING = "input:not([type=radio]):not([type=checkbox]):not([type=button]):not([type=submit]), textarea, select, [contenteditable]";
export const busy = () => Boolean(document.activeElement?.matches?.(TYPING));

// The one spotlight of the page: what the agent pointed at, where the owner is in it, and the way back. The server holds the
// spotlight (in memory, never in the KB); this holds only the owner's position (Back, Next) and the route to return to.
export function createSpotlight({ router, main, connect = connectEvents }) {
  const state = {
    connection: "connecting",
    sequence: 0,
    spotlight: null,
    log: [],
    index: 0,
    request: false,
    fresh: 0,
    present: new Set(),
    sketch: null,
    sketchRequest: false,
  };
  const listeners = new Set();
  const memory = createMemory(main);
  let scrollTo = false;
  let painted = null;

  const emit = () => {
    for (const listener of listeners) listener(state);
  };

  function repaint() {
    const { current, present } = paintSpotlight(main, state.spotlight, state.index);
    const changed = [...present].join() !== [...state.present].join();
    state.present = present;
    if (current && scrollTo) {
      scrollTo = false;
      current.scrollIntoView({ block: "center", behavior: "instant" });
    }
    // When the targets are on screen, not when the message arrived: this is the time the owner can see.
    if (main.dataset.spotlight === "on" && painted !== state.sequence) {
      painted = state.sequence;
      document.body.dataset.spotlightPaintedAt = String(Date.now());
    }
    if (changed) emit();
  }

  // Can a target be seen: it is on this page, or its own page exists.
  const reaches = (address) => state.present.has(address) || router.has(landing(address).slice(2));

  // The page that holds the target, with the Agent tab open beside it. A target the page already shows is not travelled to; one with
  // a page of its own is; one with neither stays where it is, and the Agent tab says so.
  function go(index) {
    const target = state.spotlight?.targets[index];
    if (!target) return;
    memory.remember();
    Object.assign(state, { index, request: false });
    scrollTo = true;
    const hash = landing(target.address);
    const shown = router.current().path === hash.slice(2) || elementFor(main, target.address);
    if (!shown && router.has(hash.slice(2))) location.hash = `${hash}?rail=agent`;
    else router.setQuery("rail", "agent");
    repaint();
    emit();
  }

  // The agent dismissed. A page the owner is typing on stays where it is: the way back is dropped, not taken.
  function released() {
    state.request = false;
    if (busy()) memory.forget();
    else memory.restore();
  }

  // A new sketch moves the page to it when the owner is idle and asks (in the Agent tab) when a text field has the cursor; it is
  // dropped from the page the way the spotlight is: back where the owner was, unless the owner has left the sketch or is typing.
  function followSketch(before) {
    const now = state.sketch;
    if (now && now.since !== before?.since) {
      state.sketchRequest = busy();
      if (!state.sketchRequest) memory.remember();
      if (state.sketchRequest) router.setQuery("rail", "agent");
      else location.hash = "#/sketch?rail=agent";
    } else if (!now && before) {
      state.sketchRequest = false;
      if (!busy() && router.current().path === "sketch") memory.restore();
      else memory.forget();
    }
  }

  function apply(snapshot, first) {
    if (!first && snapshot.sequence <= state.sequence) return;
    const before = state.spotlight;
    const sketched = state.sketch;
    Object.assign(state, {
      sequence: snapshot.sequence,
      log: snapshot.log,
      spotlight: snapshot.spotlight,
      sketch: snapshot.sketch ?? null,
    });
    followSketch(sketched);
    document.body.dataset.spotlightSequence = String(snapshot.sequence);
    document.body.dataset.spotlightAt = String(Date.now());
    if (snapshot.spotlight && snapshot.spotlight.since !== before?.since) {
      Object.assign(state, { index: 0, fresh: state.fresh + 1 });
      if (!busy()) return go(0);
      state.request = true;
      router.setQuery("rail", "agent"); // the side panel shows the request; the page the owner is typing on stays where it is
    } else if (!snapshot.spotlight && before) released();
    repaint();
    emit();
  }

  const stop = connect({ onSnapshot: apply, onConnection: (connection) => ((state.connection = connection), emit()) });
  const unwatch = watchMain(main, repaint);

  async function dismiss() {
    if (!state.spotlight) return;
    Object.assign(state, { spotlight: null, request: false });
    memory.restore();
    repaint();
    emit();
    const request = { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: "{}" };
    await fetch("/api/spotlight/dismiss", request).catch(() => {}); // the server keeps it until the next dismiss; this page let go
  }

  // The agent's sketch is held by the server like the spotlight; Dismiss lets go here at once and tells the server.
  async function dismissSketch() {
    if (!state.sketch) return;
    const before = state.sketch;
    state.sketch = null;
    followSketch(before);
    emit();
    const request = { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: "{}" };
    await fetch("/api/sketch/dismiss", request).catch(() => {});
  }

  const last = () => (state.spotlight?.targets.length ?? 1) - 1;
  return {
    state,
    reaches,
    dismiss,
    dismissSketch,
    openSketch() {
      memory.remember();
      state.sketchRequest = false;
      location.hash = "#/sketch?rail=agent";
      emit();
    },
    subscribe: (listener) => (listeners.add(listener), listener(state), () => listeners.delete(listener)),
    next: () => go(Math.min(state.index + 1, last())),
    back: () => go(Math.max(state.index - 1, 0)),
    show: () => go(state.index),
    close: () => (stop(), unwatch()),
  };
}
