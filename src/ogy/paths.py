"""Link paths: a kind names a route through typed links, used by staleness and by `requires` checks.

A path is a list of hops. `field` follows that link field forward (`field?key=a|b`: only to targets whose `key` is a or b),
`<-field` follows it backward (entries whose `field` points here; `<-field?key=a|b` only where the entry, or the list part
item that holds the link, has `key` a or b),
`^` goes to the entry's parent, `/kind` goes to the parts of that kind, and a final `=field` reads that field's values from
the entries reached. A final `=@id`, `=@address` or `=@fingerprint` is answered by the snapshot (keys, full addresses, or
the reached entries' own fingerprints, so a performer goes stale when the row it performs changes).

Kind files write no paths for the build hash: the `input` a kind declares on its link fields (and on its common fields and
parts, `Kind.input`) and its reverse `input_from` are read as such paths (`inputs`, `inputs_from`).
"""

from collections.abc import Mapping, Sequence

from ogy.kinds import Input, Kind, Picked, where
from ogy.links import link_items, resolve
from ogy.model import Address, Entry
from ogy.ontology import Ontology

BACK = "<-"
PARENT = "^"
VALUE = "="
PARTS = "/"
DERIVED = "=@"
ID, ADDRESS, CONTENT = DERIVED + "id", DERIVED + "address", DERIVED + "fingerprint"

type Hops = tuple[str, ...]


def kept(fields: Mapping[str, object], key: str, wanted: frozenset[str] | None) -> bool:
    return wanted is None or fields.get(key) in wanted


def _input(start: Hops, given: Input | Picked | None) -> list[Hops]:
    if isinstance(given, Picked):
        return [(*start, VALUE + field) for field in given.fields] + [(*start, PARTS + part, ID) for part in given.parts]
    return [] if given in (None, Input.NONE) else [(*start, ADDRESS if given is Input.ADDRESS else CONTENT)]


def inputs(ontology: Ontology, kind: Kind) -> list[Hops]:
    """The paths the build hash of an entry of `kind` reads: the kind's `input` of common fields and parts first, in its order,
    then the `input` of each field (common, then the kind's own) in the order declared. Undeclared is `none`."""
    parts = {part.kind for part in ontology.parts_of(kind.kind)} - set(ontology.specs(kind))
    given = {**kind.input, **{name: spec.input for name, spec in ontology.specs(kind).items() if name not in kind.input}}
    return [path for name, value in given.items() for path in _input((PARTS + name,) if name in parts else (name,), value)]


def inputs_from(kind: Kind) -> list[Hops]:
    """The reverse paths of the kind's `input_from`: the picked fields of the entries that link to it by each field named."""
    return [(BACK + name, VALUE + field) for name, picked in kind.input_from.items() for field in picked.fields]


class LinkIndex:
    """Forward and backward links of one set of entries, by field."""

    def __init__(self, ontology: Ontology, entries: Mapping[Address, Entry]) -> None:
        self.entries = entries
        self._forward: dict[tuple[Address, str], set[Address]] = {}
        self._backward: dict[tuple[Address, str], list[tuple[Address, Mapping[str, object]]]] = {}
        self._parts: dict[tuple[Address, str], set[Address]] = {}
        for address, entry in entries.items():
            parent = address.parent()
            if parent is not None and parent in entries:
                self._parts.setdefault((parent, address.kind), set()).add(address)
            for item in link_items(ontology, entry):
                target = resolve(ontology, entries, address, item).target
                if target is not None:
                    self._forward.setdefault((address, item.field), set()).add(target)
                    holder = item.item if item.item is not None else entry.fields
                    self._backward.setdefault((target, item.field), []).append((address, holder))

    def forward(self, address: Address, field: str) -> set[Address]:
        return self._forward.get((address, field), set())

    def backward(self, address: Address, field: str) -> set[Address]:
        """The entries whose `field` points here; `field?key=a|b`: only those links whose holder (the entry, or the list part
        item that holds the link) has `key` a or b."""
        name, key, wanted = where(field)
        return {source for source, holder in self._backward.get((address, name), []) if kept(holder, key, wanted)}

    def onward(self, address: Address, hop: str) -> set[Address]:
        """The targets of the link field `hop` names; `field?key=a|b`: only targets whose `key` is a or b."""
        name, key, wanted = where(hop)
        return {target for target in self.forward(address, name) if kept(self.entries[target].fields, key, wanted)}

    def parts(self, address: Address, kind: str) -> list[Address]:
        """The parts of one kind, sorted."""
        return sorted(self._parts.get((address, kind), set()))

    def walk(self, start: Address, hops: Sequence[str]) -> tuple[set[Address], list[object]]:
        """The entries a path reaches, and the values of a final `=field` hop (sorted by entry)."""
        current = {start}
        values: list[object] = []
        for hop in hops:
            if hop.startswith(DERIVED):
                break
            if hop.startswith(PARTS):
                current = {part for address in current for part in self.parts(address, hop[len(PARTS):])}
            elif hop.startswith(VALUE):
                values.extend(self.entries[address].fields.get(hop[1:]) for address in sorted(current))
                break
            elif hop == PARENT:
                current = {parent for address in current if (parent := address.parent()) is not None and parent in self.entries}
            elif hop.startswith(BACK):
                current = {source for address in current for source in self.backward(address, hop[len(BACK):])}
            else:
                current = {target for address in current for target in self.onward(address, hop)}
        return current, values
