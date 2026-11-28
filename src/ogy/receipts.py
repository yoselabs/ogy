"""Work left: what the built record says is still to do (loader-changes section 5, B1 to B3).

An entry of a kind that `needs_proof` is work until its built line matches it now; an address with a line and no entry is
removal work until the line is deleted; an entry whose evidence (a symbol, a document section) changed since it was captured is
listed.
"""

from dataclasses import dataclass
from enum import StrEnum
lazy from collections.abc import Collection, Mapping

from ogy import built, evidence, removed
from ogy.citations import uncited
from ogy.declared import Reader
from ogy.flowcheck import unoffered
from ogy.links import link_items
from ogy.requires import unmet
from ogy.settle import decisions, said_no
lazy from ogy.built import Line
lazy from ogy.snapshot import Snapshot


class Status(StrEnum):
    """Where one piece of work stands."""

    UNBUILT = "unbuilt"  # never built
    CHANGED = "changed"  # built, then its build hash changed: its meaning, its proofs or a declared input
    REMOVED = "removed"  # the entry is gone and its built line is not yet deleted
    CODE_CHANGED = "code changed since captured"
    DOC_CHANGED = "document changed since captured"
    UNOFFERED = "unoffered"  # a serving interface lists `offers` and leaves out a choice of the step
    SAID_NO = "links to an entry said no to"  # an answer took the target away: re-point the link or remove the entry
    UNCITED = "uncited"  # an answered decision that sets no entry and that no kind file, entry or code cites


@dataclass(frozen=True)
class Work:
    """One thing still to do. `address` is text: a removed entry has none to resolve."""

    address: str
    status: Status | str  # a requirement that is work names its own status in YAML (`requires: [{work: true, status: ...}]`)
    build_hash: str  # what the built line is compared with: the meaning, proofs and what the kind reaches
    built: str | None
    note: str = ""
    owed_by: str = ""  # the later layer that owes it (`ogy.owing`); empty: the entry's own layer


def _unbuilt(snapshot: Snapshot, record: Mapping[str, Line]) -> list[Work]:
    proving = [a for a in sorted(snapshot.entries) if snapshot.needs_proof(a)]
    current = {str(a): snapshot.build_hash(a) for a in proving}
    return [
        Work(text, Status(why), current[text], record[text].own if text in record else None)
        for text, why in built.work_left(record, current).items()
    ]


def _unmet(snapshot: Snapshot) -> list[Work]:
    """A requirement that is work and that an entry does not meet yet (an actor step nothing serves): under the status it names,
    its error the note, owed by the later layer its path goes back to (`ogy.owing`) or by the entry's own."""
    return [
        Work(str(address), need.status or "", "", None, need.error, snapshot.ontology.owed_by(address.kind, need, address.layer) or "")
        for address in sorted(snapshot.entries)
        for need in unmet(snapshot, address, work=True)
    ]


def _gone(record: Mapping[str, Line], snapshot: Snapshot, ledger: Mapping[str, removed.Item]) -> list[Work]:
    """B2: the `why` of the ledger item is printed beside the work. A line on a live entry that needs no proof (its kind no
    longer does, or an entity lost its transitions) is removal work too: `ogy migrate` deletes it."""
    found = [
        Work(str(address), Status.REMOVED, "", record[str(address)].own, "needs no proof: `ogy migrate` deletes the line")
        for address in sorted(snapshot.entries)
        if str(address) in record and not snapshot.needs_proof(address)
    ]
    for text in built.removal_work(record, (str(a) for a in snapshot.entries)):
        item = next((ledger[i] for i in sorted(ledger, key=len, reverse=True) if text == i or text.startswith(i + "/")), None)
        found.append(Work(text, Status.REMOVED, "", record[text].own, f"why: {item.why}" if item else "no ledger item"))
    return found


def _reads(snapshot: Snapshot, item: str) -> Reader | None:
    scheme = snapshot.ontology.declared.scheme_of(item)
    return scheme.reads if scheme else None


def _sourced(record: Mapping[str, Line], snapshot: Snapshot, read: evidence.Read) -> list[Work]:
    """B3: the symbol or the document section now is not the one the entry was captured from."""
    live = {str(a) for a in snapshot.entries}
    schemes = snapshot.ontology.declared.evidence
    now = {
        text: {link: evidence.receipt(link, read, schemes) or "" for link in line.sourced} for text, line in record.items() if text in live
    }
    return [
        Work(text, Status.DOC_CHANGED if _reads(snapshot, link) is Reader.SECTION else Status.CODE_CHANGED, "", record[text].own, link)
        for text, links in built.sourced_changes(record, now).items()
        for link in links
    ]


def _unoffered(snapshot: Snapshot) -> list[Work]:
    """A choice of a served step that no serving interface offers: work on the interfaces that list `offers`."""
    return [
        Work(str(server), Status.UNOFFERED, "", None, f"{step} offers none of {missing}") for server, step, missing in unoffered(snapshot)
    ]


def _said_no(snapshot: Snapshot) -> list[Work]:
    """An entry that still links to one an answer said no to: work until re-pointed or removed (decision
    software/writes/decision/answer-that-removes-used-entries)."""
    gone = said_no(decisions(snapshot))
    return [
        Work(str(address), Status.SAID_NO, "", None, f"{item.field}: {item.text} (no in {gone[item.text]})")
        for address in sorted(snapshot.entries)
        for item in link_items(snapshot.ontology, snapshot.entries[address])
        if item.text in gone and snapshot.resolve(item.text) is None
    ]


def _uncited(snapshot: Snapshot, code: Collection[str]) -> list[Work]:
    """An answer built where nothing names it: cite the decision from the kind file, entry or code that carries it."""
    note = 'cite it: `because` in a kind file or an entry, or "decision <address>" in a docstring'
    return [Work(str(address), Status.UNCITED, "", None, note) for address in uncited(snapshot, code)]


def work_left(
    snapshot: Snapshot,
    record: Mapping[str, Line],
    read: evidence.Read,
    ledger: Mapping[str, removed.Item] | None = None,
    code: Collection[str] = (),
) -> list[Work]:
    """Unbuilt and changed entries, unmet requirements that are work, links to an entry said no to, removal work, sources that
    changed since capture, and answered decisions nothing cites (`code`: the decisions the source files cite)."""
    return [
        *_uncited(snapshot, code),
        *_unbuilt(snapshot, record),
        *_unmet(snapshot),
        *_unoffered(snapshot),
        *_said_no(snapshot),
        *_gone(record, snapshot, ledger or {}),
        *_sourced(record, snapshot, read),
    ]
