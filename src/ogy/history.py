"""`ogy history <address | home>` (`<layer>/<area>`): computed from Git, the agreements, the answers and the removed ledger."""

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
lazy from collections.abc import Iterable
lazy from pathlib import Path

from git_porcelain import RealRepo

from ogy.base import read_ledgers
from ogy.built import Line, read_source
from ogy.semdiff import diff
from ogy.settle import decisions
from ogy.snapshot import Snapshot, load
from ogy.source import open_source
from ogy.status import agreed_in
lazy from ogy.ontology import Ontology
lazy from ogy.removed import Item

LIMIT = 100


@dataclass(frozen=True)
class Row:
    when: datetime
    who: str
    what: str
    where: str


@dataclass
class History:
    rows: list[Row] = field(default_factory=list)
    in_force: str | None = None
    notes: list[str] = field(default_factory=list)


class Nothing:
    """The knowledge base before its first commit."""

    kb, reads = "", 0

    def describe(self) -> str:
        return "nothing"

    def tree_id(self) -> str | None:
        return None

    def listing(self) -> dict[str, str]:
        return {}

    def read(self, paths: Iterable[str]) -> dict[str, str]:
        del paths
        return {}

    def repo_file(self, path: str, rev: str | None = None) -> str | None:
        del path, rev
        return None

    def cited_texts(self, paths: tuple[str, ...]) -> dict[str, str]:
        del paths
        return {}


def covers(subject: str, text: str) -> bool:
    """The address or area `subject` is `text` or holds it."""
    return text == subject or text.startswith(subject.rstrip("/") + "/")


def built_rows(older: dict[str, Line], newer: dict[str, Line], subject: str, when: datetime, where: str) -> list[Row]:
    """B4: a `built/` line this commit wrote (added or changed) or deleted. The commit that last wrote a line delivered it."""
    rows: list[Row] = []
    for address in sorted({*older, *newer}):
        if not covers(subject, address) or older.get(address) == newer.get(address):
            continue
        what = "built: line deleted (removal delivered)" if address not in newer else f"built: own {newer[address].own}"
        rows.append(Row(when, "commit", f"{what} {address}", where))
    return rows


def git_rows(repo: Path, kb: str, ontology: Ontology, rev: str, subject: str, *, limit: int = LIMIT) -> tuple[list[Row], list[str]]:
    """One row per entry change and per `built/` line change of each commit that changed `subject`, read from consecutive commits."""
    log = RealRepo(repo, ambient=os.environ).history([rev], limit=limit)
    rows: list[Row] = []
    for number, commit in enumerate(log):
        older = open_source(repo, log[number + 1].sha, kb, required=False) if number + 1 < len(log) else Nothing()
        if number + 1 == len(log) and len(log) == limit:
            return rows, [f"history is cut at {commit.sha[:12]} ({limit} commits); the changes of that commit are not shown"]
        newer = open_source(repo, commit.sha, kb, required=False)
        when, where = datetime.fromtimestamp(commit.ts, UTC), f"{commit.sha[:12]} {commit.subject}"
        for change in diff(older, newer, ontology).changes:
            if covers(subject, str(change.address)):
                names = ", ".join(item.name for item in change.fields)
                rows.append(Row(when, "commit", f"{change.change} {change.address} {names}".strip(), where))
        if older.tree_id() is None or older.tree_id() != newer.tree_id():
            rows += built_rows(read_source(older)[0], read_source(newer)[0], subject, when, where)
    return rows, []


def delivery_commit(rows: Iterable[Row], address: str) -> str | None:
    """B4: the commit that last wrote the `built/` line of `address` (its sha and subject), read from the Git rows; no `in` is stored."""
    wrote = [row for row in rows if row.what.startswith("built: own ") and row.what.endswith(f" {address}")]
    return max(wrote, key=lambda row: row.when).where if wrote else None


def said_rows(snapshot: Snapshot, subject: str) -> list[Row]:
    """Who said so: the person's yes on each entry, and the answers of the decisions, each as its short paraphrase."""
    rows = [
        Row(found.at, "human", f"agreed: {found.said}", found.where) for text, found in agreed_in(snapshot).items() if covers(subject, text)
    ]
    for decision in decisions(snapshot):
        if covers(subject, str(decision.address)):
            rows += [Row(a.at, a.who, f"answered: {a.chose} ({a.said})", a.where) for a in decision.answers if a.at]
    return rows


def ledger_rows(items: Iterable[Item], subject: str) -> list[Row]:
    """That it is gone, why, and what replaced it."""
    return [
        Row(item.at, "ogy", f"removed (why: {item.why}; replaced by: {item.replaced_by})", item.id)
        for item in items
        if covers(subject, item.id)
    ]


def in_force(snapshot: Snapshot, subject: str) -> str | None:
    for decision in decisions(snapshot):
        force = decision.in_force
        if decision.address == snapshot.resolve(subject) and force is not None:
            newest = max((a.at for a in decision.answers if a.at is not None), default=None)
            by = f"owner, {newest:%Y-%m-%d}" if force.by_answer and newest else "AI proposal, no answer yet"
            return f"In force: {force.option} ({by})."
    return None


def history(repo: Path, kb: str, ontology: Ontology, rev: str, subject: str, *, limit: int = LIMIT) -> History:
    """The rows about `subject` (an address, its part, or a home), oldest first."""
    source = open_source(repo, rev, kb)
    snapshot = load(source, ontology)
    ledgers, _ = read_ledgers(source)
    items = [item for ledger in ledgers.values() for item in ledger.items]
    rows, notes = git_rows(repo, kb, ontology, "HEAD" if rev == "." else rev, subject, limit=limit)
    rows += said_rows(snapshot, subject) + ledger_rows(items, subject)
    return History(sorted(rows, key=lambda row: row.when), in_force(snapshot, subject), notes)
