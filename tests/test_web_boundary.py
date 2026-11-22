"""Hostile browser requests must not inherit the MCP client's authority."""

import asyncio
import shutil
import socket
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.tools import FunctionTool
from starlette.testclient import TestClient

from ogy import cli
from ogy.mcp_server import build
from ogy.target import Target
from ogy.web import boundary, serve
from ogy.web.serve import application
from ogy.writes import locked

LIBRARY = Path(__file__).parent / "fixtures/tool-library"
BASE = "http://127.0.0.1:8123"
HEADERS = {"X-Ogy-Token": "test-secret"}


def test_browser_session_is_separate_single_use_and_board_only():
    """Given a browser code, exchanging it once grants board access but no MCP authority."""
    service = application(Target(LIBRARY), "test-secret")
    with TestClient(service, base_url=BASE) as client:
        assert client.get("/?t=test-secret", follow_redirects=False).status_code == 401
        response = client.get("/?t=" + service.exchange_code, follow_redirects=False)
        assert response.status_code == 303
        session = client.cookies["ogy_session"]
        assert session not in {"test-secret", service.exchange_code}
        assert client.get("/api/version").status_code == 200
        assert client.post("/mcp/", json={}).status_code == 401
        assert client.get("/?t=" + service.exchange_code, follow_redirects=False).status_code == 401
    with TestClient(application(Target(LIBRARY), "test-secret"), base_url=BASE) as other:
        other.cookies.set("ogy_session", session)
        assert other.get("/api/version").status_code == 401


@pytest.mark.parametrize(
    "headers,expected",
    [
        ({}, 403),
        ({"Origin": BASE}, 415),
        ({"Origin": BASE, "Content-Type": "application/json"}, 404),
        ({"Sec-Fetch-Site": "same-origin", "Content-Type": "application/json"}, 404),
    ],
)
def test_cookie_unsafe_methods_require_browser_provenance_and_json(headers, expected):
    """Given a board cookie, unsafe requests need same-origin provenance and JSON."""
    service = application(Target(LIBRARY), "test-secret")
    with TestClient(service, base_url=BASE) as client:
        client.get("/?t=" + service.exchange_code)
        assert client.post("/api/version", content="{}", headers=headers).status_code == expected


@pytest.mark.parametrize(
    "headers", [[("X-Ogy-Token", "test-secret"), ("X-Ogy-Token", "wrong")], [(b"X-Ogy-Token", b"wrong"), (b"X-Ogy-Token", b"\xc3\xa9")]]
)
def test_duplicate_credentials_are_refused_without_a_server_error(headers):
    """Given duplicate credentials, no parser chooses a different token than the validator."""
    service = application(Target(LIBRARY), "test-secret")
    with TestClient(service, base_url=BASE) as client:
        for route in ("/api/version", "/healthz", "/?t=" + service.exchange_code):
            assert client.get(route, headers=headers, follow_redirects=False).status_code in {400, 401}


def test_authority_and_security_headers_cover_health_and_errors():
    """Given any response, headers block framing and sniffing; localhost is not an authority."""
    with TestClient(application(Target(LIBRARY), "test-secret"), base_url=BASE) as client:
        for path in ("/healthz", "/", "/api/version", "/missing"):
            response = client.get(path, headers=HEADERS)
            assert response.headers["x-content-type-options"] == "nosniff"
            assert response.headers["x-frame-options"] == "DENY"
            assert response.headers["content-security-policy"] == "default-src 'self'; frame-ancestors 'none'"
            assert "server" not in response.headers
        assert client.get("/healthz", headers={"Host": "localhost:8123"}).status_code == 403


def test_http_tool_contract_is_stdio_minus_repository_escape_arguments():
    """Given the tool list, HTTP removes only the four escape arguments and refuses each at runtime."""

    async def scenario():
        async with Client(build()) as stdio, Client(build(LIBRARY)) as http:
            originals = {tool.name: tool.model_dump() for tool in await stdio.list_tools()}
            for tool in await http.list_tools():
                original = originals.pop(tool.name)
                for field in ("repo", "rev", "ontology", "file"):
                    original["inputSchema"]["properties"].pop(field, None)
                if "required" in original["inputSchema"]:
                    original["inputSchema"]["required"] = [
                        name for name in original["inputSchema"]["required"] if name not in {"repo", "rev", "ontology", "file"}
                    ]
                assert tool.model_dump() == original
            assert not originals
            for field in ("repo", "rev", "ontology", "file"):
                with pytest.raises(Exception, match=r"pinned|forbidden|not permitted|Unexpected keyword|Additional properties"):
                    await http.call_tool("status", {field: "/outside"})

    asyncio.run(scenario())


def test_read_cannot_observe_a_trial_write(repo):
    """Given a writer holding ogy's lock, the board refuses rather than showing trial bytes."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    with TestClient(application(target, "test-secret"), base_url=BASE, headers=HEADERS) as client:
        before = client.get("/api/version").json()
        path = repo / "docs/kb/product/lending/area.yml"
        original = path.read_text()
        with locked(target, "trial"):
            path.write_text("says: This trial will be refused.\n")
            for route in ("/api/version", "/api/inspection", "/api/entry/product/lending/actor/member"):
                assert client.get(route).status_code == 400
            path.write_text(original)
        assert client.get("/api/version").json() == before


@pytest.mark.parametrize("tool,arguments", [("show", {"address": "product/lending/actor/member"}), ("review", {})])
def test_http_mcp_reads_also_refuse_a_repository_under_trial_write(repo, tool, arguments):
    """Given the same writer lock, MCP must not expose the transient data through another route."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)

    async def scenario():
        async with Client(build(repo)) as client:
            with locked(Target(repo), "trial"):
                result = await client.call_tool(tool, arguments, raise_on_error=False)
                assert result.is_error
                assert "lock" in result.content[0].model_dump()["text"]

    asyncio.run(scenario())


def test_serve_refuses_revision_instead_of_ignoring_it():
    """Given an explicit historical revision, serve refuses before invoking a starter."""
    calls = []
    code, lines = cli.run(["--rev", "HEAD", "serve"], serve=lambda *a, **kw: calls.append(a))
    assert code == cli.REFUSED and "--rev" in " ".join(lines) and not calls


def test_browser_exchange_expires_and_never_accepts_a_header_token(monkeypatch):
    """Given an old navigation code, a later visit must request a new process link."""
    now = [100.0]
    monkeypatch.setattr(boundary.time, "monotonic", lambda: now[0])
    service = application(Target(LIBRARY), "test-secret")
    now[0] += 61
    with TestClient(service, base_url=BASE) as client:
        for code in (service.exchange_code, "test-secret"):
            assert client.get("/?t=" + code, follow_redirects=False).status_code == 401


def test_busy_port_is_a_refusal_with_an_ephemeral_port_hint(monkeypatch):
    """Given a port held by another listener, the console refuses without a traceback."""
    monkeypatch.setattr(serve, "resolve_token", lambda _: "test-secret")
    with socket.socket() as held:
        held.bind(("127.0.0.1", 0))
        held.listen()
        code, lines = cli.run(["serve", "--port", str(held.getsockname()[1])], serve=serve.main)
    assert code == cli.REFUSED and "--port 0" in " ".join(lines)


def test_console_disables_uvicorn_identifying_headers(monkeypatch):
    """Given a console server, the transport must not append a Server header after ASGI."""
    configs = []
    monkeypatch.setattr(serve.uvicorn.Server, "run", lambda self, **kw: configs.append(self.config))
    application(Target(LIBRARY), "test-secret").run(port=0)
    assert len(configs) == 1 and configs[0].server_header is False


@pytest.mark.parametrize("field", ["repo", "rev", "ontology", "file"])
def test_http_tool_runner_refuses_overrides_even_when_validation_is_bypassed(field):
    """Given direct tool execution, the runner still refuses pin escapes without reading files."""

    async def scenario():
        server = build(LIBRARY)
        tools = {tool.name: tool for tool in await server.list_tools()}
        tool = tools["put"]
        assert isinstance(tool, FunctionTool)
        with pytest.raises(Exception, match=r"pinned|forbidden"):
            tool.fn(**{field: "/synthetic-outside"})

    asyncio.run(scenario())
