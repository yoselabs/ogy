"""`ogy find`: live and removed entries by words, kind, area, state or parent. A table of what is there."""

from collections.abc import Iterable
from dataclasses import dataclass

from ogy import removed
from ogy.graph import incoming
from ogy.model import Address, area_of
from ogy.near import hint
from ogy.settle import decisions
from ogy.snapshot import Snapshot
from ogy.status import Status, agreed_hashes, status
from ogy.verdict import NotFound

SENTENCE = ("says", "question", "label", "word", "title")
REMOVED = "removed"
STATES = {Status.QUESTION: "question", Status.CHANGED: "changed", Status.BY_YOU: "you", Status.NOBODY: "nobody"}


@dataclass(frozen=True)
class Found:
    """One row: a live entry (its state is the status of its sentence) or a removed one (state `removed`)."""

    address: str
    kind: str
    state: str
    says: str
    note: str = ""  # a removed entry's why and replacement


def _live(snapshot: Snapshot, parent: str | None, cites: Address | None) -> list[Found]:
    hashes = agreed_hashes(snapshot)
    asked = {item.address: item for item in decisions(snapshot)}
    rows: list[Found] = []
    citing = {edge.address for edge in incoming(snapshot)[cites] if edge.field != "of"} if cites is not None else set()
    for address, entry in sorted(snapshot.entries.items()):
        if cites is not None and address not in citing:
            continue
        if parent is not None and str(address.parent()) != parent:
            continue
        says = next((text for name in SENTENCE if (text := entry.text(name))), "")
        if address in asked:
            state = "question" if not asked[address].answers else "you"
        else:
            state = STATES[status(snapshot, address, hashes)] if "says" in snapshot.kind_of(address).fields else ""
        rows.append(Found(str(address), address.kind, state, says))
    return rows


def _gone(items: Iterable[removed.Item], parent: str | None) -> list[Found]:
    return [Found(item.id, item.kind, REMOVED, item.said or item.title or "",
                  f"why: {item.why or 'none'}; replaced by: {item.replaced_by or 'nothing'}") for item in removed.search(items, (), parent)]


def find(snapshot: Snapshot, items: Iterable[removed.Item], words: list[str], kind: str | None, area: str | None, state: str | None,
         parent: str | None, cites: Address | None = None) -> list[Found]:
    """Rows whose address or sentence hold every word, narrowed by kind, area, state and parent (live children and removed parts)."""
    if kind is not None and kind not in snapshot.ontology.kinds:
        raise NotFound(f"no kind {kind}" + hint(kind, snapshot.ontology.kinds))
    rows = [*_live(snapshot, parent, cites), *([] if cites else _gone(items, parent))]
    needles = [word.casefold() for word in words]
    return [row for row in rows if all(word in f"{row.address} {row.says}".casefold() for word in needles)
            and kind in (None, row.kind) and area in (None, area_of(row.address, snapshot.ontology)) and state in (None, row.state)]
