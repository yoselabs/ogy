// The push channel: server-sent events from `ogy serve`. The server sends the whole state at once and after every call, so a page that
// joins late or reconnects needs no replay. While the stream is down the page asks `/api/spotlight` every two seconds and says so.
export const POLL_EVERY = 2000;

export function connectEvents({ onSnapshot, onConnection, Source = globalThis.EventSource, fetcher = globalThis.fetch.bind(globalThis) }) {
  let source = null;
  let timer = null;
  let first = true;

  async function poll() {
    try {
      const response = await fetcher("/api/spotlight", { credentials: "same-origin", cache: "no-store" });
      if (response.ok) onSnapshot(await response.json(), false);
    } catch {
      // The next tick asks again; the connection state already says what is wrong.
    }
  }
  const stopPolling = () => {
    clearInterval(timer);
    timer = null;
  };

  function open() {
    source?.close();
    source = new Source("/api/events", { withCredentials: true });
    source.addEventListener("open", () => {
      stopPolling();
      first = true; // after a reconnect the server may have restarted: its first state is taken as it comes
      onConnection("live");
    });
    source.addEventListener("spotlight", (event) => {
      onSnapshot(JSON.parse(event.data), first);
      first = false;
    });
    source.addEventListener("error", () => {
      onConnection("reconnecting");
      if (!timer) timer = setInterval(poll, POLL_EVERY);
      if (source.readyState === Source.CLOSED) setTimeout(open, POLL_EVERY); // the browser gave up: start a new stream
    });
  }
  open();
  return () => {
    stopPolling();
    source?.close();
  };
}
