"""The write operations on the worktree. Each runs under the ogy lock, writes, checks the entries it touched and, when the
check finds a new error, puts every file back and refuses.

`agree` (inside `reply`) and `answer` change the knowledge base, as `put` does; nothing here writes a status. ogy keeps no
message and no quote: an answer and an agreement keep a short paraphrase of what the person said (`said`), when (`at`) and
where (`where`, the session), in the names the settling kind gives them; who answered is computed from `delegated`."""

import datetime as dt
from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass

from atomic_io import atomic_write_text
from git_porcelain import git_dir, head
from process_lock import LockHeldError, ProcessLock

from ogy import near, removal
from ogy.edit import Editor
from ogy.fieldtypes import AGREED_HASH
from ogy.model import Address, Finding, Problem, parse_address
from ogy.removal import RemoveRefusedError
from ogy.settle import Decision, answers_key, decision_of, decisions
from ogy.target import Target, worktree_findings
from ogy.verdict import RefusalError
lazy from ogy.kinds import Settling
lazy from ogy.snapshot import Snapshot

type Clock = Callable[[], dt.datetime]
type Data = dict[str, object]

PENDING = frozenset({Problem.TERM_NOT_AGREED})  # an agreement that follows the write is no reason to refuse it


class WriteRefusedError(RefusalError):
    """The write was not made (or was put back); `reasons` say why."""


def utc_now() -> dt.datetime:
    return dt.datetime.now().astimezone().replace(microsecond=0)


@contextmanager
def locked(target: Target, label: str) -> Generator[None]:
    git = git_dir(target.repo)
    if git is None:
        raise WriteRefusedError([f"{target.repo} is not a Git repository"])
    try:
        with ProcessLock.acquire(git / "ogy.lock", label=f"ogy {label}"):
            yield
    except LockHeldError as error:
        raise WriteRefusedError([f"another ogy write holds {error.path}"]) from error


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


def commit(
    target: Target,
    touched: Callable[[Snapshot], list[Address]],
    act: Callable[[Editor], object],
    moved: Callable[[str], str] = str,
    known: set[tuple[str, str, str]] | None = None,
) -> list[str]:
    """Run `act` on the worktree (the lock is held). A finding that is new and concerns the files changed, their areas, or the
    entries `touched` names (with the decisions that settle them), puts everything back and refuses; a finding an entry had
    before it moved (`moved` gives the new address) is not new, nor is one of `known` (`findings_after`). Returns the files
    changed."""
    editor = Editor(target.repo, target.kb, target.kinds())
    before = files(target)
    known = known if known is not None else {_key(item, moved) for item in worktree_findings(target)}
    try:
        act(editor)
        after = files(target)
        changed = sorted(rel for rel in after if before.get(rel) != after[rel])
        snapshot = editor.snapshot()
        homes = {*touched(snapshot), *(d.address for a in touched(snapshot) if (d := decision_of(decisions(snapshot), a)))}
        areas = {_area(rel) for rel in changed}
        new = [
            item
            for item in worktree_findings(target)
            if _key(item) not in known
            and item.problem not in PENDING
            and (item.path in changed or item.address in homes or _area(item.path) in areas)
        ]
    except BaseException:
        restore(target, before)
        raise
    if new:
        restore(target, before)
        raise WriteRefusedError([str(item) for item in new])
    return [f"{target.kb}/{rel}".lstrip("/") for rel in changed]


def findings_after(target: Target, changed: Mapping[str, str | None]) -> set[tuple[str, str, str]]:
    """The findings of the worktree with `changed` written (`{path: text}`, None deletes), as keys; the files are put back. A
    file a kind rename moves is read nowhere before it moves, so what it held is known only after (`ogy migrate`)."""
    before, base = files(target), target.repo / target.kb
    try:
        for rel, text in changed.items():
            if text is None:
                (base / rel).unlink()
            else:
                (base / rel).parent.mkdir(parents=True, exist_ok=True)
                atomic_write_text(base / rel, text)
        return {_key(item) for item in worktree_findings(target)}
    finally:
        restore(target, before)


@dataclass(frozen=True)
class Said:
    """What a person said, as kept on an answer or an agreement: a short paraphrase, never their words, and when and where."""

    said: str
    where: str
    at: str
    who: str = "human"
    note: str | None = None

    def stamp(self, names: Settling) -> Data:
        return {names.at: self.at, names.where: self.where, names.said: self.said}


def said(text: str, where: str, at: str | None, now: Clock = utc_now, *, who: str = "human", note: str | None = None) -> Said:
    if not text.strip():
        raise WriteRefusedError(["said is a short paraphrase of what the person said, in one line"])
    if who not in ("human", "ai"):
        raise WriteRefusedError([f"from is human or ai, not {who!r}"])
    return Said(" ".join(text.split()), where, at or now().isoformat(timespec="seconds"), who, note)


def current(snapshot: Snapshot, addresses: list[Address]) -> dict[str, str]:
    return {str(address): snapshot.agreed_print(address) for address in addresses}


def stamp(editor: Editor, words: Said, hashes: Mapping[str, str]) -> None:
    """Record on each entry the person's yes to the fingerprint given: `agreed: {at, where, said, hash}`."""
    for text, fingerprint in hashes.items():
        snapshot = editor.snapshot()
        address, names = snapshot.resolve(text), settling(snapshot)
        if address is None:
            raise WriteRefusedError([f"{text} is no longer an entry"])
        editor.update(address, {snapshot.ontology.roles.agreed: {**words.stamp(names), AGREED_HASH: fingerprint}})


def settling(snapshot: Snapshot) -> Settling:
    """The settling kind's names: an answer and an agreement are written in them."""
    kind = snapshot.ontology.settling_kind()
    if kind is None or kind.settling is None:
        raise WriteRefusedError(["the ontology has no settling kind: nothing answers or agrees"])
    return kind.settling


def agree(target: Target, words: Said, texts: list[str], hashes: Mapping[str, str] | None = None) -> list[Address]:
    """A person's yes to the sentence now on each entry (or to the given fingerprints): only a person agrees."""
    if words.who != "human":
        raise WriteRefusedError(["only a person agrees to a sentence"])
    snapshot = Editor(target.repo, target.kb, target.kinds()).snapshot()
    found = [snapshot.resolve(text) for text in texts]
    if missing := [text for text, address in zip(texts, found, strict=True) if address is None]:
        raise WriteRefusedError([near.no_entry(snapshot, text) for text in missing])
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
            raise WriteRefusedError([f"{text} is no address"])
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
                removal.remove(
                    target.repo,
                    target.kb,
                    target.kinds(),
                    target.ontology,
                    text,
                    why=str(decision.address),
                    to=None,
                    now=now(),
                    last_seen=head(target.repo),
                )
            except (RemoveRefusedError, LookupError) as error:
                refused += error.reasons if isinstance(error, RemoveRefusedError) else [str(error)]
                continue
            doomed.remove(text)
            gone.append(text)
        if len(doomed) == before:
            raise WriteRefusedError(refused)
    return gone


def _delegation(snapshot: Snapshot, words: Said, delegated: str | None) -> str | None:
    """A person answers for themselves; an agent answers only under `delegated`, the decision whose person's answer let it
    decide (who answered is computed from `delegated`)."""
    if words.who == "human":
        return None
    found = next((item for item in decisions(snapshot) if delegated is not None and str(item.address) == delegated), None)
    newest = found.newest if found else None
    if newest is None or newest.who != "human":
        raise WriteRefusedError(["an agent answers only with --delegated <the decision whose answer, a person's, let it decide>"])
    return str(found.address) if found else None


def answer(target: Target, decision_text: str, option: str, words: Said, delegated: str | None = None, *, now: Clock = utc_now) -> Answered:
    """A person (or an agent under `delegated`) chose an option: append the answer and apply the option's `sets`. A person's
    answer also agrees to the entries the option sets, as their cards show them (decision answer-agrees-shown); an agent's
    agrees to nothing."""
    editor = Editor(target.repo, target.kb, target.kinds())
    snapshot = editor.snapshot()
    proof = _delegation(snapshot, words, delegated)
    found = next((item for item in decisions(snapshot) if str(item.address) == decision_text), None)
    if found is None:
        raise WriteRefusedError(
            [f"no decision {decision_text}" + near.hint(decision_text, (str(item.address) for item in decisions(snapshot)))]
        )
    if option not in found.options:
        raise WriteRefusedError([f"{decision_text} has no option {option!r} (options: {', '.join(sorted(found.options)) or 'none'})"])
    outcome: list[Answered] = []

    names, key = settling(snapshot), answers_key(snapshot)

    def act(ed: Editor) -> None:
        extra = ((names.note, words.note), (names.delegated, proof))
        item: Data = {
            names.chose: option,
            names.said: words.said,
            names.at: words.at,
            names.where: words.where,
            **{k: v for k, v in extra if v},
        }
        held = snapshot.entries[found.address].fields.get(key)
        ed.update(found.address, {key: [*(held if isinstance(held, list) else []), item]})
        changed, gone = _apply(target, ed, found, option, now)
        if words.who == "human" and changed:
            after = ed.snapshot()
            stamp(ed, words, {text: after.agreed_print(address) for text in changed if (address := after.resolve(text)) is not None})
        outcome.append(Answered(found.address, option, changed, gone))

    commit(target, lambda snap: [found.address, *(a for text in found.options[option] if (a := snap.resolve(text)))], act)
    return outcome[0]
