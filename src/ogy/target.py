"""A knowledge base to read: its repository, commit and ontology (its folder is `docs/kb`); the merge base its checks compare
against, with the land branch `ogy.yml` names (`land`)."""

from dataclasses import dataclass, replace
lazy from pathlib import Path

from git_porcelain import GitError, MissingRevision, RealRepo, head

from ogy import config
from ogy.check import check
from ogy.kindchange import migrated
from ogy.ontology import DEFAULT_ONTOLOGY, Ontology, named
from ogy.snapshot import Snapshot, load
from ogy.source import KB_DIR, Source, open_source
from ogy.verdict import MissingTargetError
lazy from ogy.model import Address, Finding

NO_COMMIT = "0" * 40  # what a removal made before the first commit last saw


def last_seen(repo: Path) -> str:
    """The commit a removal was made on (a removed item's `last_seen`): HEAD, or NO_COMMIT before the first commit."""
    try:
        return head(repo)
    except MissingRevision:
        return NO_COMMIT


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
    """The commit the knowledge base is checked against: its merge base with the land branch, None when `ogy.yml` names none
    (`ogy init --check` says so), the branch does not exist or there is no history."""
    rev = "HEAD" if target.rev == "." else target.rev
    land = config.read(target.repo).land
    if land is None:
        return None
    try:
        repo = RealRepo(target.repo)
        found = repo.merge_base(rev, land)
        return None if found is None or found == repo.commit(rev) else str(found)
    except GitError, ValueError:
        return None


def worktree_findings(target: Target) -> list[Finding]:
    """Every check on the worktree, against the merge base with the land branch when there is one."""
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


def removal_base(target: Target) -> frozenset[Address]:
    """What a removal is recorded against: the addresses of the knowledge base at the merge base with the land branch, else at HEAD
    (on the land branch itself), as written and as `ogy migrate` would write them; none before the first commit. An entry it lacks was born
    since: Git keeps it, and no ledger item is written (`check --base` asks for one only for what the base had)."""
    here = target.at(".")
    try:
        older = open_source(here.repo, merge_base(here) or "HEAD", here.kb, required=False)
    except MissingTargetError:  # no commit yet: nothing was ever recorded
        return frozenset()
    if not older.listing():
        return frozenset()
    written = load(older, here.kinds(), retyped=True)
    return frozenset(written.entries) | frozenset(migrated(written).entries)
