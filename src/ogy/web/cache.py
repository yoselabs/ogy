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
    from ogy import ops
    from ogy.target import Target


class InspectionCache:
    """Refuse during writes; even cached responses must acquire the same exclusive lock."""

    def __init__(self, target: Target) -> None:
        self.target = target.at(".")
        self.guard = threading.Lock()
        self.key: str | None = None
        self.document: Document = {}
        self.encoded = b""
        self.loaded: ops.Loaded | None = None  # the read the cached inspection came from, its files held in memory
        self.flight = threading.Lock()  # one standing computation at a time; the repository lock is not held through it
        self.standing_key: str | None = None
        self.standing_document: Document = {}
        self.standing_encoded = b""

    def current(self) -> Document:
        with self.guard, reading(self.target):
            return self._current()

    def response(self) -> tuple[Document, bytes]:
        """Return matching document and encoded bytes from one locked read."""
        with self.guard, reading(self.target):
            return self._current(), self.encoded

    def standing(self) -> Document:
        """Standing with its snapshot version: cached per input identity, computed once for concurrent requests."""
        return self.standing_response()[0]

    def standing_response(self) -> tuple[Document, bytes]:
        """The standing document and its encoded bytes. The repository lock is held only to read the files into a snapshot;
        the computation runs on that snapshot after it is released, so a trial write never waits for it."""
        with self.guard, reading(self.target):
            version = str(self._current()["snapshot"]["version"])
            key, loaded = self.key, self.loaded
            assert loaded is not None  # noqa: S101  # _current filled it
            if self.standing_key == key:
                return self.standing_document, self.standing_encoded
        with self.flight:
            if self.standing_key == key:  # another request computed it while this one waited
                return self.standing_document, self.standing_encoded
            document = {**standing(self.target, reach(loaded[1]), loaded), "version": version}
            encoded = json.dumps(document, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
            self.standing_document, self.standing_encoded, self.standing_key = document, encoded, key
            return document, encoded

    def version_in_write(self) -> str:
        """The inspection version while the caller already holds the repository's write lock."""
        with self.guard:
            return str(self._current()["snapshot"]["version"])

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
            source.read(source.listing())  # hold every file's text now: later reads, after the lock is released, see this state
            snapshot = load(source, target.kinds())
            document = inspect(snapshot)
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
            self.document, self.encoded, self.key, self.loaded = document, encoded, key, (source, snapshot)
        return self.document
