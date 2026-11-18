"""The CLI and library calls over a small knowledge base kept in Git."""

from pathlib import Path

from tests.conftest import commit, ogy

from ogy import cli, ops
from ogy.semdiff import Change


def test_show_prints_parent_links_and_referrers(repo: Path) -> None:
    code, lines = ogy(repo, "show", "product/app/workflow/borrow/step/ask/choice/go")
    assert code == cli.OK
    assert "parent: product/app/workflow/borrow/step/ask" in lines and "parent: product/app/workflow/borrow" in lines
    assert "links then -> product/app/workflow/borrow/end/done" in lines
    assert "links on -> product/app/actor/member" in lines
    assert "referenced by software/app/operation/lend (performs)" in lines


def test_show_of_a_workflow_lists_its_parts(repo: Path) -> None:
    _, lines = ogy(repo, "show", "product/app/workflow/borrow")
    assert {"part: product/app/workflow/borrow/step/ask", "part: product/app/workflow/borrow/end/done"} <= set(lines)


def test_impact_lists_the_closure(repo: Path) -> None:
    code, lines = ogy(repo, "impact", "product/app/value/fee")
    assert code == cli.OK and "reached by product/app/workflow/borrow/step/ask/timeout" in lines
    code, lines = ogy(repo, "impact", "product/app/workflow/borrow/step/ask/choice/go")
    assert {"reaches product/app/workflow/borrow/end/done", "reaches product/app/workflow/borrow", "reaches product/app/actor/member",
            "reached by software/app/operation/lend"} <= set(lines)


def test_work_and_check_exit_codes(repo: Path) -> None:
    code, lines = ogy(repo, "work")
    assert code == cli.FINDINGS and any(line.startswith("unbuilt: software/app/operation/lend") for line in lines)
    assert not any("product/app/actor" in line for line in lines)
    assert ogy(repo, "check") == (cli.OK, ["ok"])
    assert ogy(repo, "show", "product/app/value/none")[0] == cli.NOT_FOUND
    assert ogy(repo, "show", "value/fee")[0] == cli.NOT_FOUND
    assert ogy(repo, "--ontology", "nothing", "check")[0] == cli.USAGE


def test_worktree_edits_are_seen_before_commit(repo: Path) -> None:
    path = repo / "docs/kb/product/app/values.yml"
    path.write_text(path.read_text().replace("is: 2", "is: 3"))
    code, lines = ogy(repo, "diff", "HEAD", ".")
    assert code == cli.OK
    assert lines == ["changed product/app/value/fee", "  is: 2 -> 3"]
    assert ogy(repo, "--rev", ".", "check") == (cli.OK, ["ok"])


def test_diff_reads_only_changed_files(repo: Path) -> None:
    target = ops.Target(repo)
    assert ops.run_diff(target, "HEAD", "HEAD").reads == 0
    path = repo / "docs/kb/product/app/values.yml"
    path.write_text(path.read_text().replace("is: 2", "is: 4"))
    change = commit(repo, "change one value")
    run = ops.run_diff(target, f"{change}~1", change)
    assert run.reads == 2
    assert {str(item.address): item.change for item in run.value.changes} == {"product/app/value/fee": Change.CHANGED}


def test_diff_names_added_and_removed_entries(repo: Path) -> None:
    (repo / "docs/kb/product/app/values.yml").write_text("- {id: late, says: Late., is: 1, unit: days}\n")
    change = commit(repo, "replace")
    found = {str(item.address): item.change for item in ops.run_diff(ops.Target(repo), f"{change}~1", change).value.changes}
    assert found == {"product/app/value/fee": Change.REMOVED, "product/app/value/late": Change.ADDED}


def test_diagram_draws_a_workflow_only(repo: Path) -> None:
    code, lines = ogy(repo, "diagram", "product/app/workflow/borrow")
    assert code == cli.OK and lines[0] == "flowchart TD"
    assert any("ask" in line and "done" in line and "--" in line for line in lines)
    assert ogy(repo, "diagram", "product/app/value/fee") == (cli.REFUSED, ["product/app/value/fee has no flow to draw"])
