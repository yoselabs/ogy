"""What the layout leaves empty or misnamed: kinds without entries per layer (`ogy status --coverage`), areas named like the
product, and areas without the entry an `every_area` kind declares."""

from ogy.kinds import NAME, Shape
from ogy.layout import REMOVED_FILE, path_for
from ogy.model import Address, Finding, Problem
lazy from ogy.snapshot import Snapshot
lazy from ogy.source import Source


def uncovered(snapshot: Snapshot) -> dict[str, tuple[str, ...]]:
    """Per layer, the kinds that may appear in it and have no entry in it; a part lives in its parent's file, so only the
    kinds that own a file count, and a kind of the fixed folders (the constitution) belongs to no layer."""
    used = {(entry.address.layer, entry.address.kind) for entry in snapshot.entries.values()}
    return {
        layer: tuple(
            sorted(
                kind.kind
                for kind in snapshot.ontology.kinds.values()
                if kind.shape is not Shape.INLINE and layer in kind.layers and (layer, kind.kind) not in used
            )
        )
        for layer in snapshot.ontology.layers
    }


def product_areas(snapshot: Snapshot, repo_name: str) -> list[Finding]:
    """An area named like the repository names the product, not a topic: one finding per home."""
    product = repo_name.casefold().replace("_", "-").replace(" ", "-")
    homes = sorted({entry.address.home for entry in snapshot.entries.values() if entry.address.area == product and entry.address.layer})
    return [
        Finding(Problem.PRODUCT_AREA, home, f"the area is named like the product ({repo_name}); name a topic, not the product")
        for home in homes
    ]


def areas(snapshot: Snapshot, source: Source) -> list[tuple[str, str]]:
    """Every area folder that holds an entry file, as (layer, area); the fixed folders hold no area, a misnamed folder is `bad-path`,
    and a folder that holds only its removed ledger is an area no more (its entries were removed or moved)."""
    layers = snapshot.ontology.layers
    return sorted(
        {
            (parts[0], parts[1])
            for path in source.listing()
            if len(parts := path.split("/")) > 2 and parts[0] in layers and NAME.match(parts[1]) and parts[2:] != [REMOVED_FILE]
        }
    )


def check_every_area(snapshot: Snapshot, source: Source) -> list[Finding]:
    """An area of a layer that lacks the entry an `every_area` kind declares: for a single kind, its file."""
    found: list[Finding] = []
    for kind in (kind for kind in snapshot.ontology.kinds.values() if kind.every_area):
        held = {(address.layer, address.area) for address in snapshot.entries if address.kind == kind.kind and address.parent() is None}
        for layer, area in areas(snapshot, source):
            if layer in kind.layers and (layer, area) not in held:
                single = kind.shape is Shape.SINGLE
                address = Address(layer, area, ((kind.kind, area),)) if single else None
                path = path_for(kind, f"{layer}/{area}", area) if single else f"{layer}/{area}"
                detail = f"every area of {layer} holds its {kind.kind} entry: add {address or kind.kind}"
                found.append(Finding(Problem.MISSING_ENTRY, path, detail, address))
    return found
