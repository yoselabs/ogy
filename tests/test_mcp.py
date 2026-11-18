"""The MCP server offers one tool per `ogy` subcommand and answers like the CLI."""

import argparse
import asyncio
from pathlib import Path

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from tests.conftest import GOOD

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
    assert set(tools(build())) == commands() - {"mcp", "init"}  # a person runs init once; mcp is the server


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
