"""What a kind change does to the entries written before it: the renames and drops a kind file declares.

A kind that renames a field keeps the old name in `renamed: {old: new}`; one that drops a field lists it in `dropped`. An
entry that still holds an old name is `needs-migration` until `ogy migrate` (`ogy.migrate`) writes what `migrated` computes
here: every old name becomes its new one, in the entry, in the items of its `holds: list` parts and in the fields a `sets`
gives an entry of that kind; a dropped field is removed. `ogy check --base` reads the base migrated the same way, so a
migration commit is no edit of an append-only part.

`kept` says which hashes stay current: a pure rename changes no meaning, so an agreement or a built line that was current
before is current after (as a move keeps it); a dropped field that held a value changes the meaning, so its hash is left
and the entry comes back to the owner as changed. The old fingerprints are read under `before`, the kinds as they were.

A kind that moved out of a fixed folder (`moved_from`) has its entries there moved to the `shared` area of its first layer, every
address under the old folder renamed, as `ogy move` renames (`moved_table`); `migrated` reads the base that way too."""

from collections.abc import Mapping
from dataclasses import dataclass

from ogy.fieldtypes import agreed_keys
from ogy.kinds import FieldSpec, FieldType, Holds, Kind
from ogy.model import Address, Entry, parse_address
from ogy.moves import renamed
from ogy.ontology import Ontology
from ogy.snapshot import Snapshot

type Data = dict[str, object]


@dataclass(frozen=True)
class Change:
    """One old name in one entry: renamed to `new`, or dropped (`new` None) with the value it held."""

    address: Address
    field: str  # where in the entry: `unit`, `answers.said`, `sets.<address>.unit`
    new: str | None
    value: object


class _Pass:
    """Rewrites the fields of entries, collecting what it changed; `renames` and `drops` say which declarations apply."""

    def __init__(self, ontology: Ontology, renames: bool = True, drops: bool = True) -> None:
        self.ontology, self.renames, self.drops = ontology, renames, drops
        self.found: list[Change] = []
        self.tidied = 0  # agreements that lost a key the agreed type no longer has (outside every fingerprint)

    def fields(self, kind: Kind, data: Mapping[str, object], address: Address, where: str = "") -> Data:
        old, listed = kind.old_names, {part.key: part for part in self.ontology.parts_of(kind.kind) if part.holding is Holds.LIST}
        out: Data = {}
        for given, value in data.items():
            name = old.get(given, given)
            if given in old and (self.renames if name else self.drops):
                self.found.append(Change(address, where + given, name, value))
                if name is None:
                    continue
            else:
                name = given
            if name in listed and isinstance(value, list):
                part = listed[name]
                out[name] = [self.fields(part, item, address, f"{where}{name}.") if isinstance(item, dict) else item for item in value]
            elif name == self.ontology.roles.agreed and isinstance(value, dict) and set(value) - (keys := agreed_keys(self.ontology)) \
                    and self.drops:
                out[name] = {key: item for key, item in value.items() if key in keys}
                self.tidied += 1
            elif (spec := kind.fields.get(name)) is not None:
                out[name] = self._value(spec, value, address, f"{where}{name}.")
            else:
                out[name] = value
        return out

    def _value(self, spec: FieldSpec, value: object, address: Address, where: str) -> object:
        if spec.type is not FieldType.SETS or not isinstance(value, dict):
            return value
        found: Data = {}
        for key, given in value.items():
            target = parse_address(key, self.ontology) if isinstance(key, str) else None
            kind = self.ontology.get(target.kind) if target else None
            found[key] = self.fields(kind, given, address, f"{where}{key}.") if kind and isinstance(given, dict) else given
        return found


def changes(snapshot: Snapshot, renames: bool = True, drops: bool = True) -> tuple[Snapshot, list[Change]]:
    """The snapshot as a migration writes it (an entry with nothing old is the same object), and every old name it met."""
    work = _Pass(snapshot.ontology, renames, drops)
    entries: dict[Address, Entry] = {}
    for address, entry in snapshot.entries.items():
        before = (len(work.found), work.tidied)
        fields = work.fields(snapshot.kind_of(address), entry.fields, address)
        entries[address] = entry if (len(work.found), work.tidied) == before else Entry(address, entry.path, fields)
    return Snapshot(snapshot.ontology, entries, list(snapshot.findings)), work.found


def moved_table(snapshot: Snapshot) -> dict[Address, Address]:
    """Each fixed folder a kind moved out of that still holds entries -> the home `ogy migrate` moves them to, as addresses
    with no path, so every address under the old folder (a removed one too) is renamed by its prefix."""
    held = {address.area for address in snapshot.entries if not address.layer}
    return {Address("", old, ()): Address(*new.split("/"), ()) for old, new in snapshot.ontology.moved_homes().items() if old in held}


def migrated(snapshot: Snapshot) -> Snapshot:
    """The snapshot as `ogy migrate` writes it: the fields renamed and dropped, the entries of a fixed folder moved out of it."""
    return renamed(changes(snapshot)[0], moved_table(snapshot))


def _hop(hop: str, back: Mapping[str, str]) -> str:
    prefix = next((mark for mark in ("<-", "=") if hop.startswith(mark)), "")
    return prefix + back.get(hop[len(prefix):], hop[len(prefix):])


def before(ontology: Ontology) -> Ontology:
    """The kinds as they were before their declared renames and drops: a renamed field under its old name, a dropped one back
    as text. A fingerprint path names a renamed field by its old name too (the renames of every kind, as paths cross kinds)."""
    back = {new: old for kind in ontology.kinds.values() for old, new in kind.renamed.items()}
    kinds: dict[str, Kind] = {}
    for name, kind in ontology.kinds.items():
        mine = {new: old for old, new in kind.renamed.items()}
        fields = {mine.get(field, field): spec for field, spec in kind.fields.items()} | {old: FieldSpec() for old in kind.dropped}
        also, reached = (tuple(tuple(_hop(hop, back) for hop in path) for path in paths)
                         for paths in (kind.fingerprint.also, kind.fingerprint.reached))
        update = {"also": also, "reached": reached}
        kinds[name] = kind.model_copy(update={"fields": fields, "fingerprint": kind.fingerprint.model_copy(update=update)})
    return Ontology.unchecked(kinds, ontology.declared)


class Kept:
    """Which fingerprints stay current across a migration of one snapshot."""

    def __init__(self, snapshot: Snapshot) -> None:
        old = before(snapshot.ontology)
        self.was = Snapshot(old, snapshot.entries, [])
        self.dropped = Snapshot(old, changes(snapshot, renames=False)[0].entries, [])
        self.now = changes(snapshot)[0]

    def hash(self, address: Address, given: str, *, build: bool = False) -> str | None:
        """The meaning fingerprint (the build hash, for a built line) after the migration when `given` was current and no
        dropped value touched it, else None."""
        if address not in self.was.entries:
            return None
        def of(snapshot: Snapshot) -> str:
            return snapshot.build_hash(address) if build else snapshot.fingerprint(address)
        was = of(self.was)
        return of(self.now) if given == was and of(self.dropped) == was else None
