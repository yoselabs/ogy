"""An ontology: the kinds of one ontology folder, loaded from `kinds/*.yml` and checked against each other."""

from collections.abc import Mapping
from importlib.resources import files

import any_yaml
from pydantic import ValidationError

from ogy import declared as declaring
from ogy.declared import Declared, Roles
from ogy.kindlint import problems
from ogy.kinds import FILED, KINDS_DIR, ONTOLOGY_FILE, FieldSpec, Kind
from ogy.verdict import Unusable

DEFAULT_ONTOLOGY = "software"


class OntologyError(Unusable):
    """The kinds themselves are inconsistent, or no ontology has the name; nothing can be loaded against them."""

    prefix = "the kinds are inconsistent: "


class Ontology:
    """All kinds of one ontology and what its `ontology.yml` declares, checked against each other."""

    def __init__(self, kinds: Mapping[str, Kind], declared: Declared) -> None:
        self.kinds = dict(kinds)
        self.declared = declared
        found = declaring.problems(declared) + problems(self.kinds, declared)
        if found:
            raise OntologyError("; ".join(found))

    @classmethod
    def unchecked(cls, kinds: Mapping[str, Kind], declared: Declared) -> Ontology:
        """The kinds as an older ontology had them, only to fingerprint entries written under it (`kindchange.before`): their
        rules may name fields under the new names, so they are not linted."""
        made = cls.__new__(cls)
        made.kinds, made.declared = dict(kinds), declared
        return made

    @property
    def layers(self) -> tuple[str, ...]:
        return self.declared.layers

    @property
    def common(self) -> dict[str, FieldSpec]:
        """The fields every entry may carry beside its kind's."""
        return self.declared.common

    @property
    def roles(self) -> Roles:
        return self.declared.roles

    @property
    def shared(self) -> str:
        """The reserved area of every layer that holds what two of its areas use."""
        return self.declared.shared.area

    def specs(self, kind: Kind) -> dict[str, FieldSpec]:
        """Every field an entry of `kind` may carry: the common ones and the kind's."""
        return {**self.common, **kind.fields}

    def get(self, name: str) -> Kind | None:
        return self.kinds.get(name)

    def parts_of(self, parent: str) -> tuple[Kind, ...]:
        """The inline kinds that may sit inside `parent`."""
        return tuple(kind for kind in self.kinds.values() if kind.is_part(parent))

    def file_kind(self, file: str) -> Kind | None:
        """The list or single kind whose file is called `file`."""
        return next((kind for kind in self.kinds.values() if kind.shape in FILED and kind.file == file), None)

    def fixed_folders(self) -> frozenset[str]:
        """The top folders that hold no layer and no area: a kind keeps all its entries in one (the constitution), or kept them
        there before they moved into the layers (`moved_from`, until `ogy migrate`)."""
        return frozenset({kind.area for kind in self.kinds.values() if kind.area} | set(self.moved_homes()))

    def moved_homes(self) -> dict[str, str]:
        """Each fixed folder a kind moved out of -> the home `ogy migrate` moves its entries and its removed ledger to: the
        shared area of the kind's first layer."""
        return {kind.moved_folder: f"{kind.layers[0]}/{self.shared}" for kind in self.kinds.values() if kind.moved_folder}

    def moved_kind(self, rel: str) -> Kind | None:
        """The kind whose entries the fixed-folder file `rel` held before they moved into the layers."""
        return next((kind for kind in self.kinds.values() if kind.moved_from == rel), None)

    def settling_kind(self) -> Kind | None:
        return next((kind for kind in self.kinds.values() if kind.settling is not None), None)


def parse_kinds(texts: Mapping[str, str], declared: Declared) -> Ontology:
    """Build an ontology from `{kinds/<name>.yml: text}` and its `ontology.yml`."""
    kinds: dict[str, Kind] = {}
    for path, text in sorted(texts.items()):
        name = path.rsplit("/", 1)[-1].removesuffix(".yml")
        try:
            kinds[name] = Kind.model_validate(any_yaml.read(text))
        except ValidationError as error:
            raise OntologyError(f"{path}: {error}") from error
    return Ontology(kinds, declared)


def parse_declared(text: str) -> Declared:
    """An `ontology.yml`."""
    try:
        return Declared.model_validate(any_yaml.read(text))
    except ValidationError as error:
        raise OntologyError(f"{ONTOLOGY_FILE}: {error}") from error


def packaged(name: str = DEFAULT_ONTOLOGY) -> Ontology:
    """The ontology shipped in `ogy/ontologies/<name>`: its `ontology.yml` and `kinds/`."""
    root = files("ogy").joinpath("ontologies", name)
    folder = root.joinpath(KINDS_DIR)
    if not folder.is_dir() or not root.joinpath(ONTOLOGY_FILE).is_file():
        raise OntologyError(f"no ontology named {name!r}")
    texts = {f"{KINDS_DIR}/{item.name}": item.read_text() for item in folder.iterdir() if item.name.endswith(".yml")}
    return parse_kinds(texts, parse_declared(root.joinpath(ONTOLOGY_FILE).read_text()))
