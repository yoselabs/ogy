"""The test run writes the built lines (decision software/ontology/decision/built-line-writer, answered test-run-writes): with
`--ogy-stamp`, an entry whose every proof passed in the run gets its built line; a failed, skipped or unrun proof leaves its entry
as it was; without the flag nothing is written; a proof that names no test is a finding."""

import json
lazy from pathlib import Path

from tests.conftest import SOURCE
from tests.test_writes import w
lazy import pytest

from ogy import built, cli, ops
from ogy.target import Target

pytest_plugins = ["pytester"]

FILE = "tests/test_rules.py"
HELD, BROKEN, SKIPPED, HALF = (f"product/app/rule/{name}" for name in ("held", "broken", "skipped", "half"))
TESTS = """
import pytest

def test_holds():
    assert True

def test_breaks():
    assert False

@pytest.mark.skip(reason="not yet")
def test_later():
    pass

@pytest.mark.parametrize("n", [1, 2])
def test_half(n):
    assert n == 1
"""


def _rules(repo: Path) -> None:
    (repo / "tests").mkdir()
    (repo / "tests" / "test_rules.py").write_text(TESTS)
    rules = [
        {"address": HELD, "says": "It holds.", "src": [SOURCE], "proof": ["tests/test_rules.py::test_holds"]},
        {"address": BROKEN, "says": "It breaks.", "src": [SOURCE], "proof": [f"{FILE}::test_holds", f"{FILE}::test_breaks"]},
        {"address": SKIPPED, "says": "It waits.", "src": [SOURCE], "proof": ["tests/test_rules.py::test_later"]},
        {"address": HALF, "says": "It holds once.", "src": [SOURCE], "proof": ["tests/test_rules.py::test_half"]},
    ]
    code, lines = w(repo, "put", json.dumps(rules))
    assert code == cli.OK, lines


def _run(pytester: pytest.Pytester, repo: Path, *flags: str) -> None:
    pytester.runpytest_inprocess(str(repo / "tests"), f"--rootdir={repo}", "--import-mode=importlib", "-p", "no:cacheprovider", *flags)


def _unbuilt(repo: Path) -> set[str]:
    return {item.address for item in ops.run_work(Target(repo), "product").value if str(item.status) == "unbuilt"}


def test_the_run_writes_a_line_only_for_an_entry_whose_proofs_all_passed(pytester: pytest.Pytester, repo: Path) -> None:
    _rules(repo)
    assert {HELD, BROKEN, SKIPPED} <= _unbuilt(repo)
    _run(pytester, repo, "--ogy-stamp")
    record = built.read_all(repo / "docs/kb")
    assert set(record) == {HELD}  # one failing proof, a skipped one, or one parameter failing keeps the entry unbuilt
    _, snapshot = Target(repo).read()
    address = next(a for a in snapshot.entries if str(a) == HELD)
    assert record[HELD].own == snapshot.build_hash(address)
    assert SOURCE in record[HELD].sourced  # the src receipts, so a changed symbol is work again
    assert HELD not in _unbuilt(repo)
    assert {BROKEN, SKIPPED, HALF} <= _unbuilt(repo)


def test_without_the_flag_or_for_a_proof_that_did_not_run_nothing_is_written(pytester: pytest.Pytester, repo: Path) -> None:
    _rules(repo)
    _run(pytester, repo)
    assert built.read_all(repo / "docs/kb") == {}
    _run(pytester, repo, "--ogy-stamp", "-k", "breaks")  # test_holds did not run: HELD's proof is not green in this run
    assert built.read_all(repo / "docs/kb") == {}


def test_a_proof_that_names_no_test_is_a_finding(repo: Path) -> None:
    _rules(repo)
    gone = {"address": HELD, "proof": ["tests/test_rules.py::test_vanished", "tests/test_none.py::test_holds"]}
    code, lines = w(repo, "put", json.dumps([gone]))
    assert code == cli.REFUSED, lines
    text = "\n".join(lines)
    assert "names no test: tests/test_rules.py defines no test_vanished" in text
    assert "names no test: tests/test_none.py is not in the repository" in text
