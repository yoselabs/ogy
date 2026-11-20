"""`python -m ogy`: the knowledge-base commands, printed for people (the CLI) and for agents (`ogy mcp`). A thin parser over `ogy.ops`."""

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from ogy import config, ops
from ogy.commands import HANDLERS, Result
from ogy.find import STATES
from ogy.init import doctor
from ogy.ontology import DEFAULT_ONTOLOGY
from ogy.target import Target
from ogy.verdict import RefusalError, Verdict

__all__ = ["FINDINGS", "NOT_FOUND", "OK", "REFUSED", "USAGE", "Result", "main", "parser", "run", "target_of"]

OK, FINDINGS, USAGE, REFUSED, NOT_FOUND = Verdict.OK, Verdict.FINDINGS, Verdict.USAGE, Verdict.REFUSED, Verdict.NOT_FOUND
ADDRESS = "<layer>/<area>/<kind>/<id>[/<part kind>/<key>...]"
WHERE = "a uri of a scheme the answer kind accepts (`ogy kinds <answer kind>` lists them), e.g. ai:claude/<session-id>"
AT = "ISO 8601 with a UTC offset (default: now)"
SAID = "one short line: your paraphrase of what the person said, plain and fitted to the decision; never their words verbatim"
type Adder = Callable[..., argparse.ArgumentParser]  # `add_subparsers().add_parser`
UNSET = argparse.SUPPRESS  # in a command, a global flag the person did not give leaves the one before the command alone


def _globals(command: argparse.ArgumentParser, default: object) -> None:
    command.add_argument(
        "--repo", type=Path, default=Path.cwd() if default is None else default, help="the Git repository (default: the current folder)"
    )
    command.add_argument(
        "--rev",
        default=default,
        help="a commit, or . for the worktree (default: ogy.yml, else . so a read sees what was "
        "just written). Writes always change the worktree",
    )
    command.add_argument(
        "--ontology",
        default=default,
        help=f"the ontology folder in ogy/ontologies, or a folder path holding a / (relative to the repository; default: "
        f"ogy.yml, else {DEFAULT_ONTOLOGY})",
    )


def _verb(commands: Adder, name: str, about: str, detail: str = "") -> argparse.ArgumentParser:
    """A command: `about` is its line in the list; with `detail` it is the command's description (the MCP tool's)."""
    command = commands(name, help=about, description=f"{about}. {detail}" if detail else about)
    _globals(command, UNSET)
    return command


def _reads(commands: Adder) -> None:
    checking = _verb(
        commands, "check", "the problems of the knowledge base", "Exit 1 when there are any. Takes a layer or an area to check only it."
    )
    checking.add_argument("area", nargs="?", help="only this layer (product, software), <layer>/<area>, or an area in every layer")
    checking.add_argument("--base", help="the commit the entries are checked against (default: merge base with main)")
    checking.add_argument("--landing", action="store_true", help="also report what blocks a land only (proposed terms)")
    standing = _verb(
        commands,
        "status",
        "the standing of an area or of everything in one screen",
        "Counts per area, findings, work left and dropped. Saves nothing.",
    )
    standing.add_argument("area", nargs="?", help="only this layer (product, software), <layer>/<area>, or an area in every layer")
    standing.add_argument("--coverage", action="store_true", help="also, per layer, the kinds that have no entry")
    _verb(
        commands,
        "show",
        "one entry: its fields, links, parts, status, decision, sources and built line",
        "Also the entry's parents, what links to it and what it links to. For an address a decision said no to, that.",
    ).add_argument("address", help=ADDRESS)
    finding = _verb(
        commands,
        "find",
        "search live and removed entries (a table)",
        "Entries whose address or sentence hold every word, over live and removed entries, narrowed by the options.",
    )
    finding.add_argument("words", nargs="*", help="words the address or the sentence holds, all of them")
    finding.add_argument("--kind", help="only this kind of entry (see `kinds`)")
    finding.add_argument("--area", help="only this area")
    finding.add_argument("--state", choices=[*STATES.values(), "removed"], help="only this state of its sentence")
    finding.add_argument("--removed", action="store_true", help="only removed entries (same as --state removed)")
    finding.add_argument("--parent", help="only the parts of this address, live and removed")
    finding.add_argument("--cites", help="only the entries that link to this address (the ones that cite a principle)")
    _verb(
        commands,
        "anchors",
        "the GitHub anchors of a Markdown file",
        "Every heading's anchor, which is what `doc:<commit>:<file>#<anchor>` may name.",
    ).add_argument("file", help="a Markdown file of the repository")
    for name, about in (("impact", "what a change reaches and what reaches it"), ("diagram", "the flow of a workflow as Mermaid")):
        _verb(commands, name, about).add_argument("address", help=ADDRESS)
    between = _verb(commands, "diff", "the entries changed between two commits or the worktree")
    between.add_argument("before", help="a commit, or . for the worktree")
    between.add_argument("after", help="a commit, or . for the worktree")
    past = _verb(commands, "history", "what changed, who said so, what is in force; computed from Git")
    past.add_argument("address", help="an address or an area")
    past.add_argument("--limit", type=int, default=100, help="how many commits to read")


def _asks(commands: Adder) -> None:
    _verb(
        commands, "work", "what is built against the entries and what is left", "Exit 1 when work is left. Takes a layer or an area."
    ).add_argument("area", nargs="?", help="only this layer (product, software), <layer>/<area>, or an area in every layer")
    _verb(
        commands,
        "glossary",
        "the constitution, then the terms of the product, with what they say",
        "Agents read this first: every principle of the constitution, whole, then the shared terms of each layer, then the terms "
        "of each area. For one area, its terms and the shared ones it reads.",
    ).add_argument(
        "area", nargs="?", help="only this area, <layer>/<area>, with the shared terms of its layer (and, in software, of product)"
    )
    kinds = _verb(
        commands,
        "kinds",
        "the kinds of the ontology, or one",
        "What each kind is, how to decide when to use it "
        "(guidance), what it holds, links to and requires. Read `ogy kinds <kind>` before creating an entry of that kind.",
    )
    kinds.add_argument("kind", nargs="?", help="only this kind")
    kinds.add_argument(
        "--readers",
        action="store_true",
        help="for each field, what reads it: the fingerprint, requires, flow, "
        "settling, links and impact, a named check or printer; or nothing",
    )
    kinds.add_argument(
        "--map",
        action="store_true",
        help="the whole ontology as an indented tree, one line per kind grouped by "
        "layer (! required, -> one link, ->> many links, [] a list part, indentation = part of), then its rules",
    )
    asking = _verb(
        commands,
        "review",
        "what you are asked: at most 7 cards, with a count per area",
        "SAVES the round (its id is printed) that `reply --round` resolves against.",
    )
    asking.add_argument("area", nargs="?", help="only this layer (product, software), <layer>/<area>, or an area in every layer")
    asking.add_argument("--all", action="store_true", help="every card, not the first 7")
    asking.add_argument(
        "--from",
        dest="source",
        choices=["docs", "code"],
        help="page through what nobody agreed to yet that came from documents (a section or the terms of an area per page) "
        "or from code (an area per page); `yes` agrees to the page",
    )
    asking.add_argument("--page", type=int, default=1, help="with --from: the page (default 1; agreed pages drop out)")
    asking.add_argument("--md", action="store_true", help="Markdown, to paste into a ticket")
    _verb(
        commands,
        "dropped",
        "what no person has seen",
        "Proposals that say no, removals with no why, proposals that differ from the answer.",
    )
    _verb(commands, "mcp", "serve the commands as MCP tools over stdio")


def _writes(commands: Adder) -> None:
    _verb(
        commands,
        "init",
        "set the repository up: ogy.yml, docs/kb, AGENTS.md, .mcp.json, deny rules",
        "Run again to repair. Not an MCP tool: a person runs it once.",
    ).add_argument("--check", action="store_true", help="the doctor: say what is not set up, write nothing (exit 1 when something is)")
    putting = _verb(
        commands,
        "put",
        "add or change entries: one or many records in one checked, atomic write",
        "A record is a mapping: `address` (or `kind`, `layer`, `area`, `id`) and the fields of the entry; an address that "
        "exists is changed (`field: null` removes a field), a new one is added. The records are JSON or YAML "
        "(a mapping, or an array of them), as arguments, from --file (- is standard input), or both. The batch is "
        "checked together: a decision and the entries its options set may come in one call. Nothing is written "
        "when any record is refused.",
    )
    putting.add_argument("records", nargs="*", metavar="records", help="a JSON or YAML mapping or array of mappings")
    putting.add_argument("--why", help="why the parts a record drops are removed: a decision address, or plain words")
    putting.add_argument("--file", help="a file of records (- for standard input)")
    removing = _verb(commands, "remove", "delete an entry and record it in its area's removed.yml", "Always changes the worktree.")
    removing.add_argument("address", help=ADDRESS)
    removing.add_argument(
        "--why",
        required=True,
        help="why it is removed: the address of the decision that said so, or plain "
        "words (an address stays required for an entry a person agreed to)",
    )
    removing.add_argument("--to", help="the address that replaces it")
    moving = _verb(
        commands,
        "move",
        "move an entry to another area or a new id, keeping its kind and agreements",
        "Moves the entry and what it owns, and writes the new address wherever the old one is named (links, "
        "answers, removed items); an agreement that was current stays current. Records nothing: Git keeps the move, and "
        "`check --base` tells it from a loss. One atomic write.",
    )
    moving.add_argument("address", help=ADDRESS)
    moving.add_argument(
        "area",
        help="the new area, <layer>/<area> when the layer changes too (the kind must allow it), or the full new address to rename it",
    )
    _verb(
        commands,
        "migrate",
        "rewrite the entries to the field renames, drops and folder moves their kinds declare",
        "A kind file keeps a renamed field's old name (`renamed: {old: new}`) and a dropped one (`dropped: [...]`); an entry that "
        "holds one is `needs-migration`. Renames every old name (in entries, list parts and `sets`) and keeps current the "
        "agreements and built lines it only renamed; a kind that absorbed several (`was: [...]`) takes their entries, refusing two "
        "of one area and id; removes dropped fields and prints each value removed, leaving that "
        "entry's agreement so the owner sees the change. A kind that moved out of a fixed folder (`moved_from`) has its entries "
        "and removed items there moved to the area shared of its first layer, every address renamed; `move` each to the area "
        "that uses it. Records nothing. One atomic write.",
    )


def _answers(commands: Adder) -> None:
    answering = _verb(
        commands,
        "answer",
        "choose an option of a decision, with a short paraphrase of what the person said",
        "ogy keeps no message and no quote: the answer is `chose`, `said` (one short line, your paraphrase of what the "
        "person said, fitted to the decision), `from` (human, or ai with --delegated), `at` and `where`. It applies "
        "the option's sets and agrees to no sentence: only a review round's yes does. Show the paraphrase to the person "
        "in the read-back.",
    )
    answering.add_argument("decision", help="the decision's address")
    answering.add_argument("option", help="the key of the option chosen")
    answering.add_argument("--said", required=True, help=SAID)
    answering.add_argument("--where", required=True, help=WHERE)
    answering.add_argument("--at", help=AT)
    answering.add_argument("--note", help="the person's hedge or condition, paraphrased (`for now`, `on condition that ...`)")
    answering.add_argument(
        "--delegated", help="an agent answers: the decision whose answer, a person's, let it decide this; without it a person answered"
    )
    replying = _verb(
        commands,
        "reply",
        "apply the owner's reply to a review round",
        "Grammar: yes, yes all or decide (every recommendation), yes 1 3, 2: sentence, no 4, Q1 b, later. "
        "The text is the grammar line: the owner's, or your reading of their natural words. ogy keeps no message "
        "and no quote: --said is one short line, your paraphrase of what the owner said, kept with --at and --where "
        "on every answer and agreement written (`from: human`). Nothing is written when nothing applies.",
    )
    replying.add_argument("text", help="the reply as a grammar line (`yes`, `yes 1 3`, `Q1 b`)")
    replying.add_argument("--said", required=True, help=SAID)
    replying.add_argument("--where", required=True, help=WHERE)
    replying.add_argument("--at", help=AT)
    replying.add_argument("--note", help="the owner's hedge or condition, paraphrased (`for now`), on the answers written")
    replying.add_argument(
        "--round", help="the round id `review` printed (default on the CLI: the newest round of this knowledge base; required over MCP)"
    )


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(
        prog="ogy",
        description="A requirements knowledge base kept in Git. The flags --repo --rev --ontology go before or after the command.",
    )
    _globals(top, None)
    add = top.add_subparsers(dest="command", required=True, metavar="command").add_parser
    _reads(add)
    _asks(add)
    _writes(add)
    _answers(add)
    return top


def _first(*values: str | None) -> str:
    return next(value for value in values if value is not None)


def target_of(args: argparse.Namespace) -> Target:
    """The flags over `ogy.yml` over the built-in defaults."""
    settings = config.read(args.repo)
    return Target(args.repo, rev=_first(args.rev, settings.rev, "."), ontology=_first(args.ontology, settings.ontology, DEFAULT_ONTOLOGY))


def dispatch(args: argparse.Namespace, *, agent: bool, serve: Callable[[], None] | None = None) -> Result:
    if args.command == "mcp":
        if serve is None:
            return USAGE, ["the MCP server starts from the console entry: run `ogy mcp`"]
        serve()
        return OK, []
    if args.command == "init" and args.check:
        problems = doctor(args.repo)
        return (FINDINGS if problems else OK), problems or ["ogy is set up here"]
    if args.command == "init":
        done = ops.run_init(args.repo, args.ontology)
        return done.verdict, [
            f"ogy is set up for the {done.value.ontology} ontology in {done.value.kb}/",
            *(f"wrote {path}" for path in done.value.written),
        ]
    return HANDLERS[args.command](target_of(args), args, agent=agent)


def run(argv: Sequence[str], *, agent: bool = False, serve: Callable[[], None] | None = None) -> Result:
    """Run one command; `agent` prints tables and records (over MCP) instead of lines for a person.

    `serve` starts the MCP server for `ogy mcp`: the entry point above this module passes it, so this module never imports the server."""
    try:
        return dispatch(parser().parse_args(argv), agent=agent, serve=serve)
    except RefusalError as error:
        return error.verdict, error.lines()


def main(argv: Sequence[str] | None = None, *, serve: Callable[[], None] | None = None) -> int:
    code, lines = run(sys.argv[1:] if argv is None else argv, serve=serve)
    if lines:
        print("\n".join(lines), file=sys.stderr if code >= USAGE else sys.stdout)
    return code
