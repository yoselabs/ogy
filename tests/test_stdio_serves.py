"""`python -m ogy mcp` as a client starts it: a real process on stdio, the handshake, the tool list, one call and one bad call."""

import asyncio
import sys
lazy from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from tests.conftest import GOOD
from tests.test_mcp import commands

from ogy import cli
from ogy.mcp_server import NO_TOOL


def write_kb(root: Path) -> None:
    for rel, text in GOOD.items():
        (root / "docs/kb" / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / "docs/kb" / rel).write_text(text)


def test_the_real_server_lists_its_tools_answers_a_call_and_survives_a_bad_one(tmp_path: Path) -> None:
    write_kb(tmp_path)
    expected = commands() - set(NO_TOOL)

    async def session() -> None:
        transport = StdioTransport(command=sys.executable, args=["-m", "ogy", "mcp"], cwd=str(tmp_path), keep_alive=False)
        async with Client(transport) as client:
            assert {tool.name for tool in await client.list_tools()} == expected
            done = await client.call_tool("check", {"repo": str(tmp_path), "rev": "."})
            assert done.structured_content == {"exit_code": cli.OK, "output": "problem\tpath\taddress\tdetail"}
            bad = await client.call_tool("show", {"repo": str(tmp_path), "rev": ".", "address": "product/app/nope/x"}, raise_on_error=False)
            assert (
                bad.is_error and "no entry product/app/nope/x" in bad.content[0].model_dump()["text"]
            )  # an error result, not a dead transport
            again = await client.call_tool("check", {"repo": str(tmp_path), "rev": "."})
            assert not again.is_error  # and the server goes on

    asyncio.run(session())
