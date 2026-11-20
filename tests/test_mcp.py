"""The MCP server offers one tool per `ogy` subcommand and answers like the CLI."""

import argparse
import asyncio
lazy from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from tests.conftest import GOOD
lazy from fastmcp import FastMCP

from ogy import cli
from ogy.mcp_server import build


def commands() -> set[str]:
    sub = next(a for a in cli.parser()._actions if isinstance(a, argparse._SubParsersAction))
    return set(sub.choices)


def tools(server: FastMCP) -> dict[str, dict]:
    return {tool.name: tool.parameters for tool in asyncio.run(server.list_tools())}


def write_kb(root: Path) -> None:
    for rel, text in GOOD.items():
        (root / "docs/kb" / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / "docs/kb" / rel).write_text(text)


def test_one_tool_per_subcommand() -> None:
    assert set(tools(build())) == commands() - {"mcp", "init", "hook"}  # a person runs init once; mcp is the server; Git runs hook


def test_every_tool_takes_the_global_options() -> None:
    for name, schema in tools(build()).items():
        assert "kb" not in schema["properties"], name  # the folder is fixed: docs/kb
        assert {"repo", "rev"} <= set(schema["properties"]), name


def test_positionals_are_required() -> None:
    schema = tools(build())["diff"]
    assert {"before", "after"} <= set(schema["required"])
    assert "required" not in tools(build())["check"] or not tools(build())["check"]["required"]


def test_check_returns_the_cli_output(tmp_path: Path) -> None:
    write_kb(tmp_path)
    args = {"repo": str(tmp_path), "rev": "."}
    result = asyncio.run(build().call_tool("check", args))
    code, lines = cli.run(["--repo", str(tmp_path), "--rev", ".", "check"], agent=True)  # the tool answers with a table for an agent
    assert result.structured_content == {"exit_code": code, "output": "\n".join(lines)}


def call(name: str, arguments: dict[str, object]) -> str:
    """The message of the tool error a call ends in."""
    with pytest.raises(ToolError) as error:
        asyncio.run(build().call_tool(name, arguments))
    return str(error.value)


def test_exit_codes_2_to_4_are_tool_errors_and_the_server_goes_on(tmp_path: Path) -> None:
    write_kb(tmp_path)
    where = {"repo": str(tmp_path), "rev": "."}
    assert "no entry product/app/nope/x" in call("show", {**where, "address": "product/app/nope/x"})  # 4: not found
    assert "has no flow to draw" in call("diagram", {**where, "address": "product/app/actor/member"})  # 3: refused
    assert "no knowledge-base folder docs/kb/" in call("check", {"repo": str(tmp_path / "nowhere"), "rev": "."})  # 3: refused
    done = asyncio.run(build().call_tool("check", where)).structured_content
    assert done == {"exit_code": cli.OK, "output": "problem\tpath\taddress\tdetail"}


def test_the_reply_tool_requires_its_round() -> None:
    assert "round" in tools(build())["reply"]["required"]


PROTOCOL_VERSION = "2025-11-25"  # the revision this server negotiates; an SDK bump that moves it shows here as a diff


def test_the_negotiated_protocol_version_is_pinned() -> None:
    async def negotiated() -> str:
        async with Client(build()) as client:
            assert client.initialize_result is not None
            return str(client.initialize_result.protocolVersion)

    assert asyncio.run(negotiated()) == PROTOCOL_VERSION


def test_a_client_sees_the_tool_set_and_a_call_round_trips(tmp_path: Path) -> None:
    write_kb(tmp_path)

    async def session() -> tuple[set[str], bool, object]:
        async with Client(build()) as client:
            listed = {tool.name for tool in await client.list_tools()}
            result = await client.call_tool("check", {"repo": str(tmp_path), "rev": "."})
            return listed, result.is_error, result.structured_content

    listed, is_error, structured = asyncio.run(session())
    assert listed == commands() - {"mcp", "init", "hook"}
    assert not is_error and structured == {"exit_code": cli.OK, "output": "problem\tpath\taddress\tdetail"}


def test_a_wrong_or_unknown_argument_is_an_error_result_naming_it(tmp_path: Path) -> None:
    write_kb(tmp_path)
    where = {"repo": str(tmp_path), "rev": "."}

    async def bad(arguments: dict[str, object]) -> tuple[bool, str]:
        async with Client(build()) as client:
            result = await client.call_tool("show", arguments, raise_on_error=False)
            return result.is_error, result.content[0].model_dump()["text"]

    wrong_type = asyncio.run(bad({**where, "address": 5}))
    unknown = asyncio.run(bad({**where, "address": "product/app/actor/member", "colour": "red"}))
    assert wrong_type[0] and "address" in wrong_type[1]
    assert unknown[0] and "colour" in unknown[1]
