"""Load-time lints on a kind's migration declarations: renamed, dropped, revalued and absorbed kinds, and moves."""

lazy from collections.abc import Mapping

from ogy.kinds import FILED, KIND_NAME, NAME, RESERVED_AREAS, FieldType, Kind, Shape, Was
lazy from ogy.declared import Declared


def migration(declared: Declared, name: str, kind: Kind) -> list[str]:
    """A renamed field's old name is no field, its new one is; a dropped field is no field and was not renamed."""
    found = [
        f"{name}: renamed {old} is still a field or common to every kind"
        for old in kind.old_names
        if old in kind.fields or old in declared.common
    ]
    found += [f"{name}: renamed {old} to {new}, which is no field" for old, new in kind.renamed.items() if new not in kind.fields]
    found += [f"{name}: {old} is both renamed and dropped" for old in kind.dropped if old in kind.renamed]
    found += [
        f"{name}: revalued or folded {field}, which is no field" for field in (*kind.revalued, *kind.folded) if field not in kind.fields
    ]
    found += [
        f"{name}: widened {field}, which is no links field"
        for field in kind.widened
        if field not in kind.fields or kind.fields[field].type is not FieldType.LINKS
    ]
    return found


def was(kinds: Mapping[str, Kind], declared: Declared, name: str, kind: Kind) -> list[str]:
    """A renamed kind's old name is no kind any more and no other kind's old name; an old file belongs to a list or single kind
    and an old key to a part; a kind that absorbed several kinds keeps one file per entry; an old kind's renamed field is now a
    field."""
    found: list[str] = (
        [f"{name}: a kind that absorbed several kinds has shape file"] if len(kind.was) > 1 and kind.shape is not Shape.FILE else []
    )
    for old in kind.was:
        found += (
            [f"{name}: was {old.kind}, which is still a kind or no snake_case name"]
            if old.kind in kinds or not KIND_NAME.match(old.kind)
            else []
        )
        found += (
            [f"{name}: was {old.kind}, as another kind was"]
            if sum(other.kind == old.kind for each in kinds.values() for other in each.was) > 1
            else []
        )
        if old.file is not None and (kind.shape not in FILED or not old.file.endswith(".yml") or old.file == kind.file):
            found.append(f"{name}: was.file is the other .yml file a list or single kind kept its entries in")
        if old.key is not None and (kind.shape is not Shape.INLINE or old.key == kind.key):
            found.append(f"{name}: was.key is the other key a part was kept under")
        found += _was_fields(declared, name, kind, old)
    return found


def _was_fields(declared: Declared, name: str, kind: Kind, old: Was) -> list[str]:
    """An old kind's renamed field is now a field and was none, two old fields never become one, a default fills a field;
    either needs the old entries told apart from the new: by their folder (shape file), their old file or their old key."""
    fields = {*kind.fields, *declared.common}
    found = [
        f"{name}: was {old.kind} renamed {field} to {new}, which is no field" for field, new in old.renamed.items() if new not in fields
    ]
    found += [f"{name}: was {old.kind} renamed {field}, which is still a field" for field in old.renamed if field in fields]
    found += [
        f"{name}: was {old.kind} renamed two fields to {new}"
        for new in set(old.renamed.values())
        if list(old.renamed.values()).count(new) > 1
    ]
    found += [f"{name}: was {old.kind} defaults {field}, which is no field" for field in old.defaults if field not in kind.fields]
    if (old.renamed or old.defaults) and kind.shape is not Shape.FILE and not old.file and not old.key:
        found.append(f"{name}: was {old.kind} renames or defaults fields only with a new folder, file or key to tell its entries by")
    return found


def moved(name: str, kind: Kind) -> list[str]:
    """A kind may live in `shared` only under a layer; one that moved out of a fixed folder names `<folder>/<file>.yml` and moves
    there, so it is a list kind that may live in `shared`."""
    found = [f"{name}: shared belongs to kinds that live under a layer"] if kind.shared and (kind.area or not kind.layers) else []
    if kind.moved_from is None:
        return found
    folder, _, file = kind.moved_from.partition("/")
    if not NAME.match(folder) or folder in RESERVED_AREAS or "/" in file or not file.endswith(".yml"):
        found.append(f"{name}: moved_from is `<folder>/<file>.yml`, the fixed-folder file it was kept in")
    if kind.shape is not Shape.LIST or not kind.shared:
        found.append(f"{name}: moved_from belongs to a list kind that may live in shared")
    return found
