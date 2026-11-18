"""Agreement, status, the label of an unagreed entry and the review queue. Computed from a snapshot, never stored."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ogy.kinds import Harm
from ogy.links import link_items, resolve
from ogy.model import Address
from ogy.settle import Decision, decision_of, decisions, moment, settles
from ogy.snapshot import Snapshot

MAX_CARDS = 7


class Agreement(StrEnum):
    AGREED = "agreed"
    NOT_AGREED = "not agreed"
    CHANGED = "changed since agreed"


class Status(StrEnum):
    QUESTION = "question waiting"
    CHANGED = "changed since you agreed"
    BY_YOU = "decided by you"
    ANSWERED = "answered by you"
    NOBODY = "nobody agreed"


class Label(StrEnum):
    WORDS = "from your words"
    DOCS = "from docs"
    CODE = "from code"
    AI = "decided by AI"


@dataclass(frozen=True)
class Card:
    """One thing the review asks: a `question` (a decision), or a `yes` (decided by AI) or a `changed` entry."""

    kind: str  # question, differs (the guess is not the answer), yes (decided by AI) or changed
    address: Address
    harm: Harm | None
    dependants: int
    text: str = ""  # the question, or the sentence asked about
    guess: str = ""  # the option the AI guessed, for a question
    fingerprint: str = ""  # of the entry or decision as shown: a reply that finds another one is refused
    options: tuple[tuple[str, str], ...] = ()  # (key, label) of a question's options, the AI's guess first
    heard: str = ""  # what the owner said that the guess rests on, paraphrased: one yes answers the question with the guess
    evidence: str = ""  # what stands behind it: "From docs: ...", the guess's reason
    word: str = ""  # a term card: the word (the sentence is its meaning)
    avoid: tuple[str, ...] = ()  # a term card: the words it is not


@dataclass(frozen=True)
class Agreed:
    """A person's yes to an entry (its `agreed`), or the newest answer of a decision: when, where, the hash agreed to, and a
    short paraphrase of what they said."""

    at: datetime
    hash: str
    said: str = ""
    where: str = ""


def agreed_of(snapshot: Snapshot, address: Address) -> Agreed | None:
    """The entry's own `agreed`, when it is well formed."""
    item = snapshot.entries[address].fields.get("agreed")
    if not isinstance(item, dict) or not isinstance(fingerprint := item.get("hash"), str) or (when := moment(item.get("at"))) is None:
        return None
    said, where = item.get("said"), item.get("where")
    return Agreed(when, fingerprint, said if isinstance(said, str) else "", where if isinstance(where, str) else "")


def agreed_in(snapshot: Snapshot) -> dict[str, Agreed]:
    """address text -> the person's yes to it."""
    return {str(address): found for address in snapshot.entries if (found := agreed_of(snapshot, address)) is not None}


def agreed_hashes(snapshot: Snapshot) -> dict[str, str]:
    """address text -> the hash a person agreed to."""
    return {text: found.hash for text, found in agreed_in(snapshot).items()}


def agreement(snapshot: Snapshot, address: Address, hashes: dict[str, str] | None = None) -> Agreement:
    found = (hashes if hashes is not None else agreed_hashes(snapshot)).get(str(address))
    if found is None:
        return Agreement.NOT_AGREED
    return Agreement.AGREED if found == snapshot.fingerprint(address) else Agreement.CHANGED


def label(snapshot: Snapshot, address: Address) -> Label:
    """First match wins: an answered decision that settles it, a `doc:` link, a `code:` link, else decided by AI."""
    items = [item for item in snapshot.entries[address].fields.get("src") or [] if isinstance(item, str)]
    asking = decision_of(decisions(snapshot), address)
    if asking is not None and asking.answers:  # the owner chose the option that sets it; they have not read the sentence back
        return Label.WORDS
    if any(item.startswith("doc:") for item in items):
        return Label.DOCS
    return Label.CODE if any(item.startswith("code:") for item in items) else Label.AI


def status(snapshot: Snapshot, address: Address, hashes: dict[str, str] | None = None) -> Status:
    """First match wins: a decision is a question waiting or answered; else the entry's: a question waiting (a decision proposes it),
    changed since agreed, decided by you, nobody agreed."""
    own = next((d for d in decisions(snapshot) if d.address == address), None)
    if own is not None:
        return Status.ANSWERED if own.answers else Status.QUESTION
    asking = decision_of(decisions(snapshot), address)
    if asking is not None and not asking.answers:
        return Status.QUESTION
    match agreement(snapshot, address, hashes):
        case Agreement.CHANGED:
            return Status.CHANGED
        case Agreement.AGREED:
            return Status.BY_YOU
        case _:
            return Status.NOBODY


def harm(snapshot: Snapshot, address: Address) -> Harm | None:
    """The worst harm the entry's kind declares, or a field it sets declares (`harm:` in the kind file); None when none."""
    kind, fields = snapshot.kind_of(address), snapshot.entries[address].fields
    found = [*kind.harm, *(h for name, spec in kind.fields.items() if fields.get(name) is not None for h in spec.harm)]
    return min(found, default=None, key=list(Harm).index)


def dependants(snapshot: Snapshot) -> dict[Address, int]:
    """How many other entries link to each entry."""
    sources: dict[Address, set[Address]] = {}
    for address, entry in snapshot.entries.items():
        for item in link_items(snapshot.ontology, entry):
            target = resolve(snapshot.ontology, snapshot.entries, address, item).target
            if target is not None and target != address:
                sources.setdefault(target, set()).add(address)
    return {target: len(found) for target, found in sources.items()}


def rank(tag: Harm | None) -> int:
    return list(Harm).index(tag) if tag is not None else len(Harm)


def guess_differs(decision: Decision) -> bool:
    """The AI's guess names an option other than the one the owner's newest answer chose."""
    force, chose = decision.in_force, decision.guess.fields.get("chose") if decision.guess else None
    return bool(force and force.by_answer and isinstance(chose, str) and chose != force.option)


def _reason(decision: Decision) -> str:
    """The line under a question: why the AI guessed it, unless the guess rests on the owner's words (the card's `heard` line)."""
    fields = decision.guess.fields if decision.guess and not (decision.heard and not decision.answers) else {}
    value = fields.get("why")
    return f"AI guess because: {value.strip()}" if isinstance(value, str) and value.strip() else ""


def _asked(snapshot: Snapshot, decision: Decision, count: dict[Address, int], kind: str) -> Card:
    settled = [found for text in settles(decision)[0] if (found := snapshot.resolve(text)) is not None]
    tags = sorted((harm(snapshot, decision.address), *(harm(snapshot, found) for found in settled)), key=rank)
    guess = decision.guess.fields.get("chose") if decision.guess else None
    keys = sorted(decision.options, key=lambda key: (key != guess, key))  # the guess first: it is the recommended one, letter A
    said = decision.heard.fields.get("said") if decision.heard and not decision.answers else None
    options = tuple((key, str(snapshot.entries[decision.address.part("option", key)].fields.get("label", key))) for key in keys)
    return Card(kind, decision.address, tags[0] if tags else None, sum(count.get(found, 0) for found in settled),
                decision.entry.text("question") or "", guess if isinstance(guess, str) else "",
                snapshot.fingerprint(decision.address), options, said if isinstance(said, str) else "", _reason(decision))


def _says(snapshot: Snapshot, address: Address) -> str:
    return snapshot.entries[address].text("says") or ""


def evidence(snapshot: Snapshot, address: Address) -> str:
    """What stands behind an entry's sentence, in a line: the owner's answer, the document or code it came from, or nothing."""
    items = [item for item in snapshot.entries[address].fields.get("src") or [] if isinstance(item, str)]
    shown = next((item for item in items if item.startswith(("doc:", "code:"))), None)
    source = f"; {'from docs' if shown.startswith('doc:') else 'from code'}: {shown}" if shown else ""
    asking = decision_of(decisions(snapshot), address)
    force = asking.in_force if asking is not None and asking.answers else None
    if asking is not None and force is not None and force.by_answer:
        who = "An agent chose, by your delegation," if force.delegated else "You chose"
        return f"{who} {force.option} in {asking.address}{source}"
    found_label = label(snapshot, address)
    if found_label is Label.AI:
        return "Decided by AI: nothing you said supports it"
    return f"{found_label.value.capitalize()}: {shown}" if shown else found_label.value.capitalize()


def entry_card(snapshot: Snapshot, kind: str, address: Address, count: dict[Address, int]) -> Card:
    """A `yes` or `changed` card; a term shows its word, its meaning and the words it is not."""
    fields = snapshot.entries[address].fields
    avoid = fields.get("avoid") or []
    word = str(fields.get("word") or "") if address.kind == "term" else ""
    return Card(kind, address, harm(snapshot, address), count.get(address, 0), _says(snapshot, address),
                fingerprint=snapshot.fingerprint(address), evidence=evidence(snapshot, address), word=word,
                avoid=tuple(str(item) for item in avoid) if word and isinstance(avoid, list) else ())


def queue(snapshot: Snapshot, limit: int | None = MAX_CARDS) -> list[Card]:
    """Questions (and guesses that differ from the answer), then entries decided by AI and entries changed since agreed
    , each group by harm then dependants; at most `limit` in all (None: every one)."""
    count, hashes = dependants(snapshot), agreed_hashes(snapshot)
    questions = [_asked(snapshot, decision, count, "question" if not decision.answers else "differs")
                 for decision in decisions(snapshot) if not decision.answers or guess_differs(decision)]
    cards: list[Card] = []
    for address in snapshot.entries:
        if "says" not in snapshot.kind_of(address).fields or not snapshot.kind_of(address).asked:
            continue
        match status(snapshot, address, hashes):
            case Status.CHANGED:
                cards.append(entry_card(snapshot, "changed", address, count))
            case Status.NOBODY if label(snapshot, address) is Label.AI or snapshot.kind_of(address).must_be_agreed:
                cards.append(entry_card(snapshot, "yes", address, count))

    def order(card: Card) -> tuple[int, int, str]:
        return rank(card.harm), -card.dependants, str(card.address)

    return [*sorted(questions, key=order), *sorted(cards, key=order)][:limit]
