"""The glossary: the terms of every area's `glossary.yml`, the shared ones in the area `shared` of a layer. T1-T3 are pure data
checks, T4 and T5 take what another module computed, `glossary_lines` prints it.

`check_term_agreement` computes T4 and T5 from the agreement and status of each term.
"""

import re
from collections.abc import Callable, Collection, Iterator, Mapping

from ogy.kinds import SHARED_AREA
from ogy.model import Address, Entry, Finding, Problem, link_values
from ogy.snapshot import Snapshot
from ogy.source import Source
from ogy.status import Agreement, Status, agreement, status

TERM = "term"
TERM_WORDS = 15  # a term's `says` has fewer words than this
TEXT_FIELDS = frozenset({"says", "title", "question", "label", "context", "why"})
_CODE = re.compile(r"`[^`]*`")
_WORD = re.compile(r"[a-z0-9]+")  # ids split at - and _ too


def terms(snapshot: Snapshot) -> list[Entry]:
    return [entry for address, entry in sorted(snapshot.entries.items()) if address.kind == TERM]


def agreeable(snapshot: Snapshot) -> list[Entry]:
    """The entries of every kind that must be agreed (a term, a principle): only a review round's yes agrees them."""
    return [entry for address, entry in sorted(snapshot.entries.items()) if snapshot.kind_of(address).must_be_agreed]


def _words(text: str) -> list[str]:
    return _WORD.findall(_CODE.sub(" ", text).lower())


def _texts(value: object) -> Iterator[str]:
    """Agent-written texts of an entry, parts held in its fields included."""
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in TEXT_FIELDS and isinstance(item, str):
                yield item
            else:
                yield from _texts(item)
    elif isinstance(value, list):
        for item in value:
            yield from _texts(item)


def _contains(words: list[str], phrase: list[str]) -> bool:
    size = len(phrase)
    return bool(phrase) and any(words[at:at + size] == phrase for at in range(len(words) - size + 1))


def _word(entry: Entry) -> str:
    return (entry.text("word") or "").strip().lower()


def _avoided(snapshot: Snapshot, entries: list[Entry]) -> list[Finding]:
    avoided = {item: _words(item) for entry in entries for item in link_values(entry.fields.get("avoid"))}
    found: list[Finding] = []
    for address, entry in snapshot.entries.items():
        spoken = [_words(" ".join(key for _, key in address.path))] + [_words(text) for text in _texts(entry.fields)]
        for item, phrase in avoided.items():
            if any(_contains(words, phrase) for words in spoken):
                found.append(Finding(Problem.AVOIDED_WORD, entry.path, f"avoided word {item!r}", address))
    return found


def _compressed(entry: Entry) -> list[Finding]:
    """T1: a term says what it means in one line of under 15 words."""
    says = entry.text("says") or ""
    if "\n" in says.strip() or len(says.split()) >= TERM_WORDS:
        return [Finding(Problem.TERM_TOO_LONG, entry.path, f"a term says one line of under {TERM_WORDS} words, not {len(says.split())}",
                        entry.address)]
    return []


def _clashes(entries: list[Entry]) -> list[Finding]:
    """T2: no two terms share a word; no `avoid` item is a term's word."""
    found: list[Finding] = []
    seen: dict[str, Entry] = {}
    for entry in entries:
        if (word := _word(entry)) in seen:
            found.append(Finding(Problem.WORD_CLASH, entry.path, f"word {word!r} is also the word of {seen[word].address}", entry.address))
        seen.setdefault(word, entry)
    for entry in entries:
        for item in link_values(entry.fields.get("avoid")):
            if (other := seen.get(item.strip().lower())) is not None:
                found.append(Finding(Problem.WORD_CLASH, entry.path, f"avoid {item!r} is the word of {other.address}", entry.address))
    return found


def check_terms(snapshot: Snapshot, source: Source | None = None) -> list[Finding]:
    """T1, T2 and T3."""
    entries = terms(snapshot)
    found = [problem for entry in entries for problem in _compressed(entry)]
    return [*found, *_clashes(entries), *_avoided(snapshot, entries)]


def terms_not_agreed(snapshot: Snapshot, agreed: Callable[[Address], bool] | Collection[Address]) -> list[Finding]:
    """T4: `agreed` says whether a person agreed to the term or a decision with no answer yet settles it."""
    test = agreed if callable(agreed) else agreed.__contains__
    return [Finding(Problem.TERM_NOT_AGREED, e.path, f"a {k} is agreed in a review round or proposed by a decision", e.address)
            for e in agreeable(snapshot) if not test(e.address) and (k := snapshot.kind_of(e.address).kind)]


def proposed_terms(snapshot: Snapshot, proposed: Collection[Address]) -> list[Finding]:
    """T5, an error for landing only: terms that only an unanswered decision proposes."""
    return [Finding(Problem.PROPOSED_TERM, e.path, f"only an unanswered decision proposes this {k}", e.address)
            for e in agreeable(snapshot) if e.address in proposed and (k := snapshot.kind_of(e.address).kind)]


def glossary_homes(snapshot: Snapshot, home: str | None = None) -> list[str]:
    """The homes whose terms `ogy glossary` prints, in order: the `shared` area of each layer, then every other area; for one
    area (`<layer>/<area>`), the `shared` areas of its layer and of the layers before it (a software area reads product's
    too), then the area itself."""
    layers = snapshot.ontology.layers
    shared = [f"{layer}/{SHARED_AREA}" for layer in layers]
    if home is None:
        return [*shared, *sorted({entry.address.home for entry in terms(snapshot)} - set(shared))]
    seen = shared[:layers.index(home.split("/")[0]) + 1]
    return [*seen, *([home] if home not in seen else [])]


def glossary_lines(snapshot: Snapshot, home: str | None = None) -> list[str]:
    """The terms for the terminal, under the home they live in (see `glossary_homes`)."""
    lines: list[str] = []
    for where in glossary_homes(snapshot, home):
        found = sorted((entry for entry in terms(snapshot) if entry.address.home == where), key=_word)
        lines += [f"{where}:"] if found else []
        for entry in found:
            lines.append(f"  {entry.text('word')}: {entry.text('says')}")
            if items := link_values(entry.fields.get("avoid")):
                lines.append(f"    avoid: {'; '.join(items)}")
    return lines


def _agreement(snapshot: Snapshot) -> tuple[list[Address], list[Address]]:
    """The entries no person agreed to, and of those the ones an unanswered decision proposes."""
    unagreed = [e.address for e in agreeable(snapshot) if agreement(snapshot, e.address) is Agreement.NOT_AGREED]
    return unagreed, [address for address in unagreed if status(snapshot, address) is Status.QUESTION]


def waiting(snapshot: Snapshot, area: str | None = None) -> int:
    """How many terms wait for the owner: no person agreed to them and no question proposes them (those are counted as questions)."""
    unagreed, proposed = _agreement(snapshot)
    return len([a for a in unagreed if a not in proposed and area in (None, a.area)])


def check_term_agreement(snapshot: Snapshot, _source: Source | None = None) -> list[Finding]:
    """T4, for landing only: a term is agreed in a review round, or proposed by a decision with no answer yet."""
    unagreed, proposed = _agreement(snapshot)
    return terms_not_agreed(snapshot, lambda address: address not in unagreed or address in proposed)


def check_proposed_terms(snapshot: Snapshot, _source: Source | None = None) -> list[Finding]:
    """T5, for landing only."""
    return proposed_terms(snapshot, _agreement(snapshot)[1])
