"""The layout is the ontology's: guards against structure being dropped, bundled or left empty without notice."""

import shutil
from collections.abc import Callable, Mapping
lazy from pathlib import Path

from tests.conftest import Kb, ogy
from tests.test_writes import w

from ogy import cli
from ogy.coverage import product_areas, uncovered
from ogy.model import Problem
from ogy.ontology import packaged

type MakeKb = Callable[[Mapping[str, str | None] | None], Kb]


def test_a_decision_has_no_structure_flag() -> None:
    """Dropped (software/ontology/decision/flexibility-needs-evidence): no product needed it; a migration takes it out."""
    ontology = packaged()
    assert "structure" not in ontology.kinds["decision"].fields and "structure" in ontology.kinds["decision"].dropped
    assert "structure" not in ontology.declared.harms


def test_status_coverage_lists_the_kinds_with_no_entry_per_layer(repo: Path) -> None:
    code, lines = w(repo, "status", "--coverage")
    assert code == cli.OK and "coverage (kinds with no entry):" in lines
    product = next(line for line in lines if line.startswith("  product:"))
    software = next(line for line in lines if line.startswith("  software:"))
    assert "goal" in product and "capability" in product and "actor" not in product and "message" not in product
    assert "rule" in software and "interface" not in software and "handler" not in software
    assert not any(line.startswith("coverage") for line in w(repo, "status")[1])  # only when asked


def test_coverage_counts_the_kinds_that_own_a_file_by_layer(kb: MakeKb) -> None:
    found = uncovered(kb(None).snapshot)
    assert set(found) == {"product", "software"} and "step" not in found["product"] and "term" in found["product"]
    assert "workflow" not in found["product"] and "workflow" in found["software"]  # the sign-in workflow is a product entry


def test_an_area_named_like_the_repository_is_a_check_error(kb: MakeKb, repo: Path) -> None:
    snapshot = kb(None).snapshot
    assert [(str(f.problem), f.path) for f in product_areas(snapshot, "app")] == [
        ("product-area", "product/app"),
        ("product-area", "software/app"),
    ]
    assert product_areas(snapshot, "library") == [] and product_areas(snapshot, "App") != []
    named = repo.with_name("app")
    shutil.copytree(repo, named)
    code, lines = ogy(named, "--rev", ".", "check")
    assert code == cli.FINDINGS and lines[0].startswith("product-area: product/app: the area is named like the product (app)")
    assert not any(line.startswith("warning") for line in lines + ogy(named, "--rev", ".", "status")[1])
    assert ogy(repo, "--rev", ".", "check") == (cli.OK, ["ok"])  # a topic: no finding


def test_a_doc_link_must_pin_a_commit(kb: MakeKb) -> None:
    unpinned = "- {id: member, says: A person., nature: human, src: [doc:docs/spec.md#members]}\n"
    found = kb({"product/app/actors.yml": unpinned}).findings(evidence=True)
    assert (Problem.BAD_SRC, "product/app/actor/member") in found
    pinned = unpinned.replace("doc:docs", "doc:0123abc:docs")
    assert (Problem.BAD_SRC, "product/app/actor/member") not in kb({"product/app/actors.yml": pinned}).findings(evidence=True)
