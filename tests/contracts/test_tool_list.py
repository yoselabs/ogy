"""The tool list is the public contract: a committed snapshot of what a client sees, and properties every live tool must hold.

Change a description, schema or annotation on purpose, run `OGY_UPDATE_SNAPSHOT=1 uv run pytest tests/contracts`, read the diff of
`ogy.snapshot.json` and commit both.
"""

import asyncio
import json
import os
import re
from pathlib import Path

from fastmcp import Client

from ogy.mcp_server import build

SNAPSHOT = Path(__file__).parent / "ogy.snapshot.json"
ANNOTATIONS = {"readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"}
READS = {"check", "status", "show", "find", "anchors", "impact", "diagram", "diff", "history", "work", "glossary", "kinds", "dropped"}
SIZE_BUDGET = 60_000  # bytes of the serialized list: every tool description and schema enters an agent's context


def live_tools() -> list[dict]:
    async def listed() -> list[dict]:
        async with Client(build()) as client:
            tools = await client.list_tools()
        return [tool.model_dump(mode="json", by_alias=True, exclude_none=True) for tool in tools]

    return sorted(asyncio.run(listed()), key=lambda tool: tool["name"])


def test_the_tool_list_is_the_committed_snapshot() -> None:
    wire = json.dumps(live_tools(), indent=2, sort_keys=True) + "\n"
    if os.environ.get("OGY_UPDATE_SNAPSHOT") == "1":
        SNAPSHOT.write_text(wire)
    assert wire == SNAPSHOT.read_text(), "the tool list changed: regenerate with OGY_UPDATE_SNAPSHOT=1 and read the diff"


def test_every_tool_has_a_description_and_a_stable_name() -> None:
    for tool in live_tools():
        assert tool.get("description", "").strip(), tool["name"]
        assert re.fullmatch(r"[a-z][a-z0-9_]{0,127}", tool["name"]), tool["name"]  # snake_case, no dots or prefixes


def test_every_tool_sets_all_four_annotations_on_purpose() -> None:
    for tool in live_tools():
        assert set(tool["annotations"]) == ANNOTATIONS, tool["name"]
        assert tool["annotations"]["openWorldHint"] is False, tool["name"]  # one local repository, nothing open-world


def test_a_read_tool_is_read_only_and_not_destructive() -> None:
    tools = {tool["name"]: tool["annotations"] for tool in live_tools()}
    assert set(tools) >= READS
    for name in READS:
        assert tools[name]["readOnlyHint"] is True and tools[name]["destructiveHint"] is False, name
    for name in ("put", "remove", "move", "migrate"):  # these overwrite or rewrite entries
        assert tools[name]["readOnlyHint"] is False and tools[name]["destructiveHint"] is True, name


def test_every_input_schema_is_closed() -> None:
    for tool in live_tools():
        assert tool["inputSchema"].get("additionalProperties") is False, tool["name"]


def test_the_list_stays_within_its_size_budget() -> None:
    assert len(json.dumps(live_tools())) < SIZE_BUDGET
