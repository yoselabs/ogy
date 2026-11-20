"""One verdict on every result: exit codes, refusals on stderr, and a target that fails closed."""

lazy from pathlib import Path

import pytest
from git_porcelain import run_git
from tests.conftest import IDENTITY, commit, ogy

from ogy import cli, ops
from ogy.verdict import Verdict


def test_the_verdicts_are_the_exit_codes() -> None:
    assert [int(item) for item in Verdict] == [0, 1, 2, 3, 4]
    assert tuple(Verdict) == (cli.OK, cli.FINDINGS, cli.USAGE, cli.REFUSED, cli.NOT_FOUND)


def test_every_op_result_carries_its_verdict(repo: Path) -> None:
    target = ops.Target(repo)
    assert ops.run_check(target).verdict is Verdict.OK
    assert ops.run_work(target).verdict is Verdict.FINDINGS
    assert ops.run_show(target, "product/app/quantity/fee").verdict is Verdict.OK
    with pytest.raises(ops.UnknownEntryError) as error:
        ops.run_show(target, "product/app/quantity/nope")
    assert error.value.verdict is Verdict.NOT_FOUND


def test_a_missing_knowledge_base_folder_is_a_refusal_not_a_green_check(repo: Path) -> None:
    empty = repo.with_name(repo.name + "-empty")
    empty.mkdir()
    run_git(empty, "init", "-q", "-b", "main")
    run_git(empty, *IDENTITY, "commit", "--allow-empty", "-qm", "nothing")
    code, lines = ogy(empty, "check")
    assert code == cli.REFUSED and len(lines) == 1 and "no knowledge-base folder docs/kb/" in lines[0]
    code, lines = ogy(empty, "--rev", "HEAD", "glossary")
    assert code == cli.REFUSED and "--rev . reads the worktree" in lines[0]


def test_an_unknown_revision_is_a_one_line_refusal(repo: Path) -> None:
    for command in (["check"], ["glossary"], ["find", "x"], ["history", "app"]):
        code, lines = ogy(repo, "--rev", "nosuchrev", *command)
        assert code == cli.REFUSED and len(lines) == 1 and "no revision 'nosuchrev'" in lines[0], (command, lines)
    code, lines = ogy(repo, "diff", "nosuchrev", ".")
    assert code == cli.REFUSED and len(lines) == 1


def test_a_diff_may_start_before_the_knowledge_base_existed(repo: Path) -> None:
    (repo / "docs/kb").rename(repo / "kept")
    commit(repo, "without a knowledge base")
    (repo / "kept").rename(repo / "docs/kb")
    assert ogy(repo, "diff", "HEAD", ".")[0] == cli.OK  # no such folder at HEAD: everything is new
    (repo / "docs/kb").rename(repo / "kept")
    assert ogy(repo, "diff", "HEAD", ".")[0] == cli.REFUSED  # none in the worktree: a typo


def test_reads_default_to_the_worktree_and_say_so(repo: Path) -> None:
    (repo / "docs/kb/product/app/quantities.yml").write_text(
        "- {id: fee, says: The fee., is: 9, unit: EUR, src: [product/app/message/m1]}\n"
    )
    assert "is: 9" in "\n".join(ogy(repo, "show", "product/app/quantity/fee")[1])
    assert "is: 2" in "\n".join(ogy(repo, "--rev", "HEAD", "show", "product/app/quantity/fee")[1])
    assert "the worktree" in cli.parser().format_help()


def test_main_prints_refusals_to_stderr_and_returns_the_code(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def run(*argv: str) -> tuple[int, str, str]:
        code = cli.main(["--repo", str(repo), *argv])
        out = capsys.readouterr()
        return code, out.out, out.err

    repo.with_name(repo.name + "-empty").mkdir()
    code, out, err = run("--repo", str(repo.with_name(repo.name + "-empty")), "check")  # a later --repo wins
    assert code == 3 and out == "" and "no knowledge-base folder" in err and "Traceback" not in err
    code, out, err = run("show", "product/app/quantity/none")
    assert code == 4 and out == "" and "no entry product/app/quantity/none" in err
    code, out, err = run("work")
    assert code == 1 and "unbuilt" in out and err == ""
    with pytest.raises(SystemExit) as usage:
        run("check", "--bogus")
    assert usage.value.code == 2


def test_a_base_without_a_knowledge_base_has_nothing_to_compare(repo: Path) -> None:
    (repo / "docs/kb").rename(repo / "kept")
    base = commit(repo, "without a knowledge base")
    (repo / "kept").rename(repo / "docs/kb")
    (repo / "docs/kb/constitution").mkdir(exist_ok=True)
    (repo / "docs/kb/constitution/removed.yml").write_text("format: 1\nitems: []\n")
    assert ogy(repo, "--rev", ".", "check", "--base", base)[0] == cli.OK
