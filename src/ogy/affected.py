"""Affected-file selection for the pre-commit hook (owner, decision check-every-commit): the check reads the knowledge base and the
files its `src` items cite, so a commit that changes none of them has nothing new to check and the hook does no work.

The cited paths are remembered per knowledge-base tree id in one small file inside the Git directory (nothing in the worktree): a
check that ran on a tree writes its paths, the next commit reads the file and asks Git one question (`git diff --cached --quiet`)
about those paths and the knowledge base. No file, or a file of another tree: the hook cannot tell and checks."""

import json
import os
from pathlib import Path

from atomic_io import atomic_write_text
from git_porcelain import RealRepo

from ogy.evidence import Link, parse_link
from ogy.model import link_values
lazy from ogy.snapshot import Snapshot

CACHE = "ogy-cited"


def cited_paths(snapshot: Snapshot) -> list[str]:
    """The repository files the entries cite as they are now (a pinned item names a past commit, so a change to the file is no
    change to it), sorted."""
    declared = snapshot.ontology.declared
    found: set[str] = set()
    for entry in snapshot.entries.values():
        for item in link_values(entry.fields.get(declared.roles.src)):
            link = parse_link(item, declared.evidence)
            if isinstance(link, Link) and link.rev is None:
                found.add(link.path)
    return sorted(found)


def _index_env() -> dict[str, str] | None:
    index = os.environ.get("GIT_INDEX_FILE")
    return {"GIT_INDEX_FILE": str(Path(index).absolute())} if index else None


def unaffected(repo: Path, kb: str) -> bool:
    """Whether the commit holds no change under the knowledge base or in a file it cites (two Git commands, one file read)."""
    git = RealRepo(repo, ambient=os.environ)
    asked = git.try_run(repo, "rev-parse", "--git-path", CACHE, f"HEAD:{kb}")
    where, _, tree = asked.out.strip().partition("\n")
    if asked.rc != 0 or not tree:
        return False
    try:
        known = json.loads((repo / where).read_text())
    except OSError, ValueError:
        return False
    if not isinstance(known, dict) or known.get("tree") != tree or not isinstance(known.get("paths"), list):
        return False
    paths = [str(path) for path in known["paths"]]
    done = git.try_run(repo, "--literal-pathspecs", "diff", "--cached", "--quiet", "--", kb, *paths, env=_index_env())
    return done.rc == 0


def remember(repo: Path, kb: str, rev: str, snapshot: Snapshot) -> None:
    """Keep the cited paths of the knowledge base the commit `rev` holds, under its tree id."""
    git = RealRepo(repo, ambient=os.environ)
    tree = git.try_run(repo, "rev-parse", f"{rev}:{kb}")
    where = git.try_run(repo, "rev-parse", "--git-path", CACHE)
    if tree.rc != 0 or where.rc != 0:
        return
    path = repo / where.out.strip()
    atomic_write_text(path, json.dumps({"tree": tree.out.strip(), "paths": cited_paths(snapshot)}))
