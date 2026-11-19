"""`ogy migrate`: the entries follow the renames and drops their kinds declare (see `ogy.kindchange`), in one checked write.

Every old name is rewritten (`kindchange.changes`); an agreement and a built line that were current stay current when only
names changed (`kindchange.Kept`); a dropped field that held a value is printed and its entry's agreement is left, so the
owner sees the entry as changed since agreed. The entries of a fixed folder their kind moved out of (`moved_from`) go to the
`shared` area of its first layer, with the area's own entry when it has none and the folder's removed items, every address
renamed as `ogy move` renames it. Nothing is recorded: Git keeps the old names and places."""

from dataclasses import dataclass, field

from ogy import built, removed
from ogy.edit import Editor
from ogy.fieldtypes import AGREED_HASH
from ogy.kindchange import Change, Kept, changes, moved_table
from ogy.model import Address
from ogy.moves import renamer
from ogy.relocate import rename_all
from ogy.snapshot import Snapshot
from ogy.target import Target
from ogy.writes import commit


@dataclass(frozen=True)
class Migrated:
    changes: list[Change]
    agreed: list[Address]  # agreements re-set to the fingerprint after the migration
    built: list[str]  # built lines re-set
    files: list[str]
    moved: list[tuple[Address, Address]] = field(default_factory=list)  # out of a fixed folder their kind moved out of

    def lines(self) -> list[str]:
        if not self.changes and not self.moved:
            return ["nothing to migrate"]
        out = [f"renamed {c.address} {c.field} to {c.new}" if c.new else f"dropped {c.address} {c.field} (it held {c.value!r}): "
               "the owner sees this entry as changed" for c in self.changes]
        out += [f"moved {old} to {new}: `ogy move` it to the area that uses it" for old, new in self.moved]
        out += [f"kept the agreement current: {address}" for address in self.agreed]
        return out + [f"kept the built line current: {text}" for text in self.built]


def _agreements(snapshot: Snapshot, kept: Kept) -> dict[Address, dict[str, object]]:
    found: dict[Address, dict[str, object]] = {}
    for address, entry in snapshot.entries.items():
        agreed = entry.fields.get(snapshot.ontology.roles.agreed)
        given = agreed.get(AGREED_HASH) if isinstance(agreed, dict) else None
        if isinstance(agreed, dict) and isinstance(given, str) and (now := kept.hash(address, given)) not in (None, given):
            found[address] = {**agreed, AGREED_HASH: now}
    return found


def _built(target: Target, snapshot: Snapshot, kept: Kept) -> list[str]:
    """Re-set the `own` and `deps` hashes of the built lines that only a rename changed."""
    root, done = target.repo / target.kb, []
    for text, line in sorted(built.read_all(root).items()):
        address = snapshot.resolve(text)
        if address is None:
            continue
        own = kept.hash(address, line.own, build=True) or line.own
        deps = {dep: (kept.hash(found, given, build=True) if (found := snapshot.resolve(dep)) else None) or given
                for dep, given in line.deps.items()}
        if own != line.own or deps != dict(line.deps):
            built.stamp(root, snapshot.entries[address].path, text, built.Line(own, deps, line.covers, line.sourced))
            done.append(text)
    return done


def _rehome(ed: Editor, target: Target, snapshot: Snapshot, table: dict[Address, Address]) -> list[tuple[Address, Address]]:
    """Move every entry of the fixed folders in `table` to its new home, rename every address under them and move their ledgers."""
    moved = []
    for address in sorted(a for a in snapshot.entries if a.parent() is None and Address("", a.area, ()) in table):
        home = table[Address("", address.area, ())]
        new = Address(home.layer, home.area, address.path)
        ed.relocate(address, new.home)
        moved.append((address, new))
    area = snapshot.ontology.area_kind()
    homes = [Address(home.layer, home.area, ((area.kind, snapshot.ontology.shared),)) for home in table.values()] if area else []
    for here in homes:
        if here not in snapshot.entries:
            ed.put(here, snapshot.ontology.shared_fields())
    rename_all(ed, target, snapshot, table)
    root = target.repo / target.kb
    for old, new in table.items():
        removed.rehome(root, str(old), str(new))
        if (root / old.area).is_dir() and not any((root / old.area).iterdir()):
            (root / old.area).rmdir()
    return moved


def migrate(target: Target) -> Migrated:
    """Write the migration of the worktree (the lock is held); refuses, writing nothing, when it leaves a new error."""
    editor = Editor(target.repo, target.kb, target.kinds())
    snapshot = editor.snapshot()
    after, found = changes(snapshot)
    root, homes = target.repo / target.kb, snapshot.ontology.moved_homes()
    table = {**moved_table(snapshot), **{Address("", old, ()): Address(*new.split("/"), ()) for old, new in homes.items()
                                         if (root / old / removed.FILE).is_file()}}
    tidied = [address for address, entry in after.entries.items() if entry is not snapshot.entries[address]]
    if not found and not table and not tidied:
        return Migrated([], [], [], [])
    kept = Kept(snapshot)
    agreed = _agreements(snapshot, kept)
    lines: list[str] = []
    moved: list[tuple[Address, Address]] = []

    def act(ed: Editor) -> None:
        for address, entry in snapshot.entries.items():
            now = {**after.entries[address].fields, **({snapshot.ontology.roles.agreed: agreed[address]} if address in agreed else {})}
            update = {name: now.get(name) for name in {*entry.fields, *now} if now.get(name) != entry.fields.get(name)}
            if update:
                ed.update(address, update, snap=snapshot)
        lines.extend(_built(target, snapshot, kept))
        moved.extend(_rehome(ed, target, snapshot, table) if table else [])

    touched = sorted({change.address for change in found} | set(agreed) | set(tidied))
    files = commit(target, lambda _: [*touched, *(new for _, new in moved)], act, renamer(table))
    return Migrated(found, sorted(agreed), lines, files, moved)
