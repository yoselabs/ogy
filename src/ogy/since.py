"""What changed in an entry since a person agreed to it, read from Git: a `changed` card shows it, so the owner reads the
change instead of the whole sentence again. An agreement keeps only the hash: the agreed version is the entry in the oldest
commit whose file holds that same stored `agreed.hash` (following the file back through its renames) and whose knowledge base,
read as `ogy migrate` would, gives that entry the same hash again. A yes written with an edit in one commit, or a hash taken under
older kinds, finds no such version, and the card is read whole: a diff against text nobody agreed to would lie."""

from functools import lru_cache
lazy from pathlib import Path

from git_porcelain import GitError, RealRepo

from ogy.kindchange import migrated
from ogy.retype import applied
from ogy.semdiff import fields_changed
from ogy.snapshot import build, load
from ogy.source import open_source
from ogy.status import Card, Status, agreed_of, status
lazy from ogy.model import Address
lazy from ogy.ontology import Ontology
lazy from ogy.snapshot import Snapshot

SHOWN = 60  # characters of a value shown whole
AROUND = 24  # characters kept before and after the part of a long value that differs


def _text(value: object) -> str:
    return "-" if value is None else str(value)


def _differ(old: object, new: object) -> tuple[str, str]:
    """The two values, or for a long one the part that differs with a little around it, the rest cut to `...`."""
    before, after = _text(old), _text(new)
    if max(len(before), len(after)) <= SHOWN:
        return before, after
    same = next((at for at, (a, b) in enumerate(zip(before, after, strict=False)) if a != b), min(len(before), len(after)))
    tail = 0
    while tail < min(len(before), len(after)) - same and before[-1 - tail] == after[-1 - tail]:
        tail += 1
    start = before.rfind(" ", 0, same - AROUND) + 1 if same > AROUND else 0  # from the start of a word

    def cut(text: str) -> str:
        end = min(len(text), len(text) - tail + AROUND)
        piece = text[start:end]
        if len(piece) > SHOWN + 2 * AROUND:
            piece, end = piece[: SHOWN + 2 * AROUND], start  # a long rewrite: its start is enough
        return ("..." if start else "") + piece + ("..." if end < len(text) else "")

    return cut(before), cut(after)


def _commits(repo: Path, path: str) -> list[tuple[str, str]]:
    """(commit, the file's path in it) for every commit that changed the file, oldest first, following renames."""
    done = RealRepo(repo).run(repo, "log", "--follow", "--format=%x00%H", "--name-only", "--", path, check=False)
    found: list[tuple[str, str]] = []
    for block in done.out.split("\0")[1:]:
        lines = [line for line in block.splitlines() if line]
        if len(lines) >= 2:
            found.append((lines[0], lines[-1]))
    return found[::-1]


@lru_cache(maxsize=32)  # a commit's knowledge base never changes; one review rehashes many entries in the same few commits
def _whole(repo: Path, kb: str, sha: str, ontology: Ontology) -> Snapshot:
    """The whole knowledge base of commit `sha`, read as `ogy migrate` would."""
    return migrated(load(open_source(repo, sha, kb, required=False), ontology, retyped=True))


def _rehashed(repo: Path, kb: str, snapshot: Snapshot, sha: str, found: Address) -> str | None:
    """The hash a yes would take of `found` in the whole knowledge base of commit `sha`."""
    older = _whole(repo, kb, sha, snapshot.ontology)
    return older.agreed_print(found) if found in older.entries else None


def _agreed_version(repo: Path, kb: str, snapshot: Snapshot, address: Address, agreed: str) -> tuple[Snapshot, Address] | int:
    """The file of the oldest commit holding the entry (same kind and depth) with `agreed` as its stored hash, read alone as
    `ogy migrate` would read it, and the entry's address there, when its hash rehashed is `agreed` too; else how many commits
    changed the file. A later commit holding the same yes holds later edits, so only the oldest is the version agreed to."""
    prefix = f"{kb}/".lstrip("/")
    commits = _commits(repo, prefix + snapshot.entries[address].path)
    git, last = RealRepo(repo), None
    for sha, path in commits:
        tree = git.tree(sha)
        data = None if tree is None else tree.read(path)
        if data is None or data == last or not path.startswith(prefix):
            continue
        last = data
        older = migrated(build(snapshot.ontology, applied(snapshot.ontology, {path.removeprefix(prefix): data.decode()})))
        for found in older.entries:
            yes = agreed_of(older, found)
            if yes is not None and yes.hash == agreed and found.kind == address.kind and len(found.path) == len(address.path):
                return (older, found) if _rehashed(repo, kb, snapshot, sha, found) == agreed else len(commits)
    return len(commits)


def changes(repo: Path, kb: str, snapshot: Snapshot, address: Address) -> tuple[str, ...]:
    """One line per field of the entry or of its parts that changed since the person's yes, `field: old -> new`."""
    agreed = agreed_of(snapshot, address)
    if agreed is None:
        return ()
    try:
        found = _agreed_version(repo, kb, snapshot, address, agreed.hash)
    except GitError:
        found = 0
    if isinstance(found, int):
        return (f"no commit holds the version agreed to ({found} read): read it whole",)
    older, then = found
    old = {str(a).removeprefix(str(then)): older.entries[a] for a in older.entries if a == then or str(a).startswith(f"{then}/")}
    new = {
        str(a).removeprefix(str(address)): snapshot.entries[a] for a in snapshot.entries if a == address or str(a).startswith(f"{address}/")
    }
    lines: list[str] = []
    for part in sorted({*old, *new}):
        name = part.removeprefix("/") + " " if part else ""
        if part not in old or part not in new:
            lines.append(f"{name.strip()}: {'added' if part not in old else 'removed'}")
            continue
        for item in fields_changed(old[part], new[part]):
            before, after = _differ(item.old, item.new)
            lines.append(f"{name}{item.name}: {before} -> {after}")
    return tuple(lines) or ("its own fields are as agreed: what changed is something its yes reaches (a link, a step it leads to)",)


def card_changes(repo: Path, kb: str, snapshot: Snapshot, card: Card) -> tuple[str, ...]:
    """What changed since agreed, for a `changed` card: of the entry, and of each member changed since its own yes (named)."""
    if card.kind != "changed":
        return ()
    found: list[str] = []
    for address in [card.address, *(member for member, _, _ in card.members if member != card.address)]:
        if address not in snapshot.entries or status(snapshot, address) is not Status.CHANGED:
            continue
        name = "" if address == card.address else str(address).removeprefix(f"{card.address}/") + ": "
        found += [f"{name}{line}" for line in changes(repo, kb, snapshot, address)]
    return tuple(found)
