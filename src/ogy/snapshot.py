"""A whole knowledge base at one commit: its ontology, its entries by address, and what reading them found."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from content_digest import digest

from ogy.kinds import Holds, Kind
from ogy.layout import BUILT_DIR, read_files
from ogy.model import Address, Entry, Finding, Problem, link_values, parse_address
from ogy.paths import LinkIndex, inputs, inputs_from
from ogy.retype import Retype, applied, problems
lazy from ogy.ontology import Ontology
lazy from ogy.source import Source

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

FINGERPRINT_LENGTH = 12


def kb_paths(listing: Iterable[str]) -> list[str]:
    """The files the entry reader accounts for: every file outside the tool-written `built/` record (a stray one is `bad-path`)."""
    return sorted(path for path in listing if path.split("/")[0] != BUILT_DIR)


def _plain(value: object) -> object:
    """A time as YAML reads it (an answer's `at`) hashes as its ISO text."""
    return value.isoformat() if isinstance(value, datetime) else value


def fingerprint(kind: Kind, entry: Entry, parts: Sequence[object] = (), also: Sequence[object] = (), proofs: str | None = None) -> str:
    """A short hash of the entry's kind, its fields that are set and are not notes, and the content of its unkeyed parts.

    `src` and the other common fields are outside it, and so is a field the entry leaves unset: a kind that gains a field
    changes no fingerprint. The build hash adds the set of its proof ids (`proofs`: the common field that holds them) and what
    its inputs read (`input`, then `input_from` only where set: `also`)."""
    payload: dict[str, object] = {
        "kind": kind.kind,
        **{
            name: _plain(entry.fields[name])
            for name, spec in sorted(kind.fields.items())
            if not spec.note and entry.fields.get(name) is not None
        },
    }
    if parts:
        payload["parts"] = list(parts)
    if kind.fingerprint.proofs and proofs:
        payload["proofs"] = sorted(set(link_values(entry.fields.get(proofs))))
    if also:
        payload["also"] = list(also)
    return digest(payload, length=FINGERPRINT_LENGTH)


@dataclass
class Snapshot:
    """Entries keyed by address. A duplicate keeps the first and is reported."""

    ontology: Ontology
    entries: dict[Address, Entry]
    findings: list[Finding]
    _links: LinkIndex | None = field(default=None, repr=False)
    _prints: dict[tuple[Address, str], str] = field(default_factory=dict, repr=False)
    _visiting: set[Address] = field(default_factory=set, repr=False)
    _inputs: dict[str, list[tuple[str, ...]]] = field(default_factory=dict, repr=False)

    @property
    def links(self) -> LinkIndex:
        if self._links is None:
            self._links = LinkIndex(self.ontology, self.entries)
        return self._links

    def kind_of(self, address: Address) -> Kind:
        kind = self.ontology.get(address.kind)
        if kind is None:
            raise KeyError(address.kind)
        return kind

    def sentence(self, address: Address) -> str | None:
        """What the entry says: the field its kind names as its sentence."""
        name = self.kind_of(address).sentence
        return self.entries[address].text(name) if name else None

    def fingerprint(self, address: Address) -> str:
        """The meaning: the kind, the fields that are not notes and the unkeyed parts. Agreements, review cards and removed
        items hold it, so a new proof or a changed dependency never sends an entry back to the owner."""
        key = (address, "meaning")
        if key not in self._prints:
            self._prints[key] = fingerprint(self.kind_of(address), self.entries[address], self._unkeyed(address), ())
        return self._prints[key]

    def build_hash(self, address: Address, *, proofs: bool = True) -> str:
        """What the built record and work left compare: the meaning, the proofs, what the kind's inputs read (`input` of its
        link fields, common fields and parts) and its reverse inputs (`input_from`). Memoised. `proofs=False` is what reaches
        other entries along `=@fingerprint`: a delivery adding a proof upstream must not make everything downstream stale. An
        input that reads nothing is left out, each other one keyed by its path. A cycle contributes the key."""
        key = (address, "build" if proofs else "build-no-proofs")
        if key in self._prints:
            return self._prints[key]
        if address in self._visiting:
            return address.key
        self._visiting.add(address)
        try:
            kind = self.kind_of(address)
            if kind.kind not in self._inputs:
                self._inputs[kind.kind] = inputs(self.ontology, kind)
            # an input that reads nothing adds nothing: a kind that gains a link field (or a merge that brings one) stales nothing
            named = sorted(  # keyed and sorted by path: reordering a kind file's fields or inputs moves no hash
                ([" ".join(path), found] for path in self._inputs[kind.kind] if (found := self._along(address, path))),
                key=lambda item: str(item[0]),
            )
            reached = sorted(
                ([" ".join(path), found] for path in inputs_from(kind) if (found := self._along(address, path, only_set=True))),
                key=lambda item: str(item[0]),
            )
            also: list[object] = [*named, *([["reached", reached]] if reached else [])]
            entry = self.entries[address]
            self._prints[key] = fingerprint(kind, entry, self._unkeyed(address), also, self.ontology.roles.proof if proofs else None)
        finally:
            self._visiting.discard(address)
        return self._prints[key]

    def _unkeyed(self, address: Address) -> list[object]:
        """The content of the `holds: list` and `holds: one` parts, notes left out: they have no fingerprint of their own."""
        found: list[object] = []
        for part in self.ontology.parts_of(address.kind):
            notes = {name for name, spec in part.fields.items() if spec.note}
            if part.holding is Holds.LIST:
                items = self.entries[address].fields.get(part.key or "")
                kept = (
                    [{k: v for k, v in item.items() if k not in notes} if isinstance(item, dict) else item for item in items]
                    if isinstance(items, list)
                    else items
                )
                found.append([part.key, kept])
            elif part.holding is Holds.ONE and (one := address.part(part.kind)) in self.entries:
                found.append([part.key, {k: v for k, v in self.entries[one].fields.items() if k not in notes}])
        return found

    def _along(self, address: Address, path: tuple[str, ...], *, only_set: bool = False) -> list[str]:
        reached, values = self.links.walk(address, path)
        values = [value for value in values if value is not None] if only_set else values
        match path[-1] if path else "":
            case "=@id":
                return sorted(item.key for item in reached)
            case "=@address":
                return sorted(str(item) for item in reached)
            case "=@fingerprint":
                return sorted(f"{item}={self.build_hash(item, proofs=False)}" for item in reached)
            case _:
                return sorted(map(str, values))

    def parent(self, address: Address) -> Address | None:
        return address.parent()

    def resolve(self, text: str) -> Address | None:
        """Find an entry by its full address."""
        address = parse_address(text, self.ontology)
        return address if address in self.entries else None


def build(ontology: Ontology, files: dict[str, str]) -> Snapshot:
    """Read entry files into a snapshot. A file that still holds an old kind name is `needs-migration`; one at an old kind's
    path is not read (`ogy.retype`)."""
    work = Retype(ontology)
    found, findings = read_files(ontology, {rel: text for rel, text in files.items() if work.path(rel) == rel})
    findings += [Finding(Problem.NEEDS_MIGRATION, rel, why) for rel, why in sorted(problems(ontology, files).items())]
    entries: dict[Address, Entry] = {}
    for entry in found:
        if entry.address in entries:
            findings.append(Finding(Problem.DUPLICATE_ID, entry.path, f"also in {entries[entry.address].path}", entry.address))
            continue
        entries[entry.address] = entry
    return Snapshot(ontology, entries, findings)


def load(source: Source, ontology: Ontology, *, retyped: bool = False) -> Snapshot:
    """Every entry file of the knowledge base in one batch read; `retyped`: as `ogy migrate` renames the kinds (`ogy.retype`)."""
    files = source.read(kb_paths(source.listing()))
    return build(ontology, applied(ontology, files) if retyped else files)
