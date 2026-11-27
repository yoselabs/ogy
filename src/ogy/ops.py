"""The commands as library calls: each returns its typed result and how many files it read.

The CLI and the MCP server only parse and print."""

import datetime as dt
from dataclasses import dataclass, replace
from typing import override
lazy from collections.abc import Callable, Mapping
lazy from pathlib import Path

from git_porcelain import git_dir
from process_lock import LockHeldError, ProcessLock

from ogy import affected, hooks, near, put, removal, removed, reply, rounds, writes
from ogy.base import read_ledgers
from ogy.brief import Row, brief, rows
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
from ogy.model import Address, Finding, home_of, in_scope, parse_address, scopes
from ogy.overview import Overview
from ogy.readers import readers_lines
from ogy.receipts import Work, work_left
from ogy.relocate import Moved, move
from ogy.removal import Clock, RemoveRefusedError
from ogy.review import Dropped, Review, dropped, review
from ogy.semdiff import SemanticDiff, diff
from ogy.show import Shown, absent, show
from ogy.since import card_changes
from ogy.source import Source, open_source
from ogy.target import Target, last_seen, merge_base, removal_base
from ogy.terms import waiting
from ogy.tracker import Item, items
from ogy.verdict import NotFoundError, RefusalError, Verdict
from ogy.view import render as render_view
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


type Loaded = tuple[Source, Snapshot]  # one read of the knowledge base that several operations share


def _scope(snapshot: Snapshot, scope: str | None) -> str | None:
    """The scope asked for: a layer `layers:` declares (with entries or not yet), or a `<layer>/<area>` or an area that has
    entries; NotFoundError with the scopes that are near it otherwise."""
    known = set(snapshot.ontology.layers).union(*(scopes(address.home) for address in snapshot.entries))
    if scope is not None and scope not in known:
        raise NotFoundError(f"no layer or area {scope}" + near.hint(scope, known))
    return scope


def _in_scope(finding: Finding, scope: str, ontology: Ontology) -> bool:
    if finding.address is not None:
        return in_scope(finding.address.home, scope)
    parts = finding.path.split("/")
    return in_scope(home_of("/".join(parts[1:] if parts[0] == "built" else parts), ontology), scope)


def run_check(
    target: Target, base: str | None = None, *, landing: bool = False, area: str | None = None, loaded: Loaded | None = None
) -> Run[list[Finding]]:
    """Every check (of one scope when given: a layer, `<layer>/<area>` or an area); against `base` (a commit), else the merge
    base with the land branch (refused when `ogy.yml` names none, in a Git repository). `loaded` is a read the caller shares."""
    source, snapshot = loaded or target.read()
    only = _scope(snapshot, area)
    found = base or merge_base(target)
    older = open_source(target.repo, found, target.kb, required=False) if found else None
    older = older if older is not None and older.listing() else None  # no knowledge base at the base: nothing to compare with
    found_in = [
        item
        for item in check(snapshot, source, older, landing=landing, product=target.repo.resolve().name)
        if only is None or _in_scope(item, only, snapshot.ontology)
    ]
    return Run(found_in, source.reads + (older.reads if older else 0), Verdict.FINDINGS if found_in else Verdict.OK)


def run_hook(target: Target, name: str, pushed: str = "") -> Run[list[tuple[hooks.Update, list[Finding]]]]:
    """What a Git hook or the gate guards, each update checked at the commit it will hold: `pre-commit` the staged tree,
    `pre-push` each branch of the push (`pushed`: the hook's standard input), `gate` the worktree; a land (`ogy.hooks`) with the
    landing checks."""
    if name == "pre-commit" and affected.unaffected(target.repo, target.kb):
        return Run([], 0, Verdict.OK)  # affected-file selection: nothing the check reads changed, so no work
    one = {"pre-commit": hooks.staged, "gate": hooks.checked_out}.get(name)
    updates = [one(target.repo)] if one else hooks.pushed(target.repo, pushed)
    found = [(update, run_check(target.at(update.rev), update.base, landing=update.land).value) for update in updates]
    if name == "pre-commit":
        for update, _ in found:
            affected.remember(target.repo, target.kb, update.rev, target.at(update.rev).read()[1])
    return Run(found, 0, Verdict.FINDINGS if any(items for _, items in found) else Verdict.OK)


def run_waiting(target: Target, area: str | None = None) -> int:
    """How many terms wait for the owner (of one area when given); an error only under `check --landing`."""
    snapshot = target.read()[1]
    return waiting(snapshot, _scope(snapshot, area))


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


def _owes(item: Work, scope: str | None, ontology: Ontology) -> bool:
    """The work is in the scope: by the entry's own home; for a requirement a later layer owes, by that layer, by the entry's
    own bare area (an area in every layer), or by that area in the owing layer once it has one (`_scope` refuses it before)."""
    home = home_of(item.address, ontology)
    if not item.owed_by:
        return in_scope(home, scope)
    area = home.rsplit("/", 1)[-1]
    return scope in (None, item.owed_by, area, f"{item.owed_by}/{area}")


def run_work(target: Target, scope: str | None = None, loaded: Loaded | None = None) -> Run[list[Work]]:
    """What the built record says is still to do; given a scope, only in one layer (`product`: what the business still
    has to say, without the build behind it), one `<layer>/<area>`, or one area in every layer."""
    source, snapshot = loaded or target.read()
    _scope(snapshot, scope)
    work = [
        item for item in work_left(snapshot, _record(source), source.repo_file, _ledger(source)) if _owes(item, scope, snapshot.ontology)
    ]
    return Run(work, source.reads, Verdict.FINDINGS if work else Verdict.OK)


def run_brief(target: Target, text: str) -> Run[list[Row]] | None:
    """One work item's brief when `text` is an entry's address, None when it is not (a layer or an area)."""
    source, snapshot = target.read()
    address = snapshot.resolve(text)
    if address is None or address not in snapshot.entries:
        if parse_address(text, snapshot.ontology) is not None:  # an entry's address that names nothing: say what is near
            raise UnknownEntryError(near.no_entry(snapshot, text))
        return None
    record = _record(source)
    found = brief(snapshot, address, work_left(snapshot, record, source.repo_file, _ledger(source)), record)
    return Run(rows(snapshot, found), source.reads, Verdict.FINDINGS if found.work else Verdict.OK)


def run_tracker(target: Target) -> Run[list[Item]]:
    """The whole work left as items a tracker can hold."""
    source, snapshot = target.read()
    record = _record(source)
    found = items(snapshot, work_left(snapshot, record, source.repo_file, _ledger(source)), record)
    return Run(found, source.reads, Verdict.FINDINGS if found else Verdict.OK)


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


def run_export(target: Target, out: str | None = None) -> Run[Path]:
    """Write the product map page: to `out`, else into the Git directory (never committed)."""
    source, snapshot = target.read()
    git = git_dir(target.repo)
    path = Path(out) if out else (git / "ogy" / "view.html" if git else target.repo / "ogy-view.html")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_view(snapshot), encoding="utf-8")
    return Run(path, source.reads)


def run_review(
    target: Target, *, everything: bool = False, area: str | None = None, source_of: str | None = None, page: int = 1
) -> Run[Review]:
    """The cards asked (of one area when given), or one page of what came from `docs` or `code`; they are kept, by id and by
    knowledge base, as the round `reply --round` resolves."""
    source, snapshot = target.read()
    found = review(snapshot, everything=everything, area=_scope(snapshot, area), source=source_of, page=page)
    found = replace(found, cards=[replace(card, changes=card_changes(target.repo, target.kb, snapshot, card)) for card in found.cards])
    kept = rounds.save(target.repo, rounds.make(found.cards, everything=everything)) if found.cards else None
    return Run(replace(found, round_id=kept.id if kept else ""), source.reads)


def run_dropped(target: Target, loaded: Loaded | None = None) -> Run[Dropped]:
    source, snapshot = loaded or target.read()
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


def run_status(target: Target, area: str | None = None, *, with_coverage: bool = False, loaded: Loaded | None = None) -> Run[Overview]:
    """Counts per area, and how many findings, pieces of work and dropped things there are. Saves nothing.
    With `with_coverage`, also the kinds each layer has no entry of. `loaded` is a read the caller shares: one read serves all four."""
    loaded = loaded or target.read()
    source, snapshot = loaded
    only = _scope(snapshot, area)
    found, work, lost = run_check(target, area=only, loaded=loaded), run_work(target, only, loaded), run_dropped(target, loaded)
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


def run_remove(target: Target, text: str, why: str | None = None, to: str | None = None, now: Clock | None = None) -> Run[removal.Removed]:
    """Delete an entry from the worktree (whatever `--rev` says) and record it in its area's removed ledger when the base had it
    (one born since leaves no item: Git keeps it); refuses before writing."""
    clock = now or (lambda: dt.datetime.now(dt.UTC).replace(microsecond=0))
    git = git_dir(target.repo)
    if git is None:
        raise RemoveRefusedError([f"{target.repo} is not a Git repository"])
    try:
        with ProcessLock.acquire(git / "ogy.lock", label="ogy remove"):  # both writes under one lock
            item = removal.remove(
                target.repo,
                target.kb,
                target.kinds(),
                target.ontology,
                text,
                why=why,
                to=to,
                now=clock(),
                last_seen=last_seen(target.repo),
                base=removal_base(target),
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


def run_init(repo: Path, ontology: str | None = None, land: str | None = None) -> Run[Initialised]:
    return Run(init(repo, ontology, land), 0)


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
    ensure: Callable[[], None] | None = None,
) -> Run[Answered]:
    """Choose the option: the answer keeps a short paraphrase of what was said, when and where (no message, no quote);
    with `delegated` an agent answered, under the decision whose person's answer let it decide; who is never a field."""
    who = "ai" if delegated is not None else "human"
    with writes.locked(target, "answer"):
        if ensure is not None:
            ensure()  # a precondition checked under the same lock as the write (the board's inspection version)
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
    ensure: Callable[[], None] | None = None,
) -> Run[reply.Replied]:
    """Apply the owner's reply (a grammar line, with a paraphrase of what they said) to a round; findings when some item was
    refused, refused when all were."""
    with writes.locked(target, "reply"):
        if ensure is not None:
            ensure()
        done = reply.reply(target, text, said, where, at=at, round_id=round_id, now=now, note=note)
    verdict = Verdict.OK if not done.refused else Verdict.FINDINGS if done.changed else Verdict.REFUSED
    return Run(done, 0, verdict)
