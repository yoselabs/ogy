"""One loopback process for the current board API and the existing MCP tools."""

from __future__ import annotations

import asyncio
import contextlib
import secrets
import sys
from typing import TYPE_CHECKING, override

import uvicorn
from any_local_service import LocalService
from any_local_service.endpoint import published_endpoint
from any_local_service.logs import teardown_logs
from any_local_service.serve import validate_port
from async_scope.asgi import ServeError, bind_loopback
from starlette.applications import Starlette
from starlette.routing import Mount

from ogy.mcp_server import build
from ogy.verdict import RefusalError
from ogy.web import api
from ogy.web.boundary import BoardBoundary
from ogy.web.token import resolve_token

if TYPE_CHECKING:
    import socket
    from collections.abc import AsyncGenerator, Callable
    from pathlib import Path

    from starlette.types import Receive, Scope, Send

    from ogy.target import Target


class BoardService(LocalService):
    """Keep shelf's lifecycle while replacing its browser authentication at one seam."""

    def __init__(self, app: Starlette, token: str) -> None:
        super().__init__(app, token=token, header="X-Ogy-Token", cookie="ogy_session")
        self.exchange_code = secrets.token_urlsafe(32)
        self.boundary = BoardBoundary(self.app, token, exchange_code=self.exchange_code)

    @override
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.boundary(scope, receive, send)

    @override
    def run(self, *, port: int = 0, on_bound: Callable[[str], None] | None = None) -> None:
        """Disable uvicorn's identifying header until shelf exposes that safe default."""
        validate_port(port)
        with teardown_logs(), bind_loopback(port=port) as sock:
            if on_bound is not None:
                on_bound(f"http://127.0.0.1:{sock.getsockname()[1]}")
            config = uvicorn.Config(
                self, server_header=False, log_level="warning", lifespan="on", access_log=False, timeout_graceful_shutdown=2
            )
            uvicorn.Server(config).run(sockets=[sock])

    @override
    @contextlib.asynccontextmanager
    async def serving(self, *, port: int = 0, endpoint: Path | None = None) -> AsyncGenerator[str]:
        """Use the same header policy for programmatic serving and console serving."""
        validate_port(port)
        with teardown_logs(), bind_loopback(port=port) as sock:
            server = uvicorn.Server(
                uvicorn.Config(self, server_header=False, log_level="warning", lifespan="on", access_log=False, timeout_graceful_shutdown=1)
            )
            task = asyncio.create_task(_serve(server, sock))
            try:
                async with asyncio.timeout(10):
                    while not server.started:
                        if task.done():
                            await task
                            message = "server stopped during startup"
                            raise ServeError(message)
                        await asyncio.sleep(0.01)
                with published_endpoint(endpoint, f"http://127.0.0.1:{sock.getsockname()[1]}") if endpoint else contextlib.nullcontext():
                    yield f"http://127.0.0.1:{sock.getsockname()[1]}"
            finally:
                server.should_exit = True
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=3)
                except TimeoutError:
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)


async def _serve(server: uvicorn.Server, sock: socket.socket) -> None:
    try:
        await server.serve(sockets=[sock])
    except SystemExit as error:
        message = f"server failed to start ({error.code})"
        raise ServeError(message) from error


def application(target: Target, token: str) -> BoardService:
    """Compose health outside authentication and keep MCP's lifespan in the same process."""
    mcp = build(target.repo, ontology=target.ontology).http_app(
        path="/mcp/", host_origin_protection=True, json_response=True, stateless_http=True
    )
    app = Starlette(
        routes=[*api.routes(target), Mount("/", app=mcp)], lifespan=mcp.lifespan, exception_handlers={RefusalError: api.refusal}
    )
    return BoardService(app, token)


def main(target: Target, *, port: int = 8765) -> None:
    """Run the board with shelf's loopback boundary and graceful lifespan shutdown."""
    token = resolve_token(target.repo)
    service = application(target, token)

    def on_bound(url: str) -> None:
        sys.stderr.write(f"ogy board: {url}/?t={service.exchange_code}\n")

    try:
        service.run(port=port, on_bound=on_bound)
    except ValueError as error:
        raise RefusalError(str(error)) from error
    except ServeError as error:
        message = f"{error}; use --port 0 to choose an available port"
        raise RefusalError(message) from error
