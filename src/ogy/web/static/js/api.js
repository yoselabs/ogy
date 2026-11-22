export function inspectionClient(fetcher = globalThis.fetch.bind(globalThis)) {
  let document = null;
  let etag = null;
  return async function load() {
    const headers = etag ? { "If-None-Match": etag } : {};
    const response = await fetcher("/api/inspection", { credentials: "same-origin", cache: "no-cache", headers });
    if (response.status === 304 && document) return document;
    if (!response.ok) throw new Error(`Inspection: HTTP ${response.status}`);
    const next = await response.json();
    if (next.schema !== 2) throw new Error(`Unsupported inspection version: ${next.schema}`);
    document = next;
    etag = response.headers.get("ETag");
    return document;
  };
}
