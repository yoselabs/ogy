"""One work item's brief: `ogy work <address>` (decision software/cli/decision/work-brief, answered work-address).

Everything an agent reads before building one entry, computed and never stored: the entry and its work; the why above it, walked
only up (its parents, and the why links: `because` and each flow's group link such as `realizes`, the same set the work types
use); the decisions that set the entry or anything above it; and one hop around it by field, the links out of the entry and the
links into it or its parents (the interface that serves its step, the handler that performs its row). The rules of its area that
name nothing are not listed yet: which kind holds for its home is the kind-file change of bead ogy-2a0.
"""

from collections import deque
from dataclasses import dataclass

from ogy.graph import PARENT, Edge, incoming, links_of
from ogy.settle import decision_of, decisions
lazy from ogy.built import Line
lazy from ogy.model import Address
lazy from ogy.receipts import Work
lazy from ogy.snapshot import Snapshot

__all__ = ["Brief", "Row", "brief", "rows", "sentence", "why_fields"]


@dataclass(frozen=True)
class Brief:
    address: Address
    work: tuple[Work, ...]  # the entry's rows in the work left
    above: tuple[Address, ...]  # nearest first
    decided_by: tuple[Address, ...]  # the decisions that set the entry or anything above it
    links_out: tuple[Edge, ...]
    linked_from: tuple[Edge, ...]
    proof: tuple[str, ...]
    built: Line | None


def why_fields(snapshot: Snapshot) -> set[str]:
    """The links that point up to a reason: `because`, and each flow's group link (`realizes`)."""
    kinds = snapshot.ontology.kinds.values()
    return {snapshot.ontology.roles.because} | {kind.flow.group for kind in kinds if kind.flow and kind.flow.group}


def _above(snapshot: Snapshot, address: Address) -> list[Address]:
    why, seen, found = why_fields(snapshot), {address}, list[Address]()
    queue = deque([address])
    while queue:
        for edge in links_of(snapshot, queue.popleft()):
            if (edge.field == PARENT or edge.field in why) and edge.address not in seen:
                seen.add(edge.address)
                found.append(edge.address)
                queue.append(edge.address)
    return found


def _lineage(address: Address) -> list[Address]:
    out: list[Address] = []
    at: Address | None = address
    while at is not None:
        out.append(at)
        at = at.parent()
    return out


def brief(snapshot: Snapshot, address: Address, work: list[Work], record: dict[str, Line]) -> Brief:
    above = _above(snapshot, address)
    found = decisions(snapshot)
    setting = {decision.address for at in (address, *above) if (decision := decision_of(found, at)) is not None}
    why = why_fields(snapshot)
    out = tuple(edge for edge in links_of(snapshot, address) if edge.field != PARENT and edge.field not in why)
    back = incoming(snapshot)
    into = tuple(
        Edge(edge.field, edge.address)
        for at in _lineage(address)
        if at in back
        for edge in back[at]
        if edge.field != PARENT and edge.address not in above and not str(edge.address).startswith(str(address) + "/")
    )
    proof = snapshot.entries[address].fields.get(snapshot.ontology.roles.proof)
    return Brief(
        address,
        tuple(item for item in work if item.address == str(address)),
        tuple(above),
        tuple(sorted(setting)),
        out,
        tuple(dict.fromkeys(into)),
        tuple(proof) if isinstance(proof, list) else (),
        record.get(str(address)),
    )


def sentence(snapshot: Snapshot, address: Address) -> str:
    """What the entry says: its kind's sentence field, else its title, else nothing."""
    entry, kind = snapshot.entries.get(address), snapshot.kind_of(address)
    if entry is None:
        return ""
    for name in (kind.sentence, snapshot.ontology.roles.title):
        if name and isinstance(value := entry.fields.get(name), str):
            return value
    return ""


type Row = tuple[str, str, str, str]  # part, field, address, what it says


def rows(snapshot: Snapshot, found: Brief) -> list[Row]:
    """The brief as rows, in the order a reader takes them: the entry, its work, the why above, the decisions, one hop around,
    its proof and its built line."""

    def say(address: Address) -> str:
        return sentence(snapshot, address)

    head: list[Row] = [("entry", snapshot.kind_of(found.address).kind, str(found.address), say(found.address))]
    work = [("work", str(item.status), item.address, item.note) for item in found.work]
    why = [("why", snapshot.kind_of(address).kind, str(address), say(address)) for address in found.above]
    decided = [("decided by", snapshot.kind_of(address).kind, str(address), say(address)) for address in found.decided_by]
    out = [("links out", edge.field, str(edge.address), say(edge.address)) for edge in found.links_out]
    into = [("linked from", edge.field, str(edge.address), say(edge.address)) for edge in found.linked_from]
    proof = [("proof", "", item, "") for item in found.proof]
    now = snapshot.build_hash(found.address) if snapshot.needs_proof(found.address) else ""
    state = "" if not found.built else "= now" if found.built.own == now else f"!= now {now}" if now else "needs no proof"
    built = [("built", "own", found.built.own, state) if found.built else ("built", "", "no line", "")]
    return [*head, *work, *why, *decided, *out, *into, *proof, *built]
