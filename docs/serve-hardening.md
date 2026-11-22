# Serve hardening

`ogy serve` reads the live worktree and refuses `--rev`. API reads acquire
`ProcessLock.acquire_exclusive` on the same `ogy.lock` path used by writers,
through `writes.reading`. HTTP MCP reads and review-round creation use that
same read boundary; tools that change entries already acquire the writer lock.
An overlapping write produces a refusal, including for a cached response, so a
refused trial write cannot escape through the board. The non-reentrant acquire
also excludes a writer in the same process. A non-Git directory has no writer.

One document is cached by the complete KB listing's blob ids and the ontology
files' content. This includes `removed.yml` and `built/`; the API version adds
this identity to the library inspection identity. ETags are per representation;
conditional requests still authenticate and take the lock before returning 304.

The header token rotates on each start. Set `OGY_SERVE_STABLE_TOKEN=1` to retain
it for configured MCP clients. It lives in this repository's own Git metadata,
or in a private path under `$XDG_STATE_HOME/ogy` keyed by the repository path.
The printed browser URL contains a different exchange code, usable once within
60 seconds. The resulting cookie holds a random process session and works only
on board routes. It cannot authenticate MCP. Cookie-authenticated unsafe methods
require same-origin provenance and `application/json`.

HTTP MCP schemas omit `repo`, `rev`, `ontology` and `file`. Both argument
validation and the runner refuse overrides. File input is unavailable over
HTTP; use inline records. Stdio schemas are unchanged; their file paths are now
confined to the repository, including symlink targets.
Tool calls are serialized across server instances, encompassing argparse-mcp's
process-wide stderr capture as well as ogy's capture.

Inspection schema 2 preserves authored mapping order. Dates, datetimes,
non-finite floats, binary, sets, non-string-keyed mappings and absence have
typed envelopes keyed by `\u0000ogy`. An authored mapping using that reserved
key is itself escaped as a mapping envelope, so it cannot impersonate metadata.
An authored `{absent: x}` stays authored data. Unsupported JSON shapes produce
reader findings. Invalid UTF-8 is decoded strictly and becomes a YAML finding.

## Shelf release requested

No shelf files were edited. `ogy.web.boundary.BoardBoundary`, composed only by
`BoardService` in `ogy.web.serve`, contains the workaround for the installed
`any-local-service` release. The coordinator should evolve its browser boundary:

- Separate per-instance browser sessions from header tokens and restrict their
  route scope; refuse cookies on MCP routes.
- Exchange only single-use expiring navigation codes, never the header token.
- Validate unsafe cookie requests for provenance and JSON content type.
- Reject duplicate token/Host/Origin headers before either gate consumes them;
  allow only the exact IPv4 loopback authority.
- Add nosniff, framing, CSP and referrer headers on every response and disable
  uvicorn's server header in both run and serving paths.

`argparse-mcp` also redirects stderr globally: evolve it to capture parser
failures without changing process stderr, then remove ogy's serialization seam.
The `BoardService` lifecycle overrides only exist to disable the server header
on both console and programmatic serving while preserving shutdown and logging;
remove those overrides when the shelf's run and serving paths disable it.
`asgi-token-gate.stable_token` needs the filesystem guarantees now supplied at
ogy's existing `resolve_token` seam: refuse symlinks and non-regular files,
validate owner and 0600 mode before reading, and publish through exclusive
temporary creation and atomic replacement. Ogy owns the restart-rotation policy
and repository/state location; the shelf owns secure credential-file handling.
The consumer continues to use the installed dependencies; no local path pins,
release, fetch, commit or push is needed for this workaround.
