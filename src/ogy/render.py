"""Results as lines of text for people and agents. Printing only: no result is computed here."""

import json
import string

from ogy import rounds
from ogy.find import Found
from ogy.graph import Context, Impact
from ogy.history import History
from ogy.model import Finding
from ogy.overview import Overview
from ogy.receipts import Work
from ogy.review import Dropped, Review
from ogy.semdiff import SemanticDiff
from ogy.show import Shown
from ogy.status import Card, Status
from ogy.workcause import Group


def plain(value: object) -> str:
    """A field value as text: words as they are, anything else as compact JSON (no Python reprs)."""
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)


def _context(found: Context) -> list[str]:
    entry = found.entry
    lines = [f"{entry.address}  ({entry.path}, fingerprint {found.fingerprint})"]
    lines += [f"  {name}: {plain(value)}" for name, value in entry.fields.items()]
    lines += [f"parent: {address}" for address in found.parents]
    lines += [f"part: {address}" for address in found.parts]
    lines += [f"links {edge.field} -> {edge.address}" for edge in found.links]
    lines += [f"referenced by {edge.address} ({edge.field})" for edge in found.referenced_by]
    return lines


def render_anchors(found: list[tuple[str, str, int]]) -> list[str]:
    """`doc:<commit>:<file>#<anchor>` names these; a heading nested deeper is indented."""
    return [f"{anchor}   {'  ' * (level - 1)}{'#' * level} {heading}" for anchor, heading, level in found] or ["no headings"]


def render_impact(found: Impact) -> list[str]:
    lines = [f"impact of {found.address}"]
    lines += [f"reaches {address}" for address in sorted(found.reaches)]
    lines += [f"reached by {address}" for address in sorted(found.reached_by)]
    return lines


def render_work(found: list[Work], groups: list[Group] | None = None) -> list[str]:
    """One line per piece of work; with `groups`, each group under a line naming its cause (`workcause`)."""
    if groups is None:
        return [_work_line(item) for item in found] or ["no work left"]
    lines = [line for decision, realized, items in groups for line in (
        f"by {decision or 'no decision'}, for {realized or 'nothing realized'} ({len(items)}):", *map(_work_line, items))]
    return lines or ["no work left"]


def _work_line(item: Work) -> str:
    line = f"{item.status}: {item.address} (now {item.build_hash or '-'}, built {item.built or '-'})"
    return line + (f" {item.note}" if item.note else "")


def render_diff(found: SemanticDiff) -> list[str]:
    if found.same_tree:
        return ["same tree: nothing changed"]
    lines: list[str] = []
    for change in found.changes:
        lines.append(f"{change.change} {change.address}")
        lines += [f"  {item.name}: {plain(item.old)} -> {plain(item.new)}" for item in change.fields]
    return lines or ["no entry changed"]


def render_findings(found: list[Finding]) -> list[str]:
    return [str(item) for item in found] or ["ok"]


def waiting_line(count: int) -> list[str]:
    return [f"waiting for you: {count} (ogy review)"] if count else []


def _status(found: Shown) -> str:
    text = str(found.status)
    if found.agreed is not None and found.status in (Status.BY_YOU, Status.CHANGED, Status.ANSWERED):
        text += f", {found.agreed.at:%Y-%m-%d}, {found.agreed.where}"
    return text if found.status is not Status.NOBODY else f"{text}: {found.label}"


def _said(found: Shown) -> list[str]:
    """`You said (paraphrased): ...`: what the person said when they agreed or answered, as the AI put it."""
    said = found.agreed
    return [f"You said (paraphrased): {said.said}"] if said is not None and said.said else []


def _built(found: Shown) -> str:
    if found.built is None:
        return f"built ({found.built_file}): no line"
    state = "= now" if found.built.own == found.build_hash else f"!= now {found.build_hash}"
    left = ", ".join(f"{item.status} {item.note}".strip() for item in found.work) or "none"
    return f"built ({found.built_file}): own {found.built.own} {state}; covers {', '.join(found.built.covers) or '-'}; work left: {left}"


def render_show(found: Shown) -> list[str]:
    if found.context is None:
        decided = found.decided_in
        return [f"{found.address}: does not exist: decided no in {decided.decision} (by {decided.by})" if decided else str(found.address)]
    lines = _context(found.context)
    lines.append(f"status (computed): {_status(found)}")
    lines += _said(found)
    if found.decided_in is not None:
        decided = found.decided_in
        note = f"; note: {decided.note}" if decided.note else ""
        lines.append(f"Decided in (computed): {decided.decision} (in force: {decided.option or 'its guess value'}, by {decided.by}){note}")
    if found.came_from:
        lines.append(f"Came from (computed): {', '.join(found.came_from)}" + (", through the decision" if found.through_decision else ""))
    if found.settles:
        lines.append(f"Settles (computed): {', '.join(found.settles)}")
    return [*lines, _built(found)] if found.work or found.built else lines


def _card(label: str, card: Card) -> list[str]:
    harm = str(card.harm).replace("-", " ") if card.harm else ""
    notes = [text for text in (harm, f"{card.dependants} depend on it" if card.dependants else "") if text]
    lines = [f"{label}. {card.kind}  {card.address}" + (f"  ({'; '.join(notes)})" if notes else "")]
    if card.context:
        lines.append(f"   Why it comes up: {card.context}")
    lines.append(f"   {card.word}: {card.text}" if card.word else f"   {card.text}")
    if card.avoid:
        lines.append(f"   not: {'; '.join(card.avoid)}")
    if card.members:
        lines.append(f"   one yes agrees to {len(card.members)}:")
        lines += [f"   - {str(address).removeprefix(str(card.address) + '/') if address != card.address else 'itself'}: {text}"
                  for address, text, _ in card.members]
    for index, (letter, (key, text)) in enumerate(zip(string.ascii_uppercase, card.options, strict=False)):
        mark = "  (in force, an agent's answer under your delegation)" if card.kind == "delegated" else "  (recommended)"
        lines.append(f"   {letter}. {text}" + (mark if key == card.guess else ""))
        lines += [f"      then {line}" for line in (card.then[index] if index < len(card.then) else ())]
    if card.earlier:
        lines.append(f"   {card.earlier}")
    if card.alone:
        lines.append(f"   Structural: answer with its own letter ({label} {string.ascii_lowercase[0]}); yes and yes all leave it.")
    if card.kind == "question" and not card.options:
        lines.append(f"   Answer in words: {label}: <your words>")
    keys = [key for key, _ in card.options]
    if card.heard and card.guess in keys:
        lines.append(f"   You said (paraphrased): {card.heard}. Read as {string.ascii_uppercase[keys.index(card.guess)]}.")
    return lines + ([f"   {card.evidence}"] if card.evidence else [])


REPLY = "Reply: yes | yes all | yes 1 Q2 | 2: <new sentence> | no 4 | Q1 b | Q1: <your words> | later  (ogy reply)"


def _from(found: Review) -> list[str]:
    where = f" --from {found.source}" + (f" {found.area}" if found.area else "")
    if found.page == 0:
        return [f"nothing from {found.source} is waiting for you"]
    more = f"; next: ogy review{where} (the pages you agree to leave the list)" if found.pages > 1 else ""
    return [f"page {found.page} of {found.pages}: {found.title}{more}"]


def bare_yes(cards: list[tuple[str, Card]]) -> list[str]:
    """What a bare `yes` will change, and what it leaves for a letter of its own: the same rule as `reply`."""
    keys = {label: [key for key, _ in card.options] for label, card in cards}
    confirms = [f"{label} as {string.ascii_uppercase[keys[label].index(card.guess)]}" for label, card in cards
                if card.kind not in rounds.ENTRY_CARDS and not card.alone and card.heard and card.guess in keys[label]]
    agrees = [label for label, card in cards if card.kind in rounds.ENTRY_CARDS]
    will = [*([f"confirm {', '.join(confirms)}"] if confirms else []),
            *([f"agree to {len(agrees)} sentence(s) ({', '.join(agrees)})"] if agrees else [])]
    lines = [f"A bare `yes` will: {'; '.join(will)}." if will else "A bare `yes` changes nothing."]
    own = [label for label, card in cards if card.alone]
    return lines + ([f"Structural, not covered by yes or yes all: {', '.join(own)}; each needs its own letter."] if own else [])


def render_review(found: Review) -> list[str]:
    lines = [f"round {found.round_id}"] if found.round_id else []
    lines += [str(header) for header in found.headers]
    lines += _from(found) if found.source else []
    for label, card in rounds.labelled(found.cards):
        lines += ["", *_card(label, card)]
    if found.waiting:
        lines += ["", f"{found.waiting} more waiting: ogy review {found.area + ' ' if found.area else ''}--all"]
    if found.cards:
        lines += ["", *bare_yes(rounds.labelled(found.cards)), REPLY,
                  "yes agrees to the sentences and confirms every 'You said' reading; yes Q2 confirms one;",
                  "yes all (or decide) takes every recommendation"]
    return lines or ["nothing to ask"]


def render_review_md(found: Review) -> list[str]:
    """The review as Markdown for a ticket: the owner replies there and an agent runs `ogy reply --round <id>`."""
    lines = ["## ogy review" + (f", round `{found.round_id}`" if found.round_id else ""), ""]
    lines += [f"- {header}" for header in found.headers]
    lines += ["", *(f"**{line}**" for line in _from(found))] if found.source else []
    for label, card in rounds.labelled(found.cards):
        first, *rest = _card(label, card)
        lines += ["", f"### {first}", *(f"{line.strip()}  " for line in rest)]
    if found.waiting:
        lines += ["", f"{found.waiting} more waiting."]
    if found.cards:
        lines += ["", *bare_yes(rounds.labelled(found.cards)), f"{REPLY}", f"Round: `{found.round_id}`"]
    return lines if found.cards or found.source else ["nothing to ask"]


def render_dropped(found: Dropped) -> list[str]:
    lines = [f"guess says no, nobody has seen it: {address}" for address in found.guessed_no]
    lines += [f"removed with no why: {item}" for item in found.unexplained]
    lines += [f"removed with plain words, not a decision: {item}" for item in found.plain_why]
    lines += [f"answer with a note (the owner's hedge or condition): {address}" for address in found.noted]
    lines += [f"answer an agent gave under a delegation (the owner may veto): {address}" for address in found.delegated]
    return lines or ["nothing dropped"]


def render_found(found: list[Found]) -> list[str]:
    return [f"{item.address}   {item.kind}   {item.state or '-'}   {item.says}" + (f"   {item.note}" if item.note else "")
            for item in found] or ["nothing found"]


def render_status(found: Overview) -> list[str]:
    none = "every kind has entries"
    coverage = [] if found.coverage is None else [
        "coverage (kinds with no entry):", *(f"  {layer}: {', '.join(kinds) or none}" for layer, kinds in found.coverage.items())]
    return [*(str(header) for header in found.areas), *waiting_line(found.waiting),
            f"findings: {found.findings} (ogy check)", f"work left: {found.work} (ogy work)", f"dropped: {found.dropped} (ogy dropped)",
            *coverage]


def render_history(found: History) -> list[str]:
    lines = [f"{row.when:%Y-%m-%d}  {row.who}  {row.what}   {row.where}" for row in found.rows]
    return [*lines, *found.notes, *([found.in_force] if found.in_force else [])] or ["no history"]
