"""What each command runs and prints: one `ogy.ops` call, then lines for a person or, with `wire`, a table or record for an agent."""

import sys
from pathlib import Path
from typing import Protocol
lazy import argparse

from ogy import ops, put, render, wire
from ogy.model import home_of
from ogy.workcause import grouped
lazy from ogy.target import Target

type Result = tuple[int, list[str]]


class Handler(Protocol):
    """One command: what it runs and prints; `agent` asks for tables and records instead of lines for a person."""

    def __call__(self, target: Target, args: argparse.Namespace, /, *, agent: bool) -> Result: ...


def _check(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_check(target, args.base, landing=args.landing, area=args.area)
    if agent:  # a table stays a table; `status` carries the count
        return done.verdict, wire.findings(done.value)
    return done.verdict, [*render.render_findings(done.value), *render.waiting_line(ops.run_waiting(target, args.area))]


def _hook(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_hook(target, args.name, sys.stdin.read() if args.name == "pre-push" else "")
    lines: list[str] = []
    for update, found in done.value:
        lines += [f"{'land' if update.land else 'check'} {update.ref} at {update.rev[:12]}", *render.render_findings(found)]
    return done.verdict, lines


def _status(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_status(target, args.area, with_coverage=args.coverage)
    return done.verdict, wire.status(done.value) if agent else render.render_status(done.value)


def _show(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_show(target, args.address)
    return done.verdict, wire.show(done.value) if agent else render.render_show(done.value)


def _find(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_find(
        target, args.words, args.kind, args.area, state="removed" if args.removed else args.state, parent=args.parent, cites=args.cites
    )
    return done.verdict, wire.entries(done.value) if agent else render.render_found(done.value)


def _anchors(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_anchors(target, args.file)
    return done.verdict, wire.anchors(done.value) if agent else render.render_anchors(done.value)


def _impact(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_impact(target, args.address)
    return done.verdict, wire.impact(done.value) if agent else render.render_impact(done.value)


def _diagram(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_diagram(target, args.address)
    return done.verdict, done.value


def _view(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_view(target, args.out)
    return done.verdict, [f"wrote {done.value}", f"open {done.value.resolve().as_uri()}"]


def _diff(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_diff(target, args.before, args.after)
    return done.verdict, wire.diff(done.value) if agent else render.render_diff(done.value)


def _work(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_work(target, args.area)
    if agent:  # the agents' table stays flat: the cause is for a person to read
        return done.verdict, wire.work(done.value)
    return done.verdict, render.render_work(done.value, grouped(target.read()[1], done.value))


def _review(target: Target, args: argparse.Namespace, **_: object) -> Result:
    asked = ops.run_review(target, everything=args.all, area=args.area, source_of=args.source, page=args.page)
    return asked.verdict, render.render_review_md(asked.value) if args.md else render.render_review(asked.value)


def _dropped(target: Target, _: argparse.Namespace, *, agent: bool) -> Result:
    done = ops.run_dropped(target)
    return done.verdict, wire.dropped(done.value) if agent else render.render_dropped(done.value)


def _glossary(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_glossary(target, args.area)
    return done.verdict, done.value or ["no terms"]


def _history(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_history(target, args.address, args.limit)
    return done.verdict, render.render_history(done.value)


def _kinds(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_kinds(target, args.kind, with_readers=args.readers, as_map=args.map)
    return done.verdict, done.value


def _remove(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_remove(target, args.address, args.why, args.to)
    item = done.value.item
    if not done.value.recorded:
        return done.verdict, [f"removed {item.id} (fingerprint {item.hash}); not recorded: the base never had it (Git keeps it)"]
    return done.verdict, [f"removed {item.id} (fingerprint {item.hash}); recorded in {home_of(item.id, target.kinds())}/removed.yml"]


def _move(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_move(target, args.address, args.area)
    return done.verdict, [str(done.value)]


def _migrate(target: Target, _: argparse.Namespace, **__: object) -> Result:
    done = ops.run_migrate(target)
    return done.verdict, done.value.lines()


def _put(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    if args.file == "-" and agent:  # over MCP stdin is the protocol, not the caller's text
        raise ops.WriteRefusedError(["--file - reads standard input, which an MCP tool cannot: pass the records"])
    texts = [*args.records, *([sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")] if args.file else [])]
    done = ops.run_put(target, put.read_records(texts), args.why)
    return done.verdict, [str(item) for item in done.value]


def _answer(target: Target, args: argparse.Namespace, **_: object) -> Result:
    done = ops.run_answer(target, args.decision, args.option, args.said, args.where, at=args.at, note=args.note, delegated=args.delegated)
    return done.verdict, [
        f"{done.value.decision}: answered {done.value.option}",
        *(f"set {text}" for text in done.value.changed),
        *(f"removed {text}" for text in done.value.removed),
    ]


def _reply(target: Target, args: argparse.Namespace, *, agent: bool) -> Result:
    if agent and args.round is None:  # an agent names the round it means; only a person at a terminal may take the newest
        raise ops.WriteRefusedError(["name the round: --round <id> (the id is printed by `review`)"])
    done = ops.run_reply(target, args.text, args.said, args.where, at=args.at, round_id=args.round, note=args.note)
    return done.verdict, [*done.value.applied, *(f"refused {line}" for line in done.value.refused)]


HANDLERS: dict[str, Handler] = {
    "check": _check,
    "hook": _hook,
    "anchors": _anchors,
    "status": _status,
    "show": _show,
    "find": _find,
    "impact": _impact,
    "diagram": _diagram,
    "view": _view,
    "diff": _diff,
    "work": _work,
    "review": _review,
    "dropped": _dropped,
    "glossary": _glossary,
    "history": _history,
    "kinds": _kinds,
    "remove": _remove,
    "move": _move,
    "migrate": _migrate,
    "put": _put,
    "answer": _answer,
    "reply": _reply,
}
