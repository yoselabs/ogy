"""`ogy reply`: the owner's reply to a `ogy review` round (named by id, else the newest of the knowledge base), read with the
grammar printed under the cards. ogy keeps no message and no quote: the text is the grammar line (the owner's, or the agent's
reading of the owner's natural words), and `--said` is one short line, the agent's paraphrase of what the owner said, kept
with `at` and `where` on each answer and each agreement it writes (`from: human`: only a person replies to a round). When no
item applies, nothing is written.

    yes all | decide  accept every recommendation of the round: each question gets its recommended option (the guess), each card is
                      agreed to, except a structural decision (harm `structure`), which needs its own letter (`Q1 a`);
                      a card that changed since shown stays in the queue and is reported. Allowed in an --all round
    yes | yes 1 3     agree to the sentences as shown (all of them, or those cards); a bare yes is refused for a round shown with --all.
                      It also confirms every question that says "You said (paraphrased): .... Read as B.": the answer is what
                      the owner said earlier, read as that option, except a structural decision. `yes Q2` confirms one
    2: <sentence>     the owner's own sentence replaces card 2's and is agreed
    no 4              card 4 becomes a question (why, paraphrased, goes in --said); nothing is built new on it until it is answered
    Q1 b              the owner chose option B of question 1 (or its key)
    Q1: <words>       the owner answers a question that has no options; nothing is written: an agent adds an option that says it
                      and answers with it
    later             nothing changes

Items are separated by lines, `;`, or a comma before another item. A card whose entry changed since it was shown is
refused and stays in the queue; the other items still apply."""

import re
from dataclasses import dataclass
from string import ascii_uppercase
from typing import TYPE_CHECKING

from ogy import rounds
from ogy.edit import Editor
from ogy.kinds import NAME
from ogy.model import Address
from ogy.settle import Decision, decisions
from ogy.status import delegated
from ogy.verdict import NotFoundError
from ogy.writes import Clock, Said, WriteRefusedError, agree, answer, commit, current, files, said, stamp, utc_now
lazy from ogy.snapshot import Snapshot
lazy from ogy.target import Target

if TYPE_CHECKING:
    from ogy.rounds import Round, Shown

SPLIT = re.compile(r"\s*(?:\n|;|,(?=\s*(?:(?:yes|no|later|Q\d+)\b|\d+\s*:)))\s*", re.IGNORECASE)
YES = re.compile(r"(?:yes(?:\s+(all|Q?\d+(?:[\s,]+Q?\d+)*))?|(decide))", re.IGNORECASE)
CHANGE = re.compile(r"(\d+)\s*:\s*(.+)", re.DOTALL)
NO = re.compile(r"no\s+(\d+)", re.IGNORECASE)
CHOOSE = re.compile(r"Q(\d+)\s+(\S+)", re.IGNORECASE)
FILL = re.compile(r"Q(\d+)\s*:\s*(.+)", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class Replied:
    applied: list[str]
    refused: list[str]
    changed: bool  # some item wrote something


def _stale(target: Target, card: Shown) -> str | None:
    snapshot = Editor(target.repo, target.kb, target.kinds()).snapshot()
    address = snapshot.resolve(card.address)
    if address is None or snapshot.fingerprint(address) != card.fingerprint:
        return f"{card.address} changed since it was shown; it stays in the queue"
    return None


def _fresh(target: Target, card: Shown) -> None:
    if (why := _stale(target, card)) is not None:
        raise WriteRefusedError([why])


def _card(found: Round, label: str, *, entry: bool) -> Shown:
    card = next((item for item in found.cards if item.label.upper() == label.upper()), None)
    if card is None or (card.kind in rounds.ENTRY_CARDS) is not entry:
        raise WriteRefusedError([f"no {'card' if entry else 'question'} {label} in round {found.id}"])
    return card


def _one(found: Round, label: str) -> Shown:
    """The card `2: <sentence>` or `no 2` acts on: one entry, never a parent's card of several."""
    card = _card(found, label, entry=True)
    if len(card.members) > 1:
        raise WriteRefusedError([f"card {label} lists {len(card.members)} entries: say which and in what words; the agent changes it"])
    if card.members:
        address, fingerprint = card.members[0]
        return card.model_copy(update={"address": address, "fingerprint": fingerprint})
    return card


def _sentence_field(target: Target, address: str) -> str:
    snapshot = Editor(target.repo, target.kb, target.kinds()).snapshot()
    found = snapshot.resolve(address)
    kind = snapshot.kind_of(found) if found else None
    if kind is None or kind.sentence is None or not snapshot.ontology.carded(kind):
        raise WriteRefusedError([f"{address} has no sentence to replace"])
    return kind.sentence


def _change(target: Target, words: Said, card: Shown, sentence: str) -> None:
    field = _sentence_field(target, card.address)

    def act(ed: Editor) -> None:
        address = ed.snapshot().resolve(card.address)
        if address is None:
            raise WriteRefusedError([f"{card.address} is no longer an entry"])
        ed.update(address, {field: sentence.strip()})
        stamp(ed, words, current(ed.snapshot(), [address]))

    commit(target, lambda snap: [a for a in [snap.resolve(card.address)] if a], act)


def _unique(target: Target, kind: str, layer: str, area: str, stem: str) -> Address:
    taken = Editor(target.repo, target.kb, target.kinds()).snapshot().entries
    number = 1
    while (address := Address(layer, area, ((kind, stem if number == 1 else f"{stem}-{number}"),))) in taken:
        number += 1
    return address


def _question(snapshot: Snapshot, words: Said, card: Shown, field: str) -> tuple[str, dict[str, object]]:
    """A question whether the card's sentence still holds, in the settling kind's names: keep it (the guess) or drop it."""
    ontology = snapshot.ontology
    kind = ontology.settling_kind()
    names = kind.settling if kind else None
    option, guess = (ontology.get(names.option), ontology.get(names.guess)) if names else (None, None)
    if kind is None or names is None or option is None or guess is None or not (kind.sentence and option.sentence):
        raise WriteRefusedError(["the ontology has no settling kind with a question and options: nothing can ask"])

    def choice(label: str, sets: object) -> dict[str, object]:
        return {option.sentence or "": label, names.sets: {card.address: sets}}

    return kind.kind, {
        kind.sentence: f"Is this still right: {card.shown}",
        names.context: f"The owner said no on {words.at[:10]} ({words.where}): {words.said}. Built as it is until answered.",
        option.key or "": {"keep": choice("Keep it as it is", {field: card.shown}), "drop": choice("Drop it", None)},
        guess.key or "": {names.chose: "keep", names.why: "Built as it is until the owner answers."},
    }


def _reconsider(target: Target, words: Said, card: Shown) -> Address:
    snapshot = Editor(target.repo, target.kb, target.kinds()).snapshot()
    subject = snapshot.resolve(card.address)
    if subject is None:
        raise WriteRefusedError([f"{card.address} is no longer an entry"])
    field = _sentence_field(target, card.address)
    layer = subject.layer or snapshot.ontology.layers[0]  # a term has no layer: its question is the owner's, in the first layer
    key = re.sub(r"[^a-z0-9]+", "-", (subject.key or subject.kind).lower()).strip("-")
    kind, fields = _question(snapshot, words, card, field)
    address = _unique(target, kind, layer, subject.area, f"reconsider-{key if NAME.match(key) else subject.kind}")
    commit(target, lambda _: [address, subject], lambda ed: ed.put(address, fields))
    return address


def _option(card: Shown, token: str) -> str:
    if len(token) == 1 and token.upper() in ascii_uppercase[: len(card.options)]:
        return card.options[ascii_uppercase.index(token.upper())]
    return token


def _heard(target: Target, card: Shown) -> tuple[str, str] | None:
    """(option guessed, what the owner was heard to say) of a question whose guess rests on the owner's words, else None."""
    snapshot = Editor(target.repo, target.kb, target.kinds()).snapshot()
    found = next((d for d in decisions(snapshot) if str(d.address) == card.address and not d.answers), None)
    chose = found.guess.fields.get(found.names.chose) if found and found.guess else None
    heard = found.heard if found else None
    return (chose, heard) if isinstance(chose, str) and isinstance(heard, str) else None


def _confirm(target: Target, found: Round, label: str, words: Said) -> str:
    """One yes to a "You said ... Read as B" card: the answer is B, by what the owner said earlier."""
    card = _card(found, label, entry=False)
    _fresh(target, card)
    heard = _heard(target, card)
    if heard is None:
        raise WriteRefusedError([f"{card.label} rests on nothing you said: choose an option ({card.label} b)"])
    answer(target, card.address, heard[0], Said(heard[1], words.where, words.at, words.who, words.note))
    return f"{card.address} answered: {heard[0]}"


def _yes(target: Target, found: Round, words: Said, group: str | None) -> str:
    if not group and found.everything:
        raise WriteRefusedError([f"round {found.id} was shown with --all: name the cards (yes 1 3), or reply to a round of 7"])
    labels = re.findall(r"Q?\d+", group, re.IGNORECASE) if group else [c.label for c in found.cards]
    wanted = [label for label in labels if label.upper().startswith("Q")]
    if not group:  # a bare yes confirms a "You said" reading, never a structural decision
        wanted = [
            label for label in wanted if not _card(found, label, entry=False).structure and _heard(target, _card(found, label, entry=False))
        ]
    cards = [_card(found, label, entry=True) for label in labels if not label.upper().startswith("Q")]
    if not group:
        cards = [card for card in cards if card.kind in rounds.ENTRY_CARDS]
    for card in cards:
        _fresh(target, card)
    confirmed = [_confirm(target, found, label, words) for label in wanted]
    if not cards and confirmed:
        return "; ".join(confirmed)
    return "; ".join([*confirmed, f"agreed to {_agree(target, words, cards)} sentence(s)"])


def _agree(target: Target, words: Said, cards: list[Shown]) -> int:
    """Agree to every card's entry, or to every entry a parent's card lists, at the fingerprint shown; returns how many."""
    hashes = {address: fingerprint for card in cards for address, fingerprint in (card.members or ((card.address, card.fingerprint),))}
    agree(target, words, list(hashes), hashes)
    return len(hashes)


def _recommended(decision: Decision | None) -> object:
    """What `yes all` answers: the guess of a question, the option in force of a decision an agent answered under delegation."""
    if decision is None:
        return None
    if decision.answers:
        return decision.in_force.option if delegated(decision) and decision.in_force else None
    return decision.guess.fields.get(decision.names.chose) if decision.guess else None


def _accept_all(target: Target, found: Round, words: Said) -> str:
    """`yes all` / `decide`: the recommended option of every question and agreement to every card, with the one paraphrase."""
    done: list[str] = []
    kept: list[str] = []
    fresh = []
    for card in found.cards:
        if (why := _stale(target, card)) is not None:
            kept.append(why)
        elif card.kind in rounds.ENTRY_CARDS:
            fresh.append(card)
        elif card.structure:
            kept.append(f"{card.address} is structural: it needs its own letter ({card.label} a), not yes all")
        else:
            snapshot = Editor(target.repo, target.kb, target.kinds()).snapshot()
            found_decision = next((d for d in decisions(snapshot) if str(d.address) == card.address), None)
            chose = _recommended(found_decision)
            if not isinstance(chose, str) or chose not in card.options:
                kept.append(f"{card.address} has no recommended option: choose one ({card.label} a)")
                continue
            answer(target, card.address, chose, words)
            done.append(f"{card.address} answered: {chose}")
    if fresh:
        done.append(f"agreed to {_agree(target, words, fresh)} sentence(s)")
    if not done:
        raise WriteRefusedError(kept or [f"round {found.id} has nothing to accept"])
    return "; ".join([*done, *(f"not done: {why}" for why in kept)])


def _fill(target: Target, found: Round, number: str) -> str:
    """`Q1: <words>`: the owner answered a question that has no option; nothing is written, an agent writes the option."""
    card = _card(found, f"Q{number}", entry=False)
    if card.options:
        raise WriteRefusedError([f"{card.address} has options: choose one (Q{number} a)"])
    _fresh(target, card)
    return f"{card.address} has no option yet: add one that says it (`put`), then `answer` it with a paraphrase"


def _apply(target: Target, found: Round, words: Said, item: str) -> str:
    """Do one item; the line says what happened. Raises WriteRefusedError."""
    if item.lower() == "later":
        return "later: nothing changes"
    if match := YES.fullmatch(item):
        everything = match.group(2) or (match.group(1) or "").lower() == "all"
        return _accept_all(target, found, words) if everything else _yes(target, found, words, match.group(1))
    if match := CHANGE.fullmatch(item):
        card = _one(found, match.group(1))
        _fresh(target, card)
        _change(target, words, card, match.group(2))
        return f"{card.address} now says what you wrote, and is agreed"
    if match := NO.fullmatch(item):
        card = _one(found, match.group(1))
        _fresh(target, card)
        return f"{card.address} is now a question: {_reconsider(target, words, card)}"
    if match := CHOOSE.fullmatch(item):
        card = _card(found, f"Q{match.group(1)}", entry=False)
        _fresh(target, card)
        done = answer(target, card.address, _option(card, match.group(2)), words)
        return f"{done.decision} answered: {done.option}"
    if match := FILL.fullmatch(item):
        return _fill(target, found, match.group(1))
    raise WriteRefusedError([f"{item!r} is none of: yes, yes all, yes 1 3, 2: <sentence>, no 4, Q1 b, Q1: <words>, later"])


def _round(target: Target, round_id: str | None) -> Round:
    found = rounds.load(target.repo, round_id)
    if found is None:
        raise NotFoundError(f"no round {round_id}" if round_id else "no review round: run `ogy review` first")
    return found


def reply(
    target: Target,
    text: str,
    paraphrase: str,
    where: str,
    *,
    at: str | None = None,
    round_id: str | None = None,
    now: Clock = utc_now,
    note: str | None = None,
) -> Replied:
    """Apply every item of `text` (a grammar line) to the round, each on its own; the lock is held. Each answer and agreement
    keeps `paraphrase`, `at`, `where` and `from: human`."""
    found = _round(target, round_id)
    items = [item for item in SPLIT.split(text.strip()) if item]
    if not items:
        raise WriteRefusedError(["the reply is empty"])
    words = said(paraphrase, where, at, now, who="human", note=note)
    before = files(target)
    applied: list[str] = []
    refused: list[str] = []
    handled: set[str] = set()
    for item in items:
        try:
            applied.append(f"{item}: {_apply(target, _rest(found, item, handled), words, item)}")
        except WriteRefusedError as error:
            refused.append(f"{item}: {'; '.join(error.reasons)}")
        handled |= _labels(item)
    return Replied(applied, refused, files(target) != before)


def _labels(item: str) -> set[str]:
    """The card a `2: <sentence>`, `no 4`, `Q1 b` or `Q1: <words>` item answers."""
    if match := CHANGE.fullmatch(item) or NO.fullmatch(item):
        return {match.group(1)}
    if match := CHOOSE.fullmatch(item) or FILL.fullmatch(item):
        return {f"Q{match.group(1)}"}
    return set()


def _rest(found: Round, item: str, handled: set[str]) -> Round:
    """For a bare `yes` or `yes all`: the round without the cards an earlier item of the same reply already answered, so
    `2: <sentence>, yes` agrees to the others instead of refusing card 2 as changed."""
    match = YES.fullmatch(item)
    if not handled or match is None or (match.group(1) and match.group(1).lower() != "all"):
        return found
    return found.model_copy(update={"cards": tuple(card for card in found.cards if card.label.upper() not in handled)})
