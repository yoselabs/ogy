"""A knowledge base to read: its repository, commit and ontology (its folder is `docs/kb`); the merge base its checks compare against."""

from dataclasses import dataclass, replace
lazy from pathlib import Path

from git_porcelain import GitError, RealRepo

from ogy.check import check
from ogy.ontology import DEFAULT_ONTOLOGY, Ontology, named
from ogy.snapshot import Snapshot, load
from ogy.source import KB_DIR, Source, open_source
lazy from ogy.model import Finding


@dataclass(frozen=True)
class Target:
    """A knowledge base: a repository, a commit or `.` for the worktree, and its ontology. The folder is `KB_DIR`: no flag or
    setting moves it (tests of the readers name another one)."""

    repo: Path
    kb: str = KB_DIR
    rev: str = "."
    ontology: str = DEFAULT_ONTOLOGY

    def at(self, rev: str) -> Target:
        return replace(self, rev=rev)

    def kinds(self) -> Ontology:
        return named(self.ontology, self.repo)

    def read(self) -> tuple[Source, Snapshot]:
        source = open_source(self.repo, self.rev, self.kb)
        return source, load(source, self.kinds())


def merge_base(target: Target) -> str | None:
    """The commit the knowledge base is checked against: its merge base with `main`, None when there is no `main` or no history."""
    rev = "HEAD" if target.rev == "." else target.rev
    try:
        repo = RealRepo(target.repo)
        found = repo.merge_base(rev, "main")
        return None if found is None or found == repo.commit(rev) else str(found)
    except GitError, ValueError:
        return None


def worktree_findings(target: Target) -> list[Finding]:
    """Every check on the worktree, against the merge base with `main` when there is one."""
    here = target.at(".")
    source, snapshot = here.read()
    found = merge_base(here)
    older = open_source(here.repo, found, here.kb, required=False) if found else None
    return check(
        snapshot,
        source,
        older if older is not None and older.listing() else None,  # none at the base: nothing to compare
        product=here.repo.resolve().name,
    )
