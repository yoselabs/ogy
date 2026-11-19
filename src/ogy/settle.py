"""Decisions settle entries: which entries and fields, the option in force, and the fixed checks D2, D4 to D6 and D10.

Pure functions over a snapshot. The names read (option, answer, guess, sets, chose, value, said, at, where, note, delegated,
heard) come from the settling kind's `Settling`; the key its answers are kept under is the answer kind's `key`.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from ogy.kinds import Settling
from ogy.model import Address, Entry, Finding, Problem, parse_address
from ogy.snapshot import Snapshot
from ogy.source import Source

type Sets = Mapping[str, object]  # {address text: {field: value} | None}


@dataclass(frozen=True)
class Answer:
    """One answer: ogy keeps no message and no quote, only the paraphrase `said`, who (computed), when and where."""

    chose: str
    said: str
    who: str  # human, or ai under `delegated`
    at: datetime | None
    where: str = ""
    note: str | None = None  # the person's hedge or condition; outside the fingerprint
    delegated: Address | None = None  # an agent's answer: the decision whose human answer let the agent decide


@dataclass(frozen=True)
class Force:
    """What is in force: its `sets`, whether an answer or the guess put it there, and the option chosen (None for a value guess)."""

    sets: Sets
    by_answer: bool
    option: str | None
    note: str | None = None  # the newest answer's hedge or condition
    delegated: bool = False  # the newest answer was an agent's, under a person's delegation


@dataclass
class Decision:
    address: Address
    entry: Entry
    names: Settling
    options: dict[str, Sets] = field(default_factory=dict)
    answers: list[Answer] = field(default_factory=list)
    guess: Entry | None = None

    @property
    def heard(self) -> str | None:
        """What the owner said that the guess rests on, paraphrased: the guess's `heard` field."""
        value = self.guess.fields.get(self.names.heard) if self.guess else None
        return value if isinstance(value, str) and value.strip() else None

    @property
    def in_force(self) -> Force | None:
        """The answer with the newest `at`; with no answer, the guess."""
        dated = [(answer.at, answer) for answer in self.answers if answer.at is not None]
        if dated and (newest := max(dated, key=lambda item: item[0])[1]) and newest.chose in self.options:
            return Force(self.options[newest.chose], True, newest.chose, newest.note, newest.who != "human")
        if self.guess is None:
            return None
        chose, value = self.guess.fields.get(self.names.chose), self.guess.fields.get(self.names.value)
        if isinstance(chose, str):
            return Force(self.options.get(chose, {}), False, chose)
        return Force(value, False, None) if isinstance(value, dict) else None

    def sets_all(self) -> list[Sets]:
        """Every `sets` of the decision: its options' and the guess's."""
        value = self.guess.fields.get(self.names.value) if self.guess else None
        return [*self.options.values(), *([value] if isinstance(value, dict) else [])]


def resolve(snapshot: Snapshot, origin: Address, text: object, kind: str) -> Address | None:
    """A full address, or a local key of a part of `origin`, when it names an entry."""
    if not isinstance(text, str):
        return None
    found = parse_address(text, snapshot.ontology) if "/" in text else origin.part(kind, text)
    return found if found in snapshot.entries else None


def moment(value: object) -> datetime | None:
    """A time as YAML reads it, or as ISO text."""
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def settling_of(snapshot: Snapshot) -> Settling | None:
    kind = snapshot.ontology.settling_kind()
    return kind.settling if kind else None


def answers_key(snapshot: Snapshot) -> str:
    """The key the settling kind keeps its answers under: the answer kind's."""
    kind = snapshot.ontology.settling_kind()
    answer = snapshot.ontology.get(kind.settling.answer) if kind and kind.settling else None
    return answer.key or "" if answer else ""


def decisions(snapshot: Snapshot) -> list[Decision]:
    kind = snapshot.ontology.settling_kind()
    if kind is None or kind.settling is None:
        return []
    names, key = kind.settling, answers_key(snapshot)
    found: list[Decision] = []
    for address, entry in sorted(snapshot.entries.items()):
        if address.kind != kind.kind:
            continue
        decision = Decision(address, entry, names, guess=snapshot.entries.get(address.part(names.guess)))
        for part in snapshot.links.parts(address, names.option):
            sets = snapshot.entries[part].fields.get(names.sets)
            decision.options[part.key] = sets if isinstance(sets, dict) else {}
        items = entry.fields.get(key) or []
        decision.answers += [_answer(snapshot, address, names, item) for item in items if isinstance(item, dict)]
        found.append(decision)
    return found


def _text(item: Mapping[str, object], name: str) -> str | None:
    value = item.get(name)
    return value if isinstance(value, str) else None


def _answer(snapshot: Snapshot, decision: Address, names: Settling, item: Mapping[str, object]) -> Answer:
    who = "ai" if item.get(names.delegated) is not None else "human"  # computed: an answer with `delegated` is an agent's
    return Answer(str(item.get(names.chose)), _text(item, names.said) or "", who, moment(item.get(names.at)),
                  _text(item, names.where) or "", _text(item, names.note),
                  resolve(snapshot, decision, item.get(names.delegated), decision.kind))


def settles(decision: Decision) -> tuple[dict[str, set[str]], set[str]]:
    """The fields each address of the decision is given under some option or the guess, and the addresses some option sets absent."""
    fields: dict[str, set[str]] = {}
    absent: set[str] = set()
    for sets in decision.sets_all():
        for address, given in sets.items():
            fields.setdefault(address, set())
            if isinstance(given, dict):
                fields[address] |= set(given)
            else:
                absent.add(address)
    return fields, absent


def slot_index(found: list[Decision]) -> dict[tuple[str, str | None], list[Address]]:
    """(address, field) -> the decisions that set it; (address, None) is an address a decision may set absent."""
    index: dict[tuple[str, str | None], list[Address]] = {}
    for decision in found:
        fields, absent = settles(decision)
        for address, names in fields.items():
            for name in names:
                index.setdefault((address, name), []).append(decision.address)
        for address in absent:
            index.setdefault((address, None), []).append(decision.address)
    return index


def decision_of(found: list[Decision], address: Address) -> Decision | None:
    """The decision that settles an entry (the first, in address order, when a broken base has two)."""
    return next((decision for decision in found if str(address) in settles(decision)[0]), None)


def _finding(decision: Decision, problem: Problem, detail: str) -> Finding:
    return Finding(problem, decision.entry.path, detail, decision.address)


def _uneven(decision: Decision) -> list[Finding]:
    """D2: every option names the same addresses and, where two give fields, the same fields."""
    named = [set(sets) for sets in decision.options.values()]
    uneven = sorted(set.union(*named) - set.intersection(*named)) if named else []
    found = [_finding(decision, Problem.UNEVEN_OPTIONS, f"options name {uneven} unevenly")] if uneven else []
    for address in sorted(set.union(*named) if named else set()):
        given = [set(sets[address]) for sets in decision.options.values() if isinstance(sets.get(address), dict)]
        if any(item != given[0] for item in given):
            found.append(_finding(decision, Problem.UNEVEN_OPTIONS, f"{address}: options give different fields"))
    return found


def _two_homes(found: list[Decision]) -> list[Finding]:
    """D4: no slot is set by two decisions; no address is null in one decision and named by another."""
    by_address: dict[str, dict[Address, set[str | None]]] = {}
    for decision in found:
        fields, absent = settles(decision)
        for address in fields:
            by_address.setdefault(address, {})[decision.address] = set(fields[address]) | ({None} if address in absent else set())
    problems: list[Finding] = []
    for address, owners in sorted(by_address.items()):
        for number, (one, names) in enumerate(owners.items()):
            for other, more in list(owners.items())[number + 1:]:
                if (names & more) or None in names or None in more:
                    problems.append(_finding(next(item for item in found if item.address == other), Problem.TWO_HOMES,
                                             f"{address} is also settled by {one}"))
    return problems


def _times(decision: Decision) -> list[Finding]:
    """D5: two answers with equal `at`."""
    stamps = [answer.at for answer in decision.answers if answer.at is not None]
    return [_finding(decision, Problem.EQUAL_AT, "two answers have the same time")] if len(stamps) != len(set(stamps)) else []


def _in_force(snapshot: Snapshot, decision: Decision) -> list[Finding]:
    """D6: the settled entries equal the sets of the option in force."""
    force = decision.in_force
    problems: list[Finding] = []
    for text, given in sorted((force.sets if force else {}).items()):
        address = parse_address(text, snapshot.ontology)
        entry = snapshot.entries.get(address) if address else None
        if given is None and entry is not None:
            problems.append(_finding(decision, Problem.NOT_IN_FORCE, f"{text} exists but the option in force says no"))
        elif isinstance(given, dict) and entry is None:
            problems.append(_finding(decision, Problem.NOT_IN_FORCE, f"{text} is absent but the option in force gives it fields"))
        elif isinstance(given, dict) and entry is not None:
            problems += [_finding(decision, Problem.NOT_IN_FORCE, f"{text}.{name} is {entry.fields.get(name)!r}, in force: {value!r}")
                         for name, value in given.items() if entry.fields.get(name) != value]
    return problems


def _delegation(found: list[Decision], decision: Decision, answer: Answer) -> list[Finding]:
    """D10: an agent's answer (one with `delegated`) names a decision whose answer in force is a person's."""
    if answer.who == "human":
        problems: list[str] = []
    else:
        given = next((d for d in found if d.address == answer.delegated), None)
        newest = max((a for a in given.answers if a.at is not None), key=lambda a: a.at, default=None) if given else None
        problems = [] if newest is not None and newest.who == "human" else [
            "an agent's answer names in delegated the decision whose answer in force is the person's that let it decide"]
    return [_finding(decision, Problem.BAD_DELEGATION, detail) for detail in problems]


def check_decisions(snapshot: Snapshot, _source: Source) -> list[Finding]:
    """D2, D4 to D6, D10 as a check: `(Snapshot, Source) -> list[Finding]`. Not registered in `CHECKS` here."""
    found = decisions(snapshot)
    problems = _two_homes(found)
    for decision in found:
        problems += [*_uneven(decision), *_times(decision), *_in_force(snapshot, decision),
                     *(item for answer in decision.answers for item in _delegation(found, decision, answer))]
        if not decision.answers and decision.guess is None:
            problems.append(_finding(decision, Problem.NO_GUESS, "a decision with no answer needs a guess"))
    return problems
