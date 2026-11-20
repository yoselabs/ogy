"""Lints that keep one home per fact and no stored state: the built record's shape (S4), one sentence once (H3), and no
cycle along an acyclic link field.

Stored-state and `?` keys in entries (S2, S3) are found where fields are read, in `fieldtypes`."""

from ogy import built
from ogy.model import Address, Finding, Problem
from ogy.snapshot import Snapshot
from ogy.source import Source


def _twice(snapshot: Snapshot) -> list[Finding]:
    """H3: two top-level entries of one kind in one area with the same sentence (a kind a person agrees to entry by entry)."""
    seen: dict[tuple[str, str, str], str] = {}
    found: list[Finding] = []
    for address, entry in snapshot.entries.items():
        says = snapshot.sentence(address) if snapshot.ontology.carded(snapshot.kind_of(address)) else None
        if len(address.path) != 1 or says is None:
            continue
        key = (address.area, address.kind, " ".join(says.split()).lower())
        if key in seen:
            found.append(Finding(Problem.DUPLICATE_SAYS, entry.path, f"the same sentence as {seen[key]}", address))
        seen.setdefault(key, str(address))
    return found


def _leads_back(snapshot: Snapshot, start: Address, field: str) -> bool:
    """Following `field` from `start` comes back to it."""
    seen, todo = set[Address](), list(snapshot.links.forward(start, field))
    while todo:
        at = todo.pop()
        if at == start:
            return True
        if at not in seen:
            seen.add(at)
            todo += snapshot.links.forward(at, field)
    return False


def _cycles(snapshot: Snapshot) -> list[Finding]:
    """An entry a link field its kind declares `acyclic` leads back to, by that field: a card that includes itself."""
    found: list[Finding] = []
    for address, entry in snapshot.entries.items():
        for field in snapshot.kind_of(address).acyclic:
            if _leads_back(snapshot, address, field):
                found.append(Finding(Problem.LINK_CYCLE, entry.path, f"{field} leads back to this entry", address))
    return found


def check_lints(snapshot: Snapshot, source: Source) -> list[Finding]:
    return [*_twice(snapshot), *_cycles(snapshot), *built.read_source(source)[1]]
