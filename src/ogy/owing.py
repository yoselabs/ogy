"""Which layer owes a requirement, computed from `layers:` and `link_direction`, never tagged by hand.

A requirement whose path goes back (`<-field`) to kinds that only a later layer holds cannot be met in the entry's own layer:
the later layer owes it, so it is work there, never a fault here (decision checks-fault-landing-work). A forward hop never
crosses: a link names its own layer or an earlier one.
"""

lazy from collections.abc import Mapping

from ogy.hops import ANY_FIELD, BACK, PARENT, PARTS, VALUE
from ogy.kinds import ANY, LINKING, Holds, Kind, Requirement, Shape, where
lazy from ogy.declared import Declared


def kind_layers(kinds: Mapping[str, Kind], name: str) -> frozenset[str]:
    """The layers a kind may live in: its own, or a part's parents'."""
    kind = kinds.get(name)
    if kind is None:
        return frozenset()
    if kind.layers:
        return frozenset(kind.layers)
    return frozenset().union(*(kind_layers(kinds, parent) for parent in kind.part_of if parent != name))


def _links(kinds: Mapping[str, Kind], declared: Declared, name: str) -> dict[str, tuple[str, ...]]:
    """The link fields an entry of the kind holds (common ones, its own, and those of the items of its list parts): field -> to."""
    kind = kinds[name]
    held = [declared.common, kind.fields]
    held += [part.fields for part in kinds.values() if part.is_part(name) and part.holding is Holds.LIST]
    return {field: spec.to for fields in held for field, spec in fields.items() if spec.type in LINKING}


def _targets(kinds: Mapping[str, Kind], to: tuple[str, ...]) -> set[str]:
    return set(kinds) if ANY in to else {name for name in to if name in kinds}


def _hop(kinds: Mapping[str, Kind], declared: Declared, here: set[str], hop: str) -> set[str]:
    """The kinds one hop of a path may reach from `here`."""
    if hop.startswith(PARTS):
        return {hop[len(PARTS) :]} & set(kinds)
    if hop == PARENT:
        return {parent for name in here for parent in kinds[name].part_of}
    if hop.startswith(BACK):
        field = where(hop[len(BACK) :])[0]
        return {
            name
            for name in kinds
            for linked, to in _links(kinds, declared, name).items()
            if field in (ANY_FIELD, linked) and _targets(kinds, to) & here
        }
    field = where(hop)[0]
    return {target for name in here for target in _targets(kinds, _links(kinds, declared, name).get(field, ()))}


def owed_by(kinds: Mapping[str, Kind], declared: Declared, name: str, need: Requirement, layer: str) -> str | None:
    """The earliest later layer a path of the requirement crosses into from an entry of `name` in `layer`; None: no path crosses."""
    if layer not in declared.layers:
        return None
    later = set(declared.layers[declared.layers.index(layer) + 1 :])
    found: list[str] = []
    for path in need.paths if need.path else ():
        here = {name}
        for hop in path:
            if hop.startswith(VALUE):
                break
            here = _hop(kinds, declared, here, hop)
            homes = [kind_layers(kinds, reached) for reached in here]
            if hop.startswith(BACK) and here and all(home and home <= later for home in homes):
                found.append(min(frozenset().union(*homes), key=declared.layers.index))
                break
    return min(found, key=declared.layers.index) if found else None


def crosses(kinds: Mapping[str, Kind], declared: Declared, name: str, need: Requirement) -> bool:
    """A path of the requirement crosses into a later layer from some layer the kind may live in."""
    return any(owed_by(kinds, declared, name, need, layer) for layer in kind_layers(kinds, name))


def derived(kinds: Mapping[str, Kind], declared: Declared) -> dict[str, Kind]:
    """The kinds with every requirement that crosses into a later layer made work (an item of a list part has no address, so
    none of its requirements is work)."""
    found: dict[str, Kind] = {}
    for name, kind in kinds.items():
        if kind.shape is Shape.INLINE and kind.holding is Holds.LIST:
            found[name] = kind
            continue
        needs = tuple(
            need if need.work or not crosses(kinds, declared, name, need) else need.model_copy(update={"work": True})
            for need in kind.requires
        )
        found[name] = kind if needs == kind.requires else kind.model_copy(update={"requires": needs})
    return found
