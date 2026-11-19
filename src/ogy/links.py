"""Links: which values of an entry are links, and what a link names (a full address, or a local key of a nearby part)."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from ogy.kinds import ANY, FieldType, Holds
from ogy.model import Address, Entry, Problem, link_values, parse_address
from ogy.ontology import Ontology


@dataclass(frozen=True)
class LinkItem:
    """One link value as written, the field it is in and the kinds it may name."""

    field: str
    text: str
    to: tuple[str, ...]


@dataclass(frozen=True)
class Resolution:
    """What a link names: `target`, or the one problem with it."""

    target: Address | None
    problem: Problem | None = None
    detail: str = ""


def expr_reads(value: object) -> tuple[str, ...]:
    """The links of an expression `{text, reads}`."""
    return link_values(value.get("reads")) if isinstance(value, dict) else ()


def _values(spec_type: FieldType, value: object) -> tuple[str, ...]:
    return expr_reads(value) if spec_type is FieldType.EXPR else link_values(value)


def link_items(ontology: Ontology, entry: Entry) -> Iterator[LinkItem]:
    """Every link in the entry: its link fields, the `reads` of its expressions and those of its `holds: list` parts."""
    kind = ontology.get(entry.address.kind)
    if kind is None:
        return
    for name, spec in ontology.specs(kind).items():
        for text in _values(spec.type, entry.fields.get(name)) if spec.to else ():
            yield LinkItem(name, text, spec.to)
    for part in ontology.parts_of(kind.kind):
        items = entry.fields.get(part.key or "")
        if part.holding is not Holds.LIST or not isinstance(items, list):
            continue
        for item in items:
            for name, spec in part.fields.items():
                for text in _values(spec.type, item.get(name)) if spec.to and isinstance(item, dict) else ():
                    yield LinkItem(name, text, spec.to)


def _full(ontology: Ontology, entries: Mapping[Address, Entry], item: LinkItem) -> Resolution:
    target = parse_address(item.text, ontology)
    if target is None:
        return Resolution(None, Problem.BAD_LINK, f"{item.field}: {item.text!r} is not an address (<area>/<kind>/<id>)")
    if ANY not in item.to and target.kind not in item.to:
        return Resolution(None, Problem.LINK_KIND, f"{item.field} points at {list(item.to)}, not {target.kind}")
    if target not in entries:
        return Resolution(None, Problem.DANGLING_LINK, f"{item.field}: no {target}")
    return Resolution(target)


def resolve(ontology: Ontology, entries: Mapping[Address, Entry], origin: Address, item: LinkItem) -> Resolution:
    """A value with `/` is a full address; one without is a local key of a part of the nearest enclosing entry that has one."""
    if "/" in item.text:
        return _full(ontology, entries, item)
    at: Address | None = origin
    while at is not None:
        named = [at.part(kind, item.text) for kind in item.to if kind != ANY and at.part(kind, item.text) in entries]
        if len(named) > 1:
            return Resolution(None, Problem.AMBIGUOUS_LINK, f"{item.field}: {item.text!r} names {[str(found) for found in named]}")
        if named:
            return Resolution(named[0])
        at = at.parent()
    return Resolution(None, Problem.DANGLING_LINK, f"{item.field}: no part {item.text!r} of a {list(item.to)} near {origin}")
