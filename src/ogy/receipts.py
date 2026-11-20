"""Work left: what the built record says is still to do (loader-changes section 5, B1 to B3).

An entry of a kind that `needs_proof` is work until its built line matches it now; an address with a line and no entry is
removal work until the line is deleted; an entry whose evidence (a symbol, a document section) changed since it was captured is
listed.
"""

from dataclasses import dataclass
from enum import StrEnum
lazy from collections.abc import Mapping

from ogy import built, evidence, removed
from ogy.declared import Reader
from ogy.requires import unmet
lazy from ogy.built import Line
lazy from ogy.snapshot import Snapshot


class Status(StrEnum):
    """Where one piece of work stands."""

    UNBUILT = "unbuilt"  # never built
    CHANGED = "changed"  # built, then its build hash changed: its meaning, its proofs or a declared input
    UNSERVED = "unserved"  # a requirement its kind declares as work is unmet (an actor step nothing serves): to build, no fault
    REMOVED = "removed"  # the entry is gone and its built line is not yet deleted
    CODE_CHANGED = "code changed since captured"
    DOC_CHANGED = "document changed since captured"


@dataclass(frozen=True)
class Work:
    """One thing still to do. `address` is text: a removed entry has none to resolve."""

    address: str
    status: Status
    build_hash: str  # what the built line is compared with: the meaning, proofs and what the kind reaches
    built: str | None
    note: str = ""


def _unbuilt(snapshot: Snapshot, record: Mapping[str, Line]) -> list[Work]:
    proving = [a for a in sorted(snapshot.entries) if snapshot.kind_of(a).needs_proof]
    current = {str(a): snapshot.build_hash(a) for a in proving}
    return [
        Work(text, Status(why), current[text], record[text].own if text in record else None)
        for text, why in built.work_left(record, current).items()
    ]


def _unmet(snapshot: Snapshot) -> list[Work]:
    """A requirement declared `work` that an entry does not meet yet (an actor step nothing serves): its error is the note."""
    return [
        Work(str(address), Status.UNSERVED, "", None, need.error)
        for address in sorted(snapshot.entries)
        for need in unmet(snapshot, address, work=True)
    ]


def _gone(record: Mapping[str, Line], snapshot: Snapshot, ledger: Mapping[str, removed.Item]) -> list[Work]:
    """B2: the `why` of the ledger item is printed beside the work."""
    found: list[Work] = []
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


def work_left(
    snapshot: Snapshot, record: Mapping[str, Line], read: evidence.Read, ledger: Mapping[str, removed.Item] | None = None
) -> list[Work]:
    """Unbuilt and changed entries, unmet requirements that are work, removal work, and sources that changed since capture."""
    return [*_unbuilt(snapshot, record), *_unmet(snapshot), *_gone(record, snapshot, ledger or {}), *_sourced(record, snapshot, read)]
