"""`requires:` of a kind, checked on one entry or on one item of a `holds: list` part (an effect): its condition, then the
field it needs or the kinds it reaches along a link path (see `paths`), or, with `same`, a path that comes back to it.

Built here: decision software/ontology/decision/unused-is-work.
"""

from functools import partial
from typing import TYPE_CHECKING

from ogy.kinds import ANY, Holds, Requirement, where
from ogy.links import LinkItem, resolve
from ogy.model import Address, link_values
from ogy.paths import kept
lazy from ogy.settle import answered, decisions
lazy from ogy.snapshot import Snapshot
lazy from ogy.status import agreed_of

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

type Reaches = Callable[[tuple[str, ...]], bool]


def applies(need: Requirement, fields: Mapping[str, object], has_part: Callable[[str], bool], reaches: Reaches) -> bool:
    """Whether the condition holds: a field set, a part held, a field equal to one of the values, a path reaching anything
    (none: always)."""
    if need.if_set is not None:
        return fields.get(need.if_set) is not None
    if need.if_unset is not None:
        return fields.get(need.if_unset) is None
    if need.if_part is not None:
        return has_part(need.if_part)
    if need.if_equals is not None:
        return fields.get(need.if_equals.field) in need.if_equals.values
    if need.if_reaches:
        return reaches(need.if_reaches)
    return True


def _bare(fields: Mapping[str, object], without: tuple[str, ...]) -> bool:
    return all(fields.get(name) is None for name in without)


def _reached(snapshot: Snapshot, path: tuple[str, ...], origin: Address, fields: Mapping[str, object], item: str | None) -> set[Address]:
    """The entries the path reaches; from an item (of the part kind `item`) its first hop is one of the item's own link fields,
    resolved from the entry that holds it."""
    if item is None:
        return snapshot.links.walk(origin, path)[0]
    (first, key, wanted), rest = where(path[0]), path[1:]
    spec = snapshot.ontology.kinds[item].fields.get(first)
    if spec is None:
        return set()
    targets = [
        resolve(snapshot.ontology, snapshot.entries, origin, LinkItem(first, text, spec.to)).target
        for text in link_values(fields.get(first))
    ]
    return {
        reached
        for target in targets
        if target is not None and kept(target, snapshot.entries[target].fields, key, wanted)
        for reached in snapshot.links.walk(target, rest)[0]
    }


def reaching(snapshot: Snapshot, origin: Address, fields: Mapping[str, object], item: str | None = None) -> Reaches:
    """Whether a path from the entry (or from the item of the part kind `item` that it holds) reaches anything."""
    return lambda path: bool(_reached(snapshot, path, origin, fields, item))


def satisfied(
    snapshot: Snapshot, need: Requirement, kind: str, origin: Address, fields: Mapping[str, object], *, item: bool = False
) -> bool:
    """Whether the entry (or the item of kind `kind` held by `origin`) meets what the requirement asks."""
    if need.needs_field is not None:
        return fields.get(need.needs_field) is not None
    done = answered(decisions(snapshot)) if need.or_answered else None
    if done is not None and str(origin) in done[1]:
        return True
    if not need.path:
        return kind in need.kinds and _bare(fields, need.without)
    reached = {found for path in need.paths for found in _reached(snapshot, path, origin, fields, kind if item else None)}
    if need.same:
        return origin in reached and snapshot.kind_of(origin).kind in need.kinds
    return any(
        (ANY in need.kinds or address.kind in need.kinds)
        and _bare(snapshot.entries[address].fields, need.without)
        and (done is None or _vouched(snapshot, address, done[0]))
        for address in reached
    )


def _vouched(snapshot: Snapshot, address: Address, answered: set[Address]) -> bool:
    """A person stands behind the entry: a decision with an answer, or any other entry agreed to as it reads now."""
    kind = snapshot.ontology.settling_kind()
    if kind is not None and address.kind == kind.kind:
        return address in answered
    agreed = agreed_of(snapshot, address)
    return agreed is not None and agreed.hash == snapshot.agreed_print(address)


def has_part(snapshot: Snapshot, address: Address, kind: str) -> bool:
    """The entry holds a part of `kind` (an item of a list part, or an addressed part)."""
    part = snapshot.ontology.get(kind)
    if part is not None and part.holding is Holds.LIST:
        return bool(snapshot.entries[address].fields.get(part.key or ""))
    return bool(snapshot.links.parts(address, kind))


def unmet(snapshot: Snapshot, address: Address, *, work: bool) -> list[Requirement]:
    """The requirements of the entry's kind it does not meet: the faults (`work` False) or the work left (`work` True)."""
    kind, fields = snapshot.kind_of(address), snapshot.entries[address].fields
    held = partial(has_part, snapshot, address)
    return [
        need
        for need in kind.requires
        if need.work is work
        and applies(need, fields, held, reaching(snapshot, address, fields))
        and not satisfied(snapshot, need, kind.kind, address, fields)
    ]
