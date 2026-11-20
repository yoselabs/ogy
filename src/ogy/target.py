"""A knowledge base to read: its repository, commit and ontology (its folder is `docs/kb`); the merge base its checks compare
against: what has landed on the land branch `ogy.yml` names (`land`), as its remote holds it."""

import os
from dataclasses import dataclass, replace
lazy from pathlib import Path

from git_porcelain import GitError, MissingRevision, RealRepo, git_dir, head

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
        return head(repo, ambient=os.environ)
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


def landed(repo: Path) -> str:
    """What has landed: the land branch as its remote holds it, the one base every reader compares against (a check, the gate,
    a push of another branch, the removal base), so a removal and the land check never disagree. The land branch's upstream
    when it tracks a remote branch, else `origin/<land>`, else the local land branch (no remote: nothing else has landed). A
    push of the land branch itself is checked against the commit the remote held (`hooks.pushed`), the same commit when
    fetched. Refuses (NoLandError) when `ogy.yml` names no land branch."""
    land = config.land(repo)
    git = RealRepo(repo, ambient=os.environ)
    upstream = git.try_run(repo, "rev-parse", "-q", "--verify", "--symbolic-full-name", f"{land}@{{upstream}}")
    found = upstream.out.strip() if upstream.rc == 0 else ""
    if found.startswith("refs/remotes/"):
        return found
    origin = f"refs/remotes/origin/{land}"
    return origin if git.try_run(repo, "rev-parse", "-q", "--verify", f"{origin}^{{commit}}").rc == 0 else land


def merge_base(target: Target) -> str | None:
    """The commit the knowledge base is checked against: its merge base with what has landed (`landed`), None outside a Git
    repository (no history to compare with), when the branch does not exist, there is no history, or the commit is the base
    itself. Refuses (NoLandError) in a repository whose `ogy.yml` names no land branch: nothing is checked or recorded against
    a guessed base."""
    if git_dir(target.repo) is None:
        return None
    base = landed(target.repo)
    rev = "HEAD" if target.rev == "." else target.rev
    try:
        repo = RealRepo(target.repo, ambient=os.environ)
        found = repo.merge_base(rev, base)
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


def removal_source(target: Target) -> Source | None:
    """The knowledge base a removal is recorded against: at the merge base with what has landed (`landed`), else at HEAD (HEAD
    has landed); None before the first commit or when it holds no knowledge base."""
    here = target.at(".")
    try:
        older = open_source(here.repo, merge_base(here) or "HEAD", here.kb, required=False)
    except MissingTargetError:  # no commit yet: nothing was ever recorded
        return None
    return older if older.listing() else None


def removal_base(target: Target) -> frozenset[Address]:
    """What a removal is recorded against: the addresses of the knowledge base at `removal_source`, as written and as `ogy
    migrate` would write them. An entry it lacks was born since: Git keeps it, and no ledger item is written (`check --base`
    asks for one only for what the base had)."""
    older = removal_source(target)
    if older is None:
        return frozenset()
    written = load(older, target.kinds(), retyped=True)
    return frozenset(written.entries) | frozenset(migrated(written).entries)
