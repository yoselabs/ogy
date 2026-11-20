"""Read a knowledge base from a Git commit (git-porcelain: one tree listing, one batch read) or from the worktree, counting files read."""

from typing import Protocol
lazy from collections.abc import Iterable
lazy from pathlib import Path

from git_porcelain import GitError, MissingRevision, RealRepo, Tree, worktree_tree

from ogy.verdict import MissingTargetError

WORKTREE = "."
KB_DIR = "docs/kb"  # where the knowledge base lives in every repository


class Source(Protocol):
    """One snapshot of a repository: its knowledge-base files and any repository file a proof names."""

    kb: str
    reads: int

    def describe(self) -> str: ...

    def tree_id(self) -> str | None:
        """An id equal for equal knowledge-base content (Git's tree hash), None when unknown."""
        ...

    def listing(self) -> dict[str, str]:
        """`{kb-relative path: blob id}` for every file under the knowledge base."""
        ...

    def read(self, paths: Iterable[str], /) -> dict[str, str]:
        """The text of knowledge-base files; each one read counts once."""
        ...

    def repo_file(self, path: str, rev: str | None = None) -> str | None:
        """A repository-relative file's text (at the commit `rev` when given, else at this snapshot), or None when it does not exist."""
        ...


def _at(repo: Path, rev: str, path: str) -> str | None:
    """A file's text at a commit, None when the commit or the file does not exist."""
    try:
        tree = RealRepo(repo).tree(rev)
        data = None if tree is None else tree.read(path)
    except GitError:
        return None
    return None if data is None else data.decode()


class _TreeSource:
    """Knowledge-base files read through a git-porcelain `Tree`: one listing, then one batch for the files wanted."""

    def __init__(self, kb: str, tree: Tree | None) -> None:
        self.kb = kb
        self.reads = 0
        self._kb = tree
        self._texts: dict[str, str] = {}

    @property
    def present(self) -> bool:
        return self._kb is not None

    def listing(self) -> dict[str, str]:
        return {} if self._kb is None else {path: str(sha) for path, (_, sha) in self._kb.files.items()}

    def read(self, paths: Iterable[str]) -> dict[str, str]:
        wanted = sorted(set(paths))
        fresh = [path for path in wanted if path not in self._texts]
        if self._kb is not None and fresh:
            self.reads += len(fresh)
            self._texts |= {path: data.decode(errors="replace") for path, data in self._kb.read_many(fresh).items() if data is not None}
        return {path: self._texts[path] for path in wanted if path in self._texts}


class GitSource(_TreeSource):
    """A commit's knowledge base, read from the object store."""

    def __init__(self, repo: Path, rev: str, kb: str) -> None:
        self.repo = repo
        self.rev = str(RealRepo(repo).commit(rev))
        self._git = RealRepo(repo)
        super().__init__(kb, self._git.tree(f"{self.rev}:{kb}"))
        self._commit: Tree | None = None

    def describe(self) -> str:
        return self.rev[:12]

    def tree_id(self) -> str | None:
        return None if self._kb is None else str(self._kb.sha)

    def repo_file(self, path: str, rev: str | None = None) -> str | None:
        self.reads += 1
        if rev is not None:
            return _at(self.repo, rev, path)
        if self._commit is None:
            self._commit = self._git.tree(self.rev)
        data = self._commit.read(path) if self._commit is not None else None
        return None if data is None else data.decode()


class WorktreeSource(_TreeSource):
    """The files on disk, including uncommitted edits."""

    def __init__(self, root: Path, kb: str) -> None:
        self.root = root
        super().__init__(kb, worktree_tree(root, kb))

    def describe(self) -> str:
        return "worktree"

    def tree_id(self) -> str | None:
        return None

    def repo_file(self, path: str, rev: str | None = None) -> str | None:
        if rev is not None:
            self.reads += 1
            return _at(self.root, rev, path)
        target = self.root / path
        if not target.is_file():
            return None
        self.reads += 1
        return target.read_text()


def open_source(repo: Path, rev: str, kb: str, *, required: bool = True) -> Source:
    """A commit's snapshot, or the worktree for `.`. Refuses (MissingTargetError) an unknown commit, and, when `required`, a
    knowledge-base folder that is not there: an empty answer for a typo would read as a green check."""
    try:
        found: GitSource | WorktreeSource = WorktreeSource(repo, kb) if rev == WORKTREE else GitSource(repo, rev, kb)
    except MissingRevision as error:
        msg = f"no revision {rev!r} in {repo}: name a commit, or . for the worktree"
        raise MissingTargetError(msg) from error
    except GitError as error:
        msg = f"{repo} cannot be read at {rev!r}: {str(error).splitlines()[0]}"
        raise MissingTargetError(msg) from error
    if required and not found.present:
        where = "the worktree" if rev == WORKTREE else f"revision {rev}"
        hint = "" if rev == WORKTREE else "; --rev . reads the worktree"
        msg = f"no knowledge-base folder {kb or '.'}/ in {where}{hint}"
        raise MissingTargetError(msg)
    return found
