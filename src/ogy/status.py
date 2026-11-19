"""Agreement, status, the label of an unagreed entry and the review queue. Computed from a snapshot, never stored."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ogy.declared import Reader, Scheme
from ogy.fieldtypes import AGREED_HASH
from ogy.kinds import Holds, Kind
from ogy.links import link_items, resolve
from ogy.model import Address, parse_address
from ogy.settle import Decision, decision_of, decisions, moment, settles, settling_of
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
    """One thing the review asks: a `question` (a decision with no answer), a `delegated` decision (an agent answered it under
    the owner's delegation: the owner may confirm or veto), or a `yes` (decided by AI) or a `changed` entry."""

    kind: str  # question, delegated, yes (decided by AI) or changed
    address: Address
    harm: str | None  # the worst harm tag
    dependants: int
    text: str = ""  # the question, or the sentence asked about
    guess: str = ""  # the option the AI guessed, for a question; the option in force, for a delegated decision
    fingerprint: str = ""  # of the entry or decision as shown: a reply that finds another one is refused
    options: tuple[tuple[str, str], ...] = ()  # (key, label) of a question's options, the AI's guess first
    heard: str = ""  # what the owner said that the guess rests on, paraphrased: one yes answers the question with the guess
    evidence: str = ""  # what stands behind it: "From docs: ...", the guess's reason
    word: str = ""  # a term card: the word (the sentence is its meaning)
    avoid: tuple[str, ...] = ()  # a term card: the words it is not
    context: str = ""  # a decision card: why the question comes up, so the card reads on its own
    then: tuple[tuple[str, ...], ...] = ()  # a decision card: what each option (same order as `options`) makes true
    earlier: str = ""  # a delegated card: the owner's own earlier answer, which the agent's answer replaced
    members: tuple[tuple[Address, str, str], ...] = ()  # a parent's card: each waiting entry, sentence, fingerprint
    alone: bool = False  # its harm is asked alone (`asked_alone`): its own letter, never inside a bulk accept


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
    item = snapshot.entries[address].fields.get(snapshot.ontology.roles.agreed)
    names = settling_of(snapshot)
    if not isinstance(item, dict) or names is None or not isinstance(fingerprint := item.get(AGREED_HASH), str):
        return None
    if (when := moment(item.get(names.at))) is None:
        return None
    said, where = item.get(names.said), item.get(names.where)
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
    """First match wins: an answered decision that settles it, a document section, a code symbol, else decided by AI."""
    asking = decision_of(decisions(snapshot), address)
    if asking is not None and asking.answers:  # the owner chose the option that sets it; they have not read the sentence back
        return Label.WORDS
    read = {scheme.reads for _, scheme in sources(snapshot, address)}
    return Label.DOCS if Reader.SECTION in read else Label.CODE if Reader.SYMBOL in read else Label.AI


def sources(snapshot: Snapshot, address: Address) -> list[tuple[str, Scheme]]:
    """The entry's evidence items, each with its scheme."""
    items = snapshot.entries[address].fields.get(snapshot.ontology.roles.src) or []
    declared = snapshot.ontology.declared
    return [(item, scheme) for item in items if isinstance(item, str) and (scheme := declared.scheme_of(item)) is not None]


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


def _member_harms(kind: Kind, fields: Mapping[str, object]) -> list[str]:
    """The harms of the enum members the fields hold (`member_harm:` in the kind file)."""
    return [tag for name, spec in kind.fields.items() if isinstance(value := fields.get(name), str)
            for tag in spec.member_harm.get(value, ())]


def harm(snapshot: Snapshot, address: Address) -> str | None:
    """The worst harm the entry's kind declares, a field it sets declares (`harm:` in the kind file), or an enum member it or
    one of its list parts holds declares (`member_harm:`, e.g. a row whose effect deletes); None when none."""
    kind, fields = snapshot.kind_of(address), snapshot.entries[address].fields
    found = [*kind.harm, *(h for name, spec in kind.fields.items() if fields.get(name) is not None for h in spec.harm)]
    found += _member_harms(kind, fields)
    for part in snapshot.ontology.parts_of(kind.kind):
        items = fields.get(part.key or "")
        if part.holding is Holds.LIST and isinstance(items, list):
            found += [tag for item in items if isinstance(item, dict) for tag in _member_harms(part, item)]
    return min(found, default=None, key=snapshot.ontology.declared.rank)


def asked_alone(snapshot: Snapshot, tag: str | None) -> bool:
    """A card of this harm is asked on its own, never inside a bulk accept."""
    return tag is not None and tag in snapshot.ontology.declared.asked_alone


def dependants(snapshot: Snapshot) -> dict[Address, int]:
    """How many other entries link to each entry."""
    sources: dict[Address, set[Address]] = {}
    for address, entry in snapshot.entries.items():
        for item in link_items(snapshot.ontology, entry):
            target = resolve(snapshot.ontology, snapshot.entries, address, item).target
            if target is not None and target != address:
                sources.setdefault(target, set()).add(address)
    return {target: len(found) for target, found in sources.items()}


def delegated(decision: Decision) -> bool:
    """The answer in force is an agent's, under the owner's delegation: once a decision has an answer its guess is inert."""
    force = decision.in_force
    return bool(force and force.by_answer and force.delegated)


def _reason(decision: Decision) -> str:
    """The line under a question: why the AI guessed it, unless the guess rests on the owner's words (the card's `heard` line)."""
    if decision.answers:
        return ""
    fields = decision.guess.fields if decision.guess and not decision.heard else {}
    value = fields.get(decision.names.why)
    return f"AI guess because: {value.strip()}" if isinstance(value, str) and value.strip() else ""


def _asked(snapshot: Snapshot, decision: Decision, count: dict[Address, int], kind: str) -> Card:
    settled = [found for text in settles(decision)[0] if (found := snapshot.resolve(text)) is not None]
    tags = sorted((harm(snapshot, decision.address), *(harm(snapshot, found) for found in settled)), key=snapshot.ontology.declared.rank)
    force, names = decision.in_force, decision.names
    guess = force.option if decision.answers and force else decision.guess.fields.get(names.chose) if decision.guess else None
    keys = sorted(decision.options, key=lambda key: (key != guess, key))  # the guess (or the option in force) first: letter A
    said = decision.heard if not decision.answers else None
    addresses = [decision.address.part(names.option, key) for key in keys]
    options = tuple((key, snapshot.sentence(address) or key) for key, address in zip(keys, addresses, strict=True))
    return Card(kind, decision.address, tags[0] if tags else None, sum(count.get(found, 0) for found in settled),
                snapshot.sentence(decision.address) or "", guess if isinstance(guess, str) else "",
                snapshot.fingerprint(decision.address), options, said if isinstance(said, str) else "", _reason(decision),
                context=decision.entry.text(names.context) or "",
                then=tuple(_then(snapshot, snapshot.entries[address].fields.get(names.sets)) for address in addresses),
                earlier=_earlier(decision) if kind == "delegated" else "", alone=asked_alone(snapshot, tags[0] if tags else None))


def _then(snapshot: Snapshot, sets: object) -> tuple[str, ...]:
    """What an option makes true, one line per entry it sets: its sentence, its other fields, or that it does not exist."""
    if not isinstance(sets, dict):
        return ()
    lines: list[str] = []
    for target, fields in sets.items():
        if not isinstance(fields, dict):
            lines.append(f"{target} does not exist")
            continue
        address = parse_address(str(target), snapshot.ontology)
        kind = snapshot.ontology.get(address.kind) if address else None
        sentence = kind.sentence if kind else None
        says = fields.get(sentence) if sentence else None
        rest = ", ".join(f"{name} = {value}" for name, value in fields.items() if name != sentence)
        lines.append(f"{target}: {says}" if isinstance(says, str) else f"{target}")
        if rest:
            lines[-1] += ("; " if isinstance(says, str) else ": ") + rest
    return tuple(lines)


def _earlier(decision: Decision) -> str:
    """For a delegated answer: the owner's own last answer before it, when it chose another option."""
    force = decision.in_force
    dated = [item for _, item in sorted(((item.at, index), item) for index, item in enumerate(decision.answers) if item.at is not None)]
    human = [item for item in dated if item.who == "human"]
    if not human or force is None or human[-1].chose == force.option:
        return ""
    return f"You chose {human[-1].chose} earlier; an agent changed it: {dated[-1].said}"


def _says(snapshot: Snapshot, address: Address) -> str:
    return snapshot.sentence(address) or ""


def evidence(snapshot: Snapshot, address: Address) -> str:
    """What stands behind an entry's sentence, in a line: the owner's answer, the document or code it came from, or nothing."""
    shown, scheme = next(iter(sources(snapshot, address)), (None, None))
    source = f"; {'from docs' if scheme.reads is Reader.SECTION else 'from code'}: {shown}" if shown and scheme else ""
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
    """A `yes` or `changed` card; a word of the glossary shows its word, its meaning and the words it is not."""
    fields, glossary = snapshot.entries[address].fields, snapshot.kind_of(address).glossary
    avoid = fields.get(glossary.avoid) or [] if glossary else []
    word = str(fields.get(glossary.word) or "") if glossary else ""
    tag = harm(snapshot, address)
    return Card(kind, address, tag, count.get(address, 0), _says(snapshot, address), alone=asked_alone(snapshot, tag),
                fingerprint=snapshot.fingerprint(address), evidence=evidence(snapshot, address), word=word,
                avoid=tuple(str(item) for item in avoid) if word and isinstance(avoid, list) else ())


def queue(snapshot: Snapshot, limit: int | None = MAX_CARDS) -> list[Card]:
    """Questions and the decisions an agent answered under delegation, then entries decided by AI and entries changed since
    agreed, each group by harm then dependants; at most `limit` in all (None: every one)."""
    count, hashes = dependants(snapshot), agreed_hashes(snapshot)
    questions = [_asked(snapshot, decision, count, "question" if not decision.answers else "delegated")
                 for decision in decisions(snapshot) if not decision.answers or delegated(decision)]
    cards: list[Card] = []
    for address in snapshot.entries:
        if not snapshot.kind_of(address).asked or not snapshot.ontology.carded(snapshot.kind_of(address)):
            continue
        match status(snapshot, address, hashes):
            case Status.CHANGED:
                cards.append(entry_card(snapshot, "changed", address, count))
            case Status.NOBODY if label(snapshot, address) is Label.AI or snapshot.kind_of(address).must_be_agreed:
                cards.append(entry_card(snapshot, "yes", address, count))

    def order(card: Card) -> tuple[int, int, str]:
        return snapshot.ontology.declared.rank(card.harm), -card.dependants, str(card.address)

    return [*sorted(questions, key=order), *sorted(_by_parent(snapshot, cards, count), key=order)][:limit]


def _top(address: Address) -> Address:
    while (parent := address.parent()) is not None:
        address = parent
    return address


def _by_parent(snapshot: Snapshot, cards: list[Card], count: dict[Address, int]) -> list[Card]:
    """One card per workflow or entity: its waiting parts (and itself, when waiting) are listed on it, and one yes agrees to
    them all (product/review/rule/one-card-per-parent). A card of an entry with no parts stays as it is."""
    groups: dict[Address, list[Card]] = {}
    alone: list[Card] = []
    for card in cards:
        top = _top(card.address)
        if top in snapshot.entries and (top != card.address or snapshot.ontology.parts_of(top.kind)):
            groups.setdefault(top, []).append(card)
        else:
            alone.append(card)
    for top, members in groups.items():
        if [card.address for card in members] == [top]:
            alone.append(members[0])
            continue
        members.sort(key=lambda card: (card.address != top, str(card.address)))
        kind = "changed" if any(card.kind == "changed" for card in members) else "yes"
        worst = min((card.harm for card in members), key=snapshot.ontology.declared.rank, default=None)
        alone.append(Card(kind, top, worst, count.get(top, 0), _says(snapshot, top), fingerprint=snapshot.fingerprint(top),
                          alone=asked_alone(snapshot, worst),
                          evidence=evidence(snapshot, top),
                          members=tuple((card.address, card.text, card.fingerprint) for card in members)))
    return alone
