"""`requires:` of a kind, checked on one entry or on one item of a `holds: list` part (an effect): its condition, then the
field it needs or the kinds it reaches along a link path (see `paths`)."""

from collections.abc import Callable, Mapping
from functools import partial

from ogy.kinds import Holds, Requirement
from ogy.links import LinkItem, resolve
from ogy.model import Address, link_values
from ogy.snapshot import Snapshot


def applies(need: Requirement, fields: Mapping[str, object], has_part: Callable[[str], bool]) -> bool:
    """Whether the condition holds: a field set, a part held, a field equal to one of the values (none: always)."""
    if need.if_set is not None:
        return fields.get(need.if_set) is not None
    if need.if_unset is not None:
        return fields.get(need.if_unset) is None
    if need.if_part is not None:
        return has_part(need.if_part)
    if need.if_equals is not None:
        return fields.get(need.if_equals.field) in need.if_equals.values
    return True


def _bare(fields: Mapping[str, object], without: tuple[str, ...]) -> bool:
    return all(fields.get(name) is None for name in without)


def _reached(snapshot: Snapshot, path: tuple[str, ...], origin: Address, fields: Mapping[str, object], item: str | None) -> set[Address]:
    """The entries the path reaches; from an item (of the part kind `item`) its first hop is one of the item's own link fields,
    resolved from the entry that holds it."""
    if item is None:
        return snapshot.links.walk(origin, path)[0]
    first, rest = path[0], path[1:]
    spec = snapshot.ontology.kinds[item].fields.get(first)
    targets = [resolve(snapshot.ontology, snapshot.entries, origin, LinkItem(first, text, spec.to)).target
               for text in (link_values(fields.get(first)) if spec is not None else ())]
    return {reached for target in targets if target is not None for reached in snapshot.links.walk(target, rest)[0]}


def satisfied(snapshot: Snapshot, need: Requirement, kind: str, origin: Address, fields: Mapping[str, object],
              item: bool = False) -> bool:
    """Whether the entry (or the item of kind `kind` held by `origin`) meets what the requirement asks."""
    if need.needs_field is not None:
        return fields.get(need.needs_field) is not None
    if not need.path:
        return kind in need.kinds and _bare(fields, need.without)
    reached = {found for path in need.paths for found in _reached(snapshot, path, origin, fields, kind if item else None)}
    return any(address.kind in need.kinds and _bare(snapshot.entries[address].fields, need.without) for address in reached)


def has_part(snapshot: Snapshot, address: Address, kind: str) -> bool:
    """The entry holds a part of `kind` (an item of a list part, or an addressed part)."""
    part = snapshot.ontology.get(kind)
    if part is not None and part.holding is Holds.LIST:
        return bool(snapshot.entries[address].fields.get(part.key or ""))
    return bool(snapshot.links.parts(address, kind))


def unmet(snapshot: Snapshot, address: Address, work: bool) -> list[Requirement]:
    """The requirements of the entry's kind it does not meet: the faults (`work` False) or the work left (`work` True)."""
    kind, fields = snapshot.kind_of(address), snapshot.entries[address].fields
    held = partial(has_part, snapshot, address)
    return [need for need in kind.requires if need.work is work and applies(need, fields, held)
            and not satisfied(snapshot, need, kind.kind, address, fields)]
