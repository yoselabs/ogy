"""Compatibility seam for any-local-service's browser boundary (see docs/serve-hardening.md)."""

from __future__ import annotations

import secrets
import time
from typing import TYPE_CHECKING

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Message, Receive, Scope, Send


class BoardBoundary:
    """Separate browser sessions from MCP authority before shelf's header gate."""

    def __init__(self, app: ASGIApp, token: str, *, exchange_code: str) -> None:
        self.app = app
        self.token = token.encode("ascii")
        self.exchange_code = exchange_code.encode("ascii")
        self.expires = time.monotonic() + 60
        self.used = False
        self.session = secrets.token_urlsafe(32)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def secured(message: Message) -> None:
            if message["type"] == "http.response.start":
                replaced = {b"server", b"x-content-type-options", b"x-frame-options", b"content-security-policy", b"referrer-policy"}
                headers = [(key, value) for key, value in message.get("headers", []) if key.lower() not in replaced]
                headers.extend(
                    [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"content-security-policy", b"default-src 'self'; frame-ancestors 'none'"),
                        (b"referrer-policy", b"no-referrer"),
                    ]
                )
                message = {**message, "headers": headers}
            await send(message)

        if scope["type"] != "http":
            await self.app(scope, receive, secured)
            return
        request = Request(scope)
        error = self._authority(request)
        if error is not None:
            await error(scope, receive, secured)
            return
        credentials = request.headers.getlist("x-ogy-token")
        if len(credentials) > 1 or (credentials and not credentials[0].isascii()):
            await JSONResponse({"error": "invalid token header"}, status_code=401)(scope, receive, secured)
            return
        if scope["path"] == "/" and "t" in request.query_params:
            await self._exchange(request)(scope, receive, secured)
            return
        header = bool(credentials) and secrets.compare_digest(credentials[0].encode(), self.token)
        board = scope["path"] in {"/", "/board.css", "/view-contract.json"} or scope["path"].startswith(("/api/", "/static/", "/js/"))
        cookie = request.cookies.get("ogy_session", "")
        session = board and cookie.isascii() and secrets.compare_digest(cookie, self.session)
        if not header and session and request.method not in {"GET", "HEAD", "OPTIONS"}:
            error = self._unsafe(request)
            if error is not None:
                await error(scope, receive, secured)
                return
        headers = [(key, value) for key, value in scope["headers"] if key.lower() not in {b"cookie", b"x-ogy-token"}]
        if header or (session and not credentials):
            headers.append((b"x-ogy-token", self.token))
        await self.app({**scope, "headers": headers}, receive, secured)

    def _authority(self, request: Request) -> JSONResponse | None:
        server = request.scope.get("server")
        host = f"127.0.0.1:{server[1]}" if server else ""
        if request.headers.getlist("host") != [host]:
            return JSONResponse({"error": "Host refused"}, status_code=403)
        origins = request.headers.getlist("origin")
        if origins and origins != [f"http://{host}"]:
            return JSONResponse({"error": "Origin refused"}, status_code=403)
        return None

    def _unsafe(self, request: Request) -> JSONResponse | None:
        if request.headers.get("origin") is None and request.headers.get("sec-fetch-site") != "same-origin":
            return JSONResponse({"error": "same-origin provenance required"}, status_code=403)
        if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
            return JSONResponse({"error": "JSON content type required"}, status_code=415)
        return None

    def _exchange(self, request: Request) -> JSONResponse | RedirectResponse:
        codes = request.query_params.getlist("t")
        if (
            request.method != "GET"
            or self.used
            or time.monotonic() >= self.expires
            or len(codes) != 1
            or not secrets.compare_digest(codes[0].encode(), self.exchange_code)
        ):
            return JSONResponse({"error": "invalid or expired exchange code"}, status_code=401)
        self.used = True
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("ogy_session", self.session, httponly=True, samesite="strict", path="/")
        response.headers.update({"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
        return response
