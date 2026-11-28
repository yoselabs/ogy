"""The sketch: entries in the `put` format are drawn by the board and never written; what they would touch comes from the graph."""

import asyncio
import json
import shutil
from pathlib import Path

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from ogy.mcp_server import build
from ogy.target import Target
from ogy.web.serve import application
from ogy.web.spotlight import Spotlight

LIBRARY = Path(__file__).parent / "fixtures/tool-library"
HEADERS = {"X-Ogy-Token": "test-secret"}
WORKFLOW = "product/lending/workflow/reserve-a-tool"
DECISION = "product/lending/decision/late-fee"
RECORDS = [
    {
        "address": WORKFLOW,
        "says": "A member reserves a tool for a day.",
        "start": "ask",
        "realizes": ["product/lending/capability/lend-tools"],
        "steps": {
            "ask": {
                "says": "The member asks to reserve a tool.",
                "actor": "product/lending/actor/member",
                "choices": {"reserve": {"label": "Reserve", "then": "hold"}, "leave": {"label": "Leave", "then": "left"}},
            },
            "hold": {
                "says": "The library holds the tool.",
                "cases": {
                    "otherwise": {"then": "held", "effects": [{"do": "change", "on": "product/lending/entity/tool/attribute/out"}]},
                },
            },
        },
        "ends": {
            "held": {"says": "The tool is held.", "result": "success"},
            "left": {"says": "The member left.", "result": "failure"},
        },
    },
    {"address": "product/lending/actor/member", "says": "A person who borrows or reserves tools."},
]


async def next_event(lines):
    async for line in lines:
        if line.startswith("data: "):
            return json.loads(line.removeprefix("data: "))
    message = "the stream ended"
    raise AssertionError(message)


def files(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def text(result):
    return result.content[0].model_dump()["text"]


def test_a_sketch_reaches_the_page_draws_new_entries_and_writes_nothing(tmp_path):
    """Given an open stream, show carries the new entries and what they would touch; dismiss clears it; the KB is as it was."""
    shutil.copytree(LIBRARY, tmp_path, dirs_exist_ok=True)
    before = files(tmp_path)

    async def session():
        async with application(Target(tmp_path), "test-secret").serving() as url, httpx.AsyncClient(headers=HEADERS, timeout=20) as browser:
            version = (await browser.get(url + "/api/version")).json()["version"]
            async with browser.stream("GET", url + "/api/events") as stream:
                lines = stream.aiter_lines()
                assert (await next_event(lines))["sketch"] is None
                async with Client(StreamableHttpTransport(url + "/mcp/", headers=HEADERS)) as client:
                    arguments = {"action": "show", "title": "Reserve", "records": RECORDS, "decision": DECISION, "option": "two"}
                    await client.call_tool("sketch", {**arguments, "session": "test"})
                    sketch = (await asyncio.wait_for(next_event(lines), 10))["sketch"]
                    drawn = {record["address"] for record in sketch["entries"]}
                    assert WORKFLOW in drawn and f"{WORKFLOW}/step/ask" in drawn and "product/lending/actor/member" not in drawn
                    assert (sketch["decision"], sketch["option"], sketch["session"]) == (DECISION, "two", "test")
                    touched = {row["address"]: row for row in sketch["touching"]}
                    assert touched["product/lending/actor/member"]["how"] == "change"
                    assert touched["product/lending/capability/lend-tools"]["via"] == ["realizes"]
                    assert touched["product/lending/entity/tool/attribute/out"]["how"] == "link"
                    assert not drawn & set(touched)
                    assert (await browser.get(url + "/api/version")).json()["version"] == version  # shown: nothing changed
                    post = {"Content-Type": "application/json", "Origin": url}
                    assert (await browser.post(url + "/api/sketch/dismiss", headers=post)).json()["result"] == "dismissed"
                    assert (await asyncio.wait_for(next_event(lines), 10))["sketch"] is None
            assert (await browser.get(url + "/api/version")).json()["version"] == version  # dismissed: nothing changed

    asyncio.run(session())
    assert files(tmp_path) == before  # not one byte of the repository was written


def test_what_put_would_refuse_is_refused_with_its_reasons_and_logged():
    async def call(arguments):
        hub = Spotlight(sketcher=lambda *_: {"entries": []})
        async with Client(build(spotlight=hub)) as client:
            result = await client.call_tool("sketch", arguments, raise_on_error=False)
        return result, hub.snapshot()

    result, state = asyncio.run(call({"action": "show", "title": "", "records": [{"address": "a/b/c"}]}))
    assert result.is_error and "title" in text(result) and state["sketch"] is None and state["log"][0]["action"] == "refused"


def test_a_sketch_that_put_refuses_or_names_a_missing_decision_is_refused(tmp_path):
    shutil.copytree(LIBRARY, tmp_path, dirs_exist_ok=True)
    before = files(tmp_path)

    async def session():
        async with (
            application(Target(tmp_path), "test-secret").serving() as url,
            Client(StreamableHttpTransport(url + "/mcp/", headers=HEADERS)) as client,
        ):
            shown = {"action": "show", "title": "T", "records": RECORDS}
            cases = {
                "no kind": {**shown, "records": [{"address": "product/lending/nokind/x", "says": "x"}]},
                "bad field": {**shown, "records": [{"address": "product/lending/workflow/w", "start": 3}]},
                "no decision": {**shown, "decision": "product/lending/decision/nobody", "option": "a"},
                "no option": {**shown, "decision": DECISION, "option": "nine"},
                "half": {**shown, "decision": DECISION},
            }
            for name, arguments in cases.items():
                result = await client.call_tool("sketch", arguments, raise_on_error=False)
                assert result.is_error, name
            accepted = await client.call_tool("sketch", shown)
            assert not accepted.is_error and "sketched" in text(accepted)

    asyncio.run(session())
    assert files(tmp_path) == before


def test_the_sketch_tool_is_closed_described_and_annotated_like_the_others():
    async def listed():
        async with Client(build(spotlight=Spotlight())) as client:
            return {tool.name: tool.model_dump(mode="json", by_alias=True, exclude_none=True) for tool in await client.list_tools()}

    tool = asyncio.run(listed())["sketch"]
    assert tool["inputSchema"].get("additionalProperties") is False and tool["inputSchema"]["required"] == ["action"]
    assert tool["annotations"]["openWorldHint"] is False and tool["annotations"]["destructiveHint"] is False
    assert "writes no entry" in tool["description"] and len(tool["description"]) < 1200
