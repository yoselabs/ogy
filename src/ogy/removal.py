"""`ogy remove`: delete an entry or a part, and append its item (envelope and snapshot) to its area's removed ledger."""

import datetime
from collections.abc import Callable
from pathlib import Path

from ogy import removed
from ogy.edit import Editor
from ogy.kinds import Holds
from ogy.links import link_items, resolve
from ogy.model import Address, parse_address
from ogy.ontology import Ontology
from ogy.removed import Item, Parent
from ogy.settle import decisions
from ogy.snapshot import Snapshot
from ogy.verdict import Refusal

type Clock = Callable[[], datetime.datetime]


class RemoveRefused(Refusal):
    """The address cannot be removed now; `reasons` say why."""

    prefix = "not removed: "


def entry_snapshot(snapshot: Snapshot, address: Address) -> dict[str, object]:
    """The entry as it is in its file, parts included, without its key or id."""
    found: dict[str, object] = dict(snapshot.entries[address].fields)
    for child in snapshot.entries:
        if child.parent() != address:
            continue
        part, nested = snapshot.kind_of(child), entry_snapshot(snapshot, child)
        if part.holding is Holds.ONE:
            found[part.key or ""] = nested
        else:
            held = found.setdefault(part.key or "", {})
            if isinstance(held, dict):
                held[child.key] = nested
    return found


def snapshot_problems(base: Snapshot, item: Item) -> list[str]:
    """R7: the item's snapshot, hash, title and sentence are those of the entry in `base` at its id."""
    address = parse_address(item.id, base.ontology)
    if address is None or address not in base.entries:
        return [f"no entry {item.id} in the base"]
    shot, found = item.snapshot, []
    if shot != entry_snapshot(base, address):
        found.append("snapshot differs from the entry in the base")
    if item.hash != base.fingerprint(address):
        found.append(f"hash is not the fingerprint {base.fingerprint(address)}")
    if item.title != shot.get("title") or item.said != (shot.get("says") or shot.get("question")):
        found.append("title or said differs from the snapshot")
    return found


def known_addresses(snapshot: Snapshot) -> list[str]:
    """The live decisions: what a removal's `why` may name."""
    kinds = {kind.kind for kind in snapshot.ontology.kinds.values() if kind.settling is not None}
    return [str(address) for address in snapshot.entries if address.kind in kinds]


def _inside(address: Address, root: Address) -> bool:
    return address.home == root.home and address.path[: len(root.path)] == root.path


def refusals(snapshot: Snapshot, address: Address) -> list[str]:
    """Why the address cannot be removed: a live link names it or a part of it, or a decision in force gives it fields."""
    found: list[str] = []
    for origin, entry in snapshot.entries.items():
        for item in link_items(snapshot.ontology, entry):
            target = resolve(snapshot.ontology, snapshot.entries, origin, item).target
            if target is not None and _inside(target, address) and not _inside(origin, address):
                found.append(f"{origin} links to {target} ({item.field})")
    for decision in decisions(snapshot):
        force = decision.in_force
        for text, given in (force.sets if force else {}).items():
            target = parse_address(text, snapshot.ontology)
            if isinstance(given, dict) and target is not None and _inside(target, address):
                found.append(f"{decision.address} in force gives fields to {text}")
    return found


def build_item(snapshot: Snapshot, address: Address, why: str | None, replaced_by: str | None, at: datetime.datetime,
               last_seen: str, ontology: str) -> Item:
    fields = snapshot.entries[address].fields
    parent = address.parent()
    where = None
    if parent is not None:
        siblings = [a for a in snapshot.entries if a.parent() == parent and a.kind == address.kind]
        where = Parent(str(parent), snapshot.kind_of(address).key or "", siblings.index(address))
    title, says = fields.get("title"), fields.get("says") or fields.get("question")
    return Item(str(address), address.kind, where, title if isinstance(title, str) else None, says if isinstance(says, str) else None,
                why, replaced_by, at, last_seen, snapshot.fingerprint(address), ontology,
                entry_snapshot(snapshot, address))


def remove(root: Path, kb: str, ontology: Ontology, name: str, text: str, why: str | None, to: str | None,
           now: datetime.datetime, last_seen: str) -> Item:
    """Delete the entry at `text` from the worktree and append its ledger item; refuses before writing anything."""
    if not why or not why.strip():
        raise RemoveRefused(["why is required: the address of the decision that said so, or the reason in plain words"])
    editor = Editor(root, kb, ontology)
    snapshot = editor.snapshot()
    address = snapshot.resolve(text)
    if address is None:
        raise LookupError(text)
    if (earlier := interrupted(root, kb, snapshot, address)) is not None:
        editor.remove(address)  # finish the removal that crashed after its ledger write
        return earlier
    reasons = refusals(snapshot, address)
    if snapshot.kind_of(address).holding is Holds.ONE and address.parent() is not None:
        reasons.append(f"{address} is the single {address.kind} of its parent: change it, or remove the parent")
    item = build_item(snapshot, address, why, to, now, last_seen, name)
    problems = removed.check_why([item], known_addresses(snapshot))
    problems += removed.check_replacements([item], [str(a) for a in snapshot.entries])
    reasons += [f"{p.code}: {p.detail}" for p in problems]
    if reasons:
        raise RemoveRefused(reasons)
    removed.append(root / kb, address.home, item, lambda new: snapshot_problems(snapshot, new))
    editor.remove(address)
    return item


def interrupted(root: Path, kb: str, snapshot: Snapshot, address: Address) -> Item | None:
    """The ledger item of a removal that crashed between its two writes (ledger written, entry still live), else None."""
    ledgers, _ = removed.read_all(root / kb)
    found = next((i for ledger in ledgers.values() for i in ledger.items if i.id == str(address)), None)
    return found if found is not None and not snapshot_problems(snapshot, found) else None
