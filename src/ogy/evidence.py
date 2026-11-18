"""Evidence items of `src`: `code:<path>#<symbol>` and `doc:<commit>:<path>#<anchor>`, checked and hashed.

A `doc:` link pins a Git revision: the file may be deleted later, its history stays."""

import re
from dataclasses import dataclass
from typing import Protocol

import py_symbols
from any_markdown import find, outline
from content_digest import digest_text

from ogy.model import Problem
from ogy.near import hint


class Reader(Protocol):
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
    scheme: str  # "code" or "doc"
    path: str
    fragment: str  # the symbol or the anchor
    rev: str | None = None  # the commit a `doc:` link is pinned to


def parse_link(item: str) -> Link | EvidenceProblem | None:
    """A `code:`/`doc:` item as a Link, a bad-src problem when malformed, None when it is another kind of item."""
    scheme, sep, rest = item.partition(":")
    if not sep or scheme not in ("code", "doc"):
        return None
    path, hash_sep, fragment = rest.partition("#")
    rev, pinned, tail = path.partition(":")
    if scheme == "doc":
        if not pinned or not _COMMIT.fullmatch(rev):
            return EvidenceProblem(Problem.BAD_SRC, item, "doc: pins a Git revision: doc:<commit>:<repo path>#<anchor>")
        path = tail
    if not path or not hash_sep or not fragment or path.startswith("/") or ".." in path.split("/"):
        return EvidenceProblem(Problem.BAD_SRC, item, f"{scheme}: needs <repo path>#<{'symbol' if scheme == 'code' else 'anchor'}>")
    return Link(scheme, path, fragment, rev if scheme == "doc" else None)


def check_item(item: str, read: Reader) -> EvidenceProblem | None:
    """The problem with one `src` item, or None."""
    link = parse_link(item)
    if isinstance(link, EvidenceProblem):
        return link
    if link is None:
        return EvidenceProblem(Problem.BAD_SRC, item, "src is code:<path>#<symbol> or doc:<commit>:<path>#<anchor>")
    text = read(link.path, link.rev)
    return _check_doc(item, link, text) if link.scheme == "doc" else _check_code(item, link, text)


def _check_doc(item: str, link: Link, text: str | None) -> EvidenceProblem | None:
    if text is None or not link.path.endswith(".md"):
        return EvidenceProblem(Problem.MISSING_DOC, item, f"no Markdown file {link.path} at {link.rev}")
    if section_hash(text, link.fragment) is None:
        near = hint(link.fragment, (anchor for anchor, _, _ in anchors(text)))
        return EvidenceProblem(Problem.MISSING_DOC, item, f"no heading with anchor {link.fragment} in {link.path}{near}"
                               + ("" if near else f"; `ogy anchors {link.path}` lists them"))
    return None


def _check_code(item: str, link: Link, text: str | None) -> EvidenceProblem | None:
    if not link.path.endswith(".py"):
        return EvidenceProblem(Problem.BAD_SRC, item, "code: links to Python files only")
    if text is None:
        return EvidenceProblem(Problem.MISSING_CODE, item, f"no file {link.path}")
    if symbol_hash(text, link.fragment) is None:
        return EvidenceProblem(Problem.MISSING_CODE, item, f"{link.path} does not define {link.fragment}")
    return None


def check_items(items: list[str], read: Reader) -> list[EvidenceProblem]:
    return [problem for item in items if (problem := check_item(item, read)) is not None]


def receipt(item: str, read: Reader) -> str | None:
    """The `sourced` hash of a `code:` or `doc:` item now, None when it cannot be found."""
    link = parse_link(item)
    if not isinstance(link, Link):
        return None
    text = read(link.path, link.rev)
    if text is None:
        return None
    return symbol_hash(text, link.fragment) if link.scheme == "code" else section_hash(text, link.fragment)


def symbol_hash(source: str, symbol: str) -> str | None:
    """Hash of a module-level def, class, assignment or type alias (`Class.member` below); None if absent."""
    return py_symbols.symbol_hash(source, symbol, length=HASH_LENGTH)


def section_hash(markdown: str, anchor: str) -> str | None:
    """Hash of the section under the heading with this GitHub anchor (to the next heading of the same or higher level)."""
    section = find(markdown, anchor, anchors="github")
    return None if section is None or section.level == 0 else digest_text(markdown[section.start : section.end].strip(), length=HASH_LENGTH)


def anchors(markdown: str) -> list[tuple[str, str, int]]:
    """(GitHub anchor, heading text, level) of every heading of a Markdown file, in order: what `doc:<commit>:<path>#<anchor>` may name."""
    return [(row.id, row.heading, row.level) for row in outline(markdown, anchors="github") if row.level > 0]
