"""`ogy show`: an entry joined to what is computed about it, and which source each fact comes from (loader-changes section 5)."""

from dataclasses import dataclass
lazy from collections.abc import Mapping

from ogy.graph import Context, context
from ogy.model import Address, link_values
from ogy.settle import Decision, decision_of, decisions, settles
from ogy.status import Agreed, Label, Status, agreed_of, label, status
lazy from ogy.built import Line
lazy from ogy.receipts import Work
lazy from ogy.snapshot import Snapshot


@dataclass(frozen=True)
class Decided:
    """The decision that settles an entry, or that says no to an address."""

    decision: Address
    option: str | None  # the option in force
    by: str  # "you" when an answer is in force, else "AI"
    note: str | None = None  # the hedge or condition the owner put on the answer in force


@dataclass(frozen=True)
class Shown:
    """Everything `ogy show` prints about one address. `context` is None for an address that does not exist."""

    address: Address
    context: Context | None
    status: Status | None = None
    label: Label | None = None
    agreed: Agreed | None = None
    decided_in: Decided | None = None
    came_from: tuple[str, ...] = ()
    through_decision: bool = False
    settles: tuple[str, ...] = ()
    built_file: str | None = None
    built: Line | None = None
    build_hash: str = ""
    work: tuple[Work, ...] = ()


def _decided(decision: Decision) -> Decided:
    force = decision.in_force
    by = "AI" if not (force and force.by_answer) else "AI, for you" if force.delegated else "you"
    return Decided(decision.address, force.option if force else None, by, force.note if force else None)


def absent(snapshot: Snapshot, address: Address) -> Shown | None:
    """An address no entry has, when a decision in force says no to it: `does not exist: decided no in <decision>`."""
    for decision in decisions(snapshot):
        force = decision.in_force
        if force is not None and str(address) in force.sets and force.sets[str(address)] is None:
            return Shown(address, None, decided_in=_decided(decision))
    return None


def _answered(decision: Decision | None) -> Agreed | None:
    """When a decision was answered: the newest answer's time, where and paraphrase (an answer has no hash)."""
    newest = decision.newest if decision else None
    return Agreed(newest.at, "", newest.said, newest.where) if newest is not None and newest.at is not None else None


def show(snapshot: Snapshot, address: Address, record: Mapping[str, Line], work: list[Work]) -> Shown:
    found = decisions(snapshot)
    entry = snapshot.entries[address]
    settling = decision_of(found, address)
    asking = next((d for d in found if d.address == address), None)
    given, nothing = settles(asking) if asking else (dict[str, set[str]](), set[str]())
    src = snapshot.ontology.roles.src
    own = link_values(entry.fields.get(src))
    inherited = link_values(settling.entry.fields.get(src)) if settling else ()
    return Shown(
        address,
        context(snapshot, address),
        status(snapshot, address),
        label(snapshot, address),
        agreed_of(snapshot, address) or _answered(asking),
        _decided(settling) if settling else None,
        own or inherited,
        not own and bool(inherited),
        tuple(sorted({*given, *nothing})),
        f"built/{entry.path}",
        record.get(str(address)),
        snapshot.build_hash(address),
        tuple(item for item in work if item.address == str(address)),
    )
