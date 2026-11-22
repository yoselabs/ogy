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
from typing import Any, Literal, Protocol
lazy from collections.abc import Callable, Mapping, Sequence
lazy from pathlib import Path

from argparse_mcp import tools_from_parser
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.tools import FunctionTool
from fastmcp.tools.tool_transform import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field

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


class SpotlightTarget(BaseModel):
    """One entry the owner is pointed at, and the one sentence that says why."""

    model_config = ConfigDict(extra="forbid")
    address: str = Field(description="Full address of an existing entry or part, e.g. product/inspection/decision/some-question")
    says: str = Field(description="One plain sentence: why the owner should look at this entry now")


class SpotlightPort(Protocol):
    """What the board offers the spotlight and sketch tools; the web process owns it, the tools only call it."""

    def show(self, *, title: str, targets: Sequence[tuple[str, str]], session: str) -> dict[str, object]: ...
    def dismiss(self, *, session: str) -> dict[str, object]: ...
    def show_sketch(
        self, *, title: str, records: Sequence[Mapping[Any, Any]], decision: str | None, option: str | None, session: str
    ) -> dict[str, object]: ...
    def dismiss_sketch(self, *, session: str) -> dict[str, object]: ...


SPOTLIGHT_DESCRIPTION = (
    "Point the owner at entries on the open board. `show` takes a title and 1 to 12 ordered targets (address and one sentence each); "
    "the board numbers them, dims the rest and, when the owner is idle, opens the first one (when busy it asks instead). "
    "`dismiss` clears it. A new `show` replaces the previous one. The spotlight lives in memory only: it writes no entry, changes no "
    "inspection version, and is gone when the server stops. Use it to explain a decision or its consequences; "
    "it records no answer. Returns the call's sequence number; an unknown address is refused."
)


def _spotlight_tool(port: SpotlightPort) -> FunctionTool:
    def spotlight(
        action: Literal["show", "dismiss"],
        title: str = "",
        targets: list[SpotlightTarget] | None = None,
        session: str = "agent",
    ) -> dict[str, object]:
        try:
            if action == "dismiss":
                return port.dismiss(session=session)
            return port.show(title=title, targets=[(item.address, item.says) for item in targets or []], session=session)
        except RefusalError as error:
            raise ToolError("\n".join(error.lines())) from error

    hints = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    return FunctionTool.from_function(spotlight, name="spotlight", description=SPOTLIGHT_DESCRIPTION, annotations=hints)


SKETCH_DESCRIPTION = (
    "Show the owner what does not exist yet. `show` takes a title and 1 to 40 `records` in the `put` format (an `address` and the "
    "kind's fields; parents before their parts or in the same call); the board draws the new entries in the sketch treatment "
    "(dashed, hatched, labelled sketch, no status colours) with the flow renderer and lists what they would touch, from the impact "
    "operation. A record whose address, kind or fields `put` would refuse is refused with its reasons; the whole-knowledge-base "
    "checks of a write are not run, so a sketch may be unfinished. To offer Keep, name an existing `decision` and its `option` key; "
    "the owner then opens that option's answer form on the board; Keep writes nothing itself, and the answer is the owner's. "
    "`dismiss` clears the sketch. The sketch is applied to a throwaway copy: it writes no entry, changes no inspection "
    "version, and is gone when the server stops."
)


def _sketch_tool(port: SpotlightPort) -> FunctionTool:
    def sketch(
        action: Literal["show", "dismiss"],
        *,
        title: str = "",
        records: list[dict[str, Any]] | None = None,
        decision: str | None = None,
        option: str | None = None,
        session: str = "agent",
    ) -> dict[str, object]:
        try:
            if action == "dismiss":
                return port.dismiss_sketch(session=session)
            return port.show_sketch(title=title, records=records or [], decision=decision, option=option, session=session)
        except RefusalError as error:
            raise ToolError("\n".join(error.lines())) from error

    hints = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    return FunctionTool.from_function(sketch, name="sketch", description=SKETCH_DESCRIPTION, annotations=hints)


def build(repo: Path | None = None, *, ontology: str | None = None, spotlight: SpotlightPort | None = None) -> FastMCP:
    """The server: one tool per subcommand of the CLI parser (`argparse-mcp`), each running `ogy.cli.run` in this process.

    With a `spotlight` port (the board process has one) the `spotlight` and `sketch` tools are added; the stdio server has
    no board to point at."""
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
    if spotlight is not None:
        server.add_tool(_spotlight_tool(spotlight))
        server.add_tool(_sketch_tool(spotlight))
    return server


def main() -> None:
    build().run("stdio")
