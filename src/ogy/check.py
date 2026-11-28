"""`ogy check`: entries match their kind, names are sound, links resolve, flows are whole.

`CHECKS` is the list of checks run after reading; each takes the snapshot and the source and returns findings. The checks
of evidence, decisions, the glossary, the removed ledgers and the built record are in their own modules.
"""

from collections.abc import Callable
lazy from collections.abc import Mapping

from ogy.coverage import check_every_area, product_areas
from ogy.evidencecheck import check_evidence
from ogy.fieldtypes import fields_problems
from ogy.flowcheck import check_flows, check_unfinished_flows
from ogy.kindchange import migrated
from ogy.kinds import Holds, Kind
from ogy.ledgers import check_against_base, check_ledgers
from ogy.links import link_items, resolve
from ogy.lints import check_lints
from ogy.model import Entry, Finding, Problem, parse_address
from ogy.placeholders import check_placeholders
from ogy.requires import applies, reaching, satisfied, unmet
from ogy.settle import check_decisions, decisions, said_no
from ogy.snapshot import Snapshot, load
from ogy.source import Source
from ogy.terms import check_proposed_terms, check_term_agreement, check_terms

type Check = Callable[[Snapshot, Source], list[Finding]]


class Checker:
    """Collects the findings of one snapshot that concern one entry at a time."""

    def __init__(self, snapshot: Snapshot) -> None:
        self.snapshot = snapshot
        self.findings: list[Finding] = []
        self.said_no = said_no(decisions(snapshot))  # a link to one of them is work, not a finding (`receipts`)

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
        for problem, detail in fields_problems(
            self.snapshot.ontology, self.snapshot.ontology.specs(kind), entry.fields, known, old=self.snapshot.ontology.old_names(kind)
        ):
            self._add(problem, entry, detail)
        for problem in self._reshape(kind, entry.fields):
            self._add(Problem.NEEDS_MIGRATION, entry, problem)
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

    @staticmethod
    def _reshape(kind: Kind, fields: Mapping[str, object]) -> list[str]:
        """An old value the kind revalued, or a part's mapping it folded into a field: `ogy migrate` rewrites it."""
        found = [
            f"{name} holds a part's mapping, now its {inner}: run `ogy migrate`"
            for name, inner in kind.folded.items()
            if isinstance(fields.get(name), dict)
        ]
        found += [f"{name} was one link and is now a list: run `ogy migrate`" for name in kind.widened if isinstance(fields.get(name), str)]
        return found + [
            f"{name} {value} is now {', '.join(f'{k} {v}' for k, v in values[value].items())}: run `ogy migrate`"
            for name, values in kind.revalued.items()
            if isinstance(value := fields.get(name), str) and value in values
        ]

    def _layer(self, kind: Kind, entry: Entry) -> None:
        layer = entry.address.layer
        if layer and entry.address.parent() is None and layer not in kind.layers:
            self._add(Problem.BAD_LAYER, entry, f"{kind.kind} may live in the layers {list(kind.layers)}, not {layer}")
        if not layer and (folder := kind.moved_folder) is not None and entry.address.parent() is None:
            home = self.snapshot.ontology.moved_homes()[folder]
            self._add(
                Problem.NEEDS_MIGRATION,
                entry,
                f"{kind.kind} moved from {kind.moved_from} to {home}/{kind.file} and "
                "then to the area that uses it: run `ogy migrate`, then `ogy move`",
            )

    def _links(self, entry: Entry) -> None:
        declared = self.snapshot.ontology.declared
        for item in link_items(self.snapshot.ontology, entry):
            found = resolve(self.snapshot.ontology, self.snapshot.entries, entry.address, item)
            if found.problem is Problem.DANGLING_LINK and item.text in self.said_no:
                continue
            if found.problem is not None:
                self._add(found.problem, entry, found.detail)
            elif (target := found.target) is not None and declared.reversed_link(entry.address.layer, target.layer):
                self._add(
                    Problem.LAYER_DIRECTION,
                    entry,
                    f"{item.field}: {target} is in a later layer; a link stays in its layer or "
                    f"names an earlier one ({', '.join(declared.layers)})",
                )

    def _form(self, kind: Kind, entry: Entry) -> None:
        for group in kind.exactly_one_of:
            present = [name for name in group if entry.fields.get(name) is not None]
            if len(present) != 1:
                self._add(Problem.ONE_OF, entry, f"exactly one of {list(group)}, not {present}")
        for need in unmet(self.snapshot, entry.address, work=False):
            self._add(Problem.UNMET, entry, need.error)
        self._items(kind, entry)
        if kind.one_part is not None:
            rule = kind.one_part
            parts = self.snapshot.links.parts(entry.address, rule.kind)
            matching = [part for part in parts if self.snapshot.entries[part].fields.get(rule.field) == rule.equals]
            if len(matching) != 1:
                self._add(Problem.ONE_PART, entry, f"exactly one {rule.kind} with {rule.field}: {rule.equals}, found {len(matching)}")

    def _items(self, kind: Kind, entry: Entry) -> None:
        """The requirements of the items of a `holds: list` part (an effect), reported on the entry that holds them."""
        for part in self.snapshot.ontology.parts_of(kind.kind):
            items = entry.fields.get(part.key or "") if part.holding is Holds.LIST and part.requires else None
            for item in items if isinstance(items, list) else ():
                reaches = reaching(self.snapshot, entry.address, item, part.kind) if isinstance(item, dict) else None
                if reaches is None:
                    continue
                for need in (need for need in part.requires if not need.work):
                    if applies(need, item, lambda _: False, reaches) and not satisfied(
                        self.snapshot, need, part.kind, entry.address, item, item=True
                    ):
                        self._add(Problem.UNMET, entry, f"{part.key}: {need.error}")


def check_entries(snapshot: Snapshot, _source: Source) -> list[Finding]:
    return Checker(snapshot).run()


def check_sets_direction(snapshot: Snapshot, _source: Source) -> list[Finding]:
    """`layer-direction` over a decision's `sets` keys: a decision names what it sets, so it lives in that layer or a later one."""
    declared = snapshot.ontology.declared
    found: list[Finding] = []
    for decision in decisions(snapshot):
        named = sorted({text for sets in decision.sets_all() for text in (sets if isinstance(sets, dict) else ())})
        for text in named:
            target = parse_address(text, snapshot.ontology)
            if target is not None and declared.reversed_link(decision.address.layer, target.layer):
                found.append(
                    Finding(
                        Problem.LAYER_DIRECTION,
                        decision.entry.path,
                        f"sets: {text} is in a later layer; a decision "
                        f"sets entries of its layer or an earlier one ({', '.join(declared.layers)})",
                        decision.address,
                    )
                )
    return found


CHECKS: tuple[Check, ...] = (
    check_entries,
    check_sets_direction,
    check_every_area,
    check_flows,
    check_evidence,
    check_decisions,
    check_terms,
    check_placeholders,
    check_ledgers,
    check_lints,
)
# Errors only when a land is asked for: nobody has agreed yet is waiting for the owner, not a fault (`ogy check` counts it).
# A workflow whose end nothing reaches or that nothing starts is a layer not finished yet: a branch commits it, a land refuses it.
LANDING: tuple[Check, ...] = (check_term_agreement, check_proposed_terms, check_unfinished_flows)


def check(
    snapshot: Snapshot, source: Source, base: Source | None = None, *, landing: bool = False, product: str | None = None
) -> list[Finding]:
    """Every check on one snapshot; with a `base` source (the merge base), also what the base forbids changing, under
    `landing` a proposed word only when the change adds it (a word the base already had blocks no one), and with `product`
    (the repository's name) no area named like it."""
    findings = list(snapshot.findings) + (product_areas(snapshot, product) if product else [])
    for run in CHECKS:
        findings.extend(run(snapshot, source))
    older = migrated(load(base, snapshot.ontology, retyped=True)) if base is not None else None  # the base as `ogy migrate` would write it
    if landing:
        for run in LANDING:
            findings.extend(
                item
                for item in run(snapshot, source)
                if older is None or item.problem is not Problem.PROPOSED_TERM or item.address not in older.entries
            )
    if base is not None and older is not None:
        findings.extend(check_against_base(snapshot, source, older, base))
    return findings
