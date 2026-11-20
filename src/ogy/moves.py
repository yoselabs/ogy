"""Moves: an entry that changed area keeps its kind and id; nothing records it but Git. `ogy move` writes the new address
into every entry that names the old one, and `ogy check --base` tells a move from a loss by comparing the two commits:
an entry gone from one address and present at exactly one other with the same kind and id has moved; the fingerprint
only breaks ties. A rename (a new id) is found by the fingerprint alone: one gone and one arrived of a kind, same meaning.

`rewrite_fields` is the one place that knows which values of an entry are addresses; `renamed` is a snapshot as it reads
with the moved addresses written in, so an answer may differ from the base only by what a move changed. A kind
renamed in the ontology is found the same way, from Git alone (`retyped`): nothing records it either."""

from collections import defaultdict
from collections.abc import Callable, Mapping

from ogy.fieldtypes import AGREED_HASH
from ogy.kinds import FieldSpec, FieldType, Holds, Kind
from ogy.model import Address, Entry, parse_address
from ogy.ontology import Ontology
from ogy.snapshot import Snapshot

type Rename = Callable[[str], str]
type Data = dict[str, object]
type Table = Mapping[Address, Address]


def renamer(table: Table) -> Rename:
    """`old`, or an address under it (a part), becomes the same under `new`; any other text stays."""
    pairs = {str(old): str(new) for old, new in table.items()}

    def rename(text: str) -> str:
        key = max((old for old in pairs if text == old or text.startswith(old + "/")), key=len, default=None)
        return text if key is None else pairs[key] + text[len(key):]

    return rename


def _link(value: object, rename: Rename) -> object:
    return rename(value) if isinstance(value, str) and "/" in value else value


def _links(value: object, rename: Rename) -> object:
    return [_link(item, rename) for item in value] if isinstance(value, list) else value


def _sets(ontology: Ontology, value: object, rename: Rename) -> object:
    if not isinstance(value, dict):
        return value
    found: Data = {}
    for key, given in value.items():
        new = rename(key) if isinstance(key, str) else key
        address = parse_address(new, ontology) if isinstance(new, str) else None
        kind = ontology.get(address.kind) if address else None
        found[new] = rewrite_fields(ontology, kind, given, rename) if kind and isinstance(given, dict) else given
    return found


def _value(ontology: Ontology, spec: FieldSpec, value: object, rename: Rename) -> object:
    match spec.type:
        case FieldType.LINK:
            return _link(value, rename) if spec.to else value
        case FieldType.LINKS:
            return _links(value, rename) if spec.to else value
        case FieldType.EXPR if isinstance(value, dict) and spec.to:
            return {**value, "reads": _links(value["reads"], rename)} if "reads" in value else value
        case FieldType.SETS:
            return _sets(ontology, value, rename)
        case _:
            return value


def rewrite_fields(ontology: Ontology, kind: Kind, fields: Mapping[str, object], rename: Rename) -> Data:
    """The fields with every address in them renamed: link fields, `reads`, the keys of `sets`, and the items of the
    `holds: list` parts (answers and guesses too). Words are never touched."""
    specs = ontology.specs(kind)
    found: Data = {name: _value(ontology, spec, value, rename) if (spec := specs.get(name)) else value for name, value in fields.items()}
    for part in ontology.parts_of(kind.kind):
        items = fields.get(part.key or "")
        if part.holding is Holds.LIST and isinstance(items, list):
            found[part.key or ""] = [rewrite_fields(ontology, part, item, rename) if isinstance(item, dict) else item for item in items]
    return found


def rehash(before: Snapshot, after: Snapshot, was: Address, now: Address, agreed: object) -> object:
    """An entry's `agreed` that was current in `before` (at `was`) set to the fingerprint the entry has in `after` (at `now`):
    a move changes the fingerprint of what links to the moved entry, not what the person agreed to."""
    if isinstance(agreed, dict) and was in before.entries and now in after.entries and agreed.get(AGREED_HASH) == before.agreed_print(was):
        return {**agreed, AGREED_HASH: after.agreed_print(now)}
    return agreed


def renamed(snapshot: Snapshot, table: Table) -> Snapshot:
    """The snapshot with every moved address written in, as `ogy move` writes it: entries re-keyed, links renamed and
    the agreements that were current kept current."""
    if not table:
        return snapshot
    rename, ontology = renamer(table), snapshot.ontology
    entries: dict[Address, Entry] = {}
    for address, entry in snapshot.entries.items():
        new = parse_address(rename(str(address)), ontology) or address
        entries[new] = Entry(new, entry.path, rewrite_fields(ontology, snapshot.kind_of(address), entry.fields, rename))
    shifted = Snapshot(ontology, dict(entries), [])
    for address, entry in snapshot.entries.items():
        if isinstance(agreed := entry.fields.get(name := ontology.roles.agreed), dict):
            new = parse_address(rename(str(address)), ontology) or address
            entries[new] = Entry(new, entry.path, {**entries[new].fields, name: rehash(snapshot, shifted, address, new, agreed)})
    return Snapshot(ontology, entries, [])


def _named(snapshot: Snapshot) -> set[str]:
    """Every address an entry of the snapshot names, as `rewrite_fields` finds them."""
    found: set[str] = set()

    def note(text: str) -> str:
        found.add(text)
        return text

    for address, entry in snapshot.entries.items():
        rewrite_fields(snapshot.ontology, snapshot.kind_of(address), entry.fields, note)
    return found


def retyped(base: Snapshot, now: Snapshot) -> dict[Address, Address]:
    """The entries whose kind was renamed in the ontology: the base names `<layer>/<area>/<gone kind>/<id>`, a kind the ontology
    no longer has, and `now` has exactly one new entry with that layer, area and id under another kind."""
    ontology, table = now.ontology, {}
    arrived = [address for address in now.entries if address.parent() is None and address not in base.entries]
    for text in sorted(_named(base)):
        parts = text.split("/")
        if parse_address(text, ontology) is not None or len(parts) < 4 or parts[0] not in ontology.layers or parts[2] in ontology.kinds:
            continue
        old = Address(parts[0], parts[1], ((parts[2], parts[3]),))
        found = [a for a in arrived if (a.layer, a.area, a.key) == (old.layer, old.area, old.key)]
        if len(found) == 1:
            table[old] = found[0]
    return table


def _ties(base: Snapshot, now: Snapshot, olds: list[Address], news: list[Address], table: Table) -> dict[Address, Address]:
    """Several entries of one kind and id gone and arrived: an old and a new pair only when the fingerprint, the moves
    already found written in, matches for exactly that one pair."""
    matches = [(old, new) for old in olds for new in news
               if renamed(base, {**table, old: new}).fingerprint(new) == now.fingerprint(new)]
    return {old: new for old, new in matches
            if sum(1 for o, _ in matches if o == old) == 1 and sum(1 for _, n in matches if n == new) == 1}


def detect(base: Snapshot, now: Snapshot) -> dict[Address, Address]:
    """The entries that moved from `base` to `now`. An entry gone from one address with exactly one arrival of the same kind
    and id has moved, whatever its fingerprint: a changed text is an ordinary change, read as changed since agreed. The
    fingerprint only breaks ties between several of one kind and id. Anything else that is gone is not a move."""
    arrived: defaultdict[tuple[str, str], list[Address]] = defaultdict(list)
    gone: defaultdict[tuple[str, str], list[Address]] = defaultdict(list)
    for address in now.entries:
        if address.parent() is None and address not in base.entries:
            arrived[(address.kind, address.key)].append(address)
    for address in base.entries:
        if address.parent() is None and address not in now.entries:
            gone[(address.kind, address.key)].append(address)
    table = {olds[0]: arrived[key][0] for key, olds in gone.items() if len(olds) == 1 and len(arrived.get(key, [])) == 1}
    for key, olds in gone.items():
        if arrived.get(key) and (len(olds) > 1 or len(arrived[key]) > 1):
            table |= _ties(base, now, olds, arrived[key], table)
    return table | _renames(base, now, gone, arrived, table)


def _renames(base: Snapshot, now: Snapshot, gone: Mapping[tuple[str, str], list[Address]],
             arrived: Mapping[tuple[str, str], list[Address]], table: Table) -> dict[Address, Address]:
    """Entries of one kind gone under one id and arrived under another (`ogy move` to a new id): paired by the fingerprint,
    only where exactly one pair matches."""
    left = [old for key, olds in gone.items() if key not in arrived for old in olds if old not in table]
    new = [address for key, news in arrived.items() if key not in gone for address in news]
    found: dict[Address, Address] = {}
    for kind in {old.kind for old in left}:
        found |= _ties(base, now, [old for old in left if old.kind == kind], [n for n in new if n.kind == kind], table)
    return found
