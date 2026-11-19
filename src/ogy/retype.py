"""Kind renames: a kind file that renamed its kind declares the old name, `was: {kind, file, key}`, until the knowledge bases it
serves are migrated. Under the old name an entry lived in another folder (`<layer>/<area>/<old kind>/<id>.yml`), another list or
single file (`was.file`) or under another key of its parent (`was.key`), and every address that names it holds the old kind.

`retype` is the rename on the files themselves, before any entry is read: the paths (the built record's too), the part keys
inside the entries and every address in a value or a mapping key. A removed ledger keeps the names its items had. `ogy check`
reports a file it would change as `needs-migration`, `ogy migrate` writes it, and `check --base` reads the base through it."""

from collections.abc import Mapping

import any_yaml

from ogy.kinds import Holds, Kind, Shape
from ogy.layout import BUILT_DIR, REMOVED_FILE
from ogy.ontology import Ontology

type Files = Mapping[str, str]


class Retype:
    """The kind renames one ontology declares, as functions on addresses, paths and file contents."""

    def __init__(self, ontology: Ontology) -> None:
        self.ontology = ontology
        self.kinds = ontology.renamed_kinds()  # old name -> the kind now
        self.files = {kind.was.file: kind.file for kind in self.kinds.values() if kind.was and kind.was.file and kind.file}
        self.marks = (*(f"/{old}" for old in self.kinds), *(f"{kind.was.key}:" for kind in self.kinds.values()
                                                            if kind.was and kind.was.key))

    def address(self, text: str, back: bool = False) -> str:
        """`text` with every old kind name in an address renamed (`back`: every new name given its old one); any other text stays."""
        segments = text.split("/")
        head = 2 if segments[0] in self.ontology.layers else 1 if segments[0] in self.ontology.fixed_folders() else 0
        if not head or len(segments) < head + 2:
            return text
        at = head
        while at < len(segments):
            kind = self.kinds.get(segments[at]) if not back else None
            kind = kind or self.ontology.get(segments[at])
            if kind is None:
                return text
            segments[at] = kind.was.kind if back and kind.was else kind.kind
            at += 2 if kind.has_id else 1
        return "/".join(segments)

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
        return bool(self.kinds) and rel.rsplit("/", 1)[-1] != REMOVED_FILE and (
            self.path(rel) != rel or any(mark in text for mark in self.marks))

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
            return self._mapping(value, {})
        return value

    def _mapping(self, data: dict[object, object], parts: Mapping[str, Kind]) -> dict[object, object]:
        """The mapping renamed in place, its order kept: a part's old key becomes its key and the part's own entries follow."""
        items = list(data.items())
        data.clear()
        for key, value in items:
            name = parts[key].key if isinstance(key, str) and key in parts else self._value(key)
            data[name] = self._parts(parts[key], value) if isinstance(key, str) and key in parts else self._value(value)
        return data

    def _parts(self, part: Kind, value: object) -> object:
        """The parts under one key, renamed in place (a mapping or a list keeps its YAML style)."""
        if part.holding is Holds.MAP and isinstance(value, dict):
            for key, item in value.items():
                value[key] = self.entry(part, item)
            return value
        if part.holding is Holds.LIST and isinstance(value, list):
            value[:] = [self.entry(part, item) for item in value]
            return value
        return self.entry(part, value)

    def entry(self, kind: Kind, data: object) -> object:
        """One entry's mapping with its parts, renamed."""
        if not isinstance(data, dict):
            return self._value(data)
        parts: dict[str, Kind] = {}
        for part in self.ontology.parts_of(kind.kind):
            parts |= {key: part for key in (part.key, part.was.key if part.was else None) if key}
        return self._mapping(data, parts)

    def text(self, rel: str, text: str) -> str:
        """The file's text under the new names (the same text when nothing changed)."""
        try:
            data = any_yaml.load(text)
        except any_yaml.YAMLError:
            return text
        kind = self.kind_of(self.path(rel))
        if kind is None:
            done = self._value(data)
        elif kind.shape is Shape.LIST and isinstance(data, list):
            data[:] = [self.entry(kind, item) for item in data]
            done = data
        else:
            done = self.entry(kind, data)
        after = any_yaml.dump(done)
        return text if after == any_yaml.dump(any_yaml.load(text)) else after


def retype(ontology: Ontology, files: Files) -> dict[str, str | None]:
    """The files a migration to the new kind names writes: `{path: new text}`, and `{old path: None}` for a file that moved."""
    work = Retype(ontology)
    changed: dict[str, str | None] = {}
    for rel, text in files.items():
        if not work.stale(rel, text):
            continue
        new, after = work.path(rel), work.text(rel, text)
        if new != rel:
            changed[rel] = None
        if new != rel or after != text:
            changed[new] = after
    return changed


def applied(ontology: Ontology, files: Files) -> dict[str, str]:
    """The files as `ogy migrate` leaves them after the kind renames."""
    changes = retype(ontology, files)
    return {**{rel: text for rel, text in files.items() if rel not in changes}, **{rel: text for rel, text in changes.items()
                                                                                  if text is not None}}


def problems(ontology: Ontology, files: Files) -> dict[str, str]:
    """`{path: why}` for every file that still holds an old kind name: `needs-migration` until `ogy migrate`."""
    work = Retype(ontology)
    renamed = ", ".join(f"{old} is now {kind.kind}" for old, kind in sorted(work.kinds.items()))
    return {rel: f"holds old kind names ({renamed}): run `ogy migrate`" for rel, text in files.items()
            if work.stale(rel, text) and (work.path(rel) != rel or work.text(rel, text) != text)}
