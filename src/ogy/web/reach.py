"""What each decision option reaches: the `ogy impact` of every entry the option sets, on the current knowledge base."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ogy.graph import closure, incoming, links_of
from ogy.settle import decisions, resolve

if TYPE_CHECKING:
    from ogy.model import Address
    from ogy.snapshot import Snapshot

LIMIT = 50


def reach(snapshot: Snapshot) -> dict[str, dict[str, dict[str, object]]]:
    """decision address -> option address -> {sets, reach, count, truncated}.

    `sets`: the existing entries the option sets. `reach`: the union of what each one reaches and what reaches it (the two
    lists `ogy impact` prints), without the set entries themselves, sorted, at most `LIMIT`; `count` is the full number.
    An option that sets nothing, or only entries that do not exist yet, has `sets: []` and `reach: []`.
    """
    back = incoming(snapshot)
    out: dict[str, dict[str, dict[str, object]]] = {}
    for decision in decisions(snapshot):
        options: dict[str, dict[str, object]] = {}
        for key, sets in decision.options.items():
            targets = sorted({found for text in sets if (found := resolve(snapshot, decision.address, text, decision.address.kind))})
            touched: set[Address] = set()
            for target in targets:
                touched |= closure(target, lambda at: (edge.address for edge in links_of(snapshot, at)))
                touched |= closure(target, lambda at: (edge.address for edge in back[at]))
            found = sorted(str(a) for a in touched - set(targets))
            options[str(decision.address.part(decision.names.option, key))] = {
                "sets": [str(a) for a in targets],
                "reach": found[:LIMIT],
                "count": len(found),
                "truncated": len(found) > LIMIT,
            }
        out[str(decision.address)] = options
    return out
