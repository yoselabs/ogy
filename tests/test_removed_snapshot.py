"""R7 against the base: a removed item's snapshot is the entry in the base, or, when the branch changed the entry first, its
last version on the branch (base..the checked commit), read from Git history and never from the item's `last_seen`."""

lazy from pathlib import Path

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


def test_an_entry_born_on_the_branch_leaves_no_item_and_the_base_still_guards_its_own(repo: Path) -> None:
    """Fable's blocker 3: what the base never had is removed without a ledger item (Git keeps it), by `remove` and by a
    `put` that drops it; what the base had still needs one."""
    run_git(repo, "checkout", "-q", "-b", "later")
    _says(repo, "A member can borrow.")
    commit(repo, "a capability born on the branch")
    code, lines = ogy(repo, "--rev", ".", "remove", BORROW, "--why", "written by mistake")
    assert code == cli.OK and "not recorded" in lines[0], lines
    assert not (repo / LEDGER).exists() and not ops.run_check(ops.Target(repo)).value
    run_git(repo, "checkout", "-q", "--", ".")
    step = "product/app/workflow/borrow/step/ask"
    assert ogy(repo, "put", f'{{"address": "{step}/choice/skip", "label": "Skip", "then": "done"}}')[0] == cli.OK
    commit(repo, "a choice born on the branch")
    assert ogy(repo, "put", f'{{"address": "{step}", "choices": {{"go": {{"label": "Borrow", "then": "done"}}}}}}')[0] == cli.OK
    assert not (repo / LEDGER).exists() and not ops.run_check(ops.Target(repo)).value
    (repo / "docs/kb/software/app/handler/lend.yml").unlink()  # the base had it: deleted by hand, it is caught
    assert ("removed-unrecorded", "software/app/handler/lend") in {
        (item.problem.value, str(item.address)) for item in ops.run_check(ops.Target(repo)).value
    }


def test_a_typo_never_committed_on_main_does_not_burn_its_id(repo: Path) -> None:
    _says(repo, "A member can borrow.")
    _remove(repo)
    assert not (repo / LEDGER).exists()
    _says(repo, "A member can borrow a tool.")
    assert not ops.run_check(ops.Target(repo), base="HEAD").value
