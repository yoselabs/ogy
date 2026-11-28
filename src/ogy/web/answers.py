"""Board writes: the owner's click is an answer, recorded by the same operations as `ogy answer` and `ogy reply`."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from starlette.responses import JSONResponse
from starlette.routing import Route

from ogy import ops
from ogy.verdict import RefusalError

if TYPE_CHECKING:
    from collections.abc import Callable

    from starlette.requests import Request
    from starlette.responses import Response

    from ogy.target import Target
    from ogy.web.cache import InspectionCache

# A board answer says where it was given with the scheme `ui` (decision software/ontology/decision/answer-where-ui, yes-ui-token).
WHERE_PREFIX = "ui:board/"
NO_STORE = {"Cache-Control": "no-store"}


class ConflictError(RefusalError):
    """The inspection version the writer saw is no longer the repository's."""


def _fail(error: RefusalError, status: int) -> JSONResponse:
    return JSONResponse({"error": error.lines()}, status_code=status, headers=NO_STORE)


def _optional(body: dict[str, object], name: str) -> str | None:
    value = body.get(name)
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, str):
        raise RefusalError([f"{name} must be text"])
    return value


def _required(body: dict[str, object], name: str) -> str:
    value = _optional(body, name)
    if value is None:
        raise RefusalError([f"{name} is required"])
    return value


async def _body(request: Request) -> dict[str, object]:
    try:
        body = await request.json()
    except ValueError as error:
        raise RefusalError(["the body must be JSON"]) from error
    if not isinstance(body, dict):
        raise RefusalError(["the body must be a JSON object"])
    return body


def _words(body: dict[str, object]) -> tuple[str, str, str | None]:
    """The version the page read, what the owner said (a paraphrase, required) and an optional note."""
    return _required(body, "version"), _required(body, "said"), _optional(body, "note")


def routes(target: Target, cache: InspectionCache) -> list[Route]:
    where = WHERE_PREFIX + secrets.token_hex(4)

    def ensure(expected: str) -> Callable[[], None]:
        def check() -> None:
            if cache.version_in_write() != expected:
                message = "the knowledge base changed since this page was read; reload and look again before answering"
                raise ConflictError([message])

        return check

    async def answer(request: Request) -> Response:
        try:
            body = await _body(request)
            version, said, note = _words(body)
            decision, option = _required(body, "decision"), _required(body, "option")
            done = ops.run_answer(target, decision, option, said, where, note=note, ensure=ensure(version)).value
        except ConflictError as error:
            return _fail(error, 409)
        except RefusalError as error:
            return _fail(error, 400)
        return JSONResponse(
            {
                "version": cache.current()["snapshot"]["version"],
                "recorded": {"decision": str(done.decision), "option": done.option, "said": " ".join(said.split()), "note": note},
                "changed": done.changed,
                "removed": done.removed,
            },
            headers=NO_STORE,
        )

    async def reply(request: Request) -> Response:
        try:
            body = await _body(request)
            version, said, note = _words(body)
            text, round_id = _required(body, "text"), _required(body, "round")
            done = ops.run_reply(target, text, said, where, round_id=round_id, note=note, ensure=ensure(version)).value
        except ConflictError as error:
            return _fail(error, 409)
        except RefusalError as error:
            return _fail(error, 400)
        return JSONResponse(
            {
                "version": cache.current()["snapshot"]["version"],
                "recorded": {"said": " ".join(said.split()), "note": note},
                "applied": done.applied,
                "refused": done.refused,
            },
            status_code=200 if done.changed or not done.refused else 400,
            headers=NO_STORE,
        )

    return [Route("/api/answer", answer, methods=["POST"]), Route("/api/reply", reply, methods=["POST"])]
