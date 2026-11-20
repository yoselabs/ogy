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

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from ogy.fieldtypes import agreed_keys
from ogy.kinds import FieldSpec, FieldType, Holds, Input, Kind, Picked, Was
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
        old = self.ontology.old_names(kind)
        listed = {part.key: part for part in self.ontology.parts_of(kind.kind) if part.holding is Holds.LIST}
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
        return self._reshaped(kind, out, address, where) if self.renames else out

    def _reshaped(self, kind: Kind, out: Data, address: Address, where: str) -> Data:
        """A folded part becomes the one value it held; an old value becomes the fields it now is (None removes one)."""
        for name, inner in kind.folded.items():
            if isinstance(value := out.get(name), dict):
                self.found.append(Change(address, where + name, f"{name} ({inner})", value))
                out[name] = value.get(inner)
        for name, values in kind.revalued.items():
            if isinstance(value := out.get(name), str) and (now := values.get(value)) is not None:
                self.found.append(Change(address, f"{where}{name} {value}", ", ".join(f"{k} {v}" for k, v in now.items()), value))
                out = {k: v for k, v in {**out, **now}.items() if v is not None}
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


def _picked(given: Picked, back: Mapping[str, str], kinds: Mapping[str, str]) -> Picked:
    """A picked input under the old names of the fields and part kinds it picks."""
    return Picked(fields=tuple(back.get(name, name) for name in given.fields), parts=tuple(kinds.get(name, name) for name in given.parts))


def _input(given: Input | Picked | None, back: Mapping[str, str], kinds: Mapping[str, str]) -> Input | Picked | None:
    return _picked(given, back, kinds) if isinstance(given, Picked) else given


def _spec(spec: FieldSpec, kinds: Mapping[str, tuple[str, ...]], back: Mapping[str, str]) -> FieldSpec:
    first = {new: olds[0] for new, olds in kinds.items()}
    return spec.model_copy(update={"to": tuple(old for name in spec.to for old in kinds.get(name, (name,))),
                                   "input": _input(spec.input, back, first)})


def _old(kind: Kind, was: Was | None, back: Mapping[str, str], names: Mapping[str, tuple[str, ...]], fields_too: bool) -> Kind:
    """One kind as it was: under the old name `was` (None: under its own name), its fields and inputs under their old names."""
    own = {new: old for old, new in kind.renamed.items()} if fields_too else {}
    mine = own | ({new: old for old, new in was.renamed.items()} if was else {})
    first = {new: olds[0] for new, olds in names.items()}  # an input names a part kind, never a merged one (shape file)
    fields = {mine.get(field, field): _spec(spec, names, back) for field, spec in kind.fields.items()} | {
        old: FieldSpec() for old in (kind.dropped if fields_too else ())}
    given = {first.get(key, back.get(key, mine.get(key, key))): _input(value, back, first) for key, value in kind.input.items()}
    given_from = {back.get(key, key): _picked(value, back, first) for key, value in kind.input_from.items()}
    update: dict[str, object] = {"fields": fields, "input": given, "input_from": given_from,
                                 "part_of": tuple(old for parent in kind.part_of for old in names.get(parent, (parent,)))}
    if was:
        update |= {"kind": was.kind, "file": was.file or kind.file, "key": was.key or kind.key, "was": ()}
    return kind.model_copy(update=update)


def before(ontology: Ontology, kinds_too: bool = True, fields_too: bool = True) -> Ontology:
    """The kinds as they were before their declared renames and drops: a renamed field under its old name, a dropped one back
    as text, a renamed common field under its old name and, with `kinds_too` (files that still hold the old kind names), a
    renamed kind under its old name, file and key (`was`), a kind that absorbed several as each of them. An input and a
    reverse input name a renamed field or part kind by its old name too (the renames of every kind, as they cross kinds).
    Without `fields_too`, only the kind renames (with their own `was.renamed`): files already migrated to every field rename
    that still hold an old kind name."""
    common = {new: old for old, new in ontology.declared.renamed.items()} if fields_too else {}
    fields = {new: old for kind in ontology.kinds.values() for old, new in kind.renamed.items()} if fields_too else {}
    back = common | fields | {
        new: old for kind in ontology.kinds.values() for was in kind.was for old, new in was.renamed.items()}
    names = {kind.kind: tuple(old.kind for old in kind.was) for kind in ontology.kinds.values() if kind.was and kinds_too}
    kinds: dict[str, Kind] = {}
    for name, kind in ontology.kinds.items():
        for was in kind.was if kind.was and kinds_too else (None,):
            kinds[was.kind if was else name] = _old(kind, was, back, names, fields_too)
    declared = ontology.declared.model_copy(update={"common": {common.get(field, field): _spec(spec, names, back)
                                                               for field, spec in ontology.common.items()}})
    return Ontology.unchecked(kinds, declared)


class Kept:
    """Which fingerprints stay current across a migration: `old` is the knowledge base as it was, read under `before`, and
    `snapshot` the same files under the new kind names (`ogy.retype`); `back` gives a new address its old one. `also` reads
    the old files under the kind renames only (`before(..., fields_too=False)`): a hash may have been stamped either way."""

    def __init__(self, snapshot: Snapshot, old: Snapshot | None = None, back: Callable[[str], str] = str,
                 also: Snapshot | None = None) -> None:
        was = old or Snapshot(before(snapshot.ontology, kinds_too=False), snapshot.entries, [])
        self.back, self.was, self.also = back, was, also
        self.dropped = Snapshot(was.ontology, changes(was, renames=False)[0].entries, [])
        self.now = changes(snapshot)[0]

    def hash(self, address: Address, given: str, *, build: bool = False) -> str | None:
        """The meaning fingerprint (the build hash, for a built line) after the migration when `given` was current and no
        dropped value touched it, else None."""
        was = parse_address(self.back(str(address)), self.was.ontology)
        if was is None or was not in self.was.entries:
            return None
        def of(snapshot: Snapshot, at: Address) -> str:
            return snapshot.build_hash(at) if build else snapshot.agreed_print(at)
        then = of(self.was, was)
        thens = {then} | ({of(self.also, was)} if self.also is not None and was in self.also.entries else set())
        return of(self.now, address) if given in thens and of(self.dropped, was) == then else None
