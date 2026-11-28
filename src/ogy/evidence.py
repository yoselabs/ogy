"""Evidence items of `src` in the schemes the ontology declares (`evidence:` in `ontology.yml`), such as `code:<path>#<symbol>`
and `doc:<commit>:<path>#<anchor>`, checked and hashed by the reader each scheme names.

A pinned scheme names a Git revision: the file may be deleted later, its history stays.

Built here: decision product/capture/decision/intake-of-inputs.
"""

import re
from dataclasses import dataclass
from typing import Protocol
lazy from collections.abc import Mapping

import py_symbols
from any_markdown import find, github_outline
from content_digest import digest_text

from ogy.declared import Reader, Scheme
from ogy.model import Problem
from ogy.near import hint


class Read(Protocol):
    """Repository path (and a commit, for a pinned `doc:`) -> text, None when the file does not exist."""

    def __call__(self, path: str, rev: str | None = None) -> str | None: ...


HASH_LENGTH = 12
_COMMIT = re.compile(r"[0-9a-f]{7,40}")


@dataclass(frozen=True)
class EvidenceProblem:
    code: Problem  # bad-src, missing-code, missing-doc
    address: str
    detail: str


@dataclass(frozen=True)
class Link:
    scheme: str  # a scheme of the ontology's `evidence:`
    reads: Reader
    path: str
    fragment: str  # the symbol or the anchor
    rev: str | None = None  # the commit a pinned link names


def form(name: str, scheme: Scheme) -> str:
    """How an item of the scheme is written."""
    fragment = "symbol" if scheme.reads is Reader.SYMBOL else "anchor"
    return f"{name}:{'<commit>:' if scheme.pinned else ''}<path>#<{fragment}>"


def parse_link(item: str, schemes: Mapping[str, Scheme]) -> Link | EvidenceProblem | None:
    """An evidence item as a Link, a bad-src problem when malformed, None when it names no scheme of `schemes`."""
    name, sep, rest = item.partition(":")
    scheme = schemes.get(name) if sep else None
    if scheme is None:
        return None
    path, hash_sep, fragment = rest.partition("#")
    rev, pinned, tail = path.partition(":")
    if scheme.pinned:
        if not pinned or not _COMMIT.fullmatch(rev):
            return EvidenceProblem(Problem.BAD_SRC, item, f"{name}: pins a Git revision: {name}:<commit>:<repo path>#<anchor>")
        path = tail
    if not path or not hash_sep or not fragment or path.startswith("/") or ".." in path.split("/"):
        what = "symbol" if scheme.reads is Reader.SYMBOL else "anchor"
        return EvidenceProblem(Problem.BAD_SRC, item, f"{name}: needs <repo path>#<{what}>")
    return Link(name, scheme.reads, path, fragment, rev if scheme.pinned else None)


def check_item(item: str, read: Read, schemes: Mapping[str, Scheme]) -> EvidenceProblem | None:
    """The problem with one `src` item, or None."""
    link = parse_link(item, schemes)
    if isinstance(link, EvidenceProblem):
        return link
    if link is None:
        return EvidenceProblem(Problem.BAD_SRC, item, f"src is {' or '.join(form(name, s) for name, s in schemes.items())}")
    text = read(link.path, link.rev)
    files = schemes[link.scheme].files
    return _check_doc(item, link, text, files) if link.reads is Reader.SECTION else _check_code(item, link, text, files)


def _check_doc(item: str, link: Link, text: str | None, files: tuple[str, ...]) -> EvidenceProblem | None:
    if text is None or not link.path.endswith(files):
        return EvidenceProblem(Problem.MISSING_DOC, item, f"no Markdown file {link.path} at {link.rev}")
    if section_hash(text, link.fragment) is None:
        near = hint(link.fragment, (anchor for anchor, _, _ in anchors(text)))
        return EvidenceProblem(
            Problem.MISSING_DOC,
            item,
            f"no heading with anchor {link.fragment} in {link.path}{near}" + ("" if near else f"; `ogy anchors {link.path}` lists them"),
        )
    return None


def _check_code(item: str, link: Link, text: str | None, files: tuple[str, ...]) -> EvidenceProblem | None:
    if not link.path.endswith(files):
        return EvidenceProblem(Problem.BAD_SRC, item, f"{link.scheme}: links to {', '.join(files)} files only")
    if text is None:
        return EvidenceProblem(Problem.MISSING_CODE, item, f"no file {link.path}")
    if symbol_hash(text, link.fragment) is None:
        return EvidenceProblem(Problem.MISSING_CODE, item, f"{link.path} does not define {link.fragment}")
    return None


def check_items(items: list[str], read: Read, schemes: Mapping[str, Scheme]) -> list[EvidenceProblem]:
    return [problem for item in items if (problem := check_item(item, read, schemes)) is not None]


def receipt(item: str, read: Read, schemes: Mapping[str, Scheme]) -> str | None:
    """The `sourced` hash of an evidence item now, None when it cannot be found."""
    link = parse_link(item, schemes)
    if not isinstance(link, Link):
        return None
    text = read(link.path, link.rev)
    if text is None:
        return None
    return symbol_hash(text, link.fragment) if link.reads is Reader.SYMBOL else section_hash(text, link.fragment)


def symbol_hash(source: str, symbol: str) -> str | None:
    """Hash of a module-level def, class, assignment or type alias (`Class.member` below); None if absent."""
    return py_symbols.symbol_hash(source, symbol, length=HASH_LENGTH)


def section_hash(markdown: str, anchor: str) -> str | None:
    """Hash of the section under the heading with this GitHub anchor (to the next heading of the same or higher level)."""
    section = find(markdown, anchor, rows=github_outline(markdown))
    return None if section is None or section.level == 0 else digest_text(markdown[section.start : section.end].strip(), length=HASH_LENGTH)


def anchors(markdown: str) -> list[tuple[str, str, int]]:
    """(GitHub anchor, heading text, level) of every heading of a Markdown file, in order: what `doc:<commit>:<path>#<anchor>` may name."""
    return [(row.id, row.heading, row.level) for row in github_outline(markdown) if row.level > 0]
