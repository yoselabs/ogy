"""R7 against the base: a removed item's snapshot is the entry in the base, or, when the branch changed the entry first, its
last version on the branch (base..the checked commit), read from Git history and never from the item's `last_seen`."""

from pathlib import Path

import any_yaml
from git_porcelain import run_git
from tests.conftest import IDENTITY, SOURCE, commit, ogy

from ogy import cli, ops
from ogy.model import Problem

BORROW = "product/app/capability/borrow"
CAPS = "docs/kb/product/app/capabilities.yml"
LEDGER = "docs/kb/product/app/removed.yml"


def _says(repo: Path, words: str) -> None:
    (repo / CAPS).write_text(f"- {{id: borrow, says: {words}, src: ['{SOURCE}']}}\n")


def _remove(repo: Path) -> None:
    assert ogy(repo, "--rev", ".", "remove", BORROW, "--why", "not needed")[0] == cli.OK


def _item_now(repo: Path) -> str:
    """The ledger an `ogy remove` writes in the worktree as it is, then the worktree put back."""
    _remove(repo)
    text = (repo / LEDGER).read_text()
    run_git(repo, "checkout", "-q", "--", ".")
    run_git(repo, "clean", "-qfd", "docs")
    return text


def _bad(repo: Path, base: str) -> set[str]:
    return {item.detail for item in ops.run_check(ops.Target(repo), base=base).value if item.problem.value == "bad-snapshot"}


def test_an_entry_changed_on_the_branch_then_removed_keeps_its_last_version(repo: Path) -> None:
    _says(repo, "A member can borrow.")
    base = commit(repo, "a capability")
    _says(repo, "A member may borrow.")
    commit(repo, "reworded")
    _remove(repo)
    assert ops.run_check(ops.Target(repo), base=base).value == []
    commit(repo, "removed")
    assert ops.run_check(ops.Target(repo, rev="HEAD"), base=base).value == []


def test_a_snapshot_from_before_the_base_is_refused(repo: Path) -> None:
    _says(repo, "A member can borrow.")
    commit(repo, "first words")
    older = _item_now(repo)
    _says(repo, "A member may borrow.")
    base = commit(repo, "the base changes it")
    _remove(repo)
    (repo / LEDGER).write_text(older)  # main's change would go unrecorded
    assert _bad(repo, base)


def test_a_forged_last_seen_and_a_side_branch_snapshot_are_refused(repo: Path) -> None:
    _says(repo, "A member can borrow.")
    base = commit(repo, "a capability")
    run_git(repo, *IDENTITY, "checkout", "-q", "-b", "side")
    _says(repo, "A member borrows on the side.")
    side = commit(repo, "side words")
    sided = _item_now(repo)
    run_git(repo, *IDENTITY, "checkout", "-q", "main")
    _remove(repo)
    (repo / LEDGER).write_text(sided)
    assert _bad(repo, base)  # a commit on another branch is no version of this branch
    ledger = any_yaml.load(sided)
    assert isinstance(ledger, dict) and ledger["items"][0]["last_seen"] == side
    forged = sided.replace(side, run_git(repo, "rev-parse", "HEAD").strip())
    (repo / LEDGER).write_text(forged)
    assert _bad(repo, base)  # the field is never trusted


def test_an_entry_the_base_never_had_is_refused(repo: Path) -> None:
    base = run_git(repo, "rev-parse", "HEAD").strip()
    _says(repo, "A member can borrow.")
    commit(repo, "added on the branch")
    _remove(repo)
    found = {(item.problem, item.detail) for item in ops.run_check(ops.Target(repo), base=base).value}
    assert any(problem is Problem.BAD_SNAPSHOT and "no entry" in detail for problem, detail in found)
