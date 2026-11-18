"""Load-time lints on the kinds themselves: every problem is a sentence, none is fixed or guessed."""

from collections.abc import Mapping

from ogy.kinds import ANY, COMMON_FIELDS, FILED, KIND_NAME, LINKING, NAME, RESERVED_AREAS, FieldSpec, FieldType, Kind, Shape

# Facts the tool computes; no kind may store them (K22).
STORED_STATE = frozenset({
    "open", "assumed", "origin", "status", "author", "agreement", "built", "covers", "sourced", "in", "retired",
    "accepted_by", "renamed_from", "actors", "subject", "id", "settles", "settled_by", "came_from", "removed",
    "replaced_by", "superseded", "superseded_by", "deprecated", "restored", "scope", "history", "changelog", "last_seen",
})
SENTENCE_NAMES = frozenset({"states", "means", "holds", "does", "provides", "shows", "goal"})  # the sentence is `says` (K25)
REMOVED_FILE = "removed.yml"


def problems(kinds: Mapping[str, Kind], layers: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    fixed = {kind.area for kind in kinds.values() if kind.area}
    found += [f"layer {layer!r} is no valid folder name" for layer in layers
              if not NAME.match(layer) or layer in RESERVED_AREAS or layer in fixed]
    if not layers:
        found.append("the ontology declares no layers")
    for name, kind in kinds.items():
        found += [f"{name}: layer {layer!r} is not a layer of the ontology" for layer in kind.layers if layer not in layers]
        found += _shape(kinds, name, kind) + _per_area(name, kind)
        found += _fields(kinds, name, kind)
        found += _rules(kinds, name, kind)
    found += _files(kinds)
    found += _keys(kinds)
    found += _settling(kinds)
    found += _link_direction(kinds)
    return found


def _shape(kinds: Mapping[str, Kind], name: str, kind: Kind) -> list[str]:
    found: list[str] = []
    if name != kind.kind or not KIND_NAME.match(name) or name == ANY:
        found.append(f"{name}: kind name must match its file, be snake_case and not be `{ANY}`")
    if "?" in name:
        found.append(f"{name}: no name contains `?`")
    inline = kind.shape is Shape.INLINE
    if inline and (not kind.part_of or kind.key is None):
        found.append(f"{name}: an inline kind needs part_of and key")
    if not inline and (kind.part_of or kind.key is not None or kind.holds is not None):
        found.append(f"{name}: part_of, key and holds belong to inline kinds only")
    if inline and kind.area is not None:
        found.append(f"{name}: area belongs to entity and list kinds")
    found += [f"{name}: part_of names unknown kind {parent}" for parent in kind.part_of if parent not in kinds]
    if kind.area is not None and (not NAME.match(kind.area) or kind.area in RESERVED_AREAS):
        found.append(f"{name}: area {kind.area!r} is no valid area name")
    if kind.append_only and not (inline and kind.holding.value == "list"):
        found.append(f"{name}: append_only belongs to inline kinds that hold a list")
    if inline and kind.layers:
        found.append(f"{name}: layers belong to entity and list kinds; a part is in its parent's layer")
    if not inline and kind.area is None and not kind.layers:
        found.append(f"{name}: an entity or list kind declares the layers it may appear in")
    if kind.area is not None and kind.layers:
        found.append(f"{name}: a kind in the fixed folder {kind.area} has no layers")
    return found


def _per_area(name: str, kind: Kind) -> list[str]:
    """`every_area` and the single shape need areas; a kind never asked needs no agreement."""
    found: list[str] = []
    if (kind.every_area or kind.shape is Shape.SINGLE) and (kind.shape is Shape.INLINE or kind.area is not None):
        found.append(f"{name}: every_area and the single shape belong to kinds that live under a layer, in areas")
    if kind.must_be_agreed and not kind.asked:
        found.append(f"{name}: a kind that is never asked cannot need agreement")
    return found


def _fields(kinds: Mapping[str, Kind], name: str, kind: Kind) -> list[str]:
    found: list[str] = []
    for field, spec in kind.fields.items():
        where = f"{name}.{field}"
        if field in COMMON_FIELDS or field == "id":
            found.append(f"{where}: common to every kind")
        if field in STORED_STATE:
            found.append(f"{where}: {field} is computed, never stored")
        if field in SENTENCE_NAMES:
            found.append(f"{where}: the sentence is `says`")
        if "?" in field or any("?" in member for member in spec.of):
            found.append(f"{where}: no name contains `?`")
        found += _spec(kinds, where, spec)
    return found


def _spec(kinds: Mapping[str, Kind], where: str, spec: FieldSpec) -> list[str]:
    found: list[str] = []
    if (spec.type in LINKING) != bool(spec.to):
        found.append(f"{where}: link and expr fields, and only they, name target kinds in `to`")
    found += [f"{where}: links to unknown kind {target}" for target in spec.to if target != ANY and target not in kinds]
    if (spec.type is FieldType.ENUM) != bool(spec.of):
        found.append(f"{where}: enum fields, and only they, list their members in `of`")
    if (spec.type is FieldType.URI) != bool(spec.schemes):
        found.append(f"{where}: uri fields, and only they, list their `schemes`")
    return found


def _rules(kinds: Mapping[str, Kind], name: str, kind: Kind) -> list[str]:
    found: list[str] = []
    for group in kind.exactly_one_of:
        found += [f"{name}: exactly_one_of names no field {field}" for field in group if field not in kind.fields]
    for need in kind.requires:
        if need.if_set is not None and need.if_set not in kind.fields:
            found.append(f"{name}: requirement if_set names no field {need.if_set}")
        if need.if_part is not None and not (need.if_part in kinds and kinds[need.if_part].is_part(name)):
            found.append(f"{name}: requirement if_part names no part kind {need.if_part}")
        found += [f"{name}: requirement names unknown kind {target}" for target in need.kinds if target not in kinds]
    if kind.one_part is not None and kind.one_part.kind not in kinds:
        found.append(f"{name}: one_part names unknown kind {kind.one_part.kind}")
    return found


def _files(kinds: Mapping[str, Kind]) -> list[str]:
    found: list[str] = []
    seen: dict[str, str] = {}
    for name, kind in kinds.items():
        if kind.shape not in FILED:
            if kind.file is not None:
                found.append(f"{name}: file belongs to list and single kinds")
            continue
        if kind.file is None or "/" in kind.file or not kind.file.endswith(".yml"):
            found.append(f"{name}: a list or single kind names its file, `<name>.yml`")
            continue
        if kind.file in seen:
            found.append(f"{name}: file {kind.file} is also the file of {seen[kind.file]}")
        if kind.file == REMOVED_FILE or (kind.shape is Shape.LIST and kind.file.removesuffix(".yml") in kinds):
            found.append(f"{name}: file {kind.file} equals a kind name or the removed ledger")
        seen[kind.file] = name
    return found


def _keys(kinds: Mapping[str, Kind]) -> list[str]:
    """Under one parent, part keys are distinct, are no field of the parent and contain no `?`."""
    found: list[str] = []
    for parent, owner in kinds.items():
        keys: dict[str, str] = {}
        for name, kind in kinds.items():
            if not kind.is_part(parent) or kind.key is None:
                continue
            if "?" in kind.key:
                found.append(f"{name}: no name contains `?`")
            if kind.key in keys or kind.key in owner.fields or kind.key in COMMON_FIELDS:
                found.append(f"{name}: key {kind.key!r} is already used inside {parent}")
            keys[kind.key] = name
    return found


def _field_of(kinds: Mapping[str, Kind], kind: str, field: str) -> bool:
    return kind in kinds and field in kinds[kind].fields


def _settling(kinds: Mapping[str, Kind]) -> list[str]:
    settlers = [(name, kind) for name, kind in kinds.items() if kind.settling is not None]
    if len(settlers) > 1:
        return ["at most one kind settles entries (`settling:`)"]
    if not settlers or settlers[0][1].settling is None:
        return []
    name, settling = settlers[0][0], settlers[0][1].settling
    found = [f"{name}: settling names no kind {item}" for item in (settling.option, settling.answer, settling.guess)
             if item not in kinds]
    wanted = [(settling.option, settling.sets), (settling.answer, settling.chose), (settling.answer, settling.said),
              (settling.answer, settling.who), (settling.answer, settling.at), (settling.answer, settling.where),
              (settling.guess, settling.chose), (settling.guess, settling.value)]
    found += [f"{name}: settling names no field {kind}.{field}" for kind, field in wanted if not _field_of(kinds, kind, field)]
    return found


def _links_to(kind: Kind) -> set[str]:
    return {target for spec in kind.fields.values() if spec.type in LINKING for target in spec.to if target != ANY}


def _link_direction(kinds: Mapping[str, Kind]) -> list[str]:
    """Two kinds may not link to each other, except a part and its parent (K24)."""
    found: list[str] = []
    links = {name: _links_to(kind) for name, kind in kinds.items()}
    for first in sorted(kinds):
        for second in sorted(links[first]):
            if second <= first or second not in kinds or first not in links[second]:
                continue
            if not (kinds[first].is_part(second) or kinds[second].is_part(first)):
                found.append(f"{first} and {second} link to each other; a link has one direction")
    return found
