"""The `src` of every entry: a `code:` symbol or a `doc:` heading that exists (E2, E3, E6); an entry whose kind needs its own
evidence has it (E1, E4): a src, a decision settling it, a person's yes to it, or a `because` that reaches one; `proof` items
are `path::function` (E5)."""

import re

from ogy.evidence import check_items
from ogy.kinds import Evidence
from ogy.links import link_items, resolve
from ogy.model import Address, Entry, Finding, Problem, link_values
from ogy.settle import decisions, settles
from ogy.snapshot import Snapshot
from ogy.source import Source

_PROOF = re.compile(r"^[\w./-]+\.py(::[A-Za-z_]\w*)+$")


def _proofs(entry: Entry) -> list[Finding]:
    """E5: each `proof` item is `<repo path>.py::<function>` (the `{test, from}` mapping is dropped)."""
    raw = entry.fields.get("proof")
    items = raw if isinstance(raw, list) else [] if raw is None else [raw]
    return [Finding(Problem.MISSING_PROOF, entry.path, f"proof {item!r} is not <path>.py::<function>", entry.address)
            for item in items if not isinstance(item, str) or not _PROOF.match(item) or item.startswith("/") or ".." in item.split("/")]


def _grounded(snapshot: Snapshot, settled: set[str], address: Address, seen: set[Address]) -> bool:
    """E1/E4: the entry has `src`, is settled by a decision, a person agreed to it, or a `because` of it is grounded."""
    if address in seen:
        return False
    seen.add(address)
    entry, kind = snapshot.entries[address], snapshot.kind_of(address)
    if kind.evidence_mode is Evidence.NONE:
        return True
    if kind.evidence_mode is Evidence.INHERIT:
        parent = address.parent()
        return parent is None or parent not in snapshot.entries or _grounded(snapshot, settled, parent, seen)
    if link_values(entry.fields.get("src")) or str(address) in settled or isinstance(entry.fields.get("agreed"), dict):
        return True
    for item in link_items(snapshot.ontology, entry):
        found = resolve(snapshot.ontology, snapshot.entries, address, item).target if item.field == "because" else None
        if found is not None and _grounded(snapshot, settled, found, seen):
            return True
    return False


def _no_evidence(snapshot: Snapshot) -> list[Finding]:
    found = decisions(snapshot)
    settled = {text for decision in found for text in settles(decision)[0]}
    out: list[Finding] = []
    for address, entry in snapshot.entries.items():
        kind = snapshot.kind_of(address)
        if kind.evidence_mode is not Evidence.OWN or _grounded(snapshot, settled, address, set()):
            continue
        why = ("a because chain that reaches no src, no decision and no agreement" if link_values(entry.fields.get("because"))
               else "no src, no because, no decision settling it and no person's yes")
        out.append(Finding(Problem.NO_EVIDENCE, entry.path, f"{kind.kind} needs evidence of its own: {why}", address))
    return out


def check_evidence(snapshot: Snapshot, source: Source) -> list[Finding]:
    found: list[Finding] = _no_evidence(snapshot)
    for entry in snapshot.entries.values():
        found += _proofs(entry)
        items = link_values(entry.fields.get("src"))
        found += [Finding(problem.code, entry.path, f"{problem.address}: {problem.detail}", entry.address)
                  for problem in check_items(list(items), source.repo_file)]
    return found
