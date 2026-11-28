"""A sketch: entries in the `put` format, applied to a throwaway copy of the knowledge base and never to the real one.

The copy is read as it would stand after the `put`: the new entries (and their parts and links) are what the board draws, and what
the sketch would touch comes from the same graph operations as `ogy impact`. Nothing here writes into the repository.

Built here: decision product/inspection/decision/show-what-does-not-exist-yet.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ogy import put
from ogy.edit import Editor
from ogy.graph import Edge, closure, incoming, links_of
from ogy.inspect import inspect
from ogy.verdict import RefusalError
from ogy.writes import WriteRefusedError, reading

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ogy.model import Address
    from ogy.snapshot import Snapshot
    from ogy.target import Target

Json = dict[str, Any]
RECORD_LIMIT = 40
TOUCH_LIMIT = 40


def _plain(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _kept(decision: str | None, option: str | None, known: Mapping[str, Json]) -> None:
    """The decision (and its option) Keep may open the answer form for: both exist, or neither is named. Keep writes nothing
    itself: the owner's answer is recorded by the same route as any answer, and an option's `sets` cannot carry a workflow's steps."""
    if decision is None and option is None:
        return
    if decision is None or option is None:
        raise RefusalError(["name both `decision` and `option` to offer Keep, or neither"])
    found = known.get(decision)
    if found is None or found["kind"] != "decision":
        raise RefusalError([f"no such decision: {decision}"])
    if f"{decision}/option/{option}" not in known:
        raise RefusalError([f"{decision} has no option {option}"])


def _after(target: Target, records: Sequence[Mapping[Any, Any]]) -> tuple[Snapshot, Snapshot, list[tuple[Address, bool]]]:
    """(before, after, the records' addresses with whether each is new): the `put` applied to a copy that is thrown away."""
    base = target.repo / target.kb
    with tempfile.TemporaryDirectory(prefix="ogy-sketch-") as folder, reading(target):
        copy = Path(folder)
        shutil.copytree(base, copy / target.kb, ignore=shutil.ignore_patterns(".*"))
        editor = Editor(copy, target.kb, target.kinds())
        before = editor.snapshot()
        ordered = sorted(put.checked(target, before, list(records)), key=lambda item: len(item[0].path))
        try:
            for address, fields, new in ordered:
                editor.put(address, fields) if new else editor.update(address, fields)
        except KeyError as error:
            raise WriteRefusedError([f"cannot place {error.args[0]}: its parent is not there"]) from error
        return before, editor.snapshot(), [(address, new) for address, _, new in ordered]


def _touching(after: Snapshot, drawn: set[Address], changed: Mapping[Address, list[str]], says: Mapping[str, Json]) -> list[Json]:
    """The existing entries the sketch changes, links to, reaches or is reached by, nearest first, at most `TOUCH_LIMIT`."""
    back = incoming(after)
    rows: dict[str, Json] = {}

    def add(address: Address, how: str, via: list[str] | None = None) -> None:
        key = str(address)
        if address in drawn:
            return
        if key in rows:  # the nearest way stays; another field that links the same way is added to it
            if rows[key]["how"] == how:
                rows[key]["via"].extend(field for field in via or [] if field not in rows[key]["via"])
            return
        found = says.get(key, {})
        rows[key] = {"address": key, "kind": found.get("kind"), "says": found.get("says"), "how": how, "via": via or []}

    for address, fields in changed.items():
        add(address, "change", fields)
    for address in sorted(drawn):
        for edge in links_of(after, address):
            add(edge.address, "link", [edge.field])
    for address in sorted(drawn):
        for edge in back[address]:
            add(edge.address, "linked-from", [edge.field])
    for address in sorted(drawn):
        for found in _reach(after, back, address):
            add(found[1], found[0])
    return list(rows.values())


def _reach(after: Snapshot, back: Mapping[Address, list[Edge]], address: Address) -> list[tuple[str, Address]]:
    """What the entry reaches through links, then what reaches it, each with its way."""
    forward = closure(address, lambda at: (edge.address for edge in links_of(after, at)))
    behind = closure(address, lambda at: (edge.address for edge in back[at]))
    return [("reaches", found) for found in sorted(forward)] + [("reached-by", found) for found in sorted(behind)]


def build(
    target: Target, known: Mapping[str, Json], records: Sequence[Mapping[Any, Any]], *, decision: str | None, option: str | None
) -> Json:
    """What the board draws: the new entries as inspection records, and the rows of what they would touch. Refuses what `put` would."""
    if not records or len(records) > RECORD_LIMIT:
        raise RefusalError([f"give 1 to {RECORD_LIMIT} records in the `put` format"])
    _kept(decision, option, known)
    before, after, written = _after(target, records)
    drawn = {address for address in after.entries if address not in before.entries}
    document = inspect(after)
    new = {str(address) for address in drawn}
    says = {
        record["address"]: {"kind": record["kind"], "says": _plain(record["sentence"])}
        for record in document["entries"]
        if isinstance(record["address"], str) and record["address"] not in new
    }
    changed = {address: fields for address, fields in _fields(records, written) if address not in drawn}
    touching = _touching(after, drawn, changed, says)
    return {
        "entries": [record for record in document["entries"] if record["address"] in new],
        "parts": [record for record in document["parts"] if record["parent"] in new],
        "relations": [record for record in document["relations"] if record["owner"] in new],
        "touching": touching[:TOUCH_LIMIT],
        "more": max(len(touching) - TOUCH_LIMIT, 0),
        "decision": decision,
        "option": option,
    }


def _fields(records: Sequence[Mapping[Any, Any]], written: list[tuple[Address, bool]]) -> list[tuple[Address, list[str]]]:
    """Each changed (not new) record's address with the fields it sets."""
    keys = set(put.KEYS)
    by_text = {str(address): new for address, new in written}
    found = []
    for record in records:
        text = record.get("address")
        if isinstance(text, str) and by_text.get(text) is False:
            address = next(a for a, _ in written if str(a) == text)
            found.append((address, [str(name) for name in record if name not in keys]))
    return found
