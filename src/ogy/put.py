"""`ogy put`: the one way to create and update entries. It takes one or many records; a record for an existing address
changes it, a record for a new one adds it. The whole batch is checked together and written under the lock, or nothing is.

A record is a mapping: `address: <area>/<kind>/<id>[/<part kind>/<key>...]` (or `kind`, `area` and `id`), and the fields of
the entry as the kind declares them, typed as YAML. For an existing entry a field is replaced and `field: null` removes it."""

from collections.abc import Mapping
from dataclasses import dataclass

import any_yaml
from git_porcelain import head

from ogy import near, removal, removed
from ogy.edit import Editor
from ogy.fieldtypes import fields_problems
from ogy.kinds import NAME, Holds, Kind, Shape
from ogy.model import Address, parse_address
from ogy.snapshot import Snapshot
from ogy.target import Target
from ogy.writes import Data, WriteRefused, commit, utc_now

KEYS = ("address", "kind", "layer", "area", "id")


@dataclass(frozen=True)
class Put:
    address: Address
    created: bool

    def __str__(self) -> str:
        return f"{'added' if self.created else 'changed'} {self.address}"


def read_records(texts: list[str]) -> list[Mapping[object, object]]:
    """Each text is a JSON or YAML mapping or array of mappings; every mapping is one record, in order."""
    found: list[Mapping[object, object]] = []
    for number, text in enumerate(texts, 1):
        try:
            data = any_yaml.load(text)
        except any_yaml.YAMLError as error:
            raise WriteRefused([f"records {number}: not JSON or YAML ({error})"]) from error
        for item in data if isinstance(data, list) else [data]:
            if not isinstance(item, dict):
                raise WriteRefused([f"records {number}: each record is a mapping with an address and fields, not {item!r}"])
            found.append(item)
    if not found:
        raise WriteRefused(["no records: give a mapping or an array of mappings (an argument, --file or stdin)"])
    return found


def _address(snapshot: Snapshot, record: Mapping[object, object]) -> Address:
    text, parts = record.get("address"), [record.get(key) for key in KEYS[1:]]
    if isinstance(text, str) and not any(part is not None for part in parts):
        found = parse_address(text, snapshot.ontology)
        if found is None:
            hint = near.hint(text, map(str, snapshot.entries))
            raise WriteRefused([f"{text!r} is no address (<layer>/<area>/<kind>/<id>[/<part kind>/<key>...])" + hint])
        return found
    kind, layer, area, ident = parts
    if text is None and all(isinstance(part, str) for part in parts):
        return Address(str(layer), str(area), ((str(kind), str(ident)),))
    raise WriteRefused(["a record has an `address`, or `kind`, `layer`, `area` and `id`, as text"])


def _removed_ids(target: Target) -> set[str]:
    return {item.id for ledger in removed.read_all(target.repo / target.kb)[0].values() for item in ledger.items}


def _fields(record: Mapping[object, object]) -> Data:
    if bad := [key for key in record if not isinstance(key, str)]:
        raise WriteRefused([f"field names are text, not {bad[0]!r}"])
    return {str(key): value for key, value in record.items() if key not in KEYS}


def _new(snapshot: Snapshot, kind: Kind, address: Address, batch: set[Address], gone: set[str]) -> list[str]:
    """Why this address cannot be added now: a bad name, a missing parent, an id that was removed."""
    if str(address) in gone:
        return [f"{address} was removed; an id is never reused"]
    parent = address.parent()
    if parent is None:
        if kind.shape is Shape.INLINE:
            return [f"{address} is a part of {', '.join(kind.part_of)}: give the address of the part, under its parent"]
        names = [address.area, address.key]
        wrong = [] if kind.area in (None, address.area) else [f"{address.kind} lives in {kind.area}"]
        if kind.shape is Shape.SINGLE and address.key != address.area:
            wrong.append(f"the id of an {address.kind} is the name of its area: {address.home}/{address.kind}/{address.area}")
        if address.layer and address.layer not in kind.layers:
            wrong.append(f"{address.kind} may live in the layers {list(kind.layers)}, not {address.layer}")
        return wrong + [f"{name} is not kebab-case" for name in names if not NAME.match(name or "")]
    if parent not in snapshot.entries and parent not in batch:
        return [f"{address} has no parent: add {parent} first (it may be in the same call)"]
    if kind.shape is not Shape.INLINE or kind.holding is Holds.LIST:
        return [f"{address.kind} is not a part that can be added under {parent}"]
    return [] if kind.holding is Holds.ONE or NAME.match(address.key or "") else [f"{address.key} is not kebab-case"]


def _checked(target: Target, snapshot: Snapshot, records: list[Mapping[object, object]]) -> list[tuple[Address, Data, bool]]:
    """Every record as (address, fields, is new), or a refusal that names each record at fault."""
    found: list[tuple[Address, Data, bool]] = []
    problems: list[str] = []
    gone = _removed_ids(target)
    batch = {a for record in records if (a := _try(snapshot, record)) is not None}
    for number, record in enumerate(records, 1):
        try:
            address, fields = _address(snapshot, record), _fields(record)
            kind = snapshot.ontology.get(address.kind)
            if kind is None:
                raise WriteRefused([f"no kind {address.kind} (see `kinds`)"])
            if kind.append_only or kind.holding is Holds.LIST:
                raise WriteRefused([f"{address} is written once: {kind.kind} is added through its own command (`answer`)"])
            if (agreed := snapshot.ontology.roles.agreed) in fields:
                raise WriteRefused([f"{address}: {agreed} is a person's yes, written only by `reply` to a review round"])
            if held := [part.key for part in snapshot.ontology.parts_of(kind.kind) if part.append_only and part.key in fields]:
                raise WriteRefused([f"{address}: {held[0]} are added through their own command (`answer`)"])
            new = address not in snapshot.entries
            if address in {a for a, _, _ in found}:
                raise WriteRefused([f"{address} is in the call twice"])
            wrong = _new(snapshot, kind, address, batch, gone) if new else []
            known = [part.key for part in snapshot.ontology.parts_of(kind.kind) if part.key]
            given = {name: value for name, value in fields.items() if value is not None or not new}
            typed = {k: v for k, v in given.items() if v is not None}
            wrong += [f"{problem}: {detail}" for problem, detail in
                      fields_problems(snapshot.ontology, snapshot.ontology.specs(kind), typed, known, partial=not new)]
            if wrong:
                raise WriteRefused(wrong)
            found.append((address, given, new))
        except WriteRefused as error:
            problems += [f"record {number}: {reason}" for reason in error.reasons]
    if problems:
        raise WriteRefused(problems)
    return found


def _try(snapshot: Snapshot, record: Mapping[object, object]) -> Address | None:
    try:
        return _address(snapshot, record)
    except WriteRefused:
        return None


def put(target: Target, records: list[Mapping[object, object]], why: str | None = None) -> list[Put]:
    """Add or change every record in one atomic, checked write (the lock is held); parents are written before their parts.
    A record that drops parts (`cases: null`, a part left out) needs `why`: each dropped part gets its removed.yml item in the
    same write, so a reshaped step loses nothing silently."""
    editor = Editor(target.repo, target.kb, target.kinds())
    snapshot = editor.snapshot()
    ordered = sorted(_checked(target, snapshot, records), key=lambda item: len(item[0].path))
    done = [Put(address, new) for address, _, new in ordered]

    def act(ed: Editor) -> None:
        for address, fields, new in ordered:
            ed.put(address, fields) if new else ed.update(address, fields)
        _record_dropped(target, snapshot, ed.snapshot(), [address for address, _, _ in ordered], why)

    commit(target, lambda _: [address for address, _, _ in ordered], act)
    return done


def _record_dropped(target: Target, before: Snapshot, after: Snapshot, roots: list[Address], why: str | None) -> None:
    """The parts under the records' addresses that the batch dropped, each recorded in its area's removed.yml."""
    dropped = [address for address in before.entries if address not in after.entries and address not in roots
               and any(address.home == root.home and address.path[:len(root.path)] == root.path for root in roots)]
    dropped = [address for address in dropped if address.parent() not in dropped  # a dropped part takes its own parts
               and before.kind_of(address).holding is Holds.MAP]  # a single part is a field of its parent: its change shows there
    if not dropped:
        return
    if not why or not why.strip():
        raise WriteRefused([f"the batch drops {', '.join(map(str, dropped))}: give --why (a decision address, or plain words)"])
    at, seen = utc_now(), head(target.repo)
    items = [removal.build_item(before, address, why, None, at, seen, target.ontology) for address in dropped]
    problems = removed.check_why(items, removal.known_addresses(before), before.ontology.roles.agreed)
    if problems:
        raise WriteRefused([f"{problem.code}: {problem.detail}" for problem in problems])
    for address, item in zip(dropped, items, strict=True):
        try:
            removed.append(target.repo / target.kb, address.home, item, lambda new: removal.snapshot_problems(before, new))
        except removed.RemovedError as error:
            raise WriteRefused([str(error)]) from error
