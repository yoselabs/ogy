"""Standing facts formatted from the operations that own the CLI's computed values."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ogy import ops
from ogy.settle import decisions
from ogy.status import Status, status

if TYPE_CHECKING:
    from ogy.inspect import Document
    from ogy.target import Target


def standing(target: Target) -> Document:
    """Return computed standing; the locked API read attaches its inspection version."""
    overview = ops.run_status(target, None, with_coverage=False).value
    work = ops.run_work(target, None).value
    dropped = ops.run_dropped(target).value
    snapshot = target.read()[1]
    rows = {}
    for decision in decisions(snapshot):
        newest = decision.newest
        rows[str(decision.address)] = {
            "status": "waiting" if status(snapshot, decision.address) is Status.QUESTION else "answered",
            "chose": str(decision.address.part(decision.names.option, newest.chose)) if newest else None,
            "at": newest.at.isoformat() if newest and newest.at else None,
            "delegated": str(newest.delegated) if newest and newest.delegated else None,
        }
    groups = (
        ("proposal says no, nobody has seen it", dropped.proposed_no),
        ("removed with no why", dropped.unexplained),
        ("removed with plain words", dropped.plain_why),
        ("answer with a note", dropped.noted),
        ("answer given under a delegation", dropped.delegated),
    )
    return {
        "totals": {
            "waiting": sum(h.questions for h in overview.areas),
            "owed": len(work),
            "unagreed": sum(h.ai for h in overview.areas),
            "changed": sum(h.changed for h in overview.areas),
            "dropped": len(dropped),
            "findings": overview.findings,
        },
        "areas": {
            h.area: {name: getattr(h, name) for name in ("questions", "answered", "ai", "docs", "code", "you", "changed")}
            for h in overview.areas
        },
        "decisions": rows,
        "entries": {
            address: {"source": source, "changed": changed} for h in overview.areas for address, (source, changed) in h.entries.items()
        },
        "work": [{"address": w.address, "cause": str(w.status), "text": w.note} for w in work],
        "dropped": [{"address": str(address), "text": text} for text, group in groups for address in group],
        "computed": True,
    }
