"""Which layer owes a requirement, computed from `layers:` and `link_direction` (`ogy.owing`), and the work it makes."""

import json
from importlib.resources import files
lazy from pathlib import Path

import pytest
from git_porcelain import run_git
from tests.conftest import FILES, commit, ogy

from ogy import cli
from ogy.ontology import OntologyError, packaged, parse_kinds

KINDS = files("ogy").joinpath("ontologies", "software", "kinds")
STEP = "product/app/workflow/borrow/step/ask"


def test_a_requirement_that_goes_back_to_a_later_layer_is_work_owed_by_it() -> None:
    kinds = packaged()
    owed = {
        (name, need.status): kinds.owed_by(name, need, "product")
        for name, kind in kinds.kinds.items()
        for need in kind.requires
        if need.work
    }
    assert owed[("step", "unserved")] == owed[("case", "unhandled")] == owed[("attribute", "unwritten")] == "software"
    assert owed[("quantity", "unused")] is None and owed[("capability", "unrealized")] is None  # same layer: set by hand
    assert all(kinds.owed_by(name, need, "software") is None for name, kind in kinds.kinds.items() for need in kind.requires)
    tell = next(need for need in kinds.kinds["effect"].requires if need.if_equals and "tell" in need.if_equals.values)
    assert not tell.work  # a forward hop never crosses: a tell names an actor of its own layer


def test_the_loader_refuses_a_fault_that_crosses_into_a_later_layer() -> None:
    texts = {f"kinds/{item.name}": item.read_text() for item in KINDS.iterdir()}
    texts["kinds/step.yml"] = texts["kinds/step.yml"].replace(" status: unserved,", "")
    with pytest.raises(OntologyError, match="only a later layer holds, so it is work: name its status"):
        parse_kinds(texts, packaged().declared)


def test_work_of_a_layer_is_what_it_owes_and_an_unoffered_choice_is_work_not_a_fault(repo: Path) -> None:
    """Fable's blockers 5 and 7: a product choice its interface does not offer yet commits; the interface owes it."""
    page = repo / "docs/kb/software/app/interface/page.yml"
    page.write_text(page.read_text() + f"offers: [{STEP}/choice/go]\n")
    commit(repo, "the page offers go")
    code, lines = ogy(repo, "put", json.dumps({"address": f"{STEP}/choice/skip", "label": "Skip", "then": "done"}))
    assert code == cli.OK, lines
    assert ogy(repo, "--rev", ".", "check")[0] == cli.OK
    software, product = ogy(repo, "--rev", ".", "work", "software")[1], ogy(repo, "--rev", ".", "work", "product")[1]
    assert any(line.startswith("unoffered: software/app/interface/page") for line in software), software
    assert not any(line.startswith("unoffered") for line in product)
    whole = ogy(repo, "--rev", ".", "work")[1]
    assert {line for line in software + product if not line.startswith("by ")} <= set(whole)  # the whole is every layer's


@pytest.fixture
def product_only(tmp_path: Path) -> Path:
    """A product layer committed alone: the software layer is declared in `layers:` and has no entry yet."""
    run_git(tmp_path, "init", "-q", "-b", "main")
    for rel, text in FILES.items():
        if not rel.startswith("docs/kb/software/"):
            (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / rel).write_text(text)
    commit(tmp_path, "product")
    return tmp_path


def test_a_declared_layer_with_no_entries_is_a_scope_and_owes_its_work(product_only: Path) -> None:
    """Fable's review, problem 1: `work software` and `check software` before software has an entry."""
    assert ogy(product_only, "check", "software") == (cli.OK, ["ok"])
    code, software = ogy(product_only, "work", "software")
    assert code == cli.FINDINGS and any(line.startswith(f"unserved: {STEP}") for line in software), software
    product = ogy(product_only, "work", "product")[1]
    assert not any(line.startswith("unserved") for line in product), product
    assert ogy(product_only, "work", "software/app")[0] == cli.NOT_FOUND  # owed work is matched by layer, never by an area
