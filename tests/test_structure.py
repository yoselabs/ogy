"""The layout is the ontology's: guards against structure being dropped, bundled or left empty without notice."""

import json
import shutil
from collections.abc import Callable, Mapping
from pathlib import Path

import any_yaml
import pytest
from tests.conftest import Kb, ogy
from tests.test_reply import r, round_of
from tests.test_writes import OPTIONS, put, w

from ogy import cli
from ogy.coverage import product_areas, uncovered
from ogy.kinds import Harm
from ogy.model import Problem
from ogy.ontology import packaged

type MakeKb = Callable[[Mapping[str, str | None] | None], Kb]
RULE = "product/app/rule/layers-are-folders"
LAYERS = {"keep": {"label": "Keep the folders", "sets": {RULE: {"says": "Every entry lives under a layer folder."}}},
          "drop": {"label": "Drop them", "sets": {RULE: None}}}
LAYOUT = "product/app/decision/keep-the-layers"


@pytest.fixture
def structural(repo: Path) -> Path:
    """A capability nobody agreed to (card 1), a question whose guess rests on what the owner said and a structural one that does too."""
    assert put(repo, "product/app/capability/borrow", says="A member can borrow.", because=["product/app/value/fee"])[0] == cli.OK
    cited = {"chose": "two", "why": "the owner leaned to two", "heard": {"said": "Two euros seem plenty"}}
    assert put(repo, "product/app/decision/fee-amount", question="How much?", options=any_yaml.load(OPTIONS), guess=cited)[0] == cli.OK
    kept = {**cited, "chose": "keep"}
    decision = {"address": LAYOUT, "question": "Keep the layer folders?", "structure": True, "options": LAYERS, "guess": kept}
    code, lines = w(repo, "put", json.dumps([decision, {"address": RULE, "says": "Every entry lives under a layer folder."}]))
    assert code == cli.OK, lines
    return repo


def test_the_structure_tag_is_a_harm_of_the_decision_kind() -> None:
    assert Harm.STRUCTURE in list(Harm) and packaged().kinds["decision"].fields["structure"].harm == (Harm.STRUCTURE,)


def test_review_says_a_structural_question_needs_its_own_letter_and_what_a_bare_yes_changes(structural: Path) -> None:
    lines = w(structural, "review")[1]
    text = "\n".join(lines)
    assert "Q1. question  product/app/decision/keep-the-layers  (structure)" in text
    assert "Structural: answer with its own letter (Q1 a)" in text
    assert "Structural, not covered by yes or yes all: Q1; each needs its own letter." in text
    bare = next(line for line in lines if line.startswith("A bare `yes`"))
    assert bare.startswith("A bare `yes` will: confirm Q2 as A; agree to ") and "Q1" not in bare  # the structural question is not in it
    assert lines.index(bare) < next(i for i, line in enumerate(lines) if line.startswith("Reply:"))


def test_a_bare_yes_leaves_a_structural_decision_and_confirms_the_rest(structural: Path) -> None:
    lines = w(structural, "review")[1]
    code, done = r(structural, "yes", "--round", round_of(lines))
    assert code == cli.OK and "fee-amount answered: two" in done[0] and "keep-the-layers" not in done[0], done
    assert "answers" not in (structural / f"docs/kb/{LAYOUT}.yml").read_text()


@pytest.mark.parametrize("words", ["yes all", "decide"])
def test_yes_all_and_decide_leave_a_structural_decision_and_say_why(structural: Path, words: str) -> None:
    code, done = r(structural, words, "--round", round_of(w(structural, "review")[1]))
    assert code == cli.OK and "not done: product/app/decision/keep-the-layers is structural" in done[0], done
    assert "Q1 a" in done[0] and "answers" not in (structural / f"docs/kb/{LAYOUT}.yml").read_text()
    assert "fee-amount answered: two" in done[0]  # the rest of the round is accepted


def test_a_structural_decision_is_answered_with_its_own_letter(structural: Path) -> None:
    lines = w(structural, "review")[1]
    code, done = r(structural, "Q1 b", "--round", round_of(lines))
    assert code == cli.OK and done == ["Q1 b: product/app/decision/keep-the-layers answered: drop"], done
    assert "chose: drop" in (structural / f"docs/kb/{LAYOUT}.yml").read_text()


def test_status_coverage_lists_the_kinds_with_no_entry_per_layer(repo: Path) -> None:
    code, lines = w(repo, "status", "--coverage")
    assert code == cli.OK and "coverage (kinds with no entry):" in lines
    product = next(line for line in lines if line.startswith("  product:"))
    software = next(line for line in lines if line.startswith("  software:"))
    assert "goal" in product and "capability" in product and "actor" not in product and "message" not in product
    assert "command" in software and "view" not in software and "operation" not in software
    assert not any(line.startswith("coverage") for line in w(repo, "status")[1])  # only when asked


def test_coverage_counts_the_kinds_that_own_a_file_by_layer(kb: MakeKb) -> None:
    found = uncovered(kb(None).snapshot)
    assert set(found) == {"product", "software"} and "step" not in found["product"] and "term" not in found["product"]
    assert "workflow" not in found["product"] and "workflow" in found["software"]  # the sign-in workflow is a product entry


def test_an_area_named_like_the_repository_is_a_check_error(kb: MakeKb, repo: Path) -> None:
    snapshot = kb(None).snapshot
    assert [(str(f.problem), f.path) for f in product_areas(snapshot, "app")] == [("product-area", "product/app"),
                                                                                  ("product-area", "software/app")]
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
