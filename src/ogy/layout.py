"""Where files live, as the ontology declares it: `<layer>/<area>/<kind>/<id>.yml` (a list or single kind: `<layer>/<area>/<file>`), a fixed
folder for a kind that names one (`constitution/<file>`), a home's `removed.yml`, and the `built/` record. Every file under the
knowledge base is one of these; any other is `bad-path`, and no level can be skipped. The reserved area `shared` of a layer holds
only the kinds marked `shared`. A kind that moved out of a fixed folder (`moved_from`) is read there until `ogy migrate` moves it."""

from collections.abc import Mapping
from dataclasses import dataclass

import any_yaml

from ogy.kinds import FILED, NAME, Holds, Kind, Shape
from ogy.model import Address, Entry, Finding, Problem
from ogy.ontology import Ontology

SUFFIX = ".yml"
BUILT_DIR = "built"  # the tool-written built record: read by its owner, never by this reader
REMOVED_FILE = "removed.yml"  # a home's removed ledger: a core file, not an entry file


@dataclass(frozen=True)
class Place:
    """What a path says: the layer (empty in a fixed folder), the area, the kind and, for an entity or single file, the id (None for a
    list file; a single kind's id is the area's name)."""

    layer: str
    area: str
    kind: Kind
    ident: str | None

    @property
    def home(self) -> str:
        return f"{self.layer}/{self.area}" if self.layer else self.area


def _kind_at(ontology: Ontology, tail: list[str]) -> tuple[Kind, str | None] | str:
    """The kind and id a path below the home names (`<kind>/<id>.yml` or `<list file>`), or the reason it names none."""
    match tail:
        case [file]:
            kind = ontology.file_kind(file)
            return (kind, None) if kind else f"no list or single kind keeps its entries in {file}"
        case [folder, file]:
            kind = ontology.get(folder)
            return (kind, file.removesuffix(SUFFIX)) if kind and kind.shape is Shape.ENTITY else f"no entity kind {folder!r}"
        case _:
            return "an entry file is <layer>/<area>/<kind>/<id>.yml or <layer>/<area>/<list file>.yml"


def _home(ontology: Ontology, parts: list[str]) -> tuple[str, str, list[str]] | str:
    """The layer (empty in a fixed folder), the area and the rest of a path, or the reason the top of the path is wrong."""
    if parts[0] in ontology.fixed_folders():
        return "", parts[0], parts[1:]
    if parts[0] not in ontology.layers:
        return f"{parts[0]!r} is no layer ({', '.join(ontology.layers)}): an entry file is <layer>/<area>/<kind>/<id>.yml"
    if len(parts) < 3 or not NAME.match(parts[1]):
        return f"an entry file is <layer>/<area>/<kind>/<id>.yml; {parts[0]}/ holds areas (kebab-case folders), not entries"
    return parts[0], parts[1], parts[2:]


def locate(ontology: Ontology, rel: str) -> Place | str | None:
    """Read a path relative to the knowledge-base root: a Place, the reason it is `bad-path`, or None when it is no entry file."""
    parts = rel.split("/")
    if parts[0] == BUILT_DIR:
        return None
    home = _home(ontology, parts)
    if isinstance(home, str):
        return home
    layer, area, tail = home
    if tail == [REMOVED_FILE]:
        return None
    if not layer and (moved := ontology.moved_kind(rel)) is not None:
        return Place(layer, area, moved, None)  # `needs-migration` until `ogy migrate` moves it into the layers
    found = _kind_at(ontology, tail) if rel.endswith(SUFFIX) else f"only {SUFFIX} entry files live here: <layer>/<area>/<kind>/<id>.yml"
    if isinstance(found, str):
        return found
    kind, ident = found
    wrong = _misplaced(ontology, kind, layer, area)
    return wrong or Place(layer, area, kind, area if kind.shape is Shape.SINGLE else ident)


def _misplaced(ontology: Ontology, kind: Kind, layer: str, area: str) -> str | None:
    """Why `kind` may not live in this folder: a fixed folder's kind elsewhere, a layered kind in a fixed folder, or a kind not
    marked `shared` in the area `shared`."""
    if (kind.area or "") != (area if not layer else ""):
        return f"{kind.kind} lives only in the folder {kind.area}" if kind.area else f"{kind.kind} lives under a layer, not in {area}/"
    if area == ontology.shared and layer and not kind.shared:
        allowed = ", ".join(sorted(name for name, other in ontology.kinds.items() if other.shared))
        return f"the area {ontology.shared} holds only what two areas use ({allowed}); {kind.kind} lives in the area that owns it"
    return None


def path_for(kind: Kind, home: str, ident: str) -> str:
    """The file an entry of an entity, list or single kind belongs in, inside the home `<layer>/<area>` (or a fixed folder)."""
    if kind.shape in FILED:
        return f"{home}/{kind.file}"
    return f"{home}/{kind.kind}/{ident}{SUFFIX}"


class FileReader:
    """Turns one file's text into entries, using the ontology for the shape."""

    def __init__(self, ontology: Ontology) -> None:
        self.ontology = ontology
        self.entries: list[Entry] = []
        self.findings: list[Finding] = []

    def read(self, rel: str, text: str) -> None:
        place = locate(self.ontology, rel)
        if place is None:
            return
        if isinstance(place, str):
            self.findings.append(Finding(Problem.BAD_PATH, rel, place))
            return
        try:
            data = any_yaml.load(text)
        except any_yaml.YAMLError as error:
            self.findings.append(Finding(Problem.BAD_YAML, rel, str(error).splitlines()[0]))
            return
        if place.ident is not None:
            self._entry(Address(place.layer, place.area, ((place.kind.kind, place.ident),)), place.kind, data, rel)
        else:
            self._list(place, data, rel)

    def _bad(self, problem: Problem, rel: str, detail: str, address: Address | None = None) -> None:
        self.findings.append(Finding(problem, rel, detail, address))

    def _list(self, place: Place, data: object, rel: str) -> None:
        if not isinstance(data, list):
            self._bad(Problem.BAD_SHAPE, rel, "a list file holds a YAML list")
            return
        for item in data:
            ident = item.get("id") if isinstance(item, dict) else None
            if not isinstance(ident, str):
                self._bad(Problem.MISSING_FIELD, rel, "every list item needs a text id")
                continue
            fields = {k: v for k, v in item.items() if k != "id"}
            self._entry(Address(place.layer, place.area, ((place.kind.kind, ident),)), place.kind, fields, rel)

    def _entry(self, address: Address, kind: Kind, data: object, rel: str) -> None:
        if not isinstance(data, dict):
            self._bad(Problem.BAD_SHAPE, rel, "an entry is a YAML mapping", address)
            return
        if address.key and not NAME.match(address.key):
            self._bad(Problem.BAD_NAME, rel, "names are lowercase kebab-case", address)
        fields = {str(name): value for name, value in data.items()}
        for part in self.ontology.parts_of(kind.kind):
            if part.key is None or part.key not in fields or part.holding is Holds.LIST:
                continue  # a `holds: list` part has no address: the checker reads it from its parent's fields
            raw = fields.pop(part.key)
            if part.holding is Holds.ONE:
                self._entry(address.part(part.kind), part, raw, rel)
            elif isinstance(raw, dict):
                for key, item in raw.items():
                    self._entry(address.part(part.kind, str(key)), part, item, rel)
            else:
                self._bad(Problem.BAD_SHAPE, rel, f"{part.key} is a mapping of {part.kind} by key", address)
        self.entries.append(Entry(address, rel, fields))


def read_files(ontology: Ontology, files: Mapping[str, str]) -> tuple[list[Entry], list[Finding]]:
    """Every entry in `{kb-relative path: text}`, with the findings reading them produced."""
    reader = FileReader(ontology)
    for rel, text in sorted(files.items()):
        reader.read(rel, text)
    return reader.entries, reader.findings
