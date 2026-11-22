"""The console entry: the CLI with the MCP server wired in for `ogy mcp`."""

lazy from collections.abc import Sequence

from ogy import cli, mcp_server
from ogy.web import serve


def main(argv: Sequence[str] | None = None) -> int:
    return cli.main(argv, serve=serve.main, mcp=mcp_server.main)
