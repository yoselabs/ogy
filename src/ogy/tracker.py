"""The work left as items a tracker can hold (decision software/cli/decision/work-to-tracker, answered print-and-runner;
decision software/ontology/decision/delivery-record, answered tracker-names-the-entry).

One item per address in the work left: its key is the address (permanent), its fingerprint the entry's fingerprint now (empty for
an address whose entry is gone), its brief what `ogy work <address>` prints. ogy talks to no tracker: a runner outside ogy reads
these items and creates, rewrites or closes the tracker's own. Computed, never stored.
"""

import json
from dataclasses import asdict, dataclass

from ogy.brief import brief, rows, sentence
from ogy.render import render_brief
lazy from ogy.built import Line
lazy from ogy.receipts import Work
lazy from ogy.snapshot import Snapshot

__all__ = ["Item", "items", "items_json"]


@dataclass(frozen=True)
class Item:
    key: str
    title: str
    statuses: tuple[str, ...]
    fingerprint: str
    brief: str


def items(snapshot: Snapshot, work: list[Work], record: dict[str, Line]) -> list[Item]:
    by_address: dict[str, list[Work]] = {}
    for row in work:
        by_address.setdefault(row.address, []).append(row)
    found = []
    for text, rows_of in sorted(by_address.items()):
        statuses = tuple(dict.fromkeys(str(row.status) for row in rows_of))
        address = snapshot.resolve(text)
        if address is None or address not in snapshot.entries:  # removal work: the entry is gone, its line is not
            note = "; ".join(row.note for row in rows_of if row.note)
            found.append(Item(text, f"{', '.join(statuses)}: {text}", statuses, "", note))
            continue
        says = sentence(snapshot, address)
        text_brief = "\n".join(render_brief(rows(snapshot, brief(snapshot, address, work, record))))
        title = f"{', '.join(statuses)}: {text}" + (f" ({says[:80]})" if says else "")
        found.append(Item(text, title, statuses, snapshot.fingerprint(address), text_brief))
    return found


def items_json(found: list[Item]) -> list[str]:
    """The items as one JSON array, for a runner to read."""
    return [json.dumps([asdict(item) for item in found], indent=1)]
