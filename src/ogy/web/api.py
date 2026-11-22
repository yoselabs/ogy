"""Read-only board routes; each request loads the current worktree."""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
lazy from starlette.requests import Request

from ogy.inspect import inspect
from ogy.verdict import RefusalError

if TYPE_CHECKING:
    from ogy.target import Target


def routes(target: Target) -> list[Route]:
    current = target.at(".")

    def inspection(_: Request) -> JSONResponse:
        return JSONResponse(inspect(current.read()[1]), headers={"Cache-Control": "no-store"})

    def version(_: Request) -> JSONResponse:
        return JSONResponse(inspect(current.read()[1])["snapshot"], headers={"Cache-Control": "no-store"})

    def entry(request: Request) -> JSONResponse:
        document = inspect(current.read()[1])
        found = next((item for item in document["entries"] if item["address"] == request.path_params["address"]), None)
        return JSONResponse(
            found if found is not None else {"error": "entry not found"},
            status_code=200 if found else 404,
            headers={"Cache-Control": "no-store"},
        )

    def index(_: Request) -> HTMLResponse:
        return HTMLResponse(
            "<!doctype html><html><title>ogy board</title><p>The board is not built yet.</p></html>",
            headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
        )

    return [
        Route("/api/inspection", inspection),
        Route("/api/version", version),
        Route("/api/entry/{address:path}", entry),
        Route("/", index),
    ]


async def refusal(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, RefusalError):
        raise error
    return JSONResponse({"error": error.lines()}, status_code=400, headers={"Cache-Control": "no-store"})
