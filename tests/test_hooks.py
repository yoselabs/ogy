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
    assert cli.run(["--repo", str(tmp_path), "init", "--land", "main"])[0] == cli.OK
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


def test_a_branch_push_checks_against_the_merge_base_like_a_removal(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An entry born on a branch and pushed, then removed there: the removal records nothing (the merge base never had it), so
    the next push of the branch is checked against the merge base too, not the commit the remote branch held."""
    sha = first_commit(fresh)
    run_git(fresh, "switch", "-q", "-c", "later")
    actors = fresh / "docs/kb/product/shared/actors.yml"
    actors.write_text(actors.read_text() + "- {id: clerk, nature: human, says: A clerk at the desk.}\n")
    run_git(fresh, "add", "-A")
    pushed = first_commit(fresh)
    code, lines = cli.run(["--repo", str(fresh), "--rev", ".", "remove", "product/shared/actor/clerk", "--why", "No clerks"])
    assert code == cli.OK, lines
    run_git(fresh, "add", "-A")
    now = first_commit(fresh)
    code, lines = hook(fresh, monkeypatch, "pre-push", f"refs/heads/later {now} refs/heads/later {pushed}\n")
    assert code == cli.OK, lines
    code, lines = hook(fresh, monkeypatch, "pre-push", f"refs/heads/later {now} refs/heads/main {sha}\n")
    assert code == cli.FINDINGS and any("term-not-agreed" in line for line in lines), lines  # a half-finished land is refused


def test_a_land_is_checked_against_the_commit_main_held(fresh: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    actors = fresh / "docs/kb/product/shared/actors.yml"
    before = actors.read_text()
    actors.write_text(before + "- {id: clerk, nature: human, says: A clerk at the desk.}\n")
    run_git(fresh, "add", "-A")
    old = first_commit(fresh)
    actors.write_text(before)  # gone by hand, no removed.yml item
    run_git(fresh, "add", "-A")
    new = first_commit(fresh)
    code, lines = hook(fresh, monkeypatch, "pre-push", f"refs/heads/main {new} refs/heads/main {old}\n")
    assert code == cli.FINDINGS and any("removed-unrecorded" in line and "clerk" in line for line in lines), lines


def test_ogys_own_push_runs_the_landing_hook_outside_the_gate_record() -> None:
    """Fable's second review, problem 3: any-gate skips `just check` for a tree that already passed, so `git push origin HEAD:main`
    would skip the landing check; ogy's own pre-push runs `ogy hook pre-push` (`just kb`) before any-gate decides. blueprint
    allows no second pre-push hook, so it is the first command of the gate hook's entry."""
    text = (Path(__file__).parent.parent / ".pre-commit-config.yaml").read_text()
    gate = [line for line in text.splitlines() if line.lstrip().startswith("entry:") and "any_gate pre-push" in line]
    assert len(gate) == 1 and "just kb && " in gate[0] and gate[0].index("just kb") < gate[0].index("any_gate"), gate


def test_the_land_branch_is_the_one_ogy_yml_names(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fable's second review, problem 4: `ogy init` records the land branch, and the hooks read it; no `main` is assumed."""
    run_git(tmp_path, "init", "-q", "-b", "trunk")
    assert cli.run(["--repo", str(tmp_path), "init", "--land", "trunk"])[0] == cli.OK
    assert "land: trunk" in (tmp_path / "ogy.yml").read_text()
    run_git(tmp_path, "add", "-A")
    sha = first_commit(tmp_path)
    code, lines = hook(tmp_path, monkeypatch, "pre-push", f"refs/heads/trunk {sha} refs/heads/trunk {ZERO}\n")
    assert code == cli.FINDINGS and lines[0].startswith("land refs/heads/trunk"), lines
    assert hook(tmp_path, monkeypatch, "pre-push", f"refs/heads/trunk {sha} refs/heads/main {ZERO}\n")[0] == cli.OK
    (tmp_path / "ogy.yml").write_text("ontology: software\n")
    for name in ("pre-push", "gate"):
        code, lines = hook(tmp_path, monkeypatch, name, f"refs/heads/trunk {sha} refs/heads/trunk {ZERO}\n")
        assert code == cli.USAGE and lines == ["ogy.yml names no land branch (`land:`): run `ogy init`"], lines
