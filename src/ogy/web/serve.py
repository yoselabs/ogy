"""One loopback process for the current board API and the existing MCP tools."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import uvicorn
from async_scope.asgi import bind_loopback
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount

from ogy.mcp_server import build
from ogy.verdict import RefusalError
from ogy.web import api
from ogy.web.token import BrowserTokenGate, resolve_token

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Receive, Scope, Send

    from ogy.target import Target


class LoopbackBoundary:
    """Validate browser authority before public health or authentication on every route."""

    def __init__(self, app: ASGIApp, port: int | None) -> None:
        self.app, self.port = app, port

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            request = Request(scope)
            port = self.port if self.port is not None else scope["server"][1]
            hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
            if port == 80:
                hosts |= {"127.0.0.1", "localhost"}
            host = request.headers.get("host", "")
            origin = request.headers.get("origin")
            if host not in hosts or (origin is not None and origin != f"http://{host}"):
                await JSONResponse({"error": "Host or Origin refused"}, status_code=403)(scope, receive, send)
                return
            if scope["path"] == "/healthz" and scope["method"] in {"GET", "HEAD"}:
                await JSONResponse({"status": "ok"})(scope, receive, send)
                return
        await self.app(scope, receive, send)


def application(target: Target, token: str, *, port: int | None) -> ASGIApp:
    """Compose health outside authentication and keep MCP's lifespan in the same process."""
    mcp = build(target.repo).http_app(path="/mcp/", host_origin_protection=True, json_response=True, stateless_http=True)
    app = Starlette(
        routes=[*api.routes(target), Mount("/", app=mcp)], lifespan=mcp.lifespan, exception_handlers={RefusalError: api.refusal}
    )
    return LoopbackBoundary(BrowserTokenGate(app, token), port)


def main(target: Target, *, port: int = 8765) -> None:
    """Bind only loopback; uvicorn owns signal handling and graceful lifespan shutdown."""
    if not 0 <= port <= 65535:
        message = "port must be between 0 and 65535"
        raise RefusalError(message)
    token = resolve_token(target.repo)
    with bind_loopback(port=port) as sock:
        bound = sock.getsockname()[1]
        app = application(target, token, port=bound)
        sys.stderr.write(f"ogy board: http://127.0.0.1:{bound}/?t={token}\n")
        server = uvicorn.Server(uvicorn.Config(app, log_level="warning", lifespan="on", access_log=False, timeout_graceful_shutdown=2))
        server.run(sockets=[sock])
