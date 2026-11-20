"""The glossary: the entries of the kind that declares `glossary:` (the terms of every area's `glossary.yml`, the shared ones in
the shared area of a layer). Its word, sentence and avoid fields and the word limit are the ones that kind names. T1-T3 are pure
data checks, T4 and T5 take what another module computed, T6 reads the decisions, `glossary_lines` prints it.

`check_term_agreement` computes T4 and T5 from the agreement and status of each term.
"""

import re
from collections.abc import Callable, Collection, Iterator, Mapping

from ogy.model import Address, Entry, Finding, Problem, link_values
from ogy.settle import decisions
from ogy.status import Agreement, Status, agreed_hashes, agreement, status
lazy from ogy.kinds import Glossary
lazy from ogy.snapshot import Snapshot
lazy from ogy.source import Source

_CODE = re.compile(r"`[^`]*`")
_WORD = re.compile(r"[a-z0-9]+")  # ids split at - and _ too


def terms(snapshot: Snapshot) -> list[Entry]:
    kind = snapshot.ontology.glossary_kind()
    return [entry for address, entry in sorted(snapshot.entries.items()) if kind and address.kind == kind.kind]


def role(snapshot: Snapshot) -> tuple[Glossary, str] | None:
    """The glossary role and the sentence field of the glossary kind."""
    kind = snapshot.ontology.glossary_kind()
    return (kind.glossary, kind.sentence) if kind and kind.glossary and kind.sentence else None


def agreeable(snapshot: Snapshot) -> list[Entry]:
    """The entries of every kind that must be agreed (a term, a principle): only a review round's yes agrees them."""
    return [entry for address, entry in sorted(snapshot.entries.items()) if snapshot.kind_of(address).must_be_agreed]


def _words(text: str) -> list[str]:
    return _WORD.findall(_CODE.sub(" ", text).lower())


def _texts(value: object, names: frozenset[str]) -> Iterator[str]:
    """Agent-written texts of an entry (the fields `names`), parts held in its fields included."""
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in names and isinstance(item, str):
                yield item
            else:
                yield from _texts(item, names)
    elif isinstance(value, list):
        for item in value:
            yield from _texts(item, names)


def _contains(words: list[str], phrase: list[str]) -> bool:
    size = len(phrase)
    return bool(phrase) and any(words[at : at + size] == phrase for at in range(len(words) - size + 1))


def _word(glossary: Glossary, entry: Entry) -> str:
    return (entry.text(glossary.word) or "").strip().lower()


def _avoided(snapshot: Snapshot, glossary: Glossary, entries: list[Entry]) -> list[Finding]:
    avoided = {item: _words(item) for entry in entries for item in link_values(entry.fields.get(glossary.avoid))}
    names = snapshot.ontology.texts()
    found: list[Finding] = []
    for address, entry in snapshot.entries.items():
        spoken = [_words(" ".join(key for _, key in address.path))] + [_words(text) for text in _texts(entry.fields, names)]
        for item, phrase in avoided.items():
            if any(_contains(words, phrase) for words in spoken):
                found.append(Finding(Problem.AVOIDED_WORD, entry.path, f"avoided word {item!r}", address))
    return found


def _compressed(snapshot: Snapshot, glossary: Glossary, entry: Entry) -> list[Finding]:
    """T1: a term says what it means (or the entry it names says it) in one line of fewer words than the glossary's limit."""
    says, limit = snapshot.sentence(entry.address) or "", glossary.words
    if "\n" in says.strip() or len(says.split()) >= limit:
        kind = entry.address.kind
        return [
            Finding(
                Problem.TERM_TOO_LONG, entry.path, f"a {kind} says one line of under {limit} words, not {len(says.split())}", entry.address
            )
        ]
    return []


def _clashes(glossary: Glossary, entries: list[Entry]) -> list[Finding]:
    """T2: no two terms share a word; no avoided item is a term's word."""
    found: list[Finding] = []
    seen: dict[str, Entry] = {}
    for entry in entries:
        if (word := _word(glossary, entry)) in seen:
            found.append(Finding(Problem.WORD_CLASH, entry.path, f"word {word!r} is also the word of {seen[word].address}", entry.address))
        seen.setdefault(word, entry)
    found.extend(
        Finding(Problem.WORD_CLASH, entry.path, f"{glossary.avoid} {item!r} is the word of {other.address}", entry.address)
        for entry in entries
        for item in link_values(entry.fields.get(glossary.avoid))
        if (other := seen.get(item.strip().lower())) is not None
    )
    return found


def check_terms(snapshot: Snapshot, _source: Source | None = None) -> list[Finding]:
    """T1, T2 and T3."""
    if (found := role(snapshot)) is None:
        return check_term_sets(snapshot)
    glossary, _ = found
    entries = terms(snapshot)
    problems = [problem for entry in entries for problem in _compressed(snapshot, glossary, entry)]
    return [*problems, *_clashes(glossary, entries), *_avoided(snapshot, glossary, entries), *check_term_sets(snapshot)]


def check_term_sets(snapshot: Snapshot, _source: Source | None = None) -> list[Finding]:
    """T6: a decision may propose a new word or set a term to null; once a person agreed to a term, no option or proposal
    gives it fields: its words have one home, the term and its agreement."""
    agreed, kind = agreed_hashes(snapshot), snapshot.ontology.glossary_kind()
    found: list[Finding] = []
    for decision in decisions(snapshot):
        for sets in decision.sets_all():
            for text, given in sets.items():
                address = snapshot.resolve(text)
                if address is not None and kind and address.kind == kind.kind and text in agreed and given is not None:
                    found.append(
                        Finding(
                            Problem.AGREED_TERM_IN_SETS,
                            decision.entry.path,
                            f"{text} is agreed: a decision may only set it to null",
                            decision.address,
                        )
                    )
    return found


def terms_not_agreed(snapshot: Snapshot, agreed: Callable[[Address], bool] | Collection[Address]) -> list[Finding]:
    """T4: `agreed` says whether a person agreed to the term or a decision with no answer yet settles it."""
    test = agreed if callable(agreed) else agreed.__contains__
    return [
        Finding(Problem.TERM_NOT_AGREED, e.path, f"a {k} is agreed in a review round or proposed by a decision", e.address)
        for e in agreeable(snapshot)
        if not test(e.address) and (k := snapshot.kind_of(e.address).kind)
    ]


def proposed_terms(snapshot: Snapshot, proposed: Collection[Address]) -> list[Finding]:
    """T5, an error for landing only: terms that only an unanswered decision proposes."""
    return [
        Finding(Problem.PROPOSED_TERM, e.path, f"only an unanswered decision proposes this {k}", e.address)
        for e in agreeable(snapshot)
        if e.address in proposed and (k := snapshot.kind_of(e.address).kind)
    ]


def glossary_homes(snapshot: Snapshot, home: str | None = None) -> list[str]:
    """The homes whose terms `ogy glossary` prints, in order: the `shared` area of each layer, then every other area; for one
    area (`<layer>/<area>`), the `shared` areas of its layer and of the layers before it (a software area reads product's
    too), then the area itself."""
    layers = snapshot.ontology.layers
    shared = [f"{layer}/{snapshot.ontology.shared}" for layer in layers]
    if home is None:
        return [*shared, *sorted({entry.address.home for entry in terms(snapshot)} - set(shared))]
    seen = shared[: layers.index(home.split("/")[0]) + 1]
    return [*seen, *([home] if home not in seen else [])]


def glossary_lines(snapshot: Snapshot, home: str | None = None) -> list[str]:
    """The terms for the terminal, under the home they live in (see `glossary_homes`)."""
    lines: list[str] = []
    if (named := role(snapshot)) is None:
        return lines
    glossary, _ = named
    for where in glossary_homes(snapshot, home):
        found = sorted((entry for entry in terms(snapshot) if entry.address.home == where), key=lambda entry: _word(glossary, entry))
        lines += [f"{where}:"] if found else []
        for entry in found:
            pointed = link_values(entry.fields.get(glossary.names)) if glossary.names else ()
            shown = snapshot.sentence(entry.address) or ""
            lines.append(f"  {entry.text(glossary.word)}: {shown}" + (f" ({pointed[0]})" if pointed else ""))
            if items := link_values(entry.fields.get(glossary.avoid)):
                lines.append(f"    {glossary.avoid}: {'; '.join(items)}")
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
