"""The kind language: what one `kinds/<kind>.yml` file may say. Loading and cross-checking are in `ontology`."""

import re
from collections.abc import Mapping
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

    FILE = "file"  # one file per entry: <layer>/<area>/<kind>/<id>.yml
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


class Input(StrEnum):
    """How a link enters the build hash of the entry that holds it (a build input, as in Bazel and Make). The meaning
    fingerprint never reads it: agreements and review cards stay as they are."""

    NONE = "none"  # the default: a change to the target, or a relink of a note field, is no work
    ADDRESS = "address"  # the target's address: a relink of a note field is work (any other field has it in the meaning)
    CONTENT = "content"  # the target's content, its build hash without proofs: a change in the target is work


class Picked(BaseModel):
    """A narrower input: only these fields of each target (`fields: [pin]`, a dependency's pin and not its description), or
    only the addresses of these parts of each target (`parts: [choice]`, the choices of a served step)."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    fields: tuple[str, ...] = ()
    parts: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _one(self) -> Self:
        if bool(self.fields) == bool(self.parts):
            msg = "a picked input names fields or parts, one of them"
            raise ValueError(msg)
        return self


class FieldSpec(BaseModel):
    """One field of a kind. Every declared field is meaning and enters the fingerprint unless it is a `note`. A link field
    may declare its `input`: what of its targets enters the build hash. Unset reads as `none`; a link field of a kind that
    needs proof states it, `none` included."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    type: FieldType = FieldType.TEXT
    to: tuple[str, ...] = ()
    of: tuple[str, ...] = ()  # enum members
    schemes: tuple[str, ...] = ()  # uri schemes
    note: bool = False
    required: bool = False
    harm: tuple[str, ...] = ()  # what a wrong value of this field costs, for an entry that sets it (tags of `harms`)
    member_harm: dict[str, tuple[str, ...]] = {}  # an enum member's own cost, e.g. `delete: [irreversible]`
    input: Input | Picked | None = None


class Fingerprint(BaseModel):
    """What besides the meaning and the inputs (`input`, `input_from`) enters the build hash, which only the built record
    compares."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    proofs: bool = False  # the set of proof test ids: appending a proof (bug triage) makes the entry work again


class Equals(BaseModel):
    """A condition on a field's value: the entry's `field` is `value`, or one of the values listed."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    field: str
    value: str | tuple[str, ...]

    @property
    def values(self) -> tuple[str, ...]:
        return (self.value,) if isinstance(self.value, str) else self.value


class Requirement(BaseModel):
    """When the entry has field `if_set`, lacks field `if_unset`, has a part `if_part`, a field value `if_equals` or reaches
    anything along the path `if_reaches` (every entry, without one), it sets `needs_field`, or it reaches along `path` (none:
    the entry itself), or along any one of `or_paths`, an entry of `kinds` that sets none of `without`; with `same`, the path
    comes back to the entry itself (for an item of a list part, the entry that holds it). Unmet, it is `unmet-requirement`;
    with `work`, it is work left instead (what is still to be built, not a fault), under the `status` it names. A requirement
    whose path goes back to kinds only a later layer holds is work without `work` (`ogy.owing`), and names its status too."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    if_set: str | None = None
    if_unset: str | None = None
    if_part: str | None = None
    if_equals: Equals | None = None
    if_reaches: tuple[str, ...] = ()
    needs_field: str | None = None
    path: tuple[str, ...] = ()
    or_paths: tuple[tuple[str, ...], ...] = ()
    kinds: tuple[str, ...] = ()
    without: tuple[str, ...] = ()
    same: bool = False
    or_answered: bool = False  # a decision counts once answered, any other entry once agreed; one whose answer sets the entry meets it
    work: bool = False  # set by hand for work in the same layer; a requirement a later layer owes is made work on load
    status: str | None = None  # the work status an unmet `work` requirement is listed under
    error: str

    @model_validator(mode="after")
    def _one_condition(self) -> Self:
        if sum(item is not None for item in (self.if_set, self.if_unset, self.if_part, self.if_equals)) + bool(self.if_reaches) > 1:
            msg = "a requirement has one of if_set, if_unset, if_part, if_equals and if_reaches, not both"
            raise ValueError(msg)
        if self.same and not self.path:
            msg = "a requirement that comes back to the entry (same) has a path"
            raise ValueError(msg)
        if self.work and self.status is None:
            msg = "a requirement that is work names its status"
            raise ValueError(msg)
        if (self.needs_field is None) == (not self.kinds) or (self.needs_field is not None and (self.path or self.without)):
            msg = "a requirement needs a field (needs_field) or reaches kinds (path, kinds, without), not both"
            raise ValueError(msg)
        if self.or_paths and not (self.path and all(self.or_paths)):
            msg = "or_paths are further paths beside a path, none of them empty"
            raise ValueError(msg)
        return self

    @property
    def paths(self) -> tuple[tuple[str, ...], ...]:
        """Every path the requirement may be met along (one empty path: the entry itself)."""
        return (self.path, *self.or_paths)

    @property
    def condition(self) -> str:
        """The condition as words, empty for every entry."""
        if self.if_set:
            return f"with {self.if_set}"
        if self.if_unset:
            return f"without {self.if_unset}"
        if self.if_part:
            return f"with a {self.if_part}"
        if self.if_equals:
            return f"with {self.if_equals.field} {'|'.join(self.if_equals.values)}"
        if self.if_reaches:
            return f"reaching {' '.join(self.if_reaches)}"
        return ""


class ProofWhen(BaseModel):
    """A kind's entries need proof only when they hold a part of this kind (an entity with transitions)."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    if_part: str


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
    proposal: str
    sets: str  # field of an option and of the proposal: the values it gives (the proposal's when it chooses no option)
    chose: str  # field of an answer and of a proposal
    said: str  # field of an answer: a short paraphrase of what the person said, never a quote
    at: str
    where: str
    note: str
    delegated: str
    heard: str  # field of the proposal: what the owner said that it rests on, a short paraphrase, never a quote
    context: str  # field of the settling kind: why the question comes up, so its card reads on its own
    why: str  # field of the proposal: the reason for it


class Glossary(BaseModel):
    """Makes a kind the glossary: its entries are the words of the product's one language, its sentence what a word means."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    word: str  # the field holding the word people say
    avoid: str  # the field listing words never used for it: a sentence that uses one is `avoided-word`
    words: int  # its sentence has fewer words than this (`term-too-long`)
    names: str | None = None  # the link field naming the entry that defines the word: its sentence is the term's


class PrintedFirst(BaseModel):
    """Makes a kind what every agent reads first, whole, before the glossary (the constitution)."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    also: str | None = None  # a field printed under the sentence


class Flow(BaseModel):
    """Makes a container kind (a workflow) a graph: its parts are steps and ends; a step's parts are rows.

    Every name is a kind or field of this ontology, written out in its kind file, so another ontology can rename them; the
    checks are fixed:
    step shapes, every step reachable from the start, every step reaching an end or a hand-off, every end reached,
    a calling step naming every end of its callee, the serving entries offering every choice, and every container started: a root
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
    group: str | None = None  # container link field naming what the flow realizes: `ogy work` groups its work by it


class Was(BaseModel):
    """A kind's name before a rename or a merge, and where its entries were kept under it: `ogy migrate` moves them to the new
    name. A kind that absorbed several kinds lists one for each; `renamed` names the fields an entry of that old kind kept under
    another name, and `defaults` fills a field the new kind requires that the old kind did not have."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: str
    file: str | None = None  # a list or single kind's file before the rename
    key: str | None = None  # a part's key inside its parent before the rename
    renamed: dict[str, str] = {}  # old field name -> new, for the entries of this old kind only
    defaults: dict[str, str | bool | int] = {}  # a field the new kind has -> the value an entry of this old kind gets without it


class Kind(BaseModel):
    """One kind of entry, as written in `kinds/<kind>.yml`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: str
    about: str
    guidance: str | None = None  # how to decide: when to use this kind rather than its neighbours (`ogy kinds <kind>`)
    like: str | None = None  # the mainstream notion it matches, one line (`ogy kinds`, `--map`, `ogy glossary`)
    unlike: str | None = None  # the mainstream notions of the same name it does not mean, one line
    sentence: str | None = None  # the field that holds what an entry says: what a card shows, a search finds, a person agrees to
    shape: Shape
    layers: tuple[str, ...] = ()  # the layer folders this kind may appear in (the folder is the layer's only home)
    area: str | None = None  # entries live only in this fixed folder (the constitution), outside every layer
    shared: bool = False  # may live in the reserved area `shared` of a layer: what two areas use (a term, an actor, a set)
    moved_from: str | None = None  # `<folder>/<file>`: the fixed-folder file it was kept in; `ogy migrate` moves it to `shared`
    file: str | None = None  # a list or single kind's file name inside every area
    every_area: bool = False  # every area of the kind's layers holds an entry of it; an area without one is `missing-entry`
    needs_proof: bool | ProofWhen = False  # entries count as work until built; `{if_part: <kind>}`: only those holding one
    must_be_agreed: bool = False
    own_card: bool = False  # agreed only by its own card number or the owner's own sentence, never by `yes all`
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
    # the input of what the entry holds besides its own fields: a common field (rows: `satisfies: content`) or a part kind
    # (an entity: `attribute: content`); a field of its own declares its `input` itself
    input: dict[str, Input | Picked] = {}
    # reverse inputs: the entries that link here by the field named, these fields of theirs, only where set (a kind that
    # gains such a field stales nothing): a rule reads the pin of a dependency held to it, `satisfies: {fields: [pin]}`
    input_from: dict[str, Picked] = {}
    exactly_one_of: tuple[tuple[str, ...], ...] = ()  # of each group, exactly one field is set
    acyclic: tuple[str, ...] = ()  # link fields that never lead back to the entry (`link-cycle`): a card that includes cards
    requires: tuple[Requirement, ...] = ()
    one_part: OnePart | None = None
    flow: Flow | None = None
    was: tuple[Was, ...] = ()  # the kind's old name, or the old kinds it absorbed: their entries keep them until `ogy migrate`
    renamed: dict[str, str] = {}  # old field name -> new: an entry written before holds the old one until `ogy migrate`
    revalued: dict[str, dict[str, dict[str, str | bool | None]]] = {}  # field -> old value -> the fields it now is (None removes)
    folded: dict[str, str] = {}  # field that held a part's mapping -> the part's one field whose value it now holds
    dropped: tuple[str, ...] = ()  # fields the kind no longer has: `ogy migrate` removes them (a filled one comes back to the owner)

    @field_validator("part_of", mode="before")
    @classmethod
    def _parents(cls, value: object) -> object:
        return (value,) if isinstance(value, str) else value

    @field_validator("was", mode="before")
    @classmethod
    def _olds(cls, value: object) -> object:
        return (value,) if isinstance(value, Mapping) else value

    @property
    def old_names(self) -> dict[str, str | None]:
        """Each field name the kind no longer has -> the field it is now, or None when it was dropped."""
        return {**dict.fromkeys(self.dropped), **self.renamed}

    @property
    def moved_folder(self) -> str | None:
        """The fixed folder the entries were kept in before they moved into the layers (`ogy migrate` moves them)."""
        return self.moved_from.split("/", 1)[0] if self.moved_from is not None and self.layers else None

    @property
    def proves(self) -> bool:
        """Some entries of the kind need proof (all, or those holding the part `needs_proof` names): read by the kind's lints,
        readers and printers; which entry needs one is `Snapshot.needs_proof`."""
        return self.needs_proof is not False

    @property
    def proof_text(self) -> str:
        return f"needs proof with a {self.needs_proof.if_part}" if isinstance(self.needs_proof, ProofWhen) else "needs proof"

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


def where(hop: str) -> tuple[str, str, frozenset[str] | None]:
    """A path hop's field, and the key and values its `?key=a|b` keeps (None: it keeps every link)."""
    name, _, condition = hop.partition("?")
    key, _, values = condition.partition("=")
    return name, key, frozenset(values.split("|")) if condition else None


NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # an area, an id, a local key
KIND_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED_AREAS = (KINDS_DIR, "built")
ONTOLOGY_FILE = "ontology.yml"  # beside `kinds/`: the layers, common fields, harms and evidence (`declared`)
