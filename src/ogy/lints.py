"""Lints that keep one home per fact and no stored state: the built record's shape (S4) and one sentence once (H3).

Stored-state and `?` keys in entries (S2, S3) are found where fields are read, in `fieldtypes`."""

from ogy import built
from ogy.model import Finding, Problem
from ogy.snapshot import Snapshot
from ogy.source import Source


def _twice(snapshot: Snapshot) -> list[Finding]:
    """H3: two top-level entries of one kind in one area with the same `says`."""
    seen: dict[tuple[str, str, str], str] = {}
    found: list[Finding] = []
    for address, entry in snapshot.entries.items():
        says = entry.text("says")
        if len(address.path) != 1 or says is None:
            continue
        key = (address.area, address.kind, " ".join(says.split()).lower())
        if key in seen:
            found.append(Finding(Problem.DUPLICATE_SAYS, entry.path, f"the same sentence as {seen[key]}", address))
        seen.setdefault(key, str(address))
    return found


def check_lints(snapshot: Snapshot, source: Source) -> list[Finding]:
    return [*_twice(snapshot), *built.read_source(source)[1]]
