"""The constitution: the entries of the kind that declares `printed_first:` (the principles of the fixed folder `constitution/`),
printed whole to an agent before the glossary."""

from ogy.model import Entry
from ogy.snapshot import Snapshot
from ogy.terms import glossary_lines


def principles(snapshot: Snapshot) -> list[Entry]:
    kind = snapshot.ontology.printed_kind()
    return [entry for address, entry in sorted(snapshot.entries.items()) if kind and address.kind == kind.kind]


def constitution_lines(snapshot: Snapshot) -> list[str]:
    """Every printed-first entry, whole: `<id>: <sentence>`, then the field it prints under it; empty when there is none."""
    kind = snapshot.ontology.printed_kind()
    if kind is None or kind.printed_first is None or kind.sentence is None:
        return []
    lines: list[str] = []
    also = kind.printed_first.also
    for entry in principles(snapshot):
        lines.append(f"  {entry.address.key}: {entry.text(kind.sentence)}")
        if also and (text := entry.text(also)):
            lines.append(f"    {also}: {text}")
    return [f"{kind.area or kind.kind} (every decision is judged against these):", *lines, ""] if lines else []


def printed_lines(snapshot: Snapshot, home: str | None = None) -> list[str]:
    """What an agent reads first: the constitution, then the glossary (of one area and what it shares, when `home` is given)."""
    return [*constitution_lines(snapshot), *glossary_lines(snapshot, home)]
