"""One inspection per input identity, isolated from trial writes by the writer's repository lock."""

from __future__ import annotations

import json
import threading
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

from content_digest import digest

from ogy.inspect import Document, inspect
from ogy.snapshot import load
from ogy.source import open_source
from ogy.web.reach import reach
from ogy.web.standing import standing
from ogy.writes import reading

if TYPE_CHECKING:
    from ogy.target import Target


class InspectionCache:
    """Refuse during writes; even cached responses must acquire the same exclusive lock."""

    def __init__(self, target: Target) -> None:
        self.target = target.at(".")
        self.guard = threading.Lock()
        self.key: str | None = None
        self.document: Document = {}
        self.encoded = b""
        self.reached: dict[str, dict[str, dict[str, object]]] = {}
        self.reached_key: str | None = None

    def current(self) -> Document:
        with self.guard, reading(self.target):
            return self._current()

    def response(self) -> tuple[Document, bytes]:
        """Return matching document and encoded bytes from one locked read."""
        with self.guard, reading(self.target):
            return self._current(), self.encoded

    def standing(self) -> Document:
        """Read standing and its snapshot version under one repository lock."""
        with self.guard, reading(self.target):
            document = self._current()
            if self.reached_key != self.key:
                self.reached, self.reached_key = reach(self.target.read()[1]), self.key
            return {**standing(self.target, self.reached), "version": document["snapshot"]["version"]}

    def _current(self) -> Document:
        target = self.target
        root = target.repo / target.ontology if "/" in target.ontology else Path(str(files("ogy").joinpath("ontologies", target.ontology)))
        ontology_files = [root.joinpath(name) for name in ("ontology.yml", "starts.yml", "agents.md")]
        kinds = root.joinpath("kinds")
        if kinds.is_dir():
            ontology_files.extend(sorted(kinds.iterdir(), key=lambda path: path.name))
        paths = [*(target.repo / target.kb).rglob("*"), target.repo / "ogy.yml", *ontology_files]
        signature = []
        for path in sorted(paths):
            if path.is_file():
                stat = path.stat()
                signature.append((str(path), stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino))
        key = digest(signature, length=64)
        if key != self.key:
            source = open_source(target.repo, ".", target.kb)
            document = inspect(load(source, target.kinds()))
            config = target.repo / "ogy.yml"
            identity = digest(
                {
                    "listing": source.listing(),
                    "ontology": {str(path): path.read_bytes().hex() for path in ontology_files if path.is_file()},
                    "config": config.read_bytes().hex() if config.is_file() else None,
                },
                length=64,
            )
            document["snapshot"]["version"] = digest({"inputs": identity, "snapshot": document["snapshot"]}, length=64)
            encoded = json.dumps(document, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
            self.document, self.encoded, self.key = document, encoded, key
        return self.document
