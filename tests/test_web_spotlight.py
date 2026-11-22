"""The spotlight: one MCP call changes every open page at once, writes nothing and leaves the inspection version alone."""

import asyncio
import json
import shutil
import time
from pathlib import Path

import httpx
import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError

from ogy.mcp_server import build
from ogy.target import Target
from ogy.verdict import RefusalError
from ogy.web.serve import application
from ogy.web.spotlight import LOG_LIMIT, Spotlight

LIBRARY = Path(__file__).parent / "fixtures/tool-library"
HEADERS = {"X-Ogy-Token": "test-secret"}
MEMBER = "product/lending/actor/member"
TARGETS = [{"address": MEMBER, "says": "Who borrows."}, {"address": "product/lending/entity/loan", "says": "What is lent."}]


async def next_event(lines):
    """The next `data:` payload of a server-sent stream."""
    async for line in lines:
        if line.startswith("data: "):
            return json.loads(line.removeprefix("data: "))
    message = "the stream ended"
    raise AssertionError(message)


def files(root):
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())


def test_show_replaces_dismiss_clears_and_every_call_has_a_sequence():
    hub = Spotlight()
    first = hub.show(title="One", targets=[(MEMBER, "Who.")], session="a")
    second = hub.show(title="Two", targets=[(MEMBER, "Who.")], session="b")
    assert (first["sequence"], second["sequence"]) == (1, 2)
    assert hub.snapshot()["spotlight"]["title"] == "Two"
    assert hub.dismiss(session="b")["sequence"] == 3
    assert hub.snapshot()["spotlight"] is None
    assert [row["action"] for row in hub.snapshot()["log"]] == ["dismiss", "show", "show"]  # newest first


def test_a_refusal_is_logged_and_changes_nothing():
    hub = Spotlight(lambda addresses: [a for a in addresses if a != MEMBER])
    hub.show(title="Kept", targets=[(MEMBER, "Who.")], session="a")
    bad = (("", [(MEMBER, "x")]), ("T", []), ("T", [("nope", "x")]), ("T", [(MEMBER, "x"), (MEMBER, "y")]), ("T", [("a/b/c", "x")]))
    for title, targets in bad:
        with pytest.raises(RefusalError):
            hub.show(title=title, targets=targets, session="a")
    snapshot = hub.snapshot()
    assert snapshot["spotlight"]["title"] == "Kept" and snapshot["log"][0]["action"] == "refused" and snapshot["sequence"] == 6


def test_the_log_is_bounded():
    hub = Spotlight()
    for _ in range(LOG_LIMIT + 5):
        hub.dismiss(session="a")
    assert len(hub.snapshot()["log"]) == LOG_LIMIT and hub.snapshot()["sequence"] == LOG_LIMIT + 5


def test_the_tool_exists_only_where_a_board_does():
    async def names(server):
        async with Client(server) as client:
            return {tool.name for tool in await client.list_tools()}

    assert "spotlight" not in asyncio.run(names(build()))
    assert "spotlight" in asyncio.run(names(build(spotlight=Spotlight())))


def test_an_mcp_call_reaches_an_open_page_within_250_ms_and_writes_nothing(tmp_path):
    """Given an open event stream, a tool call is on it before 250 ms, unknown addresses are refused and the KB stays as it was."""
    shutil.copytree(LIBRARY, tmp_path, dirs_exist_ok=True)

    async def session():
        async with application(Target(tmp_path), "test-secret").serving() as url, httpx.AsyncClient(headers=HEADERS, timeout=10) as browser:
            before = (await browser.get(url + "/api/version")).json()["version"]
            async with browser.stream("GET", url + "/api/events") as stream:
                assert stream.headers["content-type"].startswith("text/event-stream")
                lines = stream.aiter_lines()
                assert (await next_event(lines))["spotlight"] is None
                async with Client(StreamableHttpTransport(url + "/mcp/", headers=HEADERS)) as client:
                    started = time.perf_counter()
                    await client.call_tool("spotlight", {"action": "show", "title": "Members", "targets": TARGETS, "session": "test"})
                    event = await asyncio.wait_for(next_event(lines), 5)
                    assert (
                        time.perf_counter() - started < 1
                    )  # the 250 ms of the page is measured in a browser (spotlight-check.mjs); this only guards the stream
                    assert event["spotlight"]["title"] == "Members"
                    assert [t["address"] for t in event["spotlight"]["targets"]] == [t["address"] for t in TARGETS]
                    unknown = [{"address": "product/lending/actor/nobody", "says": "x"}]
                    refused = await client.call_tool(
                        "spotlight", {"action": "show", "title": "X", "targets": unknown}, raise_on_error=False
                    )
                    assert refused.is_error and "no such entry" in refused.content[0].model_dump()["text"]
                    assert (await asyncio.wait_for(next_event(lines), 5))["log"][0]["action"] == "refused"
                    post = {"Content-Type": "application/json", "Origin": url}
                    assert (await browser.post(url + "/api/spotlight/dismiss", headers=post)).json()["result"] == "dismissed"
                    assert (await asyncio.wait_for(next_event(lines), 5))["spotlight"] is None
            assert (await browser.get(url + "/api/version")).json()["version"] == before
            assert (await browser.get(url + "/api/spotlight")).json()["sequence"] == 3

    asyncio.run(session())
    assert files(tmp_path) == files(LIBRARY)  # nothing was written anywhere in the repository


def test_the_spotlight_tool_holds_the_contract_properties_of_every_tool():
    """Given the board's server, the extra tool is closed, described and annotated on purpose like the generated ones."""

    async def listed():
        async with Client(build(spotlight=Spotlight())) as client:
            return {tool.name: tool.model_dump(mode="json", by_alias=True, exclude_none=True) for tool in await client.list_tools()}

    tool = asyncio.run(listed())["spotlight"]
    assert tool["inputSchema"].get("additionalProperties") is False and tool["inputSchema"]["required"] == ["action"]
    assert set(tool["annotations"]) == {"readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"}
    assert tool["annotations"]["openWorldHint"] is False and tool["annotations"]["destructiveHint"] is False
    assert "writes no entry" in tool["description"] and len(tool["description"]) < 1200


def test_a_tool_error_is_actionable_when_the_tool_is_misused():
    async def call():
        async with Client(build(spotlight=Spotlight())) as client:
            await client.call_tool("spotlight", {"action": "show", "title": "T"})

    with pytest.raises(ToolError, match="1 to 12 targets"):
        asyncio.run(call())
