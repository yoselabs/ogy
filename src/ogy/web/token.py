"""One seam over shelf authentication, including browser navigation's cookie exchange."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from asgi_token_gate import StaticTokenGate, stable_token
from git_porcelain import git_dir
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

if TYPE_CHECKING:
    from pathlib import Path

    from starlette.types import ASGIApp, Receive, Scope, Send


def resolve_token(repo: Path) -> str:
    folder = git_dir(repo)
    path = (folder / "ogy" if folder is not None else repo / ".ogy") / "server.token"
    token = stable_token(path)
    path.chmod(0o600)
    return token


class BrowserTokenGate:
    """Exchange a root navigation token for an HttpOnly cookie; reuse shelf's header gate."""

    def __init__(self, app: ASGIApp, token: str) -> None:
        self.app = StaticTokenGate(app, token, header="X-Ogy-Token")
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
            return
        if scope["type"] == "http":
            request = Request(scope)
            if scope["path"] == "/" and "t" in request.query_params:
                given = request.query_params["t"]
                response = (
                    RedirectResponse("/", status_code=303)
                    if secrets.compare_digest(given.encode(), self.token.encode())
                    else JSONResponse({"error": "invalid token"}, status_code=401)
                )
                if response.status_code == 303:
                    response.set_cookie("ogy_session", self.token, httponly=True, samesite="strict", path="/")
                response.headers.update({"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
                await response(scope, receive, send)
                return
            cookie = request.cookies.get("ogy_session")
            credential = request.headers.get("x-ogy-token", cookie or "")
            if not credential.isascii():
                await JSONResponse({"error": "invalid token"}, status_code=401)(scope, receive, send)
                return
            if cookie and "x-ogy-token" not in request.headers:
                scope = {**scope, "headers": [*scope["headers"], (b"x-ogy-token", cookie.encode())]}
        await self.app(scope, receive, send)
