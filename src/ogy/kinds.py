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


class Harm(StrEnum):
    """What goes wrong if an entry's sentence is wrong; the order is the order the review asks them in."""

    STRUCTURE = "structure"  # the layout, layers, kinds or paths: asked on its own card, never inside a bulk accept
    MOVES_MONEY = "moves-money"
    TELLS_OUTSIDE = "tells-outside"
    IRREVERSIBLE = "irreversible"
    WHO_IS_ALLOWED = "who-is-allowed"


class FieldSpec(BaseModel):
    """One field of a kind. Every declared field is meaning and enters the fingerprint unless it is a `note`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    type: FieldType = FieldType.TEXT
    to: tuple[str, ...] = ()
    of: tuple[str, ...] = ()  # enum members
    schemes: tuple[str, ...] = ()  # uri schemes
    note: bool = False
    required: bool = False
    harm: tuple[Harm, ...] = ()  # what a wrong value of this field costs, for an entry that sets it


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
    """Makes a kind the one that settles entries: the parts and fields the fixed checks of a decision read."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    option: str = "option"
    answer: str = "answer"
    guess: str = "guess"
    sets: str = "sets"  # field of the option
    chose: str = "chose"  # field of an answer and of a guess
    value: str = "sets"  # field of the guess: the values it gives when it chooses no option
    said: str = "said"  # fields of an answer and of the guess's `heard`: a short paraphrase, never a quote
    who: str = "from"  # field of an answer: human or ai
    at: str = "at"
    where: str = "where"
    note: str = "note"
    delegated: str = "delegated"
    heard: str = "heard"  # the part of a guess: what the owner said that it rests on


class Flow(BaseModel):
    """Makes a container kind (a workflow) a graph: its parts are steps and ends; a step's parts are rows.

    Every name is a kind or field of this ontology, so another ontology can rename them; the checks are fixed:
    step shapes, every step reachable from the start, every step reaching an end or a hand-off, every end reached,
    a calling step naming every end of its callee, the serving views offering every choice, and no orphan container.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    start: str = "start"  # container field: the first step
    trigger: str = "trigger"  # container field: how it starts
    called: str = "called"  # the trigger value that needs a caller: something must hand off to or call it
    step: str = "step"
    end: str = "end"
    choice: str = "choice"  # rows of an actor step
    case: str = "case"  # rows of a system or calling step, lowest `order` first
    timeout: str = "timeout"  # the optional timeout row of an actor step
    then: str = "then"  # the edge, on a step (plain system step) or on a row
    actor: str = "actor"
    calls: str = "calls"
    covers: str = "covers_ends"  # a calling step's case names the callee ends it answers
    when: str = "when"
    order: str = "order"
    otherwise: str = "otherwise"  # the local key of the one case without a condition
    serves: str = "serves"
    servers: tuple[str, ...] = ("view", "command")
    offers: str = "offers"  # a serving entry offering only some choices lists them; without it, it offers all
    guard: str = "guard"  # a guard on a step sends the work to its `denied` target when its condition does not hold
    guarded: str = "on"
    denied: str = "else"


class Kind(BaseModel):
    """One kind of entry, as written in `kinds/<kind>.yml`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: str
    about: str
    guidance: str | None = None  # how to decide: when to use this kind rather than its neighbours (`ogy kinds <kind>`)
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
    harm: tuple[Harm, ...] = ()  # what a wrong sentence of this kind costs; read by the review queue
    append_only: bool = False
    evidence: Evidence | None = None
    holds: Holds | None = None
    settling: Settling | None = None
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
    def moved(self) -> tuple[str, str] | None:
        """(the fixed folder the entries were kept in, the home `ogy migrate` moves them to: the first layer's `shared`)."""
        if self.moved_from is None or not self.layers:
            return None
        return self.moved_from.split("/", 1)[0], f"{self.layers[0]}/{SHARED_AREA}"

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
SHARED_AREA = "shared"  # the area of every layer that holds what two of its areas use; only `shared` kinds live there
ONTOLOGY_FILE = "ontology.yml"  # beside `kinds/`: the layers every entry lives under

# Fields every entry may carry, all outside the fingerprint. `src` says where a sentence came from; `agreed` is the person's
# yes to it in a review round (written only by `reply`).
COMMON_FIELDS: dict[str, FieldSpec] = {
    "title": FieldSpec(note=True),
    "src": FieldSpec(type=FieldType.TEXTS, note=True),
    "because": FieldSpec(type=FieldType.LINKS, to=(ANY,)),
    "proof": FieldSpec(type=FieldType.TEXTS),
    "agreed": FieldSpec(type=FieldType.AGREED, note=True),
}
