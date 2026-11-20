"""`ogy hook`: what a Git hook (or a repository's gate) checks, and the one decision "is this a land", made from the ref being
updated.

Every hook calls this entry point (ogy's own through prek and its gate, and the ones `ogy init` writes), so no hook copy decides
it alone. A land is an update of the main branch: a push whose remote ref is `refs/heads/main` (checked against the commit main
held there; any other pushed branch against its merge base with main, as a removal is recorded), or the gate run with main
checked out. A land gets `check --landing`; any other update the plain check. A commit is never a land: a merge into main runs
no pre-commit hook, so the push is where a land is caught, and a fresh repository's starting entries wait for the owner's yes
in review, which comes before its first push to main, not before its first commit."""

import os
from dataclasses import dataclass
lazy from pathlib import Path

from git_porcelain import RealRepo

from ogy.target import MAIN

LAND = f"refs/heads/{MAIN}"
BRANCHES = "refs/heads/"
STAGED = {"GIT_AUTHOR_NAME": "ogy hook", "GIT_AUTHOR_EMAIL": "ogy", "GIT_COMMITTER_NAME": "ogy hook", "GIT_COMMITTER_EMAIL": "ogy"}


@dataclass(frozen=True)
class Update:
    """A ref a hook guards, the commit it will hold, the commit to check against (None: the merge base with main) and whether
    the update lands."""

    ref: str
    rev: str
    base: str | None
    land: bool


def _zero(sha: str) -> bool:
    return set(sha) == {"0"}


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    """git's answer, stripped; empty when it says no (`-q` reads)."""
    done = RealRepo(repo).run(repo, *args, check=False, env=env)
    return done.out.strip() if done.rc == 0 else ""


def staged(repo: Path) -> Update:
    """pre-commit: a throwaway commit of the index (the one `git commit` writes from, `GIT_INDEX_FILE` in a hook), on HEAD."""
    index = os.environ.get("GIT_INDEX_FILE")
    env = {"GIT_INDEX_FILE": str(Path(index).absolute())} if index else {}
    git = RealRepo(repo)
    tree = git.run(repo, "write-tree", env=env).out.strip()
    parent = _git(repo, "rev-parse", "-q", "--verify", "HEAD")
    rev = git.run(repo, "commit-tree", tree, *(("-p", parent) if parent else ()), "-m", "staged", env=STAGED).out.strip()
    branch = _git(repo, "symbolic-ref", "-q", "HEAD")
    return Update(branch or "HEAD", rev, None, land=False)


def checked_out(repo: Path) -> Update:
    """The gate: the worktree, as an update of the branch checked out."""
    branch = _git(repo, "symbolic-ref", "-q", "HEAD")
    return Update(branch or "HEAD", ".", None, land=branch == LAND)


def pushed(repo: Path, text: str) -> list[Update]:
    """pre-push: one update per line of `<local ref> <local sha> <remote ref> <remote sha>` that pushes a branch; a deletion
    and a tag check nothing. Only the remote ref decides a land. A land is checked against the commit main held there; any
    other branch against its merge base with main, the base a removal is recorded against (`removal_base`), so a branch that
    removed an entry it was born with is not refused for the copy the remote branch still holds."""
    found: list[Update] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        _, sha, remote, old = parts
        if _zero(sha) or not remote.startswith(BRANCHES):
            continue
        land = remote == LAND
        known = not _zero(old) and bool(_git(repo, "rev-parse", "-q", "--verify", f"{old}^{{commit}}"))
        found.append(Update(remote, sha, old if known and land else None, land=land))
    return found
