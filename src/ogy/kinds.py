"""The kind language: what one `kinds/<kind>.yml` file may say. Loading and cross-checking are in `ontology`."""

import re
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

KINDS_DIR = "kinds"
ANY = "any"  # a link target: an entry of any kind


class FieldType(StrEnum):
    """What a field holds."""

    TEXT = "text"
    TEXTS = "texts"
    NUMBER = "number"
    FLAG = "flag"
    LINK = "link"
    LINKS = "links"
    ENUM = "enum"
    URI = "uri"
    TIME = "time"
    EXPR = "expr"  # {text, reads}: `text` is never parsed, `reads` are links
    SETS = "sets"  # {address: {field: value} | null}
    AGREED = "agreed"  # {at, where, from, said, hash}: a person's yes, in a review round, to the entry's sentence as fingerprinted


LINKING = frozenset({FieldType.LINK, FieldType.LINKS, FieldType.EXPR})


class Shape(StrEnum):
    """Where a kind's entries live on disk."""

    ENTITY = "entity"  # one file per entry: <layer>/<area>/<kind>/<id>.yml
    LIST = "list"  # one file per layer and area, named by the kind's `file`, holding a list of entries with `id`
    SINGLE = "single"  # one file per area, named by the kind's `file`, holding one entry whose id is the area's name
    INLINE = "inline"  # a part kept inside its parent's file, under the part kind's `key`


FILED = frozenset({Shape.LIST, Shape.SINGLE})  # the shapes whose entries live in a named file of their area


class Holds(StrEnum):
    """How an inline kind sits under its key."""

    MAP = "map"  # {local key: fields}; every part has an address
    LIST = "list"  # items without a key; no address, they cannot be linked
    ONE = "one"  # a single mapping; its address is the parent's plus the kind


class Evidence(StrEnum):
    OWN = "own"
    INHERIT = "inherit"
    NONE = "none"


class FieldSpec(BaseModel):
    """One field of a kind. Every declared field is meaning and enters the fingerprint unless it is a `note`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    type: FieldType = FieldType.TEXT
    to: tuple[str, ...] = ()
    of: tuple[str, ...] = ()  # enum members
    schemes: tuple[str, ...] = ()  # uri schemes
    note: bool = False
    required: bool = False
    harm: tuple[str, ...] = ()  # what a wrong value of this field costs, for an entry that sets it (tags of `harms`)


class Fingerprint(BaseModel):
    """What besides the meaning enters the build hash, which only the built record compares. `also` are link paths ending in
    `=field` (see paths)."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    proofs: bool = False  # the set of proof test ids: appending a proof (bug triage) makes the entry work again
    also: tuple[tuple[str, ...], ...] = ()
    # paths that enter it only where they reach a value (an entry without the final field is passed over): a kind that
    # gains one stales nothing, such as the pins of the externals held to a rule
    reached: tuple[tuple[str, ...], ...] = ()


class Equals(BaseModel):
    """A condition on a field's value: the entry's `field` is `value`, or one of the values listed."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    field: str
    value: str | tuple[str, ...]

    @property
    def values(self) -> tuple[str, ...]:
        return (self.value,) if isinstance(self.value, str) else self.value


class Requirement(BaseModel):
    """When the entry has field `if_set`, a part `if_part` or a field value `if_equals` (every entry, without one), it sets
    `needs_field`, or it reaches along `path` (none: the entry itself) an entry of `kinds` that sets none of `without`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    if_set: str | None = None
    if_part: str | None = None
    if_equals: Equals | None = None
    needs_field: str | None = None
    path: tuple[str, ...] = ()
    kinds: tuple[str, ...] = ()
    without: tuple[str, ...] = ()
    error: str

    @model_validator(mode="after")
    def _one_condition(self) -> Self:
        if sum(item is not None for item in (self.if_set, self.if_part, self.if_equals)) > 1:
            raise ValueError("a requirement has one of if_set, if_part and if_equals, not both")
        if (self.needs_field is None) == (not self.kinds) or (self.needs_field is not None and (self.path or self.without)):
            raise ValueError("a requirement needs a field (needs_field) or reaches kinds (path, kinds, without), not both")
        return self

    @property
    def condition(self) -> str:
        """The condition as words, empty for every entry."""
        if self.if_set:
            return f"with {self.if_set}"
        if self.if_part:
            return f"with a {self.if_part}"
        if self.if_equals:
            return f"with {self.if_equals.field} {'|'.join(self.if_equals.values)}"
        return ""


class OnePart(BaseModel):
    """Exactly one part of this kind (of `kind`) has `field` equal to `equals`, such as one `otherwise` case."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: str
    field: str
    equals: str


class Settling(BaseModel):
    """Makes a kind the one that settles entries: the parts and fields the fixed checks of a decision read. The kind file
    names every one; the engine knows none."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    option: str
    answer: str
    guess: str
    sets: str  # field of the option
    chose: str  # field of an answer and of a guess
    value: str  # field of the guess: the values it gives when it chooses no option
    said: str  # fields of an answer and of the guess's `heard`: a short paraphrase, never a quote
    at: str
    where: str
    note: str
    delegated: str
    heard: str  # the part of a guess: what the owner said that it rests on
    context: str  # field of the settling kind: why the question comes up, so its card reads on its own
    why: str  # field of the guess: the reason for it


class Glossary(BaseModel):
    """Makes a kind the glossary: its entries are the words of the product's one language, its sentence what a word means."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    word: str  # the field holding the word people say
    avoid: str  # the field listing words never used for it: a sentence that uses one is `avoided-word`
    words: int  # its sentence has fewer words than this (`term-too-long`)


class PrintedFirst(BaseModel):
    """Makes a kind what every agent reads first, whole, before the glossary (the constitution)."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    also: str | None = None  # a field printed under the sentence


class Flow(BaseModel):
    """Makes a container kind (a workflow) a graph: its parts are steps and ends; a step's parts are rows.

    Every name is a kind or field of this ontology, written out in its kind file, so another ontology can rename them; the
    checks are fixed:
    step shapes, every step reachable from the start, every step reaching an end or a hand-off, every end reached,
    a calling step naming every end of its callee, the serving views offering every choice, and every container started: a root
    (an actor on its first step, or a `roots` field set) or led to from a started one.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    start: str  # container field: the first step
    roots: tuple[str, ...]  # container fields that start it from outside, as an actor on the first step does
    step: str
    end: str
    choice: str  # rows of an actor step
    case: str  # rows of a system or calling step, lowest `order` first
    timeout: str  # the optional timeout row of an actor step
    then: str  # the edge, on a step (plain system step) or on a row
    actor: str
    calls: str
    covers: str  # a calling step's case names the callee ends it answers
    when: str
    order: str
    otherwise: str  # the local key of the one case without a condition
    serves: str
    servers: tuple[str, ...]
    offers: str  # a serving entry offering only some choices lists them; without it, it offers all
    guard: str  # a guard on a step sends the work to its `denied` target when its condition does not hold
    guarded: str
    denied: str


class Kind(BaseModel):
    """One kind of entry, as written in `kinds/<kind>.yml`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: str
    about: str
    guidance: str | None = None  # how to decide: when to use this kind rather than its neighbours (`ogy kinds <kind>`)
    sentence: str | None = None  # the field that holds what an entry says: what a card shows, a search finds, a person agrees to
    shape: Shape
    layers: tuple[str, ...] = ()  # the layer folders this kind may appear in (the folder is the layer's only home)
    area: str | None = None  # entries live only in this fixed folder (the constitution), outside every layer
    shared: bool = False  # may live in the reserved area `shared` of a layer: what two areas use (a term, an actor, a set)
    moved_from: str | None = None  # `<folder>/<file>`: the fixed-folder file it was kept in; `ogy migrate` moves it to `shared`
    file: str | None = None  # a list or single kind's file name inside every area
    every_area: bool = False  # every area of the kind's layers holds an entry of it; an area without one is `missing-entry`
    needs_proof: bool = False  # entries count as work until built
    must_be_agreed: bool = False
    asked: bool = True  # false: its sentence is never put to the owner, so it gets no review card and needs no agreement
    harm: tuple[str, ...] = ()  # what a wrong sentence of this kind costs (tags of `harms`); read by the review queue
    append_only: bool = False
    evidence: Evidence | None = None
    holds: Holds | None = None
    settling: Settling | None = None
    glossary: Glossary | None = None
    printed_first: PrintedFirst | None = None
    fields: dict[str, FieldSpec] = {}
    part_of: tuple[str, ...] = ()  # an inline kind's parent kinds
    key: str | None = None  # an inline part's key inside the parent entry
    fingerprint: Fingerprint = Fingerprint()
    exactly_one_of: tuple[tuple[str, ...], ...] = ()  # of each group, exactly one field is set
    requires: tuple[Requirement, ...] = ()
    one_part: OnePart | None = None
    flow: Flow | None = None
    renamed: dict[str, str] = {}  # old field name -> new: an entry written before holds the old one until `ogy migrate`
    dropped: tuple[str, ...] = ()  # fields the kind no longer has: `ogy migrate` removes them (a filled one comes back to the owner)

    @field_validator("part_of", mode="before")
    @classmethod
    def _parents(cls, value: object) -> object:
        return (value,) if isinstance(value, str) else value

    @property
    def old_names(self) -> dict[str, str | None]:
        """Each field name the kind no longer has -> the field it is now, or None when it was dropped."""
        return {**dict.fromkeys(self.dropped), **self.renamed}

    @property
    def moved_folder(self) -> str | None:
        """The fixed folder the entries were kept in before they moved into the layers (`ogy migrate` moves them)."""
        return self.moved_from.split("/", 1)[0] if self.moved_from is not None and self.layers else None

    @property
    def holding(self) -> Holds:
        return self.holds or Holds.MAP

    @property
    def evidence_mode(self) -> Evidence:
        return self.evidence or (Evidence.INHERIT if self.shape is Shape.INLINE else Evidence.OWN)

    def is_part(self, parent: str) -> bool:
        return self.shape is Shape.INLINE and parent in self.part_of

    @property
    def addressable(self) -> bool:
        """Entries of this kind have an address (everything but the items of a `holds: list` part)."""
        return self.shape is not Shape.INLINE or self.holding is not Holds.LIST

    @property
    def has_id(self) -> bool:
        """The address of an entry of this kind ends in an id (a `holds: one` part is named by its kind alone)."""
        return self.addressable and not (self.shape is Shape.INLINE and self.holding is Holds.ONE)


NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # an area, an id, a local key
KIND_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED_AREAS = (KINDS_DIR, "built")
ONTOLOGY_FILE = "ontology.yml"  # beside `kinds/`: the layers, common fields, harms and evidence (`declared`)
