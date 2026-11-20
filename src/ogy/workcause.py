"""`ogy work` for a person, grouped by cause: the decision that set the entry (or one of its parents), then what its flow
realizes (the container's `flow.group` link). Display only: nothing routes on it, and the agents' table stays flat."""

lazy from collections.abc import Iterable

from ogy.receipts import Work
from ogy.settle import Decision, decision_of, decisions
lazy from ogy.model import Address
lazy from ogy.snapshot import Snapshot

type Group = tuple[str, str, list[Work]]  # decision, what the flow realizes ("" for none), the work under them


def _lineage(address: Address) -> Iterable[Address]:
    at: Address | None = address
    while at is not None:
        yield at
        at = at.parent()


def _decision(found: list[Decision], address: Address) -> str:
    return next((str(decision.address) for at in _lineage(address) if (decision := decision_of(found, at)) is not None), "")


def _realized(snapshot: Snapshot, address: Address) -> str:
    top = list(_lineage(address))[-1]
    flow = snapshot.kind_of(top).flow if top in snapshot.entries else None
    targets: list[Address] = sorted(snapshot.links.forward(top, flow.group)) if flow is not None and flow.group is not None else []
    return str(targets[0]) if targets else ""


def grouped(snapshot: Snapshot, work: list[Work]) -> list[Group]:
    """The work by cause, decisions in address order and work with no decision last; within each, by what is realized."""
    found, groups = decisions(snapshot), dict[tuple[str, str], list[Work]]()
    for item in work:
        address = snapshot.resolve(item.address)
        key = (_decision(found, address), _realized(snapshot, address)) if address is not None else ("", "")
        groups.setdefault(key, []).append(item)
    return [
        (decision, realized, items)
        for (decision, realized), items in sorted(
            groups.items(), key=lambda pair: (pair[0][0] == "", pair[0][0], pair[0][1] == "", pair[0][1])
        )
    ]
