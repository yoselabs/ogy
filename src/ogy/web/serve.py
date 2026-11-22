"""One loopback process for the current board API and the existing MCP tools."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from any_local_service import LocalService
from starlette.applications import Starlette
from starlette.routing import Mount

from ogy.mcp_server import build
from ogy.verdict import RefusalError
from ogy.web import api
from ogy.web.token import resolve_token

if TYPE_CHECKING:
    from ogy.target import Target


def application(target: Target, token: str) -> LocalService:
    """Compose health outside authentication and keep MCP's lifespan in the same process."""
    mcp = build(target.repo).http_app(path="/mcp/", host_origin_protection=True, json_response=True, stateless_http=True)
    app = Starlette(
        routes=[*api.routes(target), Mount("/", app=mcp)], lifespan=mcp.lifespan, exception_handlers={RefusalError: api.refusal}
    )
    return LocalService(app, token=token, header="X-Ogy-Token", cookie="ogy_session")


def main(target: Target, *, port: int = 8765) -> None:
    """Run the board with shelf's loopback boundary and graceful lifespan shutdown."""
    token = resolve_token(target.repo)
    service = application(target, token)

    def on_bound(url: str) -> None:
        sys.stderr.write(f"ogy board: {url}/?t={token}\n")

    try:
        service.run(port=port, on_bound=on_bound)
    except ValueError as error:
        raise RefusalError(str(error)) from error
