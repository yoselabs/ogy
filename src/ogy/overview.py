"""`ogy status`: the standing of the knowledge base in one screen. Computed; nothing is saved."""

from dataclasses import dataclass

from ogy.review import Header


@dataclass(frozen=True)
class Overview:
    """Counts per area, and how many findings, pieces of work left and dropped things there are (the area asked for, or all)."""

    areas: list[Header]
    findings: int
    work: int
    dropped: int
    waiting: int = 0  # terms no one has agreed to yet
    coverage: dict[str, tuple[str, ...]] | None = None  # per layer, the kinds with no entry; only for `status --coverage`
