// One conditional-GET client per API route: the ETag keeps an unchanged document from being parsed again.
function client(path, label, check, fetcher) {
  let document = null;
  let etag = null;
  return async function load() {
    const headers = etag ? { "If-None-Match": etag } : {};
    const response = await fetcher(path, { credentials: "same-origin", cache: "no-cache", headers });
    if (response.status === 304 && document) return document;
    if (!response.ok) throw Object.assign(new Error(`${label}: HTTP ${response.status}`), { status: response.status });
    const next = await response.json();
    check(next);
    document = next;
    etag = response.headers.get("ETag");
    return document;
  };
}

export function inspectionClient(fetcher = globalThis.fetch.bind(globalThis)) {
  return client(
    "/api/inspection",
    "Inspection",
    (next) => {
      if (next.schema !== 2) throw new Error(`Unsupported inspection version: ${next.schema}`);
    },
    fetcher,
  );
}

export function standingClient(fetcher = globalThis.fetch.bind(globalThis)) {
  return client(
    "/api/standing",
    "Standing",
    (next) => {
      if (!next.totals) throw new Error("Standing: no totals");
    },
    fetcher,
  );
}

// The cheap question: which snapshot is the KB at now? Standing is asked again only when the answer changes.
export function versionClient(fetcher = globalThis.fetch.bind(globalThis)) {
  return async function current() {
    const response = await fetcher("/api/version", { credentials: "same-origin", cache: "no-cache" });
    if (!response.ok) throw new Error(`Version: HTTP ${response.status}`);
    return (await response.json()).version;
  };
}
