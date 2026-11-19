"""The write operations on the worktree. Each runs under the ogy lock, writes, checks the entries it touched and, when the
check finds a new error, puts every file back and refuses.

`agree` (inside `reply`) and `answer` change the knowledge base, as `put` does; nothing here writes a status. ogy keeps no
message and no quote: an answer and an agreement keep a short paraphrase of what the person said (`said`), who (`from`),
when (`at`) and where (`where`, the session)."""

import datetime
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass

from atomic_io import atomic_write_text
from git_porcelain import git_dir, head
from process_lock import LockHeldError, ProcessLock

from ogy import near, removal
from ogy.edit import Editor
from ogy.model import Address, Finding, Problem, parse_address
from ogy.removal import RemoveRefused
from ogy.settle import Decision, decision_of, decisions
from ogy.snapshot import Snapshot
from ogy.target import Target, worktree_findings
from ogy.verdict import Refusal

type Clock = Callable[[], datetime.datetime]
type Data = dict[str, object]

PENDING = frozenset({Problem.TERM_NOT_AGREED})  # an agreement that follows the write is no reason to refuse it


class WriteRefused(Refusal):
    """The write was not made (or was put back); `reasons` say why."""


def utc_now() -> datetime.datetime:
    return datetime.datetime.now().astimezone().replace(microsecond=0)


@contextmanager
def locked(target: Target, label: str) -> Iterator[None]:
    git = git_dir(target.repo)
    if git is None:
        raise WriteRefused([f"{target.repo} is not a Git repository"])
    try:
        with ProcessLock.acquire(git / "ogy.lock", label=f"ogy {label}"):
            yield
    except LockHeldError as error:
        raise WriteRefused([f"another ogy write holds {error.path}"]) from error


def files(target: Target) -> dict[str, str]:
    base = target.repo / target.kb
    found = {path.relative_to(base).as_posix(): path for path in sorted(base.rglob("*.yml")) if path.is_file()}
    return {rel: path.read_text() for rel, path in found.items() if not any(part.startswith(".") for part in rel.split("/"))}


def restore(target: Target, before: Mapping[str, str]) -> None:
    base = target.repo / target.kb
    for rel in files(target).keys() - before.keys():
        (base / rel).unlink()
    for rel, text in before.items():
        if not (base / rel).exists() or (base / rel).read_text() != text:
            atomic_write_text(base / rel, text)


def _key(finding: Finding, rename: Callable[[str], str] = str) -> tuple[str, str, str]:
    """A finding at an entry is the same finding wherever its file is; `rename` gives a moved entry its new address."""
    return str(finding.problem), rename(str(finding.address)) if finding.address else finding.path, finding.detail


def _area(rel: str) -> str:
    """The folder a file sits in below its layer (`<layer>/<area>`): a new finding there concerns the write that changed it."""
    return "/".join(rel.split("/")[:2])


def commit(target: Target, touched: Callable[[Snapshot], list[Address]], act: Callable[[Editor], object],
           moved: Callable[[str], str] = str) -> list[str]:
    """Run `act` on the worktree (the lock is held). A finding that is new and concerns the files changed, their areas, or the
    entries `touched` names (with the decisions that settle them), puts everything back and refuses; a finding an entry had
    before it moved (`moved` gives the new address) is not new. Returns the files changed."""
    editor = Editor(target.repo, target.kb, target.kinds())
    before, known = files(target), {_key(item, moved) for item in worktree_findings(target)}
    try:
        act(editor)
        after = files(target)
        changed = sorted(rel for rel in after if before.get(rel) != after[rel])
        snapshot = editor.snapshot()
        homes = {*touched(snapshot), *(d.address for a in touched(snapshot) if (d := decision_of(decisions(snapshot), a)))}
        areas = {_area(rel) for rel in changed}
        new = [item for item in worktree_findings(target) if _key(item) not in known and item.problem not in PENDING
               and (item.path in changed or item.address in homes or _area(item.path) in areas)]
    except BaseException:
        restore(target, before)
        raise
    if new:
        restore(target, before)
        raise WriteRefused([str(item) for item in new])
    return [f"{target.kb}/{rel}".lstrip("/") for rel in changed]


@dataclass(frozen=True)
class Said:
    """What a person said, as kept on an answer or an agreement: a short paraphrase, never their words, and when and where."""

    said: str
    where: str
    at: str
    who: str = "human"
    note: str | None = None

    def stamp(self) -> Data:
        return {"at": self.at, "where": self.where, "from": self.who, "said": self.said}


def said(text: str, where: str, at: str | None, now: Clock = utc_now, who: str = "human", note: str | None = None) -> Said:
    if not text.strip():
        raise WriteRefused(["said is a short paraphrase of what the person said, in one line"])
    if who not in ("human", "ai"):
        raise WriteRefused([f"from is human or ai, not {who!r}"])
    return Said(" ".join(text.split()), where, at or now().isoformat(timespec="seconds"), who, note)


def current(snapshot: Snapshot, addresses: list[Address]) -> dict[str, str]:
    return {str(address): snapshot.fingerprint(address) for address in addresses}


def stamp(editor: Editor, words: Said, hashes: Mapping[str, str]) -> None:
    """Record on each entry the person's yes to the fingerprint given: `agreed: {at, where, from: human, said, hash}`."""
    for text, fingerprint in hashes.items():
        address = editor.snapshot().resolve(text)
        assert address is not None
        editor.update(address, {"agreed": {**words.stamp(), "hash": fingerprint}})


def agree(target: Target, words: Said, texts: list[str], hashes: Mapping[str, str] | None = None) -> list[Address]:
    """A person's yes to the sentence now on each entry (or to the given fingerprints): only a person agrees."""
    if words.who != "human":
        raise WriteRefused(["only a person agrees to a sentence"])
    snapshot = Editor(target.repo, target.kb, target.kinds()).snapshot()
    found = [snapshot.resolve(text) for text in texts]
    if missing := [text for text, address in zip(texts, found, strict=True) if address is None]:
        raise WriteRefused([near.no_entry(snapshot, text) for text in missing])
    addresses = [address for address in found if address is not None]
    given = hashes if hashes is not None else current(snapshot, addresses)
    commit(target, lambda _: addresses, lambda ed: stamp(ed, words, {str(a): given[str(a)] for a in addresses}))
    return addresses


@dataclass(frozen=True)
class Answered:
    decision: Address
    option: str
    changed: list[str]
    removed: list[str]


def _apply(target: Target, editor: Editor, decision: Decision, option: str, now: Clock) -> tuple[list[str], list[str]]:
    """Put the chosen option's `sets` in the worktree: fields given, entries added, then the entries that must not exist
    removed, each after the others of the set that link to it (a transition before the state it ends in)."""
    changed: list[str] = []
    doomed: list[str] = []
    for text, given in sorted(decision.options[option].items()):
        snapshot = editor.snapshot()
        address = parse_address(text, snapshot.ontology)
        if address is None:
            raise WriteRefused([f"{text} is no address"])
        if given is None:
            doomed += [text] if address in snapshot.entries else []
        elif isinstance(given, dict):
            editor.update(address, given) if address in snapshot.entries else editor.put(address, given)
            changed.append(text)
    return changed, _remove_all(target, decision, doomed, now)


def _remove_all(target: Target, decision: Decision, doomed: list[str], now: Clock) -> list[str]:
    """Remove every entry of `doomed`, in passes: one still linked to by another of them waits for the next pass; a pass
    that removes nothing refuses with the reasons."""
    gone: list[str] = []
    while doomed:
        refused: list[str] = []
        before = len(doomed)
        for text in list(doomed):
            try:
                removal.remove(target.repo, target.kb, target.kinds(), target.ontology, text, str(decision.address), None, now(),
                               head(target.repo))
            except (RemoveRefused, LookupError) as error:
                refused += error.reasons if isinstance(error, RemoveRefused) else [str(error)]
                continue
            doomed.remove(text)
            gone.append(text)
        if len(doomed) == before:
            raise WriteRefused(refused)
    return gone


def _delegation(snapshot: Snapshot, words: Said, delegated: str | None) -> str | None:
    """A person answers for themselves; an agent (`from: ai`) answers only under `delegated`, the decision whose person's
    answer let it decide."""
    if words.who == "human":
        if delegated is not None:
            raise WriteRefused(["a person's answer is not delegated: --delegated goes with --from ai"])
        return None
    found = next((item for item in decisions(snapshot) if delegated is not None and str(item.address) == delegated), None)
    newest = max((a for a in found.answers if a.at is not None), key=lambda a: a.at, default=None) if found else None
    if newest is None or newest.who != "human":
        raise WriteRefused(["an agent answers only with --delegated <the decision whose answer, a person's, let it decide>"])
    return str(found.address) if found else None


def answer(target: Target, decision_text: str, option: str, words: Said, delegated: str | None = None,
           now: Clock = utc_now) -> Answered:
    """A person (or an agent under `delegated`) chose an option: append the answer and apply the option's `sets`. The choice
    is the whole answer: it agrees to no sentence the person did not see; only a review round's `yes` does (`reply`)."""
    editor = Editor(target.repo, target.kb, target.kinds())
    snapshot = editor.snapshot()
    proof = _delegation(snapshot, words, delegated)
    found = next((item for item in decisions(snapshot) if str(item.address) == decision_text), None)
    if found is None:
        raise WriteRefused([f"no decision {decision_text}" + near.hint(decision_text, (str(item.address) for item in decisions(snapshot)))])
    if option not in found.options:
        raise WriteRefused([f"{decision_text} has no option {option!r} (options: {', '.join(sorted(found.options)) or 'none'})"])
    outcome: list[Answered] = []

    def act(ed: Editor) -> None:
        extra = (("note", words.note), ("delegated", proof))
        item: Data = {"chose": option, "said": words.said, "from": words.who, "at": words.at, "where": words.where,
                      **{k: v for k, v in extra if v}}
        held = snapshot.entries[found.address].fields.get("answers")
        ed.update(found.address, {"answers": [*(held if isinstance(held, list) else []), item]})
        changed, gone = _apply(target, ed, found, option, now)
        outcome.append(Answered(found.address, option, changed, gone))

    commit(target, lambda snap: [found.address, *(a for text in found.options[option] if (a := snap.resolve(text)))], act)
    return outcome[0]
