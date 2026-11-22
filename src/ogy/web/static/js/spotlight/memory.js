// Where the owner was before a spotlight moved the page: the exact route and the scroll position, so Dismiss can give both back.
export function createMemory(main) {
  let prior = null;
  return {
    // The first move only: later hops of the same spotlight keep the original place.
    remember() {
      prior ||= { hash: location.hash, top: main.scrollTop };
    },
    forget() {
      prior = null;
    },
    restore() {
      const back = prior;
      prior = null;
      if (!back) return;
      if (location.hash !== back.hash) location.hash = back.hash;
      const started = performance.now();
      // The page mounts after the hash changes: ask again until it is tall enough to scroll there.
      const settle = () => {
        main.scrollTop = back.top;
        if (Math.abs(main.scrollTop - back.top) > 1 && performance.now() - started < 2000) requestAnimationFrame(settle);
      };
      requestAnimationFrame(settle);
    },
  };
}
