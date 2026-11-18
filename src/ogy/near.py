"""Near misses: what a person meant when the name they typed is not there."""

import difflib
from collections.abc import Iterable

from ogy.snapshot import Snapshot

MOST = 3


def near(wanted: str, candidates: Iterable[str]) -> list[str]:
    """Up to three candidates that look like `wanted`: close spellings first, then those ending in the same last segment."""
    known = sorted(set(candidates))
    close = difflib.get_close_matches(wanted, known, n=MOST, cutoff=0.6)
    tail = wanted.rstrip("/").rsplit("/", 1)[-1].replace("_", "-")
    same = [item for item in known if item.rsplit("/", 1)[-1] == tail and item not in close]
    return [*close, *same][:MOST]


def hint(wanted: str, candidates: Iterable[str]) -> str:
    """` (did you mean a, b?)`, or nothing when no candidate is near."""
    found = near(wanted, candidates)
    return f" (did you mean {', '.join(found)}?)" if found else ""


def no_entry(snapshot: Snapshot, text: str, kind: str | None = None) -> str:
    """`no entry <text>`, with the addresses of the snapshot that are near it (of one kind when `kind` is given)."""
    return f"no entry {text}" + hint(text, (str(a) for a in snapshot.entries if kind in (None, a.kind)))
