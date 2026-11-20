"""Which layer owes a requirement, computed from `layers:` and `link_direction`, never tagged by hand.

A requirement whose path goes back (`<-field`) to kinds that only a later layer holds may be met by that layer, so it is work,
never a fault (decision checks-fault-landing-work). The later layer owes it only when every alternative path crosses; when one
can be met in reach of the entry's own layer, it is that layer's work. A forward hop never crosses: a link names its own layer
or an earlier one.
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


def _crossed(kinds: Mapping[str, Kind], declared: Declared, name: str, path: tuple[str, ...], later: set[str]) -> str | None:
    """The earliest later layer one path goes back into from an entry of `name`; None: the path stays in reach of its layer."""
    here = {name}
    for hop in path:
        if hop.startswith(VALUE):
            return None
        here = _hop(kinds, declared, here, hop)
        homes = [kind_layers(kinds, reached) for reached in here]
        if hop.startswith(BACK) and here and all(home and home <= later for home in homes):
            return min(frozenset().union(*homes), key=declared.layers.index)
    return None


def _paths_crossed(kinds: Mapping[str, Kind], declared: Declared, name: str, need: Requirement, layer: str) -> list[str | None]:
    """For each alternative path of the requirement, the later layer it crosses into from `layer`, or None."""
    if layer not in declared.layers or not need.path:
        return []
    later = set(declared.layers[declared.layers.index(layer) + 1 :])
    return [_crossed(kinds, declared, name, tuple(path), later) for path in need.paths]


def owed_by(kinds: Mapping[str, Kind], declared: Declared, name: str, need: Requirement, layer: str) -> str | None:
    """The later layer that owes the requirement of an entry of `name` in `layer`: only when every alternative path crosses into
    one (the earliest of them); None, the entry's own layer, when some path can be met without a later layer."""
    found = _paths_crossed(kinds, declared, name, need, layer)
    if not found or None in found:
        return None
    return min((item for item in found if item is not None), key=declared.layers.index)


def crosses(kinds: Mapping[str, Kind], declared: Declared, name: str, need: Requirement) -> bool:
    """Some path of the requirement crosses into a later layer from some layer the kind may live in: a later layer can meet it,
    so it is work, never a fault (owed by that layer only when every path crosses, `owed_by`)."""
    return any(any(_paths_crossed(kinds, declared, name, need, layer)) for layer in kind_layers(kinds, name))


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
