"""`ogy hook`: the one entry point every Git hook calls; it decides from the ref being updated whether the update is a land."""

import io
lazy from pathlib import Path

import pytest
from git_porcelain import run_git
from tests.conftest import IDENTITY

from ogy import cli
from ogy.mcp_server import NO_TOOL

ZERO = "0" * 40


@pytest.fixture
def fresh(tmp_path: Path) -> Path:
    """A repository `ogy init` just set up: its starting principle waits for the owner's yes, so it is not ready to land."""
    run_git(tmp_path, "init", "-q", "-b", "main")
    assert cli.run(["--repo", str(tmp_path), "init"])[0] == cli.OK
    run_git(tmp_path, "add", "-A")
    return tmp_path


def hook(repo: Path, monkeypatch: pytest.MonkeyPatch, name: str, stdin: str = "") -> tuple[int, list[str]]:
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    return cli.run(["--repo", str(repo), "hook", name])


def first_commit(repo: Path) -> str:
    run_git(repo, *IDENTITY, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "init")
    return run_git(repo, "rev-parse", "HEAD").strip()


def test_a_fresh_repository_makes_its_first_commit_on_main(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A commit is never a land: the owner agrees in review before the first push to main, not before the first commit."""
    code, lines = hook(fresh, monkeypatch, "pre-commit")
    assert code == cli.OK, lines
    assert not any("term-not-agreed" in line for line in lines)


def test_the_pre_commit_check_reads_the_staged_tree(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    broken = fresh / "docs/kb/product/shared/actors.yml"
    broken.write_text(broken.read_text() + "- {id: ghost, nature: robot, says: A ghost.}\n")
    assert hook(fresh, monkeypatch, "pre-commit")[0] == cli.OK  # unstaged: the commit does not hold it
    run_git(fresh, "add", "-A")
    code, lines = hook(fresh, monkeypatch, "pre-commit")
    assert code == cli.FINDINGS and any("ghost" in line for line in lines), lines


def test_a_push_to_main_lands_and_runs_the_landing_checks(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sha = first_commit(fresh)
    code, lines = hook(fresh, monkeypatch, "pre-push", f"refs/heads/main {sha} refs/heads/main {ZERO}\n")
    assert code == cli.FINDINGS and any("term-not-agreed" in line for line in lines), lines
    assert any(line.startswith("land refs/heads/main") for line in lines), lines


def test_a_push_of_another_branch_is_no_land(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sha = first_commit(fresh)
    code, lines = hook(fresh, monkeypatch, "pre-push", f"refs/heads/later {sha} refs/heads/later {ZERO}\n")
    assert code == cli.OK and not any("term-not-agreed" in line for line in lines), lines
    code, lines = hook(fresh, monkeypatch, "pre-push", f"refs/heads/main {sha} refs/heads/feature/main {ZERO}\n")
    assert code == cli.OK, lines  # the remote ref decides, not the local one


def test_a_deletion_and_a_tag_check_nothing(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sha = first_commit(fresh)
    lines = f"(delete) {ZERO} refs/heads/main {sha}\nrefs/tags/v1 {sha} refs/tags/v1 {ZERO}\n"
    assert hook(fresh, monkeypatch, "pre-push", lines) == (cli.OK, [])


def test_every_ref_of_a_push_is_decided_on_its_own(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sha = first_commit(fresh)
    text = f"refs/heads/later {sha} refs/heads/later {ZERO}\nrefs/heads/main {sha} refs/heads/main {ZERO}\n"
    code, lines = hook(fresh, monkeypatch, "pre-push", text)
    assert code == cli.FINDINGS and [line.split()[0] for line in lines if line.startswith(("land ", "check "))] == ["check", "land"]


def test_the_hooks_init_writes_call_the_one_entry_point(fresh: Path) -> None:
    for name in ("pre-commit", "pre-push"):
        text = (fresh / ".githooks" / name).read_text()
        assert f'hook {name} "$@"' in text and "--landing" not in text and "write-tree" not in text, text
        assert (fresh / ".githooks" / name).stat().st_mode & 0o111
    lines = cli.run(["--repo", str(fresh), "init", "--check"])[1]
    assert lines == ["ogy is set up here"], lines
    (fresh / ".githooks/pre-push").unlink()
    assert any("pre-push" in line for line in cli.run(["--repo", str(fresh), "init", "--check"])[1])


def test_hook_is_no_mcp_tool() -> None:
    assert "hook" in NO_TOOL


def test_the_gate_lands_with_main_checked_out_and_not_on_a_branch(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first_commit(fresh)
    code, lines = hook(fresh, monkeypatch, "gate")
    assert code == cli.FINDINGS and lines[0] == "land refs/heads/main at ." and any("term-not-agreed" in line for line in lines)
    run_git(fresh, "switch", "-q", "-c", "later")
    assert hook(fresh, monkeypatch, "gate") == (cli.OK, ["check refs/heads/later at .", "ok"])
