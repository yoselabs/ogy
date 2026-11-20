"""A removed ledger that follows a move: the addresses in its items are renamed, or a fixed folder's ledger joins its new home's."""

import dataclasses
from typing import TYPE_CHECKING

import any_yaml

from ogy.removed import FILE, FORMAT, Item, Ledger, Parent, RemovedError, is_address, parse, raw_item

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from pathlib import Path


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
    return lambda text: new + text[len(old) :] if text.startswith(old + "/") else text


def moved_item(item: Item, rename: Callable[[str], str]) -> Item:
    parent = item.parent and Parent(rename(item.parent.address), item.parent.key, item.parent.position)
    return dataclasses.replace(
        item,
        id=rename(item.id),
        parent=parent,
        why=item.why and rename(item.why),
        replaced_by=item.replaced_by and rename(item.replaced_by),
    )


def rehomed(ledgers: Mapping[str, Ledger], old: str, new: str) -> dict[str, Ledger]:
    """The ledgers after the home `old` (a fixed folder its kind moved out of) became `new`: its items follow the items `new`
    already holds, every address in them under `new`. What `rehome` writes and how `check --base` reads the base."""
    found = dict(ledgers)
    moved = found.pop(old, None)
    if moved is None:
        return found
    held = found[new].items if new in found else ()
    found[new] = Ledger(new, FORMAT, (*held, *(moved_item(item, _prefixed(old, new)) for item in moved.items)))
    return found


def rehome(root: Path, old: str, new: str) -> list[str]:
    """Write `rehomed` for the ledger of `old`: its items go to the end of `new`'s ledger and its file is deleted (`ogy migrate`,
    the one change to a ledger besides an append and a move's `follow`). Returns the files written, relative to `root`."""
    ledgers, problems = parse(
        {f"{home}/{FILE}": (root / home / FILE).read_text(encoding="utf-8") for home in (old, new) if (root / home / FILE).is_file()}
    )
    if problems:
        raise RemovedError(problems)
    if old not in ledgers:
        return []
    ledger = rehomed(ledgers, old, new)[new]
    path = root / new / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    any_yaml.write(path, {"format": FORMAT, "items": [raw_item(item) for item in ledger.items]})
    (root / old / FILE).unlink()
    return [f"{old}/{FILE}", f"{new}/{FILE}"]
