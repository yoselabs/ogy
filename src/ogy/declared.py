"""What an ontology's `ontology.yml` declares beside its kinds: the layers, the shared area of every layer, the fields every
entry may carry and the roles the engine reads them in, the harm tags in the order the review asks them, the evidence
schemes of `src` and the form of a proof, and the field names no kind may use. The engine reads these names; it knows none."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from ogy.kinds import FieldSpec


class Roles(BaseModel):
    """Which common field the engine reads for what: each value is a field of `common`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    title: str  # a short name, shown where an entry has no sentence
    src: str  # where an entry came from: evidence items of the schemes below
    because: str  # the reason an entry cites; it grounds the entry's evidence when it reaches a grounded one
    proof: str  # the tests that prove an entry built: `<path>::<function>`
    agreed: str  # a person's yes in a review round, written only by `reply`


class Reader(StrEnum):
    """How the engine reads what an evidence item names: these are the readers ogy has."""

    SYMBOL = "symbol"  # a module-level definition of a source file, hashed (a change to it is work)
    SECTION = "section"  # the section under a Markdown heading, by its GitHub anchor


class Scheme(BaseModel):
    """One evidence scheme of `src`: `<scheme>:<path>#<symbol>`, or `<scheme>:<commit>:<path>#<anchor>` when `pinned`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    reads: Reader
    files: tuple[str, ...]  # the file suffixes it may name
    pinned: bool = False  # it pins a Git revision: the file may be deleted later, its history stays


class Proof(BaseModel):
    """The form of a proof item: `<path><suffix>::<function>[::<function>...]`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    files: tuple[str, ...]


class Shared(BaseModel):
    """The reserved area of every layer that holds what two of its areas use, and the sentence of its own area entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    area: str
    says: str


class Reserved(BaseModel):
    """Field names no kind may declare."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    computed: tuple[str, ...] = ()  # facts the tool computes: no kind stores them, and an entry that holds one is `stored-state`
    sentence: tuple[str, ...] = ()  # other names for a sentence: a kind names its sentence field with `sentence:`


class Declared(BaseModel):
    """An `ontology.yml`."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    layers: tuple[str, ...]  # the top folders entries live under, in order: a later layer may name an earlier one
    shared: Shared
    common: dict[str, FieldSpec]  # fields every entry may carry beside its kind's
    renamed: dict[str, str] = {}  # old common field name -> new: an entry written before holds the old one until `ogy migrate`
    roles: Roles
    harms: tuple[str, ...] = ()  # what a wrong sentence costs, in the order the review asks them
    asked_alone: tuple[str, ...] = ()  # harm tags asked on their own card, never inside a bulk accept
    evidence: dict[str, Scheme] = {}
    proof: Proof
    reserved: Reserved = Reserved()

    def rank(self, tag: str | None) -> int:
        """The review order of a harm tag; no tag comes last."""
        return self.harms.index(tag) if tag in self.harms else len(self.harms)

    def scheme_of(self, item: str) -> Scheme | None:
        """The evidence scheme an item names, None when it names none."""
        name, colon, _ = item.partition(":")
        return self.evidence.get(name) if colon else None


def problems(declared: Declared) -> list[str]:
    """Each role names a common field; every tag asked alone is a harm; every scheme and the proof name file suffixes."""
    found = [f"roles: {role} names no common field {name}" for role, name in declared.roles.model_dump().items()
             if name not in declared.common]
    found += [f"renamed: {old} is now {new}, which is no common field" for old, new in declared.renamed.items()
              if new not in declared.common]
    found += [f"asked_alone: {tag} is no harm" for tag in declared.asked_alone if tag not in declared.harms]
    found += [f"evidence: {name} reads no files" for name, scheme in declared.evidence.items() if not scheme.files]
    return found + ([] if declared.proof.files else ["proof: names no file suffix"])
