"""`ogy mcp`: the `ogy` commands as MCP tools over stdio, one tool per subcommand.

The tools are built from the argparse structure of `ogy.cli.parser()` by shelf's `argparse-mcp`, so a new subcommand appears
here without an edit; its description is the command's own (`init`, `mcp`, `serve` and `hook` are no tools).
Each tool calls `ogy.cli.run` in this process, the same operation the CLI uses.
The global options (`--repo`, `--rev`, ...) are inputs of every tool. The result is
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
import threading
from functools import wraps
from typing import Any
lazy from collections.abc import Callable, Sequence
lazy from pathlib import Path

from argparse_mcp import tools_from_parser
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.tools import FunctionTool
from fastmcp.tools.tool_transform import ToolAnnotations

from ogy import cli
from ogy.target import Target
from ogy.verdict import RefusalError
from ogy.writes import reading

NO_TOOL = ("mcp", "init", "hook", "serve")  # server starters, setup and the Git hook are not tools

# Annotations are hints to the client, all four set: the read tools change nothing; `review` saves a round; `answer` and `reply`
# add agreements; `put`, `remove`, `move` and `migrate` overwrite or rewrite entries. Every tool works on one local repository.
WRITES_ADDING = {"review", "answer", "reply"}
WRITES_OVERWRITING = {"put", "remove", "move", "migrate"}
_CALL_LOCK = threading.RLock()
HTTP_FORBIDDEN = frozenset({"repo", "rev", "ontology", "file"})


def _guarded(fn: Callable[..., Any], *, pinned: bool) -> Callable[..., Any]:
    # Any: argparse-mcp owns the generated callable's signature and result model.
    @wraps(fn)
    def call(**values: object) -> object:
        if pinned and any(values.get(field) is not None for field in HTTP_FORBIDDEN):
            message = "HTTP tools are pinned; repo, rev, ontology and file are forbidden"
            raise ToolError(message)
        # argparse-mcp also redirects stderr: serialize the complete dependency call, across server instances.
        with _CALL_LOCK:
            return fn(**values)

    return call


def annotations(name: str) -> ToolAnnotations:
    """The four hints of a tool: read-only (and so idempotent), adding, or overwriting."""
    reads = name not in WRITES_ADDING | WRITES_OVERWRITING
    return ToolAnnotations(
        readOnlyHint=reads,
        destructiveHint=name in WRITES_OVERWRITING,
        idempotentHint=reads or name in {"put", "move", "migrate"},
        openWorldHint=False,
    )


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


def _pinned_run(repo: Path, ontology: str | None, argv: Sequence[str]) -> cli.Result:
    if any(arg.split("=", 1)[0] in {"--repo", "--rev", "--ontology", "--file"} for arg in argv):
        message = "HTTP tools are pinned; repository overrides and file are forbidden"
        raise ToolError(message)
    pinned = ["--repo", str(repo), "--rev", "."]
    if ontology is not None:
        pinned.extend(["--ontology", ontology])
    if argv and argv[0] in (WRITES_OVERWRITING | WRITES_ADDING) - {"review"}:
        return _run([*pinned, *argv])
    try:
        with reading(Target(repo)):
            return _run([*pinned, *argv])
    except RefusalError as error:
        raise ToolError("\n".join(error.lines())) from error


def build(repo: Path | None = None, *, ontology: str | None = None) -> FastMCP:
    """The server: one tool per subcommand of the CLI parser (`argparse-mcp`), each running `ogy.cli.run` in this process."""
    top = cli.parser()
    server = FastMCP("ogy", instructions=top.description, strict_input_validation=repo is not None)

    def run(argv: Sequence[str]) -> cli.Result:
        return _run(argv) if repo is None else _pinned_run(repo, ontology, argv)

    for tool in tools_from_parser(top, run, usage=cli.USAGE):
        if tool.name == "reply":  # the round is named over MCP: a bare reply would resolve against whichever round is newest
            tool.parameters["required"] = [*tool.parameters.get("required", []), "round"]
        if tool.name not in NO_TOOL:
            if isinstance(tool, FunctionTool):
                tool.fn = _guarded(tool.fn, pinned=repo is not None)
            if repo is not None:
                for field in HTTP_FORBIDDEN:
                    tool.parameters["properties"].pop(field, None)
                if "required" in tool.parameters:
                    tool.parameters["required"] = [name for name in tool.parameters["required"] if name not in HTTP_FORBIDDEN]
            tool.annotations = annotations(tool.name)
            server.add_tool(tool)
    return server


def main() -> None:
    build().run("stdio")
