// The standing facts as the page holds them. Computing them reads the whole KB, so they are loaded once and asked again only
// when the snapshot version moves (checked on a timer and when the tab returns), never on a bare timer.
export function createLive(load, version, { every = 10000 } = {}) {
  const listeners = new Set();
  const state = { data: null, error: null, updated: null, loading: false };
  let loaded = null;
  const emit = () => {
    for (const listener of listeners) listener(state);
  };
  async function refresh() {
    if (state.loading) return;
    state.loading = true;
    emit();
    try {
      const data = await load();
      if (data.version !== loaded) state.updated = new Date();
      loaded = data.version;
      Object.assign(state, { data, error: null });
    } catch (error) {
      state.error = error;
    }
    state.loading = false;
    emit();
  }
  async function check() {
    try {
      if ((await version()) !== loaded) await refresh();
    } catch {
      // The next tick asks again; the last facts stay on screen.
    }
  }
  return {
    state,
    refresh,
    subscribe: (listener) => (listeners.add(listener), listener(state), () => listeners.delete(listener)),
    start() {
      setInterval(check, every);
      document.addEventListener("visibilitychange", () => document.visibilityState === "visible" && check());
      return refresh();
    },
  };
}
