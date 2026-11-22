"""The loopback board reads current entries and shares its authenticated process with MCP."""

import asyncio
import shutil
from pathlib import Path

import httpx
import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from starlette.testclient import TestClient
from static_page_check import budget_problems, colour_problems, import_problems, page_problems

from ogy import cli
from ogy.inspect import inspect
from ogy.mcp_server import build
from ogy.target import Target
from ogy.web import serve
from ogy.web.serve import application
from ogy.web.token import resolve_token

LIBRARY = Path(__file__).parent / "fixtures/tool-library"
HEADERS = {"X-Ogy-Token": "test-secret"}
VENDORED = ("vendor/elk.bundled.js", "vendor/lit-html.js")
STATIC = Path(__file__).resolve().parents[1] / "src/ogy/web/static"
BOARD_ROUTES = ("/", "/board.css", "/view-contract.json", *("/" + path.relative_to(STATIC).as_posix() for path in STATIC.rglob("*.js")))


@pytest.mark.parametrize("source", [LIBRARY, Path(__file__).resolve().parents[1]], ids=["tool-library", "ogy"])
def test_health_is_public_but_every_board_and_mcp_route_requires_auth(tmp_path, source):
    """Given the fixture, health precedes auth and API inspection equals the library document."""
    shutil.copytree(source / "docs/kb", tmp_path / "docs/kb")
    target = Target(tmp_path)
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123") as client:
        assert client.get("/healthz").json()["ready"] is True
        for route in (
            *BOARD_ROUTES,
            "/api/inspection",
            "/api/version",
            "/api/events",
            "/api/spotlight",
            "/api/entry/product/app/actor/member",
            "/mcp/",
        ):
            assert client.get(route).status_code == 401
            assert client.get(route, headers={"X-Ogy-Token": "wrong"}).status_code == 401
        document = inspect(target.read()[1])
        received = client.get("/api/inspection", headers=HEADERS).json()
        document["snapshot"]["version"] = received["snapshot"]["version"]
        assert received == document
        entry = document["entries"][0]
        assert client.get("/api/entry/" + entry["address"], headers=HEADERS).json() == entry
        assert client.get("/api/entry/missing", headers=HEADERS).status_code == 404
        page = client.get("/", headers=HEADERS)
        assert 'src="js/main.js"' in page.text
        assert 'href="board.css"' in page.text
        assert "default-src 'self'" in page.headers["content-security-policy"]
        assert "script-src" not in page.headers["content-security-policy"]
        for route, content_type in (("/board.css", "text/css"), ("/js/main.js", "javascript"), ("/view-contract.json", "application/json")):
            response = client.get(route, headers=HEADERS)
            assert response.status_code == 200
            assert content_type in response.headers["content-type"]
        assert client.get("/js/missing.js", headers=HEADERS).status_code == 404


def test_an_ogy_write_changes_the_next_version_and_inspection(repo):
    """Given a running board, a per-write operation is visible without restarting it."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        before = client.get("/api/version").json()
        record = '{"address":"product/lending/actor/member","says":"A person borrowing tools."}'
        code, lines = cli.run(["--repo", str(repo), "put", record])
        assert code == 0, lines
        assert client.get("/api/version").json() != before
        received = client.get("/api/inspection").json()
        expected = inspect(target.read()[1])
        expected["snapshot"]["version"] = received["snapshot"]["version"]
        assert received == expected


@pytest.mark.parametrize("path", ["/healthz", "/api/inspection", "/mcp/", "/"])
@pytest.mark.parametrize(
    "headers", [{"Host": "evil.example"}, {"Host": "localhost:8123"}, {"Origin": "http://evil.example"}, {"Origin": "null"}]
)
def test_host_and_origin_are_checked_even_with_a_valid_token(path, headers):
    """Given a rebound Host or cross-site Origin, all HTTP routes refuse the request."""
    with TestClient(application(Target(LIBRARY), "test-secret"), base_url="http://127.0.0.1:8123") as client:
        assert client.get(path, headers={**HEADERS, **headers}).status_code == 403


def test_browser_exchanges_url_token_for_a_cookie_and_redirects_without_the_secret():
    """Given the printed URL, navigation establishes a private cookie then removes the URL token."""
    service = application(Target(LIBRARY), "test-secret")
    with TestClient(service, base_url="http://127.0.0.1:8123") as client:
        assert client.get("/?t=wrong", follow_redirects=False).status_code == 401
        response = client.get("/?t=" + service.exchange_code, follow_redirects=False)
        assert response.status_code == 303 and response.headers["location"] == "/"
        cookie = response.headers["set-cookie"]
        assert "HttpOnly" in cookie and "SameSite=strict" in cookie and "Path=/" in cookie
        assert response.headers["referrer-policy"] == "no-referrer"
        assert client.get("/api/inspection").status_code == 200
        for path in BOARD_ROUTES:
            assert client.get(path).status_code == 200
        assert client.get("/api/inspection", headers={"Origin": "http://evil.example"}).status_code == 403


def test_board_assets_resolve_locally_and_keep_colours_in_the_stylesheet(tmp_path):
    """Given the shipped shell, its imports and page references resolve within the package."""
    assert import_problems(STATIC, vendored=VENDORED) == []
    assert page_problems(STATIC) == []
    assert colour_problems(STATIC, "board.css", vendored=VENDORED) == []
    authored = tmp_path / "static"
    shutil.copytree(STATIC, authored, ignore=shutil.ignore_patterns("vendor"))
    assert budget_problems(authored, 100 * 1024) == []


def test_board_modules_stay_within_the_source_file_cap():
    """Given every shipped ES module, none exceeds the repository's 400-line cap."""
    modules = sorted(path for path in STATIC.rglob("*.js") if "vendor" not in path.parts)
    assert modules
    assert [str(path) for path in modules if len(path.read_text(encoding="utf-8").splitlines()) > 400] == []


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

    assert cli.run(["--repo", str(tmp_path), "serve", "--port", "0"], serve=start) == (0, [])
    assert calls == [(Target(tmp_path), 0)]


def test_http_mcp_lists_the_stdio_tools_and_stops_with_its_process_scope(tmp_path):
    """Given one ephemeral loopback server, authenticated MCP lists exactly the stdio tool set."""
    shutil.copytree(LIBRARY, tmp_path, dirs_exist_ok=True)

    async def session():
        async with application(Target(tmp_path), "test-secret").serving() as url:
            async with httpx.AsyncClient() as browser:
                response = await browser.get(url + "/healthz")
                assert response.status_code == 200 and "server" not in response.headers
            transport = StreamableHttpTransport(url + "/mcp/", headers=HEADERS)
            async with Client(transport) as client:
                names = {tool.name for tool in await client.list_tools()}
                result = await client.call_tool("show", {"address": "product/lending/actor/member"})
                assert not result.is_error and "A person who borrows tools." in result.content[0].model_dump()["text"]
            assert names == {tool.name for tool in await build().list_tools()} | {"spotlight"}
            assert not names & {"view", "serve"}

    asyncio.run(session())


def test_the_token_is_private_and_survives_an_explicit_stable_restart(repo, monkeypatch):
    """Given a fresh instance, its stable secret is minted privately and reused."""
    monkeypatch.setenv("OGY_SERVE_STABLE_TOKEN", "1")
    first = resolve_token(repo)
    path = repo / ".git/ogy/server.token"
    assert first and path.stat().st_mode & 0o777 == 0o600
    assert resolve_token(repo) == first


@pytest.mark.parametrize("options, expected", [({}, 8765), ({"port": 0}, 0)])
def test_console_uses_the_service_port_and_prints_its_bound_browser_url(monkeypatch, capsys, options, expected):
    """Given default or ephemeral serving, the browser URL uses the actual bound address and ogy's token."""
    calls = []

    def run(self, *, port, on_bound):
        calls.append((self, port))
        on_bound("http://127.0.0.1:43210")

    monkeypatch.setattr(serve.BoardService, "run", run)
    monkeypatch.setattr(serve, "resolve_token", lambda _: "test-secret")
    serve.main(Target(LIBRARY), **options)
    assert len(calls) == 1 and isinstance(calls[0][0], serve.BoardService) and calls[0][1] == expected
    assert capsys.readouterr().err == f"ogy board: http://127.0.0.1:43210/?t={calls[0][0].exchange_code}\n"
    assert calls[0][0].exchange_code != "test-secret"


@pytest.mark.parametrize("port", [-1, 65536])
def test_console_reports_service_port_validation_as_an_ogy_refusal(monkeypatch, port):
    """Given an invalid port, the CLI reports the shelf refusal through ogy's normal error result."""
    monkeypatch.setattr(serve, "resolve_token", lambda _: "test-secret")
    code, lines = cli.run(["serve", "--port", str(port)], serve=serve.main)
    assert code == cli.REFUSED and lines == ["refused: port must be between 0 and 65535"]
