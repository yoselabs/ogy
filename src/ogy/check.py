"""`ogy check`: entries match their kind, names are sound, links resolve, flows are whole.

`CHECKS` is the list of checks run after reading; each takes the snapshot and the source and returns findings. The checks
of evidence, decisions, the glossary, the removed ledgers and the built record are in their own modules.
"""

from collections.abc import Callable

from ogy.coverage import check_every_area, product_areas
from ogy.evidencecheck import check_evidence
from ogy.fieldtypes import fields_problems
from ogy.flowcheck import check_flows
from ogy.kindchange import migrated
from ogy.kinds import COMMON_FIELDS, Holds, Kind
from ogy.ledgers import check_against_base, check_ledgers
from ogy.links import link_items, resolve
from ogy.lints import check_lints
from ogy.model import Address, Entry, Finding, Problem
from ogy.settle import check_decisions
from ogy.snapshot import Snapshot, load
from ogy.source import Source
from ogy.terms import check_proposed_terms, check_term_agreement, check_terms

type Check = Callable[[Snapshot, Source], list[Finding]]


class Checker:
    """Collects the findings of one snapshot that concern one entry at a time."""

    def __init__(self, snapshot: Snapshot) -> None:
        self.snapshot = snapshot
        self.findings: list[Finding] = []

    def run(self) -> list[Finding]:
        for entry in self.snapshot.entries.values():
            kind = self.snapshot.kind_of(entry.address)
            self._fields(kind, entry)
            self._layer(kind, entry)
            self._links(entry)
            self._form(kind, entry)
        return self.findings

    def _add(self, problem: Problem, entry: Entry, detail: str) -> None:
        self.findings.append(Finding(problem, entry.path, detail, entry.address))

    def _fields(self, kind: Kind, entry: Entry) -> None:
        listed = [part for part in self.snapshot.ontology.parts_of(kind.kind) if part.holding is Holds.LIST]
        known = {part.key for part in listed if part.key}
        for problem, detail in fields_problems(self.snapshot.ontology, {**COMMON_FIELDS, **kind.fields}, entry.fields, known,
                                               old=kind.old_names):
            self._add(problem, entry, detail)
        for part in listed:
            items = entry.fields.get(part.key or "")
            if items is None:
                continue
            if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
                self._add(Problem.WRONG_TYPE, entry, f"{part.key} is a list of {part.kind} mappings")
                continue
            for item in items:
                for problem, detail in fields_problems(self.snapshot.ontology, part.fields, item, old=part.old_names):
                    self._add(problem, entry, f"{part.key}: {detail}")

    def _layer(self, kind: Kind, entry: Entry) -> None:
        layer = entry.address.layer
        if layer and entry.address.parent() is None and layer not in kind.layers:
            self._add(Problem.BAD_LAYER, entry, f"{kind.kind} may live in the layers {list(kind.layers)}, not {layer}")
        if not layer and kind.moved is not None and entry.address.parent() is None:
            self._add(Problem.NEEDS_MIGRATION, entry, f"{kind.kind} moved from {kind.moved_from} to {kind.moved[1]}/{kind.file} and "
                      "then to the area that uses it: run `ogy migrate`, then `ogy move`")

    def _links(self, entry: Entry) -> None:
        for item in link_items(self.snapshot.ontology, entry):
            found = resolve(self.snapshot.ontology, self.snapshot.entries, entry.address, item)
            if found.problem is not None:
                self._add(found.problem, entry, found.detail)

    def _has_part(self, address: Address, kind: str) -> bool:
        part = self.snapshot.ontology.get(kind)
        if part is not None and part.holding is Holds.LIST:
            return bool(self.snapshot.entries[address].fields.get(part.key or ""))
        return bool(self.snapshot.links.parts(address, kind))

    def _form(self, kind: Kind, entry: Entry) -> None:
        for group in kind.exactly_one_of:
            present = [name for name in group if entry.fields.get(name) is not None]
            if len(present) != 1:
                self._add(Problem.ONE_OF, entry, f"exactly one of {list(group)}, not {present}")
        for need in kind.requires:
            if need.if_set is not None and entry.fields.get(need.if_set) is None:
                continue
            if need.if_part is not None and not self._has_part(entry.address, need.if_part):
                continue
            reached, _ = self.snapshot.links.walk(entry.address, need.path)
            if not any(address.kind in need.kinds for address in reached):
                self._add(Problem.UNMET, entry, need.error)
        if kind.one_part is not None:
            rule = kind.one_part
            parts = self.snapshot.links.parts(entry.address, rule.kind)
            matching = [part for part in parts if self.snapshot.entries[part].fields.get(rule.field) == rule.equals]
            if len(matching) != 1:
                self._add(Problem.ONE_PART, entry, f"exactly one {rule.kind} with {rule.field}: {rule.equals}, found {len(matching)}")


def check_entries(snapshot: Snapshot, _source: Source) -> list[Finding]:
    return Checker(snapshot).run()


CHECKS: tuple[Check, ...] = (check_entries, check_every_area, check_flows, check_evidence, check_decisions, check_terms, check_ledgers,
                             check_lints)
# Errors only when a land is asked for: nobody has agreed yet is waiting for the owner, not a fault (`ogy check` counts it).
LANDING: tuple[Check, ...] = (check_term_agreement, check_proposed_terms)


def check(snapshot: Snapshot, source: Source, base: Source | None = None, landing: bool = False,
          product: str | None = None) -> list[Finding]:
    """Every check on one snapshot; with a `base` source (the merge base), also what the base forbids changing, under
    `landing` a proposed word only when the change adds it (a word the base already had blocks no one), and with `product`
    (the repository's name) no area named like it."""
    findings = list(snapshot.findings) + (product_areas(snapshot, product) if product else [])
    for run in CHECKS:
        findings.extend(run(snapshot, source))
    older = migrated(load(base, snapshot.ontology)) if base is not None else None  # the base as `ogy migrate` would write it
    if landing:
        for run in LANDING:
            findings.extend(item for item in run(snapshot, source)
                            if older is None or item.problem is not Problem.PROPOSED_TERM or item.address not in older.entries)
    if base is not None and older is not None:
        findings.extend(check_against_base(snapshot, source, older, base))
    return findings
