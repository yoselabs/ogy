"""The `src` of every entry: items of the ontology's evidence schemes that exist (E2, E3, E6); an entry whose kind needs its own
evidence has it (E1, E4): a src, a decision settling it, a person's yes to it, or a `because` that reaches one; `proof` items
are `path::function` naming a test that exists (E5). The common fields are read in the roles `ontology.yml` gives them."""

import re
lazy from collections.abc import Callable

from ogy.evidence import check_items, symbol_hash
from ogy.kinds import Evidence
from ogy.links import link_items, resolve
from ogy.model import Address, Entry, Finding, Problem, link_values
from ogy.settle import decisions, settles
lazy from ogy.declared import Declared
lazy from ogy.snapshot import Snapshot
lazy from ogy.source import Source


def _proofs(declared: Declared, entry: Entry, read: Callable[[str], str | None]) -> list[Finding]:
    """E5: each proof item is `<repo path><suffix>::<function>`, a suffix of the ontology's `proof.files`, and names a test that
    exists: the file is in the repository and defines the function (`Class::method` for a method) (decision built-line-writer)."""
    name, suffixes = declared.roles.proof, declared.proof.files
    form = re.compile(rf"^[\w./-]+(?:{'|'.join(map(re.escape, suffixes))})(::[A-Za-z_]\w*)+$")
    raw = entry.fields.get(name)
    items: list[object] = raw if isinstance(raw, list) else [] if raw is None else [raw]
    found: list[Finding] = []
    for item in items:
        if not isinstance(item, str) or not form.match(item) or item.startswith("/") or ".." in item.split("/"):
            found.append(
                Finding(Problem.MISSING_PROOF, entry.path, f"{name} {item!r} is not <path>{'|'.join(suffixes)}::<function>", entry.address)
            )
        elif (why := _absent(item, read)) is not None:
            found.append(Finding(Problem.MISSING_PROOF, entry.path, f"{name} {item!r} names no test: {why}", entry.address))
    return found


def _absent(item: str, read: Callable[[str], str | None]) -> str | None:
    path, *names = item.split("::")
    text = read(path)
    if text is None:
        return f"{path} is not in the repository"
    return None if symbol_hash(text, ".".join(names)) is not None else f"{path} defines no {'.'.join(names)}"


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
    roles = snapshot.ontology.roles
    if link_values(entry.fields.get(roles.src)) or str(address) in settled or isinstance(entry.fields.get(roles.agreed), dict):
        return True
    for item in link_items(snapshot.ontology, entry):
        found = resolve(snapshot.ontology, snapshot.entries, address, item).target if item.field == roles.because else None
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
        roles = snapshot.ontology.roles
        why = (
            f"a {roles.because} chain that reaches no {roles.src}, no decision and no agreement"
            if link_values(entry.fields.get(roles.because))
            else f"no {roles.src}, no {roles.because}, no decision settling it and no person's yes"
        )
        out.append(Finding(Problem.NO_EVIDENCE, entry.path, f"{kind.kind} needs evidence of its own: {why}", address))
    return out


def check_evidence(snapshot: Snapshot, source: Source) -> list[Finding]:
    found: list[Finding] = _no_evidence(snapshot)
    declared = snapshot.ontology.declared
    for entry in snapshot.entries.values():
        found += _proofs(declared, entry, source.repo_file)
        items = link_values(entry.fields.get(declared.roles.src))
        found += [
            Finding(problem.code, entry.path, f"{problem.address}: {problem.detail}", entry.address)
            for problem in check_items(list(items), source.repo_file, declared.evidence)
        ]
    return found
