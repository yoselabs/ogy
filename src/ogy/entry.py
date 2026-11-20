"""The console entry: the CLI with the MCP server wired in for `ogy mcp`."""

lazy from collections.abc import Sequence

from ogy import cli, mcp_server


def main(argv: Sequence[str] | None = None) -> int:
    return cli.main(argv, serve=mcp_server.main)
