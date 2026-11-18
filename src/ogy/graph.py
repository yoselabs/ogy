"""`context` and `impact`: what an entry is connected to, through typed links and parts."""

from collections import deque
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from ogy.links import link_items, resolve
from ogy.model import Address, Entry
from ogy.snapshot import Snapshot

PARENT = "of"  # the edge from a part to its parent


@dataclass(frozen=True)
class Edge:
    field: str
    address: Address


def links_of(snapshot: Snapshot, address: Address) -> list[Edge]:
    """Resolving links out of an entry, plus the edge to its parent when it is a part."""
    edges: list[Edge] = []
    for item in link_items(snapshot.ontology, snapshot.entries[address]):
        target = resolve(snapshot.ontology, snapshot.entries, address, item).target
        if target is not None:
            edges.append(Edge(item.field, target))
    parent = address.parent()
    if parent is not None and parent in snapshot.entries:
        edges.append(Edge(PARENT, parent))
    return edges


def incoming(snapshot: Snapshot) -> dict[Address, list[Edge]]:
    """For each entry, the entries whose links (or part edge) point at it."""
    found: dict[Address, list[Edge]] = {address: [] for address in snapshot.entries}
    for address in snapshot.entries:
        for edge in links_of(snapshot, address):
            found[edge.address].append(Edge(edge.field, address))
    return found


def closure(start: Address, step: Callable[[Address], Iterable[Address]]) -> set[Address]:
    seen: set[Address] = set()
    queue = deque([start])
    while queue:
        for nxt in step(queue.popleft()):
            if nxt not in seen and nxt != start:
                seen.add(nxt)
                queue.append(nxt)
    return seen


@dataclass(frozen=True)
class Impact:
    """`reaches`: everything the entry's links lead to, transitively. `reached_by`: everything that leads to it."""

    address: Address
    reaches: frozenset[Address]
    reached_by: frozenset[Address]


def impact(snapshot: Snapshot, address: Address) -> Impact:
    back = incoming(snapshot)
    reaches = closure(address, lambda at: (edge.address for edge in links_of(snapshot, at)))
    reached_by = closure(address, lambda at: (edge.address for edge in back[at]))
    return Impact(address, frozenset(reaches), frozenset(reached_by))


@dataclass(frozen=True)
class Context:
    """What an agent reads before changing one entry."""

    entry: Entry
    fingerprint: str
    parents: tuple[Address, ...]
    parts: tuple[Address, ...]
    links: tuple[Edge, ...]
    referenced_by: tuple[Edge, ...]


def context(snapshot: Snapshot, address: Address) -> Context:
    parents: list[Address] = []
    at = address.parent()
    while at is not None and at in snapshot.entries:
        parents.append(at)
        at = at.parent()
    back = incoming(snapshot)
    parts = tuple(sorted(edge.address for edge in back[address] if edge.field == PARENT))
    referenced = tuple(edge for edge in back[address] if edge.field != PARENT)
    links = tuple(edge for edge in links_of(snapshot, address) if edge.field != PARENT)
    return Context(snapshot.entries[address], snapshot.fingerprint(address), tuple(parents), parts, links, referenced)
