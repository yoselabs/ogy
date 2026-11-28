"""Load-time lints on the kinds themselves: every problem is a sentence, none is fixed or guessed."""

lazy from collections.abc import Mapping

from ogy.kindlint_change import migration, moved, was
from ogy.kinds import (
    ANY,
    FILED,
    KIND_NAME,
    LINKING,
    NAME,
    RESERVED_AREAS,
    FieldSpec,
    FieldType,
    Holds,
    Input,
    Kind,
    Picked,
    ProofWhen,
    Requirement,
    Shape,
    where,
)
lazy from ogy.declared import Declared

REMOVED_FILE = "removed.yml"


def problems(kinds: Mapping[str, Kind], declared: Declared) -> list[str]:
    found: list[str] = []
    layers = declared.layers
    fixed = {kind.area for kind in kinds.values() if kind.area} | {kind.moved_folder for kind in kinds.values() if kind.moved_folder}
    found += [
        f"layer {layer!r} is no valid folder name"
        for layer in layers
        if not NAME.match(layer) or layer in RESERVED_AREAS or layer in fixed or layer == declared.shared.area
    ]
    if not NAME.match(declared.shared.area) or declared.shared.area in RESERVED_AREAS:
        found.append(f"shared area {declared.shared.area!r} is no valid area name")
    if not layers:
        found.append("the ontology declares no layers")
    for name, kind in kinds.items():
        found += [f"{name}: layer {layer!r} is not a layer of the ontology" for layer in kind.layers if layer not in layers]
        found += _shape(kinds, name, kind) + _per_area(name, kind)
        found += _fields(kinds, declared, name, kind)
        found += _rules(kinds, name, kind) + _inputs(kinds, declared, name, kind)
        found += migration(declared, name, kind) + moved(name, kind) + was(kinds, declared, name, kind)
    found += [
        problem for field, spec in declared.common.items() for problem in _picked(kinds, f"common {field}", spec, spec.input, common=True)
    ]
    found += _files(kinds)
    found += _keys(kinds, declared)
    found += _settling(kinds) + _roles(kinds)
    found += _link_direction(kinds)
    found += [
        f"{name}: flow group {kind.flow.group} is no link field of the kind"
        for name, kind in kinds.items()
        if kind.flow is not None
        and kind.flow.group is not None
        and (kind.flow.group not in kind.fields or kind.fields[kind.flow.group].type not in {FieldType.LINK, FieldType.LINKS})
    ]
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
        found.append(f"{name}: area belongs to file and list kinds")
    found += [f"{name}: part_of names unknown kind {parent}" for parent in kind.part_of if parent not in kinds]
    if kind.area is not None and (not NAME.match(kind.area) or kind.area in RESERVED_AREAS):
        found.append(f"{name}: area {kind.area!r} is no valid area name")
    if kind.append_only and not (inline and kind.holding.value == "list"):
        found.append(f"{name}: append_only belongs to inline kinds that hold a list")
    if inline and kind.layers:
        found.append(f"{name}: layers belong to file and list kinds; a part is in its parent's layer")
    if not inline and kind.area is None and not kind.layers:
        found.append(f"{name}: a file or list kind declares the layers it may appear in")
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


def _fields(kinds: Mapping[str, Kind], declared: Declared, name: str, kind: Kind) -> list[str]:
    found = [f"{name}: harm {tag} is no harm of the ontology" for tag in kind.harm if tag not in declared.harms]
    for field, spec in kind.fields.items():
        where = f"{name}.{field}"
        if field in declared.common or field == "id":
            found.append(f"{where}: common to every kind")
        if field in declared.reserved.computed:
            found.append(f"{where}: {field} is computed, never stored")
        if field in declared.reserved.sentence:
            found.append(f"{where}: another name for a sentence; the kind names its sentence field")
        found += [f"{where}: harm {tag} is no harm of the ontology" for tag in spec.harm if tag not in declared.harms]
        found += [f"{where}: member {member} is not in of" for member in spec.member_harm if member not in spec.of]
        found += [
            f"{where}: harm {tag} of {member} is no harm of the ontology"
            for member, tags in spec.member_harm.items()
            for tag in tags
            if tag not in declared.harms
        ]
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
    return found + _picked(kinds, where, spec, spec.input)


def _picked(kinds: Mapping[str, Kind], where: str, spec: FieldSpec, given: Input | Picked | None, *, common: bool = False) -> list[str]:
    """An input is declared on a link or expr field; `address` only on a note or a common field (a kind's own field that is not
    a note has the address in the meaning already); a picked one names fields, or part kinds, of every kind it links to."""
    if given in (None, Input.NONE):
        return []
    if spec.type not in LINKING:
        return [f"{where}: only a link or expr field is an input"]
    if given is Input.ADDRESS and not (spec.note or common):
        return [f"{where}: input address on a field that is not a note is the meaning already; say none"]
    if not isinstance(given, Picked):
        return []
    targets = [kinds[target] for target in spec.to if target in kinds]
    return (
        [
            f"{where}: input picks {field}, no field of {target.kind}"
            for field in given.fields
            for target in targets
            if field not in target.fields
        ]
        + [
            f"{where}: input picks {part}, no part of {target.kind}"
            for part in given.parts
            for target in targets
            if not (part in kinds and kinds[part].is_part(target.kind))
        ]
        + [
            f"{where}: input picks {field}, {_SOME.format(target.kind)}"
            for field in given.fields
            for target in targets
            if field in _partial(target)
        ]
    )


_SOME = "which {} took from only some of the kinds it absorbed (`was.renamed`); a build before the merge has no one name for it"


def _partial(kind: Kind) -> set[str]:
    """The fields a kind that absorbed several has under a name that not every old kind's `was.renamed` gives it: a picked input
    of one cannot be read back under a single old name."""
    news = {new for old in kind.was for new in old.renamed.values()} if len(kind.was) > 1 else set()
    return {new for new in news if any(new not in old.renamed.values() for old in kind.was)}


def _inputs(kinds: Mapping[str, Kind], declared: Declared, name: str, kind: Kind) -> list[str]:
    """A kind's `input` names a common field or one of its part kinds (not both; a part is read whole or by address);
    `input_from` names a link field that leads here and picks fields of the kinds that hold it; a kind that needs proof
    states the input of each of its link fields, its own and the common ones (in `ontology.yml` or its `input` map)."""
    found: list[str] = []
    for key, given in kind.input.items():
        where, part = f"{name}.input.{key}", key in kinds and kinds[key].is_part(name)
        if key in kind.fields:
            found.append(f"{where}: a field of its own declares its input itself")
        elif (key in declared.common) == part:
            found.append(f"{where}: names a common field or a part kind, one of them")
        elif part and isinstance(given, Picked):
            found.append(f"{where}: a part is an input whole (content) or by address")
        elif not part:
            found += _picked(kinds, where, declared.common[key], given, common=True)
    for key, picked in kind.input_from.items():
        holders = [
            other
            for other in kinds.values()
            if (spec := {**declared.common, **other.fields}.get(key)) is not None and {name, ANY} & set(spec.to)
        ]
        if not holders or picked.parts:
            found.append(f"{kind.kind}.input_from.{key}: names a link field that leads here, and picks fields of its holders")
        found += [
            f"{name}.input_from.{key}: picks {field}, no field of a kind linking here by {key}"
            for field in picked.fields
            if holders and not any(field in other.fields for other in holders)
        ]
        found += [
            f"{name}.input_from.{key}: {field}, {_SOME.format(other.kind)}"
            for other in holders
            for field in (key, *picked.fields)
            if field in _partial(other)
        ]
    when = kind.needs_proof if isinstance(kind.needs_proof, ProofWhen) else None
    if when is not None and not (when.if_part in kinds and kinds[when.if_part].is_part(name)):
        found.append(f"{name}: needs_proof if_part names no part kind {when.if_part}")
    if kind.proves:
        found += [
            f"{name}.{field}: a link field of a kind that needs proof states its input (none, address or content)"
            for field, spec in {**declared.common, **kind.fields}.items()
            if spec.type in LINKING and spec.input is None and field not in kind.input
        ]
    return found


def _rules(kinds: Mapping[str, Kind], name: str, kind: Kind) -> list[str]:
    found: list[str] = []
    for group in kind.exactly_one_of:
        found += [f"{name}: exactly_one_of names no field {field}" for field in group if field not in kind.fields]
    found += [
        f"{name}: acyclic names {field}, no link field of the kind to its own kind"
        for field in kind.acyclic
        if field not in kind.fields or kind.fields[field].type not in (FieldType.LINK, FieldType.LINKS) or name not in kind.fields[field].to
    ]
    for need in kind.requires:
        found += [
            f"{name}: requirement {key} names no field {field}"
            for key, field in (("if_set", need.if_set), ("if_unset", need.if_unset))
            if field is not None and field not in kind.fields
        ]
        if need.if_part is not None and not (need.if_part in kinds and kinds[need.if_part].is_part(name)):
            found.append(f"{name}: requirement if_part names no part kind {need.if_part}")
        found += [f"{name}: requirement names unknown kind {target}" for target in need.kinds if target not in kinds and target != ANY]
        found += _requirement(kinds, name, kind, need)
    if kind.one_part is not None and kind.one_part.kind not in kinds:
        found.append(f"{name}: one_part names unknown kind {kind.one_part.kind}")
    return found


def _requirement(kinds: Mapping[str, Kind], name: str, kind: Kind, need: Requirement) -> list[str]:
    """`if_equals` names a field and, for an enum, its members; `needs_field` a field; each of `without` is a field of one of
    `kinds`; an item of a list part has no address, so its path starts at one of its link fields and its condition is a field."""
    found: list[str] = []
    if (equals := need.if_equals) is not None:
        spec = kind.fields.get(equals.field)
        if spec is None:
            found.append(f"{name}: requirement if_equals names no field {equals.field}")
        elif spec.type is FieldType.ENUM:
            found += [
                f"{name}: requirement if_equals: {value} is no member of {equals.field}" for value in equals.values if value not in spec.of
            ]
    if need.needs_field is not None and need.needs_field not in kind.fields:
        found.append(f"{name}: requirement needs_field names no field {need.needs_field}")
    found += [
        f"{name}: requirement without names {field}, no field of {list(need.kinds)}"
        for field in need.without
        if not any(field in kinds[target].fields for target in need.kinds if target in kinds)
    ]
    # the kinds come here with `ogy.owing.derived` applied: a requirement a later layer owes is already work
    if need.work and need.status is None:
        found.append(f"{name}: requirement {need.error!r} goes back to kinds only a later layer holds, so it is work: name its status")
    if kind.shape is Shape.INLINE and kind.holding is Holds.LIST:
        if need.if_part is not None:
            found.append(f"{name}: an item of a list part holds no parts, so no requirement has if_part")
        if any(
            path and (where(path[0])[0] not in kind.fields or kind.fields[where(path[0])[0]].type not in (FieldType.LINK, FieldType.LINKS))
            for path in (*need.paths, need.if_reaches)
        ):
            found.append(f"{name}: the path of an item of a list part starts at one of its link fields")
        if need.work:
            found.append(f"{name}: an item of a list part has no address, so no requirement of it is work")
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


def _keys(kinds: Mapping[str, Kind], declared: Declared) -> list[str]:
    """Under one parent, part keys are distinct, are no field of the parent and contain no `?`."""
    found: list[str] = []
    for parent, owner in kinds.items():
        keys: dict[str, str] = {}
        for name, kind in kinds.items():
            if not kind.is_part(parent) or kind.key is None:
                continue
            if "?" in kind.key:
                found.append(f"{name}: no name contains `?`")
            if kind.key in keys or kind.key in owner.fields or kind.key in declared.common:
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
    found = [
        f"{name}: settling names no kind {item}" for item in (settling.option, settling.answer, settling.proposal) if item not in kinds
    ]
    wanted = [
        (settling.option, settling.sets),
        (settling.answer, settling.chose),
        (settling.answer, settling.said),
        (settling.answer, settling.at),
        (settling.answer, settling.where),
        (settling.proposal, settling.chose),
        (name, settling.context),
        (settling.proposal, settling.why),
        (settling.proposal, settling.heard),
    ]
    found += [f"{name}: settling names no field {kind}.{field}" for kind, field in wanted if not _field_of(kinds, kind, field)]
    return found


def _roles(kinds: Mapping[str, Kind]) -> list[str]:
    """A sentence is a text field of its kind; the glossary and the printed-first kind are one kind each, with a sentence, and
    name their own fields."""
    found = [
        f"{name}: sentence {kind.sentence} is no text field"
        for name, kind in kinds.items()
        if kind.sentence is not None and (kind.sentence not in kind.fields or kind.fields[kind.sentence].type is not FieldType.TEXT)
    ]
    glossary = [(name, kind, kind.glossary) for name, kind in kinds.items() if kind.glossary]
    printed = [(name, kind, kind.printed_first) for name, kind in kinds.items() if kind.printed_first]
    found += ["at most one kind is the glossary"] if len(glossary) > 1 else []
    found += ["at most one kind is printed first"] if len(printed) > 1 else []
    for name, kind, role in glossary:
        found += [f"{name}: glossary names no field {field}" for field in (role.word, role.avoid) if field not in kind.fields]
        if role.names is not None and (role.names not in kind.fields or kind.fields[role.names].type is not FieldType.LINK):
            found.append(f"{name}: glossary names {role.names}, no link field of the kind")
        found += [f"{name}: the glossary kind names its sentence"] if kind.sentence is None else []
    for name, kind, role in printed:
        found += [f"{name}: printed_first names no field {role.also}"] if role.also and role.also not in kind.fields else []
        found += [f"{name}: the printed-first kind names its sentence"] if kind.sentence is None else []
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
