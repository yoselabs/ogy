"""The commands as library calls: each returns its typed result and how many files it read.

The CLI and the MCP server only parse and print."""

import datetime as dt
from dataclasses import dataclass, replace
from typing import override
lazy from collections.abc import Mapping
lazy from pathlib import Path

from git_porcelain import git_dir, head
from process_lock import LockHeldError, ProcessLock

from ogy import near, put, removal, removed, reply, rounds, writes
from ogy.base import read_ledgers
from ogy.built import Line, read_source
from ogy.check import check
from ogy.constitution import printed_lines
from ogy.coverage import uncovered
from ogy.diagram import mermaid
from ogy.evidence import anchors
from ogy.find import Found, find
from ogy.graph import Impact, impact
from ogy.history import History, history
from ogy.init import Initialised, InitRefusedError, init
from ogy.kindmap import map_lines
from ogy.kindtext import kinds_lines
from ogy.migrate import Migrated, migrate
from ogy.model import Address, Finding, area_of, home_of, parse_address
from ogy.overview import Overview
from ogy.readers import readers_lines
from ogy.receipts import Work, work_left
from ogy.relocate import Moved, move
from ogy.removal import Clock, RemoveRefusedError
from ogy.review import Dropped, Review, dropped, review
from ogy.semdiff import SemanticDiff, diff
from ogy.show import Shown, absent, show
from ogy.source import Source, open_source
from ogy.target import Target, merge_base
from ogy.terms import waiting
from ogy.verdict import NotFoundError, RefusalError, Verdict
from ogy.writes import Answered, WriteRefusedError
lazy from ogy.ontology import Ontology
lazy from ogy.snapshot import Snapshot

__all__ = [
    "Answered",
    "InitRefusedError",
    "NotAFlowError",
    "RemoveRefusedError",
    "Run",
    "Target",
    "UnknownEntryError",
    "WriteRefusedError",
    "merge_base",
]


@dataclass(frozen=True)
class Run[T]:
    """What an operation returns: the typed value, how many files it read, and how it ended."""

    value: T
    reads: int
    verdict: Verdict = Verdict.OK


class UnknownEntryError(NotFoundError):
    """No entry has this address; the reason is `no entry <address>` and the addresses that are near it."""


class NotAFlowError(RefusalError):
    """The entry's kind declares no `flow:`, so it has no diagram."""

    prefix = ""

    @override
    def lines(self) -> list[str]:
        return [f"{reason} has no flow to draw" for reason in self.reasons]


def _resolve(snapshot: Snapshot, text: str) -> Address:
    address = snapshot.resolve(text)
    if address is None:
        raise UnknownEntryError(near.no_entry(snapshot, text))
    return address


def _area(snapshot: Snapshot, area: str | None) -> str | None:
    """The area asked for, which must have entries; NotFoundError with the areas that are near it otherwise."""
    areas = {address.area for address in snapshot.entries}
    if area is not None and area not in areas:
        raise NotFoundError(f"no area {area}" + near.hint(area, areas))
    return area


def _in_area(finding: Finding, area: str, ontology: Ontology) -> bool:
    if finding.address is not None:
        return finding.address.area == area
    parts = finding.path.split("/")
    return area_of("/".join(parts[1:] if parts[0] == "built" else parts), ontology) == area


def run_check(target: Target, base: str | None = None, *, landing: bool = False, area: str | None = None) -> Run[list[Finding]]:
    """Every check (of one area when given); against `base` (a commit), else the merge base with `main` when there is one."""
    source, snapshot = target.read()
    only = _area(snapshot, area)
    found = base or merge_base(target)
    older = open_source(target.repo, found, target.kb, required=False) if found else None
    older = older if older is not None and older.listing() else None  # no knowledge base at the base: nothing to compare with
    found_in = [
        item
        for item in check(snapshot, source, older, landing=landing, product=target.repo.resolve().name)
        if only is None or _in_area(item, only, snapshot.ontology)
    ]
    return Run(found_in, source.reads + (older.reads if older else 0), Verdict.FINDINGS if found_in else Verdict.OK)


def run_waiting(target: Target, area: str | None = None) -> int:
    """How many terms wait for the owner (of one area when given); an error only under `check --landing`."""
    snapshot = target.read()[1]
    return waiting(snapshot, _area(snapshot, area))


def run_anchors(target: Target, path: str) -> Run[list[tuple[str, str, int]]]:
    """The GitHub anchors of a Markdown file at the revision read (the worktree by default): (anchor, heading, level)."""
    source, _ = target.read()
    text = source.repo_file(path)
    if text is None or not path.endswith(".md"):
        msg = f"no Markdown file {path}"
        raise NotFoundError(msg)
    return Run(anchors(text), source.reads)


def run_impact(target: Target, text: str) -> Run[Impact]:
    source, snapshot = target.read()
    return Run(impact(snapshot, _resolve(snapshot, text)), source.reads)


def _record(source: Source) -> dict[str, Line]:
    return read_source(source)[0]


def _ledger(source: Source) -> dict[str, removed.Item]:
    return {item.id: item for ledger in read_ledgers(source)[0].values() for item in ledger.items}


def _scopes(home: str) -> set[str]:
    """What a home answers to: itself (`<layer>/<area>`), its layer and its area."""
    return {home, *home.split("/")}


def run_work(target: Target, scope: str | None = None) -> Run[list[Work]]:
    """What the built record says is still to do; given a scope, only in one layer (`product`: what the business still
    has to say, without the build behind it), one `<layer>/<area>`, or one area in every layer."""
    source, snapshot = target.read()
    homes = {address.home for address in snapshot.entries}
    known = set().union(*(_scopes(home) for home in homes))
    if scope is not None and scope not in known:
        raise NotFoundError(f"no layer or area {scope}" + near.hint(scope, known))
    work = [
        item
        for item in work_left(snapshot, _record(source), source.repo_file, _ledger(source))
        if scope is None or scope in _scopes(home_of(str(item.address), snapshot.ontology))
    ]
    return Run(work, source.reads, Verdict.FINDINGS if work else Verdict.OK)


def run_show(target: Target, text: str) -> Run[Shown]:
    """The entry with its status, label, decision, sources and built record; for an address a decision says no to, that."""
    source, snapshot = target.read()
    address = snapshot.resolve(text)
    if address is None:
        parsed = parse_address(text, snapshot.ontology)
        gone = absent(snapshot, parsed) if parsed else None
        if gone is None:
            raise UnknownEntryError(near.no_entry(snapshot, text))
        return Run(gone, source.reads)
    work = work_left(snapshot, _record(source), source.repo_file, _ledger(source))
    return Run(show(snapshot, address, _record(source), work), source.reads)


def run_diff(target: Target, before: str, after: str) -> Run[SemanticDiff]:
    old = open_source(target.repo, before, target.kb, required=False)
    new = open_source(target.repo, after, target.kb)
    return Run(diff(old, new, target.kinds()), old.reads + new.reads)


def run_diagram(target: Target, text: str) -> Run[list[str]]:
    source, snapshot = target.read()
    address = _resolve(snapshot, text)
    flow = snapshot.kind_of(address).flow
    if flow is None:
        raise NotAFlowError(text)
    return Run(mermaid(snapshot, flow, address), source.reads)


def run_review(
    target: Target, *, everything: bool = False, area: str | None = None, source_of: str | None = None, page: int = 1
) -> Run[Review]:
    """The cards asked (of one area when given), or one page of what came from `docs` or `code`; they are kept, by id and by
    knowledge base, as the round `reply --round` resolves."""
    source, snapshot = target.read()
    found = review(snapshot, everything=everything, area=_area(snapshot, area), source=source_of, page=page)
    kept = rounds.save(target.repo, rounds.make(found.cards, everything=everything)) if found.cards else None
    return Run(replace(found, round_id=kept.id if kept else ""), source.reads)


def run_dropped(target: Target) -> Run[Dropped]:
    source, snapshot = target.read()
    return Run(dropped(snapshot, list(_ledger(source).values())), source.reads)


def run_glossary(target: Target, home: str | None = None) -> Run[list[str]]:
    """The constitution, then the terms: every one, or those of one area (`<layer>/<area>`) and of the shared areas it reads."""
    source, snapshot = target.read()
    homes = {address.home for address in snapshot.entries if address.layer}
    if home is not None and home not in homes:
        raise NotFoundError(f"no area {home} (give <layer>/<area>)" + near.hint(home, homes))
    return Run(printed_lines(snapshot, home), source.reads)


def run_find(
    target: Target,
    words: list[str],
    kind: str | None = None,
    area: str | None = None,
    *,
    state: str | None = None,
    parent: str | None = None,
    cites: str | None = None,
) -> Run[list[Found]]:
    """Live and removed entries whose address or sentence hold every word, narrowed by kind, area, state and parent."""
    source, snapshot = target.read()
    return Run(
        find(
            snapshot,
            _ledger(source).values(),
            words,
            kind,
            area,
            state=state,
            parent=parent,
            cites=_resolve(snapshot, cites) if cites else None,
        ),
        source.reads,
    )


def run_status(target: Target, area: str | None = None, *, with_coverage: bool = False) -> Run[Overview]:
    """Counts per area, and how many findings, pieces of work and dropped things there are. Saves nothing.
    With `with_coverage`, also the kinds each layer has no entry of."""
    source, snapshot = target.read()
    only = _area(snapshot, area)
    found, work, lost = run_check(target, area=only), run_work(target, only), run_dropped(target)
    standing = review(snapshot, everything=True, area=only).headers
    return Run(
        Overview(
            standing,
            len(found.value),
            len(work.value),
            len(lost.value),
            waiting(snapshot, only),
            uncovered(snapshot) if with_coverage else None,
        ),
        source.reads,
    )


def run_remove(target: Target, text: str, why: str | None = None, to: str | None = None, now: Clock | None = None) -> Run[removed.Item]:
    """Delete an entry from the worktree (whatever `--rev` says) and record it in its area's removed ledger; refuses before writing."""
    clock = now or (lambda: dt.datetime.now(dt.UTC).replace(microsecond=0))
    git = git_dir(target.repo)
    if git is None:
        raise RemoveRefusedError([f"{target.repo} is not a Git repository"])
    try:
        with ProcessLock.acquire(git / "ogy.lock", label="ogy remove"):  # both writes under one lock
            item = removal.remove(
                target.repo, target.kb, target.kinds(), target.ontology, text, why=why, to=to, now=clock(), last_seen=head(target.repo)
            )
    except LockHeldError as error:
        raise RemoveRefusedError([f"another ogy write holds {error.path}"]) from error
    except LookupError as error:
        raise UnknownEntryError(near.no_entry(target.read()[1], text)) from error
    return Run(item, 0)


def run_move(target: Target, text: str, area: str) -> Run[Moved]:
    """Move an entry to another area, keeping its id, kind and agreements, in one atomic, checked write that records nothing."""
    with writes.locked(target, "move"):
        return Run(move(target, text, area), 0)


def run_migrate(target: Target) -> Run[Migrated]:
    """Rewrite the entries to the renames and drops their kinds declare, in one atomic, checked write that records nothing."""
    with writes.locked(target, "migrate"):
        return Run(migrate(target), 0)


def run_history(target: Target, text: str, limit: int = 100) -> Run[History]:
    return Run(history(target.repo, target.kb, target.kinds(), target.rev, text, limit=limit), 0)


def run_kinds(target: Target, kind: str | None = None, *, with_readers: bool = False, as_map: bool = False) -> Run[list[str]]:
    """The kinds as text (about, guidance, fields, rules); with `with_readers`, what reads each field of them instead; with
    `as_map`, the whole ontology as an indented tree, then its declared rules."""
    lines = kinds_lines(target.kinds(), kind)  # also refuses a kind that does not exist
    if as_map:
        return Run(map_lines(target.kinds()), 0)
    return Run(readers_lines(target.kinds(), kind) if with_readers else lines, 0)


def run_init(repo: Path, ontology: str | None = None) -> Run[Initialised]:
    return Run(init(repo, ontology), 0)


def run_put(target: Target, records: list[Mapping[object, object]], why: str | None = None) -> Run[list[put.Put]]:
    """Add or change one or many entries in one atomic, checked write; the batch is put back when it breaks the knowledge base.
    Parts a record drops are recorded as removed, with `why`."""
    with writes.locked(target, "put"):
        return Run(put.put(target, records, why), 0)


def run_answer(
    target: Target,
    decision: str,
    option: str,
    said: str,
    where: str,
    *,
    at: str | None = None,
    note: str | None = None,
    delegated: str | None = None,
    now: writes.Clock = writes.utc_now,
) -> Run[Answered]:
    """Choose the option: the answer keeps a short paraphrase of what was said, when and where (no message, no quote);
    with `delegated` an agent answered, under the decision whose person's answer let it decide; who is never a field."""
    who = "ai" if delegated is not None else "human"
    with writes.locked(target, "answer"):
        return Run(writes.answer(target, decision, option, writes.said(said, where, at, now, who=who, note=note), delegated, now=now), 0)


def run_reply(
    target: Target,
    text: str,
    said: str,
    where: str,
    *,
    at: str | None = None,
    round_id: str | None = None,
    now: writes.Clock = writes.utc_now,
    note: str | None = None,
) -> Run[reply.Replied]:
    """Apply the owner's reply (a grammar line, with a paraphrase of what they said) to a round; findings when some item was
    refused, refused when all were."""
    with writes.locked(target, "reply"):
        done = reply.reply(target, text, said, where, at=at, round_id=round_id, now=now, note=note)
    verdict = Verdict.OK if not done.refused else Verdict.FINDINGS if done.changed else Verdict.REFUSED
    return Run(done, 0, verdict)
