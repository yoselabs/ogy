"""Checks against the base commit (C2, C3, R1, R3): what Git history says may not change.

`ogy.ledgers` reads the merge base through the source helpers and calls it, when a base is given.

Entries and their `removed.yml` ledgers are the only inputs; nothing is read from Git here. A move is no removal and has
no record: the entities that moved between the two commits are found by `moves.detect` (and those whose kind the ontology
renamed by `moves.retyped`), and the base is compared with those addresses written in. Anything else gone since the base
needs the item of a decided removal.
"""

import dataclasses
from typing import TYPE_CHECKING

from ogy import removed
from ogy.kinds import Holds
from ogy.layout import REMOVED_FILE
from ogy.model import Address, Entry, Finding, Problem, parse_address
from ogy.moves import detect, renamed, retyped
lazy from ogy.snapshot import Snapshot
lazy from ogy.source import Source

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from ogy.removed import Item, Ledger


def read_ledgers(source: Source) -> tuple[dict[str, Ledger], list[removed.Problem]]:
    """The `removed.yml` of every home in one source: the ledgers by home and the R4 problems of the ones that do not read."""
    paths = [path for path in source.listing() if path.count("/") in (1, 2) and path.endswith("/" + REMOVED_FILE)]
    return removed.parse(source.read(paths))


def check_base(
    current: Snapshot, base: Snapshot, ledgers: Mapping[str, Ledger] | None = None, base_ledgers: Mapping[str, Ledger] | None = None
) -> list[Finding]:
    """Everything the base forbids changing: append-only parts (C2) other than by a move, ids gone without a ledger item and
    not moved (C3, R1), and edited ledgers (R3)."""
    now, before = ledgers or {}, base_ledgers or {}
    shifted = renamed(base, {**retyped(base, current), **detect(base, current)})
    found = _kept(current, shifted)
    live = {str(address) for address in current.entries}
    gone = {str(address): entry for address, entry in shifted.entries.items() if str(address) not in live}
    items = [item for ledger in now.values() for item in ledger.items]
    for problem in removed.check_unrecorded(gone, live, items):
        entry = gone[problem.address]
        found.append(Finding(Problem.REMOVED_UNRECORDED, entry.path, problem.detail, entry.address))
    for home, old in sorted(before.items()):
        for problem in removed.check_append_only(old, now.get(home), home, _same(current)):
            found.append(Finding(Problem.EDITED_APPEND_ONLY, f"{home}/{REMOVED_FILE}", problem.detail))
    return found


def _same(current: Snapshot) -> Callable[[Item, Item], bool]:
    """R3's equality: an item may change only where its `why` or `replaced_by` follows a move (same kinds and ids, the old
    address gone, the new one live)."""

    def follows(old: str | None, new: str | None) -> bool:
        before = parse_address(old, current.ontology) if old else None
        after = parse_address(new, current.ontology) if new else None
        return (
            before is not None
            and after is not None
            and before.path == after.path
            and after in current.entries
            and before not in current.entries
        )

    def same(old: Item, new: Item) -> bool:
        why = new.why if follows(old.why, new.why) else old.why
        to = new.replaced_by if follows(old.replaced_by, new.replaced_by) else old.replaced_by
        return dataclasses.replace(old, why=why, replaced_by=to) == new

    return same


def _kept(current: Snapshot, base: Snapshot) -> list[Finding]:
    """C2 for the addresses in both snapshots (`base` with the moves written in)."""
    found: list[Finding] = []
    for address, old in base.entries.items():
        entry = current.entries.get(address)
        if entry is None or current.ontology.get(address.kind) is None:
            continue
        for part in current.ontology.parts_of(address.kind):
            if part.append_only and part.holding is Holds.LIST:
                found.extend(_appended(entry.address, entry, old, part.key or ""))
    return found


def _appended(address: Address, entry: Entry, old: Entry, key: str) -> list[Finding]:
    before, after = old.fields.get(key), entry.fields.get(key)
    was: list[object] = before if isinstance(before, list) else []
    now: list[object] = after if isinstance(after, list) else []
    for place, item in enumerate(was):
        if place >= len(now) or now[place] != item:
            what = "removed" if place >= len(now) else "changed"
            return [Finding(Problem.EDITED_APPEND_ONLY, entry.path, f"{key} item {place} was {what}; only add after it", address)]
    return []
