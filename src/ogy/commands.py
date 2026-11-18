"""What each command runs and prints: one `ogy.ops` call, then lines for a person or, with `wire`, a table or record for an agent."""

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from ogy import ops, put, render, wire
from ogy.target import Target

type Result = tuple[int, list[str]]
type Handler = Callable[[Target, argparse.Namespace, bool], Result]


def _check(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_check(target, args.base, args.landing, args.area)
    if agent:  # a table stays a table; `status` carries the count
        return done.verdict, wire.findings(done.value)
    return done.verdict, [*render.render_findings(done.value), *render.waiting_line(ops.run_waiting(target, args.area))]


def _status(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_status(target, args.area, args.coverage)
    return done.verdict, wire.status(done.value) if agent else render.render_status(done.value)


def _show(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_show(target, args.address)
    return done.verdict, wire.show(done.value) if agent else render.render_show(done.value)


def _find(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_find(target, args.words, args.kind, args.area, "removed" if args.removed else args.state, args.parent, args.cites)
    return done.verdict, wire.entries(done.value) if agent else render.render_found(done.value)


def _anchors(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_anchors(target, args.file)
    return done.verdict, wire.anchors(done.value) if agent else render.render_anchors(done.value)


def _impact(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_impact(target, args.address)
    return done.verdict, wire.impact(done.value) if agent else render.render_impact(done.value)


def _diagram(target: Target, args: argparse.Namespace, _: bool) -> Result:
    done = ops.run_diagram(target, args.address)
    return done.verdict, done.value


def _diff(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_diff(target, args.before, args.after)
    return done.verdict, wire.diff(done.value) if agent else render.render_diff(done.value)


def _work(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_work(target, args.area)
    return done.verdict, wire.work(done.value) if agent else render.render_work(done.value)


def _review(target: Target, args: argparse.Namespace, _: bool) -> Result:
    asked = ops.run_review(target, args.all, args.area, args.source, args.page)
    return asked.verdict, render.render_review_md(asked.value) if args.md else render.render_review(asked.value)


def _dropped(target: Target, _: argparse.Namespace, agent: bool) -> Result:
    done = ops.run_dropped(target)
    return done.verdict, wire.dropped(done.value) if agent else render.render_dropped(done.value)


def _glossary(target: Target, _: argparse.Namespace, __: bool) -> Result:
    done = ops.run_glossary(target)
    return done.verdict, done.value or ["no terms"]


def _history(target: Target, args: argparse.Namespace, _: bool) -> Result:
    done = ops.run_history(target, args.address, args.limit)
    return done.verdict, render.render_history(done.value)


def _kinds(target: Target, args: argparse.Namespace, _: bool) -> Result:
    done = ops.run_kinds(target, args.kind)
    return done.verdict, done.value


def _remove(target: Target, args: argparse.Namespace, _: bool) -> Result:
    done = ops.run_remove(target, args.address, args.why, args.to)
    return done.verdict, [f"removed {done.value.id} (fingerprint {done.value.hash}); recorded in {done.value.id.split('/')[0]}/removed.yml"]


def _move(target: Target, args: argparse.Namespace, _: bool) -> Result:
    done = ops.run_move(target, args.address, args.area)
    return done.verdict, [str(done.value)]


def _put(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    if args.file == "-" and agent:  # over MCP stdin is the protocol, not the caller's text
        raise ops.WriteRefused(["--file - reads standard input, which an MCP tool cannot: pass the records"])
    texts = [*args.records, *([sys.stdin.read() if args.file == "-" else Path(args.file).read_text()] if args.file else [])]
    done = ops.run_put(target, put.read_records(texts))
    return done.verdict, [str(item) for item in done.value]


def _answer(target: Target, args: argparse.Namespace, _: bool) -> Result:
    done = ops.run_answer(target, args.decision, args.option, args.said, args.where, args.at, args.who, args.note, args.delegated)
    return done.verdict, [f"{done.value.decision}: answered {done.value.option}", *(f"set {text}" for text in done.value.changed),
                          *(f"removed {text}" for text in done.value.removed)]


def _reply(target: Target, args: argparse.Namespace, agent: bool) -> Result:
    if agent and args.round is None:  # an agent names the round it means; only a person at a terminal may take the newest
        raise ops.WriteRefused(["name the round: --round <id> (the id is printed by `review`)"])
    done = ops.run_reply(target, args.text, args.said, args.where, args.at, args.round, note=args.note)
    return done.verdict, [*done.value.applied, *(f"refused {line}" for line in done.value.refused)]


HANDLERS: dict[str, Handler] = {
    "check": _check, "anchors": _anchors, "status": _status, "show": _show, "find": _find, "impact": _impact, "diagram": _diagram,
    "diff": _diff, "work": _work, "review": _review, "dropped": _dropped, "glossary": _glossary, "history": _history, "kinds": _kinds,
    "remove": _remove, "move": _move, "put": _put, "answer": _answer, "reply": _reply,
}
