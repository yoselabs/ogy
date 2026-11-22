"""The loopback board reads current entries and shares its authenticated process with MCP."""

import asyncio
import shutil
import signal
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import override
lazy from socket import socket

import httpx
import pytest
from async_scope.asgi import serve_asgi
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from starlette.testclient import TestClient

from ogy import cli
from ogy.inspect import inspect
from ogy.mcp_server import build
from ogy.target import Target
from ogy.web import serve
from ogy.web.serve import application
from ogy.web.token import resolve_token

LIBRARY = Path(__file__).parent / "fixtures/tool-library"
HEADERS = {"X-Ogy-Token": "test-secret"}


@pytest.mark.parametrize("source", [LIBRARY, Path(__file__).resolve().parents[1]], ids=["tool-library", "ogy"])
def test_health_is_public_but_every_board_and_mcp_route_requires_auth(tmp_path, source):
    """Given the fixture, health precedes auth and API inspection equals the library document."""
    shutil.copytree(source / "docs/kb", tmp_path / "docs/kb")
    target = Target(tmp_path)
    with TestClient(application(target, "test-secret", port=8123), base_url="http://127.0.0.1:8123") as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        for route in ("/", "/api/inspection", "/api/version", "/api/entry/product/app/actor/member", "/mcp/"):
            assert client.get(route).status_code == 401
            assert client.get(route, headers={"X-Ogy-Token": "wrong"}).status_code == 401
        document = inspect(target.read()[1])
        assert client.get("/api/inspection", headers=HEADERS).json() == document
        entry = document["entries"][0]
        assert client.get("/api/entry/" + entry["address"], headers=HEADERS).json() == entry
        assert client.get("/api/entry/missing", headers=HEADERS).status_code == 404
        assert "not built yet" in client.get("/", headers=HEADERS).text


def test_an_ogy_write_changes_the_next_version_and_inspection(repo):
    """Given a running board, a per-write operation is visible without restarting it."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    with TestClient(application(target, "test-secret", port=8123), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        before = client.get("/api/version").json()
        record = '{"address":"product/lending/actor/member","says":"A person borrowing tools."}'
        code, lines = cli.run(["--repo", str(repo), "put", record])
        assert code == 0, lines
        assert client.get("/api/version").json() != before
        assert client.get("/api/inspection").json() == inspect(target.read()[1])


@pytest.mark.parametrize("path", ["/healthz", "/api/inspection", "/mcp/", "/"])
@pytest.mark.parametrize("headers", [{"Host": "evil.example"}, {"Origin": "http://evil.example"}, {"Origin": "null"}])
def test_host_and_origin_are_checked_even_with_a_valid_token(path, headers):
    """Given a rebound Host or cross-site Origin, all HTTP routes refuse the request."""
    with TestClient(application(Target(LIBRARY), "test-secret", port=8123), base_url="http://127.0.0.1:8123") as client:
        assert client.get(path, headers={**HEADERS, **headers}).status_code == 403


def test_browser_exchanges_url_token_for_a_cookie_and_redirects_without_the_secret():
    """Given the printed URL, navigation establishes a private cookie then removes the URL token."""
    with TestClient(application(Target(LIBRARY), "test-secret", port=8123), base_url="http://127.0.0.1:8123") as client:
        assert client.get("/?t=wrong", follow_redirects=False).status_code == 401
        response = client.get("/?t=test-secret", follow_redirects=False)
        assert response.status_code == 303 and response.headers["location"] == "/"
        cookie = response.headers["set-cookie"]
        assert "HttpOnly" in cookie and "SameSite=strict" in cookie and "Path=/" in cookie
        assert response.headers["referrer-policy"] == "no-referrer"
        assert client.get("/api/inspection").status_code == 200
        assert client.get("/api/inspection", headers={"Origin": "http://evil.example"}).status_code == 403


def test_serve_help_never_starts_a_server_and_view_is_absent():
    """Given a help probe, neither the MCP callback nor board callback is invoked."""

    def unexpected(*args, **kwargs):
        pytest.fail("help started a server")

    with pytest.raises(SystemExit) as stop:
        cli.main(["serve", "--help"], serve=unexpected)
    assert stop.value.code == 0
    with pytest.raises(SystemExit):
        cli.run(["view"])


def test_serve_injects_the_worktree_target_and_port(tmp_path):
    """Given command flags, the board starter receives the repository's live worktree."""
    calls = []

    def start(target, *, port):
        calls.append((target, port))

    assert cli.run(["--repo", str(tmp_path), "--rev", "HEAD", "serve", "--port", "0"], serve=start) == (0, [])
    assert calls == [(Target(tmp_path), 0)]


def test_http_mcp_lists_the_stdio_tools_and_stops_with_its_process_scope():
    """Given one ephemeral loopback server, authenticated MCP lists exactly the stdio tool set."""

    async def session():
        async with serve_asgi(application(Target(LIBRARY), "test-secret", port=None)) as url:
            transport = StreamableHttpTransport(url + "/mcp/", headers=HEADERS)
            async with Client(transport) as client:
                names = {tool.name for tool in await client.list_tools()}
                result = await client.call_tool("show", {"address": "product/lending/actor/member"})
                assert not result.is_error and "A person who borrows tools." in result.content[0].model_dump()["text"]
            assert names == {tool.name for tool in await build().list_tools()}
            assert not names & {"view", "serve"}

    asyncio.run(session())


def test_the_token_is_private_and_survives_a_server_restart(repo):
    """Given a fresh instance, its stable secret is minted privately and reused."""
    first = resolve_token(repo)
    path = repo / ".git/ogy/server.token"
    assert first and path.stat().st_mode & 0o777 == 0o600
    assert resolve_token(repo) == first


def test_the_console_server_stops_on_its_interrupt_path(monkeypatch):
    """Given the console runner on port zero, its SIGINT handler stops the server and releases its socket."""
    ready = threading.Event()
    running = []

    class ObservedServer(serve.uvicorn.Server):
        @override
        async def startup(self, sockets: list[socket] | None = None):
            await super().startup(sockets)
            assert sockets is not None
            running.append((self, sockets[0].getsockname()[1]))
            ready.set()

    monkeypatch.setattr(serve.uvicorn, "Server", ObservedServer)
    monkeypatch.setattr(serve, "resolve_token", lambda _: "test-secret")
    with ThreadPoolExecutor(max_workers=1) as pool:
        task = pool.submit(serve.main, Target(LIBRARY), port=0)
        try:
            assert ready.wait(timeout=5), "the console server did not start"
            server, port = running[0]
            assert httpx.get(f"http://127.0.0.1:{port}/healthz").status_code == 200
        finally:
            if running:
                running[0][0].handle_exit(signal.SIGINT, None)
        task.result(timeout=5)
        assert not server.servers[0].is_serving()
