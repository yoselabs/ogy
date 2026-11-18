"""Change entries in the worktree by address, whatever file shape their kind uses. Returns the paths written."""

from collections.abc import Mapping
from pathlib import Path

import any_yaml

from ogy.kinds import Holds, Kind, Shape
from ogy.layout import path_for
from ogy.model import Address
from ogy.ontology import Ontology
from ogy.snapshot import Snapshot, load
from ogy.source import WorktreeSource

type Data = dict[str, object]


class Editor:
    """Edits a knowledge base on disk. Every call re-reads what it needs, so edits never see a stale snapshot."""

    def __init__(self, root: Path, kb: str, ontology: Ontology) -> None:
        self.root = root
        self.kb = kb
        self.ontology = ontology

    def snapshot(self) -> Snapshot:
        return load(WorktreeSource(self.root, self.kb), self.ontology)

    def _read(self, rel: str) -> object:
        path = self.root / self.kb / rel
        return any_yaml.load(path.read_text()) if path.exists() else None

    def _write(self, rel: str, data: object) -> str:
        """Write `data` into the file, keeping its comments."""
        path = self.root / self.kb / rel
        any_yaml.write(path, data)
        return f"{self.kb}/{rel}"

    def _kind(self, name: str) -> Kind:
        kind = self.ontology.get(name)
        if kind is None:
            raise KeyError(name)
        return kind

    def _top(self, data: object, address: Address) -> Data | None:
        """The mapping of the file's own entry: the whole file for an entity, the item with the id in a list."""
        if isinstance(data, dict):
            return data
        for item in data if isinstance(data, list) else []:
            if isinstance(item, dict) and item.get("id") == address.path[0][1]:
                return item
        return None

    def _node(self, data: object, address: Address) -> Data | None:
        """The mapping that holds `address` inside a file's data."""
        node = self._top(data, address)
        for kind, key in address.path[1:]:
            part = self._kind(kind)
            held = node.get(part.key or "") if node is not None else None
            found = held if part.holding is Holds.ONE else held.get(key) if isinstance(held, dict) else None
            node = found if isinstance(found, dict) else None
        return node

    def put(self, address: Address, fields: Mapping[str, object]) -> list[str]:
        """Add an entry, or replace the fields of an existing one."""
        snap = self.snapshot()
        if address in snap.entries:
            return self.update(address, {**dict.fromkeys(snap.entries[address].fields), **fields}, snap=snap)
        kind = self._kind(address.kind)
        parent = address.parent()
        if parent is not None:
            rel = snap.entries[parent].path
            data = self._read(rel)
            node = self._node(data, parent)
            if node is None:
                raise KeyError(str(parent))
            if kind.holding is Holds.ONE:
                node[kind.key or ""] = dict(fields)
            else:
                held = node.setdefault(kind.key or "", {})
                if isinstance(held, dict):
                    held[address.key] = dict(fields)
            return [self._write(rel, data)]
        rel = path_for(kind, address.home, address.key)
        if kind.shape is Shape.LIST:
            data = self._read(rel)
            items = data if isinstance(data, list) else []
            items.append({"id": address.key, **fields})
            return [self._write(rel, items)]
        return [self._write(rel, dict(fields))]

    def update(self, address: Address, fields: Mapping[str, object | None], snap: Snapshot | None = None) -> list[str]:
        """Set fields; a None value removes the field."""
        snap = snap or self.snapshot()
        rel = snap.entries[address].path
        data = self._read(rel)
        node = self._node(data, address)
        if node is None:
            raise KeyError(str(address))
        for name, value in fields.items():
            if value is None:
                node.pop(name, None)
            else:
                node[name] = value
        return [self._write(rel, data)]

    def remove(self, address: Address) -> list[str]:
        snap = self.snapshot()
        rel = snap.entries[address].path
        kind = self._kind(address.kind)
        parent = address.parent()
        if parent is None and kind.shape is not Shape.LIST:
            (self.root / self.kb / rel).unlink()
            return [f"{self.kb}/{rel}"]
        data = self._read(rel)
        if parent is None and isinstance(data, list):
            data = [item for item in data if not (isinstance(item, dict) and item.get("id") == address.key)]
        else:
            node = self._node(data, parent) if parent is not None else None
            held = node.get(kind.key or "") if node is not None else None
            if node is not None and kind.holding is Holds.ONE:
                node.pop(kind.key or "", None)
            elif isinstance(held, dict):
                held.pop(address.key, None)
        return [self._write(rel, data)]

    def relocate(self, address: Address, home: str) -> list[str]:
        """Move a top-level entry, with every part it owns, to another home (`<layer>/<area>`); its content is not touched."""
        rel, kind = self.snapshot().entries[address].path, self._kind(address.kind)
        new = path_for(kind, home, address.key)
        (self.root / self.kb / new).parent.mkdir(parents=True, exist_ok=True)
        if kind.shape is not Shape.LIST:
            (self.root / self.kb / rel).rename(self.root / self.kb / new)
            return [f"{self.kb}/{rel}", f"{self.kb}/{new}"]
        data = self._read(rel)
        items = data if isinstance(data, list) else []
        item = next(item for item in items if isinstance(item, dict) and item.get("id") == address.key)
        rest = [other for other in items if other is not item]
        if rest:
            self._write(rel, rest)
        else:
            (self.root / self.kb / rel).unlink()
        held = self._read(new)
        self._write(new, [*(held if isinstance(held, list) else []), item])
        return [f"{self.kb}/{rel}", f"{self.kb}/{new}"]
