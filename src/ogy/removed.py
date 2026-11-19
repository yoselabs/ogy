"""The removed ledger: `removed.yml` in a home (`<layer>/<area>/`, or a fixed folder such as `constitution/`), format 1, written
only by ogy, append-only, one format for every ontology.

Plain data in and out (address strings, dicts, a root Path) so any caller can wire it in. The checks are pure functions
that return problems; the snapshot is opaque and checked only by a validator the caller passes when an item is
appended."""

import dataclasses
import datetime
import operator
import re
from collections.abc import Callable, Collection, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

import any_yaml

__all__ = [
    "FILE",
    "FORMAT",
    "Item",
    "Ledger",
    "Parent",
    "Problem",
    "RemovedError",
    "append",
    "check_append_only",
    "check_envelope",
    "check_links",
    "check_new_snapshots",
    "check_replacements",
    "check_unrecorded",
    "check_why",
    "find_reuse",
    "follow",
    "from_raw",
    "parse",
    "read_all",
    "rehome",
    "rehomed",
    "search",
]

FORMAT = 1
FILE = "removed.yml"
_KEYS = ("id", "kind", "parent", "title", "said", "why", "replaced_by", "at", "last_seen", "hash", "ontology")
_SHA = re.compile(r"[0-9a-f]{40}")
_HASH = re.compile(r"[0-9a-f]{12}")


@dataclass(frozen=True)
class Problem:
    code: str
    address: str
    detail: str


@dataclass(frozen=True)
class Parent:
    address: str
    key: str
    position: int


@dataclass(frozen=True)
class Item:
    id: str
    kind: str
    parent: Parent | None
    title: str | None
    said: str | None
    why: str | None
    replaced_by: str | None
    at: datetime.datetime
    last_seen: str
    hash: str
    ontology: str
    snapshot: dict[str, object]


@dataclass(frozen=True)
class Ledger:
    home: str
    format: int
    items: tuple[Item, ...]


class RemovedError(Exception):
    def __init__(self, problems: list[Problem]):
        super().__init__("; ".join(f"{p.code} {p.address}: {p.detail}" for p in problems))
        self.problems = problems


def _segments(address: str) -> list[str]:
    return address.split("/")


def is_part(address: str, home: str) -> bool:
    """An address longer than `<home>/<kind>/<id>`."""
    return len(_segments(address)) > len(_segments(home)) + 2


def _bad(address: str, detail: str) -> Problem:
    return Problem("bad-removed", address, detail)


def _text_or_none(value: object) -> bool:
    return value is None or isinstance(value, str)


def _when(value: object) -> datetime.datetime | None:
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except ValueError:
            return None
    if isinstance(value, datetime.datetime) and value.utcoffset() is not None:
        return value
    return None


def _parent_problems(raw: dict[str, object], address: str, home: str) -> list[Problem]:
    parent, parts = raw.get("parent"), _segments(address)
    if not is_part(address, home):
        return [] if parent is None else [_bad(address, "parent must be null for an entity")]
    if not isinstance(parent, dict) or set(parent) != {"address", "key", "position"}:
        return [_bad(address, "parent must be {address, key, position} for a part")]
    ok = (isinstance(parent["address"], str) and isinstance(parent["key"], str)
          and isinstance(parent["position"], int) and not isinstance(parent["position"], bool))
    if not ok or parent["position"] < 0:
        return [_bad(address, "parent has wrong types")]
    if parent["address"] != "/".join(parts[:-2]):
        return [_bad(address, "parent.address is not id without its last two segments")]
    return []


def check_envelope(raw: object, home: str) -> list[Problem]:
    """R4 for one item: exactly the envelope keys (plus snapshot), the types, kind and home agreeing with id."""
    if not isinstance(raw, dict):
        return [_bad(home, "an item is not a mapping")]
    address = raw.get("id") if isinstance(raw.get("id"), str) else home
    if set(raw) != {*_KEYS, "snapshot"}:
        return [_bad(address, f"keys differ from the envelope: {sorted(set(raw) ^ {*_KEYS, 'snapshot'})}")]
    problems: list[Problem] = []
    if not isinstance(raw["id"], str) or not raw["id"].startswith(home + "/") or len(_segments(raw["id"])) < len(_segments(home)) + 2:
        return [_bad(address, f"id is not an address in {home}")]
    if raw["kind"] != _segments(address)[-2]:
        problems.append(_bad(address, "kind differs from the kind in id"))
    problems += _parent_problems(raw, address, home)
    if not all(_text_or_none(raw[k]) for k in ("title", "said", "why", "replaced_by")):
        problems.append(_bad(address, "title, said, why, replaced_by are text or null"))
    if _when(raw["at"]) is None:
        problems.append(_bad(address, "at is a date-time with a UTC offset"))
    if not (isinstance(raw["last_seen"], str) and _SHA.fullmatch(raw["last_seen"])):
        problems.append(_bad(address, "last_seen is 40 hex"))
    if not (isinstance(raw["hash"], str) and _HASH.fullmatch(raw["hash"])):
        problems.append(_bad(address, "hash is 12 hex"))
    if not (isinstance(raw["ontology"], str) and raw["ontology"]) or not isinstance(raw["snapshot"], dict):
        problems.append(_bad(address, "ontology is a name and snapshot a mapping"))
    return problems


def _text(raw: dict[str, object], key: str) -> str | None:
    value = raw[key]
    return None if value is None else str(value)


def from_raw(raw: dict[str, object]) -> Item:
    """The item of a mapping that `check_envelope` accepted."""
    parent, at, snapshot = raw["parent"], _when(raw["at"]), raw["snapshot"]
    if at is None or not isinstance(parent, dict | None) or not isinstance(snapshot, dict):
        raise ValueError("not an item: check its envelope first")
    return Item(str(raw["id"]), str(raw["kind"]),
                None if parent is None else Parent(str(parent["address"]), str(parent["key"]), int(parent["position"])),
                _text(raw, "title"), _text(raw, "said"), _text(raw, "why"), _text(raw, "replaced_by"), at,
                str(raw["last_seen"]), str(raw["hash"]), str(raw["ontology"]), snapshot)


def _raw(item: Item) -> dict[str, object]:
    parent = None if item.parent is None else {"address": item.parent.address, "key": item.parent.key,
                                               "position": item.parent.position}
    return {**{k: getattr(item, k) for k in _KEYS}, "parent": parent, "snapshot": item.snapshot}


def _ledger(home: str, text: str) -> tuple[Ledger | None, list[Problem]]:
    try:
        doc = any_yaml.load(text)
    except any_yaml.YAMLError as error:
        return None, [_bad(home, f"unreadable YAML: {error}")]
    if not isinstance(doc, dict) or set(doc) != {"format", "items"} or not isinstance(doc["items"], list):
        return None, [_bad(home, "a ledger holds exactly `format` and `items`")]
    if doc["format"] != FORMAT:
        return None, [_bad(home, f"unknown removed format {doc['format']!r}; this ogy reads {FORMAT}")]
    found = [p for raw in doc["items"] for p in check_envelope(raw, home)]
    ids = [raw["id"] for raw in doc["items"] if isinstance(raw, dict) and "id" in raw]
    found += [_bad(i, "id appears twice") for i in sorted({i for i in ids if ids.count(i) > 1})]
    return (None if found else Ledger(home, FORMAT, tuple(from_raw(raw) for raw in doc["items"]))), found


def parse(texts: Mapping[str, str]) -> tuple[dict[str, Ledger], list[Problem]]:
    """The ledgers in `{<home>/removed.yml: text}`, by home, and R4 problems (a bad file is left out)."""
    ledgers: dict[str, Ledger] = {}
    problems: list[Problem] = []
    for path, text in sorted(texts.items()):
        ledger, found = _ledger(path.removesuffix("/" + FILE), text)
        problems += found
        if ledger is not None:
            ledgers[ledger.home] = ledger
    return ledgers, problems


def read_all(root: Path) -> tuple[dict[str, Ledger], list[Problem]]:
    """Every `<home>/removed.yml` under `root` (`<layer>/<area>/`, or a fixed folder): the ledgers by home, and R4 problems."""
    found = [*root.glob(f"*/{FILE}"), *root.glob(f"*/*/{FILE}")]
    return parse({path.relative_to(root).as_posix(): path.read_text(encoding="utf-8") for path in found})


def _all_items(ledgers: Iterable[Ledger]) -> list[Item]:
    return [item for ledger in ledgers for item in ledger.items]


def append(root: Path, home: str, item: Item, snapshot_check: Callable[[Item], list[str]]) -> None:
    """Add one item at the end of its home's file. Raises RemovedError when the envelope is bad, the id is already in
    a ledger, or `snapshot_check` (given the item; returns problem details) finds the snapshot wanting (R7)."""
    problems = check_envelope(_raw(item), home)
    ledgers, existing = read_all(root)
    if existing:
        raise RemovedError(existing)
    if any(old.id == item.id for old in _all_items(ledgers.values())):
        problems.append(Problem("id-reused", item.id, "this id is already in a removed.yml"))
    if not problems:
        problems += [Problem("bad-snapshot", item.id, d) for d in snapshot_check(item)]
    if problems:
        raise RemovedError(problems)
    path = root / home / FILE
    any_yaml.append_item_file(path, "items", _raw(item), initial=f"format: {FORMAT}\n")


def follow(root: Path, rename: Callable[[str], str]) -> list[str]:
    """After a move: the `why` and `replaced_by` of every item name the address the entry has now (the only change to an
    item R3 lets through). Returns the files rewritten, relative to `root`."""
    written: list[str] = []
    for path in sorted([*root.glob(f"*/{FILE}"), *root.glob(f"*/*/{FILE}")]):
        doc = any_yaml.load(path.read_text(encoding="utf-8"))
        items = doc.get("items") if isinstance(doc, dict) else None
        changed = False
        for raw in items if isinstance(items, list) else []:
            for key in ("why", "replaced_by"):
                if isinstance(raw, dict) and isinstance(value := raw.get(key), str) and is_address(value) and rename(value) != value:
                    raw[key], changed = rename(value), True
        if changed:
            any_yaml.write(path, doc)
            written.append(path.relative_to(root).as_posix())
    return written


def _prefixed(old: str, new: str) -> Callable[[str], str]:
    return lambda text: new + text[len(old):] if text.startswith(old + "/") else text


def _moved_item(item: Item, rename: Callable[[str], str]) -> Item:
    parent = item.parent and Parent(rename(item.parent.address), item.parent.key, item.parent.position)
    return dataclasses.replace(item, id=rename(item.id), parent=parent, why=item.why and rename(item.why),
                               replaced_by=item.replaced_by and rename(item.replaced_by))


def rehomed(ledgers: Mapping[str, Ledger], old: str, new: str) -> dict[str, Ledger]:
    """The ledgers after the home `old` (a fixed folder its kind moved out of) became `new`: its items follow the items `new`
    already holds, every address in them under `new`. What `rehome` writes and how `check --base` reads the base."""
    found = dict(ledgers)
    moved = found.pop(old, None)
    if moved is None:
        return found
    held = found[new].items if new in found else ()
    found[new] = Ledger(new, FORMAT, (*held, *(_moved_item(item, _prefixed(old, new)) for item in moved.items)))
    return found


def rehome(root: Path, old: str, new: str) -> list[str]:
    """Write `rehomed` for the ledger of `old`: its items go to the end of `new`'s ledger and its file is deleted (`ogy migrate`,
    the one change to a ledger besides an append and a move's `follow`). Returns the files written, relative to `root`."""
    ledgers, problems = parse({f"{home}/{FILE}": (root / home / FILE).read_text(encoding="utf-8")
                               for home in (old, new) if (root / home / FILE).is_file()})
    if problems:
        raise RemovedError(problems)
    if old not in ledgers:
        return []
    ledger = rehomed(ledgers, old, new)[new]
    path = root / new / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    any_yaml.write(path, {"format": FORMAT, "items": [_raw(item) for item in ledger.items]})
    (root / old / FILE).unlink()
    return [f"{old}/{FILE}", f"{new}/{FILE}"]


def check_new_snapshots(items: Iterable[Item], base_ids: Collection[str],
                        validator: Callable[[Item], list[str]]) -> list[Problem]:
    """R7: only items not in the base are checked; an old snapshot is never read."""
    return [Problem("bad-snapshot", i.id, d) for i in items if i.id not in base_ids for d in validator(i)]


def check_append_only(base: Ledger | None, current: Ledger | None, home: str,
                      same: Callable[[Item, Item], bool] = operator.eq) -> list[Problem]:
    """R3: against the base version of a home's ledger; `same(old, now)` says an item is unchanged (by default: equal)."""
    if base is None:
        return []
    if current is None:
        return [Problem("edited-append-only", home, "the file is gone")]
    if current.format != base.format:
        return [Problem("edited-append-only", home, "format changed")]
    for place, old in enumerate(base.items):
        if place >= len(current.items) or not same(old, current.items[place]):
            return [Problem("edited-append-only", old.id, f"item {place} is not as in the base")]
    return []


def _covers(removed: str, address: str) -> bool:
    return address == removed or address.startswith(removed + "/")


def find_reuse(items: Iterable[Item], live: Iterable[str]) -> list[Problem]:
    """R2: a live address equal to an item's id, or under one."""
    ids = [item.id for item in items]
    return [Problem("id-reused", a, f"{i} is in a removed.yml") for a in sorted(live) for i in ids if _covers(i, a)]


def check_unrecorded(base: Iterable[str], live: Collection[str], items: Iterable[Item]) -> list[Problem]:
    """R1: an address in the base and absent now needs an item at it or above it."""
    ids = [item.id for item in items]
    return [Problem("removed-unrecorded", a, "gone since the base and no removed.yml item covers it")
            for a in sorted(base) if a not in live and not any(_covers(i, a) for i in ids)]


ADDRESSY = re.compile(r"[a-z0-9-]+(?:/[a-z0-9_-]+)+")


def is_address(why: str | None) -> bool:
    """A `why` that is shaped like an address names a decision; any other `why` is the person's plain words."""
    return why is not None and ADDRESSY.fullmatch(why) is not None


def check_why(items: Iterable[Item], known: Collection[str], agreed: str) -> list[Problem]:
    """R5: a `why` shaped like an address names a live decision (`known`) or a removed item; any other is plain words.
    An item whose snapshot a person agreed to (its common field `agreed`) needs an address, not plain words or none."""
    items = list(items)
    seen = {*known, *(i.id for i in items)}
    out = [Problem("removed-without-why", i.id, f"why {i.why} is no decision")
           for i in items if is_address(i.why) and i.why not in seen]
    return out + [Problem("removed-without-why", i.id, "a person agreed to it, so why is the address of a decision")
                  for i in items if not is_address(i.why) and isinstance(i.snapshot.get(agreed), dict)]


def check_replacements(items: Iterable[Item], live: Collection[str]) -> list[Problem]:
    """R6: every `replaced_by` chain ends at a live address; a dead end or a cycle is broken."""
    by_id = {i.id: i for i in items}
    out: list[Problem] = []
    for item in by_id.values():
        step, seen = item, {item.id}
        while step.replaced_by is not None and step.replaced_by not in live:
            nxt = by_id.get(step.replaced_by)
            if nxt is None or nxt.id in seen:
                out.append(Problem("broken-link", item.id, f"replaced_by {item.replaced_by} ends at {step.replaced_by}"
                                   + (" in a cycle" if nxt else " which is gone")))
                break
            step = nxt
            seen.add(step.id)
        else:
            if step.replaced_by is None and step is not item:
                out.append(Problem("broken-link", item.id, f"replaced_by chain ends at {step.id}, removed for good"))
    return out


def check_links(links: Iterable[tuple[str, str]], items: Iterable[Item]) -> list[Problem]:
    """R8: (source, target) pairs whose target is removed; the text names the item's why and replacement. The caller
    leaves out the allowed ones (`agreed`, an item's why and parent.address)."""
    by_id = {i.id: i for i in items}
    return [Problem("broken-link", s, f"{t} was removed (why: {by_id[t].why}, replaced by: {by_id[t].replaced_by})")
            for s, t in links if t in by_id]


def search(items: Iterable[Item], words: Iterable[str] = (), parent: str | None = None) -> list[Item]:
    """Items whose id, title or said hold every word; or, with `parent`, the removed parts of that address by
    position, then the removed parts of those."""
    items = list(items)
    if parent is None:
        needles = [w.casefold() for w in words]
        return [i for i in items if all(w in f"{i.id} {i.title or ''} {i.said or ''}".casefold() for w in needles)]
    out: list[Item] = []
    level = [parent]
    while level:
        kids = sorted((i for i in items if i.parent and i.parent.address in level and i not in out),
                      key=lambda i: (level.index(i.parent.address) if i.parent else 0, i.parent.position if i.parent else 0))
        out += kids
        level = [i.id for i in kids]
    return out
