"""What has landed: the base a removal is recorded against and the base a land is checked against are one, the land branch
as the remote holds it (`target.landed`), so a part born and dropped on an unpushed land branch leaves no ledger item."""

import io
import json
lazy from pathlib import Path

import pytest
from git_porcelain import run_git
from tests.conftest import commit, ogy

from ogy import cli

CHOICES = "product/app/workflow/borrow/step/ask"
SKIP = f"{CHOICES}/choice/skip"
GO = {"label": "Borrow", "then": "done", "effects": [{"do": "tell", "on": "product/app/actor/member"}]}


def w(repo: Path, *argv: str) -> tuple[int, list[str]]:
    return ogy(repo, "--rev", ".", *argv)


def agreed(repo: Path) -> None:
    round_id = w(repo, "review")[1][0].split()[-1]
    code, lines = w(repo, "reply", "yes all", "--said", "Agreed to all", "--where", "ai:claude/1", "--round", round_id)
    assert code == cli.OK, lines
    commit(repo, "agreed")


@pytest.fixture
def pushed(repo: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The repository with every entry agreed and pushed to a remote, so main and origin/main hold the same commit."""
    agreed(repo)
    remote = tmp_path_factory.mktemp("remote") / "kb.git"
    run_git(repo, "clone", "-q", "--bare", str(repo), str(remote))
    run_git(repo, "remote", "add", "origin", str(remote))
    run_git(repo, "fetch", "-q", "origin")
    run_git(repo, "branch", "-q", "--set-upstream-to", "origin/main", "main")
    return repo


def test_a_part_born_and_dropped_on_unpushed_main_leaves_no_item_and_lands(pushed: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The owner's push of main, refused with `bad-snapshot`: a part added in a local commit on main and dropped in the next
    was recorded, because the removal base was local main; the land check compares with origin's main, which never had it."""
    old = run_git(pushed, "rev-parse", "origin/main").strip()
    skip = {"label": "Skip", "then": "done"}
    code, lines = w(pushed, "put", json.dumps({"address": CHOICES, "choices": {"go": GO, "skip": skip}}))
    assert code == cli.OK, lines
    agreed(pushed)
    code, lines = w(pushed, "put", json.dumps({"address": CHOICES, "choices": {"go": GO}}), "--why", "No skipping")
    assert code == cli.OK, lines
    assert not (pushed / "docs/kb/product/app/removed.yml").exists()
    agreed(pushed)
    new = run_git(pushed, "rev-parse", "HEAD").strip()
    monkeypatch.setattr("sys.stdin", io.StringIO(f"refs/heads/main {new} refs/heads/main {old}\n"))
    code, lines = ogy(pushed, "hook", "pre-push")
    assert code == cli.OK, lines


def choices(repo: Path, *keys: str, why: str | None = None) -> None:
    given = {"go": GO, **{key: {"label": key.title(), "then": "done"} for key in keys}}
    code, lines = w(repo, "put", json.dumps({"address": CHOICES, "choices": given}), *(("--why", why) if why else ()))
    assert code == cli.OK, lines


def test_migrate_drops_an_item_the_base_never_had_and_keeps_the_others(pushed: Path) -> None:
    """The item the old removal base (local main) wrote goes on the next `ogy migrate`, printed: no removal writes it now. The
    item for a part the base had stays, and stays once it has landed too."""
    choices(pushed, "keep")
    agreed(pushed)
    landed = run_git(pushed, "rev-parse", "HEAD").strip()
    run_git(pushed, "update-ref", "refs/remotes/origin/main", landed)  # keep has landed
    choices(pushed, "keep", "skip")
    agreed(pushed)
    run_git(pushed, "branch", "-q", "--unset-upstream", "main")
    run_git(pushed, "update-ref", "-d", "refs/remotes/origin/main")  # the base as it was: local main
    choices(pushed, why="Neither")
    ledger = pushed / "docs/kb/product/app/removed.yml"
    assert "choice/skip" in ledger.read_text() and "choice/keep" in ledger.read_text()
    run_git(pushed, "update-ref", "refs/remotes/origin/main", landed)
    code, lines = w(pushed, "migrate")
    assert code == cli.OK and lines == [f"dropped the removed item {SKIP}: the base never had it (Git keeps it)"], lines
    assert "choice/skip" not in ledger.read_text() and "choice/keep" in ledger.read_text()
    assert w(pushed, "check")[0] == cli.OK
    assert w(pushed, "migrate")[1] == ["nothing to migrate"]
    run_git(pushed, "update-ref", "refs/remotes/origin/main", commit(pushed, "neither"))  # landed: the base's ledger holds keep
    assert w(pushed, "migrate")[1] == ["nothing to migrate"]  # an item the base's ledger holds stays, its entry long gone
