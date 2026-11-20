"""What changed in an entry since a person agreed to it, read from Git: a `changed` card shows it, so the owner reads the
change instead of the whole sentence again. An agreement keeps only the hash, so the agreed version is the newest commit
whose file holds the entry with that hash."""

lazy from pathlib import Path

from git_porcelain import GitError, RealRepo

from ogy.semdiff import fields_changed
from ogy.snapshot import build
from ogy.status import Card, Status, agreed_of, status
lazy from ogy.model import Address
lazy from ogy.snapshot import Snapshot

HISTORY = 200  # commits read back for the agreed version
SHOWN = 60  # characters of a value shown


def _short(value: object) -> str:
    text = "-" if value is None else str(value)
    return text if len(text) <= SHOWN else text[: SHOWN - 3] + "..."


def _agreed_version(repo: Path, kb: str, snapshot: Snapshot, address: Address, agreed: str) -> Snapshot | None:
    """The entry's file, at the newest commit where the entry's agreed hash is `agreed`, read alone."""
    rel = snapshot.entries[address].path
    path, last = f"{kb}/{rel}".lstrip("/"), None
    try:
        git = RealRepo(repo)
        for commit in git.history(["HEAD"], limit=HISTORY):
            tree = git.tree(commit.sha)
            data = None if tree is None else tree.read(path)
            if data is None or data == last:
                continue
            last, older = data, build(snapshot.ontology, {rel: data.decode()})
            if address in older.entries and older.agreed_print(address) == agreed:
                return older
    except GitError:
        return None
    return None


def changes(repo: Path, kb: str, snapshot: Snapshot, address: Address) -> tuple[str, ...]:
    """One line per field of the entry or of its parts that changed since the person's yes, `field: old -> new`."""
    agreed = agreed_of(snapshot, address)
    if agreed is None:
        return ()
    older = _agreed_version(repo, kb, snapshot, address, agreed.hash)
    if older is None:
        return (f"the agreed version is not in the last {HISTORY} commits: read it whole",)
    inside = [a for a in sorted({*older.entries, *snapshot.entries}) if a == address or str(a).startswith(f"{address}/")]
    lines: list[str] = []
    for part in inside:
        name = "" if part == address else str(part).removeprefix(f"{address}/") + " "
        old, new = older.entries.get(part), snapshot.entries.get(part)
        if old is None or new is None:
            lines.append(f"{name.strip()}: {'added' if old is None else 'removed'}")
            continue
        lines += [f"{name}{item.name}: {_short(item.old)} -> {_short(item.new)}" for item in fields_changed(old, new)]
    return tuple(lines)


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
