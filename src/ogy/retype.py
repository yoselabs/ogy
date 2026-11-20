"""Kind renames and merges: a kind file that renamed its kind declares the old name, `was: {kind, file, key, renamed}`, until
the knowledge bases it serves are migrated; a kind that absorbed several kinds lists them, `was: [{kind: a}, {kind: b}]`. Under
the old name an entry lived in another folder (`<layer>/<area>/<old kind>/<id>.yml`), another list or single file (`was.file`)
or under another key of its parent (`was.key`), held some fields under the old kind's names (`was.renamed`), and every address
that names it holds the old kind. Two files that would become one (a merge of two kinds whose entries share an area and an id)
are a `collision`: nothing moves until one is `ogy move`d to a new id under the kinds before the merge.

`retype` is the rename on the files themselves, before any entry is read: the paths (the built record's too), the part keys
inside the entries and every address in a value or a mapping key. A removed ledger keeps the names its items had. `ogy check`
reports a file it would change as `needs-migration`, `ogy migrate` writes it, and `check --base` reads the base through it."""

from collections import defaultdict
from collections.abc import Mapping
from itertools import product

import any_yaml

from ogy.kinds import Holds, Kind, Shape, Was
from ogy.layout import BUILT_DIR, REMOVED_FILE
lazy from ogy.ontology import Ontology

type Files = Mapping[str, str]
type Parts = Mapping[str, tuple[Kind, Was | None]]  # a key in an entry -> the part kind under it, the old kind it was kept as


class Retype:
    """The kind renames one ontology declares, as functions on addresses, paths and file contents."""

    def __init__(self, ontology: Ontology) -> None:
        self.ontology = ontology
        self.kinds = ontology.renamed_kinds()  # old name -> the kind now
        self.files = {old.file: kind.file for kind in self.kinds.values() for old in kind.was if old.file and kind.file}
        self.marks = (*(f"/{old}" for old in self.kinds), *(f"{old.key}:" for kind in self.kinds.values() for old in kind.was if old.key))

    def _kinds(self, text: str, *, back: bool) -> list[list[str]] | None:
        """Each segment of the address `text` as the names it may have (the old names, with `back`), None for other text."""
        segments = text.split("/")
        head = 2 if segments[0] in self.ontology.layers else 1 if segments[0] in self.ontology.fixed_folders() else 0
        if not head or len(segments) < head + 2:
            return None
        names, at = [[segment] for segment in segments], head
        while at < len(segments):
            kind = (None if back else self.kinds.get(segments[at])) or self.ontology.get(segments[at])
            if kind is None:
                return None
            names[at] = [old.kind for old in kind.was] if back and kind.was else [kind.kind]
            at += 2 if kind.has_id else 1
        return names

    def address(self, text: str) -> str:
        """`text` with every old kind name in an address renamed; any other text stays."""
        names = self._kinds(text, back=False)
        return "/".join(options[0] for options in names) if names else text

    def olds(self, text: str) -> list[str]:
        """Every address the entry at `text` may have had under the old kind names (several for a kind that absorbed several)."""
        names = self._kinds(text, back=True)
        return ["/".join(each) for each in product(*names)] if names else [text]

    def path(self, rel: str) -> str:
        """The file an entry file (or its built record) is at under the new kind names."""
        parts = rel.split("/")
        if parts[0] == BUILT_DIR:
            return f"{BUILT_DIR}/{self.path('/'.join(parts[1:]))}"
        if parts[0] not in self.ontology.layers or len(parts) < 3:
            return rel
        match parts[2:]:
            case [file] if file in self.files:
                return "/".join([*parts[:2], self.files[file]])
            case [folder, file] if folder in self.kinds and self.kinds[folder].shape is Shape.FILE:
                return "/".join([*parts[:2], self.kinds[folder].kind, file])
            case _:
                return rel

    def stale(self, rel: str, text: str) -> bool:
        """The file holds an old name: its path, an address or a part key may change (a cheap test, before any parse)."""
        return (
            bool(self.kinds)
            and rel.rsplit("/", 1)[-1] != REMOVED_FILE
            and (self.path(rel) != rel or any(mark in text for mark in self.marks))
        )

    def was(self, rel: str) -> Was | None:
        """The old kind whose entries an entry file held before the rename (None: the file kept its kind)."""
        parts = rel.split("/")
        if parts[0] not in self.ontology.layers or len(parts) < 3:
            return None
        match parts[2:]:
            case [file] if file in self.files:
                return next(old for kind in self.kinds.values() for old in kind.was if old.file == file)
            case [folder, _] if folder in self.kinds:
                return next(old for old in self.kinds[folder].was if old.kind == folder)
            case _:
                return None

    def kind_of(self, rel: str) -> Kind | None:
        """The kind of the entries a (renamed) entry file holds, None for the built record and any other file."""
        parts = rel.split("/")
        if parts[0] not in self.ontology.layers or len(parts) < 3:
            return None
        match parts[2:]:
            case [file]:
                return self.ontology.file_kind(file)
            case [folder, _]:
                return self.ontology.get(folder)
            case _:
                return None

    def _value(self, value: object) -> object:
        if isinstance(value, str):
            return self.address(value)
        if isinstance(value, list):
            value[:] = [self._value(item) for item in value]
            return value
        if isinstance(value, dict):
            return self._mapping(value, {}, {})
        return value

    def _old(self, text: str) -> Was | None:
        """The old kind an address names its entry by, when that kind was renamed (a `sets` key: the fields it gives follow)."""
        if self.address(text) == text:
            return None
        ends = text.split("/")[-2:]
        return next((old for name in ends if name in self.kinds for old in self.kinds[name].was if old.kind == name), None)

    def _mapping(self, data: dict[object, object], parts: Parts, renames: Mapping[str, str]) -> dict[object, object]:
        """The mapping renamed in place, its order kept: a part's old key becomes its key and the part's own entries follow, an
        old kind's field its new name, and the fields given to an entry named by an old kind theirs."""
        items = list(data.items())
        data.clear()
        for key, value in items:
            if isinstance(key, str) and key in parts:
                part, old = parts[key]
                data[part.key] = self._parts(part, value, old)
            elif isinstance(key, str) and isinstance(value, dict) and (old := self._old(key)) and old.renamed:
                data[self.address(key)] = self._mapping(value, {}, old.renamed)
            else:
                data[renames[key] if isinstance(key, str) and key in renames else self._value(key)] = self._value(value)
        return data

    def _parts(self, part: Kind, value: object, old: Was | None) -> object:
        """The parts under one key, renamed in place (a mapping or a list keeps its YAML style)."""
        if part.holding is Holds.MAP and isinstance(value, dict):
            for key, item in value.items():
                value[key] = self.entry(part, item, old)
            return value
        if part.holding is Holds.LIST and isinstance(value, list):
            value[:] = [self.entry(part, item, old) for item in value]
            return value
        return self.entry(part, value, old)

    def entry(self, kind: Kind, data: object, old: Was | None = None) -> object:
        """One entry's mapping with its parts, renamed; `old`: the kind it was written under, whose own field names follow and
        whose defaults fill the fields it lacks."""
        if not isinstance(data, dict):
            return self._value(data)
        parts: dict[str, tuple[Kind, Was | None]] = {}
        for part in self.ontology.parts_of(kind.kind):
            parts |= {part.key: (part, None)} if part.key else {}
            parts |= {was.key: (part, was) for was in part.was if was.key}  # only an old key tells an old part from a new one
        done = self._mapping(data, parts, old.renamed if old else {})
        for field, value in old.defaults.items() if old else ():
            done.setdefault(field, value)
        return done

    def text(self, rel: str, text: str) -> str:
        """The file's text under the new names (the same text when nothing changed)."""
        try:
            data = any_yaml.load(text)
        except any_yaml.YAMLError:
            return text
        kind, old = self.kind_of(self.path(rel)), self.was(rel)
        if kind is None:
            done = self._value(data)
        elif kind.shape is Shape.LIST and isinstance(data, list):
            data[:] = [self.entry(kind, item, old) for item in data]
            done = data
        else:
            done = self.entry(kind, data, old)
        after = any_yaml.dump(done)
        return text if after == any_yaml.dump(any_yaml.load(text)) else after


def collisions(ontology: Ontology, files: Files) -> dict[str, str]:
    """`{path: why}` for the files a migration would write over each other: two entries of kinds merged into one, with one area
    and id, or an entry moving onto a file that is already there. The built records of these entries stay with them."""
    work, onto = Retype(ontology), defaultdict[str, list[str]](list)
    for rel in (rel for rel in files if rel.split("/")[0] != BUILT_DIR):
        onto[work.path(rel) if work.stale(rel, files[rel]) else rel].append(rel)
    found: dict[str, str] = {}
    for new, rels in onto.items():
        moving = sorted(rel for rel in rels if rel != new)
        if len(rels) < 2:
            continue
        if new in rels:
            why = (
                f"{' and '.join(map(_named, moving))} would move onto {_named(new)}, which is already there: `ogy move` one "
                "of them to a new id first"
            )
        else:
            why = (
                f"{' and '.join(map(_named, moving))} would both become {_named(new)}: `ogy move` one of them to a new id "
                "first, with the ogy version (its kinds) from before the merge"
            )
        found |= dict.fromkeys(rels, why)
    return found


def _named(rel: str) -> str:
    """The address of the entry a file of one entry holds, else the path."""
    parts = rel.split("/")
    return rel.removesuffix(".yml") if len(parts) == 4 else rel


def retype(ontology: Ontology, files: Files, stuck: Mapping[str, str] | None = None) -> dict[str, str | None]:
    """The files a migration to the new kind names writes: `{path: new text}`, and `{old path: None}` for a file that moved. A
    file in a collision (`stuck`, computed when not given) and its built record stay where they are."""
    work, stuck = Retype(ontology), collisions(ontology, files) if stuck is None else stuck
    held = {*stuck, *(f"{BUILT_DIR}/{rel}" for rel in stuck)}
    changed: dict[str, str | None] = {}
    for rel, text in files.items():
        if rel in held or not work.stale(rel, text):
            continue
        new, after = work.path(rel), work.text(rel, text)
        if new != rel:
            changed[rel] = None
        if new != rel or after != text:
            changed[new] = after
    return changed


def applied(ontology: Ontology, files: Files, stuck: Mapping[str, str] | None = None) -> dict[str, str]:
    """The files as `ogy migrate` leaves them after the kind renames."""
    changes = retype(ontology, files, stuck)
    return {
        **{rel: text for rel, text in files.items() if rel not in changes},
        **{rel: text for rel, text in changes.items() if text is not None},
    }


def problems(ontology: Ontology, files: Files) -> dict[str, str]:
    """`{path: why}` for every file that still holds an old kind name: `needs-migration` until `ogy migrate`, or until one of
    two files that would become one is moved."""
    work = Retype(ontology)
    renamed = ", ".join(f"{old} is now {kind.kind}" for old, kind in sorted(work.kinds.items()))
    return {
        rel: f"holds old kind names ({renamed}): run `ogy migrate`"
        for rel, text in files.items()
        if work.stale(rel, text) and (work.path(rel) != rel or work.text(rel, text) != text)
    } | collisions(ontology, files)
