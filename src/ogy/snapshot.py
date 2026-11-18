"""A whole knowledge base at one commit: its ontology, its entries by address, and what reading them found."""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime

from content_digest import digest

from ogy.kinds import Holds, Kind
from ogy.layout import BUILT_DIR, read_files
from ogy.model import Address, Entry, Finding, Problem, link_values, parse_address
from ogy.ontology import Ontology
from ogy.paths import LinkIndex
from ogy.source import Source

FINGERPRINT_LENGTH = 12


def kb_paths(listing: Iterable[str]) -> list[str]:
    """The files the entry reader accounts for: every file outside the tool-written `built/` record (a stray one is `bad-path`)."""
    return sorted(path for path in listing if path.split("/")[0] != BUILT_DIR)


def _plain(value: object) -> object:
    """A time as YAML reads it (an answer's `at`) hashes as its ISO text."""
    return value.isoformat() if isinstance(value, datetime) else value


def fingerprint(kind: Kind, entry: Entry, parts: Sequence[object] = (), also: Sequence[object] = (), proofs: bool = True) -> str:
    """A short hash of the entry's kind, its fields that are set and are not notes, and the content of its unkeyed parts.

    `src` and the other common fields are outside it, and so is a field the entry leaves unset: a kind that gains a field
    changes no fingerprint. A kind may add the set of its proof ids and values reached along link paths (`also`)."""
    payload: dict[str, object] = {"kind": kind.kind, **{name: _plain(entry.fields[name]) for name, spec in sorted(kind.fields.items())
                                                        if not spec.note and entry.fields.get(name) is not None}}
    if parts:
        payload["parts"] = list(parts)
    if kind.fingerprint.proofs and proofs:
        payload["proofs"] = sorted(set(link_values(entry.fields.get("proof"))))
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
    _prints: dict[tuple[Address, bool], str] = field(default_factory=dict, repr=False)
    _visiting: set[Address] = field(default_factory=set, repr=False)

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

    def fingerprint(self, address: Address, *, proofs: bool = True) -> str:
        """Memoised. `proofs=False` is the meaning alone, which is what reaches other entries along `=@fingerprint`:
        a delivery adding a proof upstream must not make everything downstream stale. A cycle contributes the key."""
        key = (address, proofs)
        if key in self._prints:
            return self._prints[key]
        if address in self._visiting:
            return address.key
        self._visiting.add(address)
        try:
            kind = self.kind_of(address)
            also: list[object] = [self._along(address, path) for path in kind.fingerprint.also]
            reached = [[n, found] for n, path in enumerate(kind.fingerprint.reached) if (found := self._along(address, path, True))]
            also += [["reached", reached]] if reached else []
            entry = self.entries[address]
            self._prints[key] = fingerprint(kind, entry, self._unkeyed(address), also, proofs)
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
                kept = [{k: v for k, v in item.items() if k not in notes} if isinstance(item, dict) else item
                        for item in items] if isinstance(items, list) else items
                found.append([part.key, kept])
            elif part.holding is Holds.ONE and (one := address.part(part.kind)) in self.entries:
                found.append([part.key, {k: v for k, v in self.entries[one].fields.items() if k not in notes}])
        return found

    def _along(self, address: Address, path: tuple[str, ...], only_set: bool = False) -> list[str]:
        reached, values = self.links.walk(address, path)
        values = [value for value in values if value is not None] if only_set else values
        match path[-1] if path else "":
            case "=@id":
                return sorted(item.key for item in reached)
            case "=@fingerprint":
                return sorted(f"{item}={self.fingerprint(item, proofs=False)}" for item in reached)
            case _:
                return sorted(map(str, values))

    def parent(self, address: Address) -> Address | None:
        return address.parent()

    def resolve(self, text: str) -> Address | None:
        """Find an entry by its full address."""
        address = parse_address(text, self.ontology)
        return address if address in self.entries else None


def build(ontology: Ontology, files: dict[str, str]) -> Snapshot:
    """Read entry files into a snapshot."""
    found, findings = read_files(ontology, files)
    entries: dict[Address, Entry] = {}
    for entry in found:
        if entry.address in entries:
            findings.append(Finding(Problem.DUPLICATE_ID, entry.path, f"also in {entries[entry.address].path}", entry.address))
            continue
        entries[entry.address] = entry
    return Snapshot(ontology, entries, findings)


def load(source: Source, ontology: Ontology) -> Snapshot:
    """Every entry file of the knowledge base in one batch read."""
    return build(ontology, source.read(kb_paths(source.listing())))
