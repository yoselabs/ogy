"""Read-only board routes sharing an input-keyed inspection cache under the repository lock."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from content_digest import digest
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
lazy from starlette.requests import Request

from ogy.verdict import RefusalError
from ogy.web.cache import InspectionCache

if TYPE_CHECKING:
    from ogy.target import Target


def routes(target: Target) -> list[Route | Mount]:
    cache = InspectionCache(target)
    static = Path(__file__).with_name("static")

    def response(request: Request, data: object, version: str, *, status: int = 200, encoded: bytes | None = None) -> Response:
        etag = '"' + digest({"version": version, "path": request.url.path}, length=64) + '"'
        headers = {"Cache-Control": "private, no-cache", "ETag": etag, "Vary": "Cookie, X-Ogy-Token"}
        matches = [item.strip().removeprefix("W/") for item in request.headers.get("if-none-match", "").split(",")]
        if status == 200 and (etag in matches or "*" in matches):
            return Response(status_code=304, headers=headers)
        if encoded is not None:
            return Response(encoded, status_code=status, headers=headers, media_type="application/json")
        return JSONResponse(data, status_code=status, headers=headers)

    def inspection(request: Request) -> Response:
        document, encoded = cache.response()
        return response(request, document, document["snapshot"]["version"], encoded=encoded)

    def version(request: Request) -> Response:
        document = cache.current()
        return response(request, document["snapshot"], document["snapshot"]["version"])

    def standing(request: Request) -> Response:
        data = cache.standing()
        return response(request, data, data["version"])

    def entry(request: Request) -> Response:
        document = cache.current()
        found = next((item for item in document["entries"] if item["address"] == request.path_params["address"]), None)
        return response(
            request,
            found if found is not None else {"error": "entry not found"},
            document["snapshot"]["version"],
            status=200 if found else 404,
        )

    def index(_: Request) -> FileResponse:
        return FileResponse(
            static / "index.html",
            headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
        )

    def asset(request: Request) -> FileResponse:
        return FileResponse(static / request.url.path.removeprefix("/"), headers={"Cache-Control": "no-cache"})

    return [
        Route("/api/inspection", inspection),
        Route("/api/standing", standing),
        Route("/api/version", version),
        Route("/api/entry/{address:path}", entry),
        Route("/", index),
        Route("/board.css", asset),
        Route("/view-contract.json", asset),
        Mount("/js", app=StaticFiles(directory=static / "js")),
    ]


async def refusal(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, RefusalError):
        raise error
    return JSONResponse({"error": error.lines()}, status_code=400, headers={"Cache-Control": "no-store"})
