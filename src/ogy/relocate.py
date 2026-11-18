"""`ogy move`: an entry changes area and keeps its id, its kind, its agreements and its answers.

One checked write (`writes.commit`: made whole or put back): the file or list item and every part go to the new area, and
every address that names the old one is rewritten in the same write, wherever it is: links, `sets` keys, guesses, the
answers, and the `why` of a removed item. An agreement that was current stays current. A move writes no removed.yml item:
Git keeps the record, and `ogy check --base` tells the move from a loss (`ogy.moves.detect`)."""

from dataclasses import dataclass

from ogy import near, removed
from ogy.edit import Editor
from ogy.kinds import NAME, SHARED_AREA, Shape
from ogy.model import Address, Entry, parse_address
from ogy.moves import Table, rehash, renamer, rewrite_fields
from ogy.snapshot import Snapshot
from ogy.target import Target
from ogy.writes import WriteRefused, commit


@dataclass(frozen=True)
class Moved:
    old: Address
    new: Address
    changed: list[str]

    def __str__(self) -> str:
        return f"moved {self.old} to {self.new}"


def destination(snapshot: Snapshot, address: Address, text: str) -> Address:
    """The address an entry gets in `<area>` or `<layer>/<area>`, or why it may not go there."""
    kind, parts = snapshot.kind_of(address), text.split("/")
    layered = len(parts) == 2 and parts[0] in snapshot.ontology.layers
    layer, area = (parts[0], parts[1]) if layered else (address.layer, parts[0])
    if address.parent() is not None:
        raise WriteRefused([f"{address} is a part: it moves with its {address.parent()}"])
    if kind.area is not None:
        raise WriteRefused([f"{address.kind} lives only in the folder {kind.area}: it has no area to move to"])
    if not address.layer:
        raise WriteRefused([f"{address} is in a folder {address.kind} moved out of: run `ogy migrate` first"])
    if kind.shape is Shape.SINGLE:
        raise WriteRefused([f"{address.kind} is the entry of its area itself: it does not move"])
    if len(parts) > 2 or (len(parts) == 2 and not layered) or not NAME.match(area):
        raise WriteRefused([f"{text!r} is no area: give <area> or <layer>/<area> (kebab-case, layers {list(snapshot.ontology.layers)})"])
    if layer not in kind.layers:
        raise WriteRefused([f"{address.kind} may live in the layers {list(kind.layers)}, not {layer}"])
    if area == SHARED_AREA and not kind.shared:
        raise WriteRefused([f"the area {SHARED_AREA} holds only what two areas use; {address.kind} stays in the area that owns it"])
    new = Address(layer, area, address.path)
    if new == address:
        raise WriteRefused([f"{address} is already in {layer}/{area}"])
    return new


def _taken(target: Target, snapshot: Snapshot, new: Address) -> list[str]:
    ledgers, _ = removed.read_all(target.repo / target.kb)
    gone = {item.id for ledger in ledgers.values() for item in ledger.items}
    if new in snapshot.entries:
        return [f"{new} exists"]
    return [f"{new} was removed (it is in a removed.yml); an id is never reused"] if str(new) in gone else []


def rename_all(ed: Editor, target: Target, before: Snapshot, table: Table) -> None:
    """Every entry that names an old address (or one under it) names the new one, and every agreement that was current stays
    current; the removed items follow. `ogy move` and `ogy migrate` (an entry out of a fixed folder) call it after the files moved."""
    rename = renamer(table)
    ontology = target.kinds()
    seen = ed.snapshot()  # moved, nothing renamed yet; the paths do not change below, so one read serves every update
    after = Snapshot(ontology, {address: Entry(address, entry.path, rewrite_fields(ontology, seen.kind_of(address), entry.fields, rename))
                                for address, entry in seen.entries.items()}, [])
    back = renamer({new: old for old, new in table.items()})
    for address, entry in seen.entries.items():
        now = dict(after.entries[address].fields)
        if isinstance(agreed := entry.fields.get("agreed"), dict) and (was := parse_address(back(str(address)), ontology)) is not None:
            now["agreed"] = rehash(before, after, was, address, agreed)
        if changes := {name: value for name, value in now.items() if value != entry.fields.get(name)}:
            ed.update(address, changes, snap=seen)
    removed.follow(target.repo / target.kb, rename)


def move(target: Target, text: str, area: str) -> Moved:
    """Move the entry at `text` to `area` (the lock is held); refuses before writing anything that cannot be made whole."""
    editor = Editor(target.repo, target.kb, target.kinds())
    snapshot = editor.snapshot()
    old = snapshot.resolve(text)
    if old is None:
        raise WriteRefused([near.no_entry(snapshot, text)])
    new = destination(snapshot, old, area)
    if reasons := _taken(target, snapshot, new):
        raise WriteRefused(reasons)

    def act(ed: Editor) -> None:
        ed.relocate(old, new.home)
        rename_all(ed, target, snapshot, {old: new})

    return Moved(old, new, commit(target, lambda _: [new], act, renamer({old: new})))
