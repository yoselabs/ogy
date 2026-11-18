"""`ogy mcp`: the `ogy` commands as MCP tools over stdio, one tool per subcommand.

The tools are built from the argparse structure of `ogy.cli.parser()` by shelf's `argparse-mcp`, so a new subcommand appears
here without an edit; its description is the command's own (`init` and `mcp` are no tools). Each tool calls `ogy.cli.run` in this
process, the same operation the CLI uses. The global options (`--repo`, `--rev`, ...) are inputs of every tool. The result is
the exit code and the output: a table or a record for an agent.

Configure it per repository in `.mcp.json` at the repository root (the server starts in that folder, so `--repo`
defaults to it):

    {
      "mcpServers": {
        "ogy": {"command": "uvx", "args": ["--from", "git+https://github.com/yoselabs/ogy", "ogy", "mcp"]}
      }
    }
"""

import contextlib
import io
from collections.abc import Sequence

from argparse_mcp import tools_from_parser
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from ogy import cli

NO_TOOL = ("mcp", "init")  # the subcommand that starts this server, and the one a person runs once to set a repository up


def _run(argv: Sequence[str]) -> cli.Result:
    """The CLI's result; usage errors, refusals and entries not found (exit codes 2 to 4) are tool errors, not output."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            code, lines = cli.run(argv, agent=True)  # tables and records for an agent, not lines for a person
    except SystemExit as stop:  # argparse rejected the input
        raise ToolError(err.getvalue().strip() or f"usage error ({stop.code})") from stop
    if code >= cli.USAGE:
        raise ToolError("\n".join(lines))
    return code, lines


def build() -> FastMCP:
    """The server: one tool per subcommand of the CLI parser (`argparse-mcp`), each running `ogy.cli.run` in this process."""
    top = cli.parser()
    server = FastMCP("ogy", instructions=top.description)
    for tool in tools_from_parser(top, _run, usage=cli.USAGE):
        if tool.name == "reply":  # the round is named over MCP: a bare reply would resolve against whichever round is newest
            tool.parameters["required"] = [*tool.parameters.get("required", []), "round"]
        if tool.name not in NO_TOOL:
            server.add_tool(tool)
    return server


def main() -> None:
    build().run("stdio")
