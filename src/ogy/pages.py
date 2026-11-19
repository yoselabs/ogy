"""`ogy review --from docs|code`: the entries nobody has agreed to whose sentence came from a document or from code, paged.

A page is one document section (or the terms of one area) for `docs`, one area for `code`, cut to at most `PAGE` cards. A page is
a round like any other: the owner's `yes` agrees to all of it, `yes 2 5` to some. What the owner agreed to leaves the pages."""

from dataclasses import dataclass

from ogy.declared import Reader
from ogy.evidence import Link, parse_link
from ogy.model import link_values
from ogy.snapshot import Snapshot
from ogy.status import Card, Label, Status, agreed_hashes, dependants, entry_card, label, status

PAGE = 12
SOURCES = {"docs": Label.DOCS, "code": Label.CODE}


@dataclass(frozen=True)
class Page:
    title: str
    cards: tuple[Card, ...]


def _group(snapshot: Snapshot, card: Card, source: Label) -> str:
    fields = snapshot.entries[card.address].fields
    if source is Label.CODE:
        return f"{card.address.home}: from code"
    if card.word:
        return f"{card.address.home}: terms"
    schemes = snapshot.ontology.declared.evidence
    where = next((link for item in link_values(fields.get(snapshot.ontology.roles.src))
                  if isinstance(link := parse_link(item, schemes), Link) and link.reads is Reader.SECTION), None)
    return f"{card.address.home}: {f'{where.path}#{where.fragment}' if where else ''}"


def pages(snapshot: Snapshot, source: str, area: str | None = None) -> list[Page]:
    """The pages of one source, each group in address order; empty when the owner has agreed to everything of it."""
    wanted, count, hashes = SOURCES[source], dependants(snapshot), agreed_hashes(snapshot)
    groups: dict[str, list[Card]] = {}
    for address in snapshot.entries:
        if not snapshot.ontology.carded(snapshot.kind_of(address)):
            continue
        if area not in (None, address.area) or status(snapshot, address, hashes) is not Status.NOBODY:
            continue
        if label(snapshot, address) is not wanted:
            continue
        card = entry_card(snapshot, "yes", address, count)
        groups.setdefault(_group(snapshot, card, wanted), []).append(card)
    found: list[Page] = []
    for title, cards in sorted(groups.items()):
        ordered = sorted(cards, key=lambda c: (snapshot.ontology.declared.rank(c.harm), -c.dependants, str(c.address)))
        chunks = [ordered[at:at + PAGE] for at in range(0, len(ordered), PAGE)]
        found += [Page(title if len(chunks) == 1 else f"{title} ({n}/{len(chunks)})", tuple(chunk)) for n, chunk in enumerate(chunks, 1)]
    return found
