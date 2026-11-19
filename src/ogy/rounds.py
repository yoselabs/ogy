"""The rounds of `ogy review`: the cards as they were shown, kept by id so that a reply resolves against what the owner saw.

The last few rounds are kept. It is local working state next to the Git directory,
never part of the knowledge base."""

import re
from pathlib import Path

from atomic_io import atomic_write_text
from content_digest import digest_text
from git_porcelain import git_dir
from pydantic import BaseModel, ConfigDict, ValidationError

from ogy.kinds import Harm
from ogy.status import Card

FOLDER = "ogy-rounds"
KEEP = 10
ID = re.compile(r"r[0-9a-f]+")
ENTRY_CARDS = ("yes", "changed")


class Shown(BaseModel):
    """One card as shown: its label (`Q1`, `2`), what it points at and the fingerprint of that when it was shown."""

    model_config = ConfigDict(frozen=True)

    label: str
    kind: str
    address: str
    shown: str
    fingerprint: str
    options: tuple[str, ...] = ()
    structure: bool = False  # a structural decision: it needs its own letter, a bare `yes` and `yes all` leave it
    members: tuple[tuple[str, str], ...] = ()  # a parent's card: the address and fingerprint of each entry one yes agrees to


class Round(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    everything: bool  # shown with --all: a bare `yes` would agree to cards the owner may not have read
    cards: tuple[Shown, ...]
    seq: int = 0  # the order of saving; the newest has the largest


def labelled(cards: list[Card]) -> list[tuple[str, Card]]:
    """Questions are `Q1`, `Q2`...; every other card is `1`, `2`..."""
    asked, entries = iter(range(1, len(cards) + 1)), iter(range(1, len(cards) + 1))
    return [(f"Q{next(asked)}" if card.kind not in ENTRY_CARDS else str(next(entries)), card) for card in cards]


def make(cards: list[Card], everything: bool) -> Round:
    shown = tuple(Shown(label=label, kind=card.kind, address=str(card.address), shown=card.text, fingerprint=card.fingerprint,
                        options=tuple(key for key, _ in card.options), structure=card.harm is Harm.STRUCTURE,
                        members=tuple((str(address), fingerprint) for address, _, fingerprint in card.members))
                  for label, card in labelled(cards))
    body = Round(id="", everything=everything, cards=shown).model_dump_json()
    return Round(id="r" + digest_text(body, length=6), everything=everything, cards=shown)


def _folder(repo: Path) -> Path | None:
    git = git_dir(repo)
    return None if git is None else git / FOLDER


def _read(path: Path) -> Round | None:
    try:
        return Round.model_validate_json(path.read_text())
    except (ValidationError, OSError):
        return None


def _all(repo: Path) -> list[Round]:
    folder = _folder(repo)
    found = [_read(path) for path in sorted(folder.glob("*.json"))] if folder is not None and folder.is_dir() else []
    return sorted((item for item in found if item is not None), key=lambda item: item.seq)


def save(repo: Path, found: Round) -> Round:
    """Keep the round as the newest and forget all but the last `KEEP`; returns it as kept."""
    folder = _folder(repo)
    if folder is None:
        return found
    held = _all(repo)
    kept = found.model_copy(update={"seq": max((item.seq for item in held), default=0) + 1})
    atomic_write_text(folder / f"{found.id}.json", kept.model_dump_json())
    others = [item for item in held if item.id != found.id]
    for old in others[: max(0, len(others) + 1 - KEEP)]:
        (folder / f"{old.id}.json").unlink(missing_ok=True)
    return kept


def load(repo: Path, round_id: str | None = None) -> Round | None:
    """The round with this id, or the newest round of the repository; None when there is none."""
    if round_id is not None:
        return next((item for item in _all(repo) if item.id == round_id), None) if ID.fullmatch(round_id) else None
    return next(iter(reversed(_all(repo))), None)
