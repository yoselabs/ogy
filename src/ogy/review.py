"""What the owner is asked: a count per area, and what no person has seen yet. Computed from a snapshot."""

from collections import Counter
from dataclasses import dataclass

from ogy.model import Address
from ogy.pages import pages
from ogy.removed import Item, is_address
from ogy.settle import decisions
from ogy.snapshot import Snapshot
from ogy.status import MAX_CARDS, Card, Label, Status, agreed_hashes, guess_differs, label, queue, status
from ogy.verdict import NotFound


@dataclass(frozen=True)
class Header:
    """One home's (`<layer>/<area>`) standing. Decisions are counted apart from entries:
    `land   6 questions open · 5 answered by you | entries: 0 decided by AI · 6 from docs · 39 from code · 0 decided by you · 0 changed`."""

    area: str
    questions: int
    answered: int
    ai: int
    docs: int
    code: int
    you: int
    changed: int = 0

    def __str__(self) -> str:
        return (f"{self.area}   {self.questions} questions open · {self.answered} answered by you | entries: {self.ai} {Label.AI} · "
                f"{self.docs} {Label.DOCS} · {self.code} {Label.CODE} · {self.you} {Status.BY_YOU} · {self.changed} changed since agreed")


def headers(snapshot: Snapshot) -> list[Header]:
    count: dict[str, Counter[str]] = {}
    hashes = agreed_hashes(snapshot)
    for decision in decisions(snapshot):
        count.setdefault(decision.address.home, Counter())["answered" if decision.answers else "question"] += 1
    for address in snapshot.entries:
        if "says" not in snapshot.kind_of(address).fields or not snapshot.kind_of(address).asked:
            continue
        found = count.setdefault(address.home, Counter())
        match status(snapshot, address, hashes):
            case Status.BY_YOU:
                found["you"] += 1
            case Status.CHANGED:
                found["changed"] += 1
            case Status.NOBODY:
                found[str(label(snapshot, address))] += 1
    return [Header(area, n["question"], n["answered"], n[Label.AI], n[Label.DOCS], n[Label.CODE], n["you"], n["changed"])
            for area, n in sorted(count.items())]


@dataclass(frozen=True)
class Review:
    """The standing of every area, and the cards the owner is asked (at most 7 unless everything is asked for)."""

    headers: list[Header]
    cards: list[Card]
    waiting: int  # the cards the 7 leave out
    round_id: str = ""  # the round `review` saved; `reply --round` names it
    area: str = ""  # the one area asked about; empty for all
    source: str = ""  # `docs` or `code` when the cards are a page of what came from there
    page: int = 0
    pages: int = 0
    title: str = ""  # the page's document section, the terms of an area, or an area


def _headers(snapshot: Snapshot, area: str | None) -> list[Header]:
    return [item for item in headers(snapshot) if area in (None, item.area.rsplit("/", 1)[-1])]


def review(snapshot: Snapshot, everything: bool = False, area: str | None = None, source: str | None = None, page: int = 1) -> Review:
    if source is not None:
        found = pages(snapshot, source, area)
        if found and not 1 <= page <= len(found):
            raise NotFound(f"no page {page} of {source}: there are {len(found)}")
        shown = found[page - 1] if found else None
        return Review(_headers(snapshot, area), list(shown.cards) if shown else [], 0,
                      area=area or "", source=source, page=page if shown else 0, pages=len(found), title=shown.title if shown else "")
    cards = [card for card in queue(snapshot, None) if area in (None, card.address.area)]
    shown = cards if everything else cards[:MAX_CARDS]
    return Review(_headers(snapshot, area), shown, len(cards) - len(shown), area=area or "")


@dataclass(frozen=True)
class Dropped:
    """What no person has seen, and what a person only half said."""

    guessed_no: tuple[Address, ...]  # the AI's guess in force says no (sets an address to null)
    unexplained: tuple[str, ...]  # removed ids whose `why` is null (older removals; a new one always has a why)
    differs: tuple[Address, ...]  # the guess is not the owner's answer (also a card)
    plain_why: tuple[str, ...] = ()  # removed ids whose `why` is plain words, not the address of a decision
    noted: tuple[Address, ...] = ()  # decisions with an answer that carries a note: the owner's hedge or condition
    delegated: tuple[Address, ...] = ()  # decisions with an answer an agent gave under a delegation: the person may veto it

    def __len__(self) -> int:
        return sum(len(group) for group in (self.guessed_no, self.unexplained, self.differs, self.plain_why, self.noted, self.delegated))


def dropped(snapshot: Snapshot, ledger: list[Item]) -> Dropped:
    found = decisions(snapshot)
    guessed = [d.address for d in found if (force := d.in_force) and not force.by_answer and None in force.sets.values()]
    differs = [d.address for d in found if guess_differs(d)]
    noted = [d.address for d in found if any(a.note for a in d.answers)]
    delegated = [d.address for d in found if any(a.who == "ai" for a in d.answers)]
    plain = [item.id for item in ledger if item.why is not None and not is_address(item.why)]
    return Dropped(tuple(guessed), tuple(item.id for item in ledger if item.why is None), tuple(differs), tuple(plain), tuple(noted),
                   tuple(delegated))
