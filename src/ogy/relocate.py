"""`ogy move`: an entry changes area, or its id (a rename), and keeps its kind, its agreements and its answers.

One checked write (`writes.commit`: made whole or put back): the file or list item and every part go to the new area, and
every address that names the old one is rewritten in the same write, wherever it is: links, `sets` keys, proposals, the
answers, and the `why` of a removed item. An agreement that was current stays current. A move writes no removed.yml item:
Git keeps the record, and `ogy check --base` tells the move from a loss (`ogy.moves.detect`)."""

from dataclasses import dataclass

from ogy import built, near, removed, removed_moves
from ogy.edit import Editor
from ogy.kinds import NAME, Shape
from ogy.model import Address, Entry, parse_address
from ogy.moves import Table, rehash, renamer, rewrite_fields
from ogy.snapshot import Snapshot
from ogy.writes import WriteRefusedError, commit
lazy from ogy.target import Target


@dataclass(frozen=True)
class Moved:
    old: Address
    new: Address
    changed: list[str]

    def __str__(self) -> str:
        return f"moved {self.old} to {self.new}"


def _renamed(snapshot: Snapshot, address: Address, text: str) -> tuple[str, str, str] | None:
    """`<layer>/<area>/<kind>/<id>`: the layer, area and new id of a rename (the kind stays); None when `text` names an area."""
    if len(text.split("/")) < 4:
        return None
    new = parse_address(text, snapshot.ontology)
    if new is None or new.parent() is not None or new.kind != address.kind:
        shapes = f"<area>, <layer>/<area> or <layer>/<area>/{address.kind}/<id>"
        raise WriteRefusedError([f"{text!r} is no address of a {address.kind}: give {shapes}"])
    return new.layer, new.area, new.key


def destination(snapshot: Snapshot, address: Address, text: str) -> Address:
    """The address an entry gets in `<area>`, `<layer>/<area>` or at `<layer>/<area>/<kind>/<id>`, or why it may not go there."""
    kind, parts = snapshot.kind_of(address), text.split("/")
    renamed = _renamed(snapshot, address, text)
    layered = renamed is None and len(parts) == 2 and parts[0] in snapshot.ontology.layers
    layer, area = renamed[:2] if renamed else (parts[0], parts[1]) if layered else (address.layer, parts[0])
    key = renamed[2] if renamed else address.key
    if address.parent() is not None:
        raise WriteRefusedError([f"{address} is a part: it moves with its {address.parent()}"])
    if kind.area is not None:
        raise WriteRefusedError([f"{address.kind} lives only in the folder {kind.area}: it has no area to move to"])
    if not address.layer:
        raise WriteRefusedError([f"{address} is in a folder {address.kind} moved out of: run `ogy migrate` first"])
    if kind.shape is Shape.SINGLE:
        raise WriteRefusedError([f"{address.kind} is the entry of its area itself: it does not move"])
    if (not renamed and (len(parts) > 2 or (len(parts) == 2 and not layered))) or not NAME.match(area):
        raise WriteRefusedError(
            [f"{text!r} is no area: give <area> or <layer>/<area> (kebab-case, layers {list(snapshot.ontology.layers)})"]
        )
    if layer not in kind.layers:
        raise WriteRefusedError([f"{address.kind} may live in the layers {list(kind.layers)}, not {layer}"])
    if area == (shared := snapshot.ontology.shared) and not kind.shared:
        raise WriteRefusedError([f"the area {shared} holds only what two areas use; {address.kind} stays in the area that owns it"])
    new = Address(layer, area, ((address.kind, key),))
    if new == address:
        raise WriteRefusedError([f"{address} is already {'there' if renamed else f'in {layer}/{area}'}"])
    return new


def _taken(target: Target, snapshot: Snapshot, new: Address) -> list[str]:
    ledgers, _ = removed.read_all(target.repo / target.kb)
    gone = {item.id for ledger in ledgers.values() for item in ledger.items}
    if new in snapshot.entries:
        return [f"{new} exists"]
    return [f"{new} was removed (it is in a removed.yml); an id is never reused"] if str(new) in gone else []


def carry_built(ed: Editor, target: Target, before: Snapshot, table: Table) -> None:
    """The built line of a moved entry (and of its parts) follows it to the built file of its new source file; one that was
    current stays current, so a move is no build work."""
    root, rename = target.repo / target.kb, renamer(table)
    folder, after = root / built.BUILT, ed.snapshot()
    carried: list[tuple[Address, built.Line]] = []
    for file in sorted(folder.rglob("*.yml")) if folder.is_dir() else ():
        source = file.relative_to(folder).as_posix()
        lines = built.read(root, source)
        gone = {text: line for text, line in lines.items() if rename(text) != text}
        for text, line in gone.items():
            del lines[text]
            was, now = parse_address(text, before.ontology), parse_address(rename(text), after.ontology)
            if was is None or now is None or now not in after.entries:
                continue
            current = was in before.entries and line.own == before.build_hash(was)
            own = after.build_hash(now) if current else line.own
            carried.append((now, built.Line(own, tuple(map(rename, line.covers)), line.sourced)))
        if gone:
            built.write(root, source, lines)
    for address, line in carried:
        built.stamp(root, after.entries[address].path, str(address), line)


def rename_all(ed: Editor, target: Target, before: Snapshot, table: Table) -> None:
    """Every entry that names an old address (or one under it) names the new one, and every agreement that was current stays
    current; the removed items follow. `ogy move` and `ogy migrate` (an entry out of a fixed folder) call it after the files moved."""
    rename = renamer(table)
    ontology = target.kinds()
    seen = ed.snapshot()  # moved, nothing renamed yet; the paths do not change below, so one read serves every update
    after = Snapshot(
        ontology,
        {
            address: Entry(address, entry.path, rewrite_fields(ontology, seen.kind_of(address), entry.fields, rename))
            for address, entry in seen.entries.items()
        },
        [],
    )
    back = renamer({new: old for old, new in table.items()})
    for address, entry in seen.entries.items():
        now = dict(after.entries[address].fields)
        name = ontology.roles.agreed
        if isinstance(agreed := entry.fields.get(name), dict) and (was := parse_address(back(str(address)), ontology)) is not None:
            now[name] = rehash(before, after, was, address, agreed)
        if changes := {name: value for name, value in now.items() if value != entry.fields.get(name)}:
            ed.update(address, changes, snap=seen)
    removed_moves.follow(target.repo / target.kb, rename)


def move(target: Target, text: str, area: str) -> Moved:
    """Move the entry at `text` to `area` (the lock is held); refuses before writing anything that cannot be made whole."""
    editor = Editor(target.repo, target.kb, target.kinds())
    snapshot = editor.snapshot()
    old = snapshot.resolve(text)
    if old is None:
        raise WriteRefusedError([near.no_entry(snapshot, text)])
    new = destination(snapshot, old, area)
    if reasons := _taken(target, snapshot, new):
        raise WriteRefusedError(reasons)

    def act(ed: Editor) -> None:
        ed.relocate(old, new.home, new.key if new.key != old.key else "")
        rename_all(ed, target, snapshot, {old: new})
        carry_built(ed, target, snapshot, {old: new})

    return Moved(old, new, commit(target, lambda _: [new], act, renamer({old: new})))
