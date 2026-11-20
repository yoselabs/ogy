"""The constitution: a fixed folder beside the glossary, agreed by the owner, cited with `because`, printed first."""

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

from ogy.constitution import printed_lines
from ogy.find import find
from ogy.graph import context
from ogy.layout import locate, path_for
from ogy.model import Address, Problem
from ogy.review import review
lazy from ogy.ontology import Ontology

if TYPE_CHECKING:
    from conftest import Kb

type Make = Callable[[Mapping[str, str | None] | None], Kb]

SAY = "- {id: graph, says: The ontology is a graph of linked entries., why: Storage is no meaning.}\n"
PRINCIPLE = Address("", "constitution", (("principle", "graph"),))
RULE = {"software/app/rule/stored-anywhere.yml": "says: An entry may be stored anywhere.\nbecause: [constitution/principle/graph]\n"}


def test_constitution_is_a_second_fixed_folder(kb: Make, ontology: Ontology) -> None:
    snapshot = kb({"constitution/principles.yml": SAY}).snapshot
    where = path_for(ontology.kinds["principle"], "constitution", "graph")
    assert snapshot.entries[PRINCIPLE].path == "constitution/principles.yml" == where
    assert str(PRINCIPLE) == "constitution/principle/graph" and snapshot.resolve("constitution/principle/graph") == PRINCIPLE
    assert not isinstance(locate(ontology, "constitution/principles.yml"), str)
    elsewhere = kb({"product/app/principles.yml": SAY}).findings()
    assert (Problem.BAD_PATH, "product/app/principles.yml") in elsewhere


def test_principle_needs_says_and_the_owner(kb: Make) -> None:
    assert (Problem.MISSING_FIELD, "constitution/principle/graph") in kb({"constitution/principles.yml": "- {id: graph}\n"}).findings()
    assert (Problem.TERM_NOT_AGREED, "constitution/principle/graph") in kb({"constitution/principles.yml": SAY}).findings(landing=True)


def test_review_asks_a_principle_nobody_agreed_to(kb: Make) -> None:
    snapshot = kb({"constitution/principles.yml": SAY}).snapshot
    asked = review(snapshot, area="constitution")
    assert [card.address for card in asked.cards] == [PRINCIPLE]
    assert [item.area for item in asked.headers] == ["constitution"]


def test_find_and_show_list_who_cites_a_principle(kb: Make) -> None:
    snapshot = kb({"constitution/principles.yml": SAY, **RULE}).snapshot
    rows = find(snapshot, [], [], None, None, state=None, parent=None, cites=PRINCIPLE)
    assert [row.address for row in rows] == ["software/app/rule/stored-anywhere"]
    assert [str(edge.address) for edge in context(snapshot, PRINCIPLE).referenced_by] == ["software/app/rule/stored-anywhere"]


def test_agents_read_the_constitution_before_the_glossary(kb: Make) -> None:
    glossary = "- {id: land, word: land, says: To finish a delivery.}\n"
    both = printed_lines(kb({"constitution/principles.yml": SAY, "product/shared/glossary.yml": glossary}).snapshot)
    assert both[0].startswith("constitution")
    assert both.index("  land: To finish a delivery.") > both.index("    why: Storage is no meaning.")
    assert "  graph: The ontology is a graph of linked entries." in both
    none = kb({"constitution/principles.yml": "[]\n", "product/shared/glossary.yml": glossary}).snapshot
    lines = printed_lines(none)
    assert lines[:3] == ["product/shared:", "  land: To finish a delivery.", ""]
    assert lines[3] == "kinds, like and unlike:" and "  actor: like a UML actor; unlike" in lines[4]  # the kinds, after the words
