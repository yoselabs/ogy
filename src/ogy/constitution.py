"""The constitution: the principles of the fixed folder `constitution/`, printed whole to an agent before the glossary."""

from ogy.model import Entry
from ogy.snapshot import Snapshot
from ogy.terms import glossary_lines

PRINCIPLE = "principle"


def principles(snapshot: Snapshot) -> list[Entry]:
    return [entry for address, entry in sorted(snapshot.entries.items()) if address.kind == PRINCIPLE]


def constitution_lines(snapshot: Snapshot) -> list[str]:
    """Every principle, whole: `<id>: <says>`, then its `why`; empty when the knowledge base has none."""
    lines: list[str] = []
    for entry in principles(snapshot):
        lines.append(f"  {entry.address.key}: {entry.text('says')}")
        if why := entry.text("why"):
            lines.append(f"    why: {why}")
    return ["constitution (every decision is judged against these):", *lines, ""] if lines else []


def printed_lines(snapshot: Snapshot, home: str | None = None) -> list[str]:
    """What an agent reads first: the constitution, then the glossary (of one area and what it shares, when `home` is given)."""
    return [*constitution_lines(snapshot), *glossary_lines(snapshot, home)]
