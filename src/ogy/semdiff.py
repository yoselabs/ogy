"""`ogy diff A B`: changes by address and field, reading only the files whose content changed."""

from dataclasses import dataclass, field
from enum import StrEnum

from ogy.model import Address, Entry
from ogy.ontology import Ontology
from ogy.snapshot import build, kb_paths
from ogy.source import Source


class Change(StrEnum):
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"


@dataclass(frozen=True)
class FieldChange:
    name: str
    old: object
    new: object


@dataclass(frozen=True)
class EntryChange:
    address: Address
    change: Change
    fields: tuple[FieldChange, ...] = ()


@dataclass
class SemanticDiff:
    changes: list[EntryChange] = field(default_factory=list)
    files_changed: tuple[str, ...] = ()
    same_tree: bool = False

    def by_address(self) -> dict[Address, EntryChange]:
        return {change.address: change for change in self.changes}


def _fields(old: Entry | None, new: Entry | None) -> tuple[FieldChange, ...]:
    before, after = (old.fields if old else {}), (new.fields if new else {})
    return tuple(FieldChange(name, before.get(name), after.get(name)) for name in sorted(set(before) | set(after))
                 if before.get(name) != after.get(name))


def diff(before: Source, after: Source, ontology: Ontology) -> SemanticDiff:
    """Equal tree ids mean nothing changed and nothing is read."""
    tree = before.tree_id()
    if tree is not None and tree == after.tree_id():
        return SemanticDiff(same_tree=True)
    old_list, new_list = before.listing(), after.listing()
    changed = kb_paths(path for path in set(old_list) | set(new_list) if old_list.get(path) != new_list.get(path))
    old_entries = build(ontology, before.read(path for path in changed if path in old_list)).entries
    new_entries = build(ontology, after.read(path for path in changed if path in new_list)).entries
    result = SemanticDiff(files_changed=tuple(changed))
    for address in sorted(set(old_entries) | set(new_entries)):
        old, new = old_entries.get(address), new_entries.get(address)
        if old is None:
            result.changes.append(EntryChange(address, Change.ADDED, _fields(None, new)))
        elif new is None:
            result.changes.append(EntryChange(address, Change.REMOVED))
        elif fields := _fields(old, new):
            result.changes.append(EntryChange(address, Change.CHANGED, fields))
    return result
