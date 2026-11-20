"""Addresses, entries and the problems found while reading them."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from ogy.kinds import NAME, Kind, Shape
from ogy.ontology import Ontology


@dataclass(frozen=True, order=True)
class Address:
    """An entry's identity: `<layer>/<area>/<kind>/<id>`, and a part's is its parent's plus `/<part kind>/<key>`.

    The folder is the layer's only home: the layer is the first segment, and every such address keeps its area (what two
    areas share is in the area `shared`). An entry of a kind that names a fixed folder (the constitution) has no layer:
    `constitution/<kind>/<id>`. A `holds: one` part is its parent's address plus `/<part kind>`
    (its key is empty). No dots, no `:`.
    """

    layer: str
    area: str
    path: tuple[tuple[str, str], ...]

    def __str__(self) -> str:
        head = [self.layer, self.area] if self.layer else [self.area]
        return "/".join([*head, *(f"{kind}/{key}" if key else kind for kind, key in self.path)])

    @property
    def home(self) -> str:
        """The folder the entry's file sits in: `<layer>/<area>`, or the fixed folder."""
        return f"{self.layer}/{self.area}" if self.layer else self.area

    @property
    def kind(self) -> str:
        return self.path[-1][0]

    @property
    def key(self) -> str:
        """The id of an entry, the local key of a part, empty for a `holds: one` part."""
        return self.path[-1][1]

    def parent(self) -> Address | None:
        return Address(self.layer, self.area, self.path[:-1]) if len(self.path) > 1 else None

    def part(self, kind: str, key: str = "") -> Address:
        return Address(self.layer, self.area, (*self.path, (kind, key)))


def _fits(kind: Kind, path: list[tuple[str, str]]) -> bool:
    """A first kind is an entity or list kind; each next one is a part of the one before."""
    return kind.is_part(path[-1][0]) if path else kind.shape is not Shape.INLINE


def parse_address(text: str, ontology: Ontology) -> Address | None:
    """Read `<layer>/<area>/<kind>/<id>[/<part kind>/<key>...]` (or `constitution/<kind>/<id>...`); None when it is no address here."""
    segments = text.split("/")
    layer = segments[0] if segments[0] in ontology.layers else ""
    head = 2 if layer else 1
    if len(segments) < head + 2 or not NAME.match(segments[head - 1]) or (not layer and segments[0] not in ontology.fixed_folders()):
        return None
    path: list[tuple[str, str]] = []
    rest = segments[head:]
    while rest:
        kind = ontology.get(rest.pop(0))
        if kind is None or not kind.addressable or not _fits(kind, path):
            return None
        if not kind.has_id:
            path.append((kind.kind, ""))
        elif rest and NAME.match(rest[0]):
            path.append((kind.kind, rest.pop(0)))
        else:
            return None
    return Address(layer, segments[head - 1], tuple(path))


def home_of(text: str, ontology: Ontology) -> str:
    """The folder an address names without parsing it (a removed address may name nothing live): `<layer>/<area>`, or a fixed folder."""
    segments = text.split("/")
    return "/".join(segments[:2]) if segments[0] in ontology.layers else segments[0]


def area_of(text: str, ontology: Ontology) -> str:
    return home_of(text, ontology).rsplit("/", 1)[-1]


class Problem(StrEnum):
    """Every check `ogy check` makes."""

    BAD_YAML = "bad-yaml"
    BAD_PATH = "bad-path"
    UNKNOWN_KIND = "unknown-kind"
    BAD_SHAPE = "bad-shape"
    BAD_NAME = "bad-name"
    DUPLICATE_ID = "duplicate-id"
    UNKNOWN_FIELD = "unknown-field"
    MISSING_FIELD = "missing-field"
    WRONG_TYPE = "wrong-type"
    BAD_LAYER = "bad-layer"
    BAD_LINK = "bad-link"
    LINK_KIND = "link-kind"
    DANGLING_LINK = "dangling-link"
    AMBIGUOUS_LINK = "ambiguous-link"
    MISSING_PROOF = "missing-proof"
    NO_EVIDENCE = "no-evidence"
    ONE_OF = "one-of"
    UNMET = "unmet-requirement"
    ONE_PART = "one-part"
    STEP_SHAPE = "step-shape"
    UNREACHABLE = "unreachable"
    NO_END = "no-path-to-end"
    END_UNREACHED = "end-unreached"
    UNCOVERED_END = "uncovered-end"
    NOT_OFFERED = "choice-not-offered"
    NEVER_STARTED = "never-started"
    LINK_CYCLE = "link-cycle"
    STORED_STATE = "stored-state"
    BAD_KEY = "bad-key"
    DUPLICATE_SAYS = "duplicate-says"
    BAD_BUILT = "bad-built"
    BAD_SRC = "bad-src"
    MISSING_CODE = "missing-code"
    MISSING_DOC = "missing-doc"
    UNEVEN_OPTIONS = "uneven-options"
    TWO_HOMES = "two-homes"
    EQUAL_AT = "equal-at"
    NOT_IN_FORCE = "not-in-force"
    BAD_DELEGATION = "bad-delegation"
    NO_GUESS = "no-guess"
    WORD_CLASH = "word-clash"
    AVOIDED_WORD = "avoided-word"
    TERM_TOO_LONG = "term-too-long"
    TERM_NOT_AGREED = "term-not-agreed"
    PROPOSED_TERM = "proposed-term"
    AGREED_TERM_IN_SETS = "agreed-term-in-sets"
    EDITED_APPEND_ONLY = "edited-append-only"
    REMOVED_UNRECORDED = "removed-unrecorded"
    ID_REUSED = "id-reused"
    BAD_REMOVED = "bad-removed"
    BAD_SNAPSHOT = "bad-snapshot"
    REMOVED_WITHOUT_WHY = "removed-without-why"
    LINK_TO_REMOVED = "link-to-removed"
    PRODUCT_AREA = "product-area"
    MISSING_ENTRY = "missing-entry"
    NEEDS_MIGRATION = "needs-migration"


@dataclass(frozen=True)
class Finding:
    """One problem at one place."""

    problem: Problem
    path: str
    detail: str
    address: Address | None = None

    def __str__(self) -> str:
        where = f"{self.path} {self.address}" if self.address else self.path
        return f"{self.problem}: {where}: {self.detail}"


@dataclass(frozen=True)
class Entry:
    """One entry as written: its file and its fields. A `holds: list` part stays in its parent's fields under its key."""

    address: Address
    path: str
    fields: Mapping[str, object] = field(default_factory=dict)

    @property
    def area(self) -> str:
        return self.address.area

    def text(self, name: str) -> str | None:
        value = self.fields.get(name)
        return value if isinstance(value, str) else None


def link_values(value: object) -> tuple[str, ...]:
    """The texts a one-or-many field holds (links, proofs), ignoring anything that is not text."""
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(item for item in value if isinstance(item, str))
    return ()
