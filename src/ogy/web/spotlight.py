"""The board's one spotlight and one sketch: attention and a drawing held in memory, never written to the KB, and pushed to every open
page as server-sent events.

An agent points the owner at entries with a title and ordered targets, one sentence each. The spotlight lives until it is dismissed or
replaced and is gone when the server stops. A sketch (entries in the `put` format, drawn but never written) lives the same way. Neither
changes an entry, so the inspection version stays what it was.
"""

from __future__ import annotations

import asyncio
import json
import re
import threading
from collections import deque
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from ogy.verdict import RefusalError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Mapping, Sequence

    from starlette.requests import Request

LOG_LIMIT = 30  # one board, a bounded session log
TARGET_LIMIT = 12
TITLE_LIMIT = 120
SENTENCE_LIMIT = 240
KEEPALIVE_SECONDS = 15
Json = dict[str, Any]  # one JSON document: what a page is sent, and what a tool call answers
ADDRESS = re.compile(r"[^/\s]+(?:/[^/\s]+)+")


class Spotlight:
    """Current spotlight, its bounded log and the open pages listening. Safe to call from tool threads and the event loop."""

    def __init__(
        self,
        missing: Callable[[Sequence[str]], list[str]] | None = None,
        sketcher: Callable[[Sequence[Mapping[Any, Any]], str | None, str | None], Json] | None = None,
    ) -> None:
        self._missing = missing  # the addresses among those given that no entry (or part of one) has
        self._sketcher = sketcher  # records, decision, option -> what the page draws; refuses what `put` would refuse
        self._sketch: Json | None = None
        self._lock = threading.Lock()
        self._sequence = 0
        self._current: Json | None = None
        self._log: deque[Json] = deque(maxlen=LOG_LIMIT)
        self._listeners: dict[asyncio.Queue[Json], asyncio.AbstractEventLoop] = {}

    def show(self, *, title: str, targets: Sequence[tuple[str, str]], session: str) -> Json:
        """Replace the spotlight. Every refusal is recorded in the log before it is raised."""
        problems = self._problems(title, targets)
        if problems:
            self._record("refused", session, title, len(targets), "; ".join(problems))
            raise RefusalError(problems)
        rows = [{"address": address, "says": says} for address, says in targets]
        with self._lock:
            self._current = {"title": title, "targets": rows, "session": session, "since": _now()}
        return self._record("show", session, title, len(rows), "shown")

    def dismiss(self, *, session: str) -> Json:
        with self._lock:
            had = self._current is not None
            self._current = None
        return self._record("dismiss", session, "", 0, "dismissed" if had else "nothing to dismiss")

    def show_sketch(
        self,
        *,
        title: str,
        records: Sequence[Mapping[Any, Any]],
        decision: str | None,
        option: str | None,
        session: str,
    ) -> Json:
        """Replace the sketch. Every refusal is recorded in the log before it is raised."""
        try:
            drawn = self._drawn(title, records, decision, option)
        except RefusalError as error:
            self._record("refused", session, title, len(records), "; ".join(error.lines()))
            raise
        with self._lock:
            self._sketch = {"title": title, "session": session, "since": _now(), **drawn}
        return self._record("sketch", session, title, len(drawn.get("entries", [])), "sketched")

    def _drawn(self, title: str, records: Sequence[Mapping[Any, Any]], decision: str | None, option: str | None) -> Json:
        if not title.strip() or len(title) > TITLE_LIMIT:
            raise RefusalError([f"the title is one line of 1 to {TITLE_LIMIT} characters"])
        return self._sketcher(records, decision, option) if self._sketcher else {}

    def dismiss_sketch(self, *, session: str) -> Json:
        with self._lock:
            had = self._sketch is not None
            self._sketch = None
        return self._record("unsketch", session, "", 0, "dismissed" if had else "nothing to dismiss")

    def snapshot(self) -> Json:
        with self._lock:
            return self._snapshot()

    def listen(self) -> asyncio.Queue[Json]:
        queue: asyncio.Queue[Json] = asyncio.Queue()
        with self._lock:
            self._listeners[queue] = asyncio.get_running_loop()
        return queue

    def drop(self, queue: asyncio.Queue[Json]) -> None:
        with self._lock:
            self._listeners.pop(queue, None)

    def _problems(self, title: str, targets: Sequence[tuple[str, str]]) -> list[str]:
        problems = []
        if not title.strip() or len(title) > TITLE_LIMIT:
            problems.append(f"the title is one line of 1 to {TITLE_LIMIT} characters")
        if not targets or len(targets) > TARGET_LIMIT:
            problems.append(f"give 1 to {TARGET_LIMIT} targets")
        problems.extend(f"not an address: {address}" for address, _ in targets if not ADDRESS.fullmatch(address))
        problems.extend(
            f"the sentence of {address} is 1 to {SENTENCE_LIMIT} characters"
            for address, says in targets
            if not says.strip() or len(says) > SENTENCE_LIMIT
        )
        if len({address for address, _ in targets}) != len(targets):
            problems.append("an address is named twice")
        if not problems and self._missing is not None:
            problems.extend(f"no such entry: {address}" for address in self._missing([address for address, _ in targets]))
        return problems

    def _record(self, action: str, session: str, title: str, count: int, result: str) -> Json:
        with self._lock:
            self._sequence += 1
            entry = {"sequence": self._sequence, "at": _now(), "session": session, "action": action}
            self._log.appendleft({**entry, "title": title, "targets": count, "result": result})
            snapshot = self._snapshot()
            for queue, loop in list(self._listeners.items()):
                loop.call_soon_threadsafe(queue.put_nowait, snapshot)
        return {"sequence": snapshot["sequence"], "result": result}

    def _snapshot(self) -> Json:
        return {"sequence": self._sequence, "spotlight": self._current, "sketch": self._sketch, "log": list(self._log)}


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def _frame(snapshot: Json) -> bytes:
    data = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
    return f"id: {snapshot['sequence']}\nevent: spotlight\ndata: {data}\n\n".encode()


def routes(hub: Spotlight) -> list[Route]:
    """`/api/events` pushes the whole state at once and after every call; `/api/spotlight` is the polling fallback; the two
    dismiss routes are the board's own Dismiss."""

    async def events(_: Request) -> StreamingResponse:
        queue = hub.listen()

        async def body() -> AsyncGenerator[bytes]:
            try:
                yield b"retry: 1000\n\n"
                yield _frame(hub.snapshot())  # listening first: a call between the two is delivered, never lost
                while True:
                    try:
                        yield _frame(await asyncio.wait_for(queue.get(), KEEPALIVE_SECONDS))
                    except TimeoutError:
                        yield b": keepalive\n\n"
            finally:
                hub.drop(queue)

        return StreamingResponse(body(), media_type="text/event-stream", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})

    async def state(_: Request) -> JSONResponse:
        return JSONResponse(hub.snapshot(), headers={"Cache-Control": "no-store"})

    async def dismiss(_: Request) -> JSONResponse:
        return JSONResponse(hub.dismiss(session="board"), headers={"Cache-Control": "no-store"})

    async def dismiss_sketch(_: Request) -> JSONResponse:
        return JSONResponse(hub.dismiss_sketch(session="board"), headers={"Cache-Control": "no-store"})

    return [
        Route("/api/events", events),
        Route("/api/spotlight", state),
        Route("/api/spotlight/dismiss", dismiss, methods=["POST"]),
        Route("/api/sketch/dismiss", dismiss_sketch, methods=["POST"]),
    ]
