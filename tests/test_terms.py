"""The glossary checks T1-T5 and the terminal listing."""

from ogy.model import Address, Problem
from ogy.ontology import packaged
from ogy.snapshot import Snapshot, build
from ogy.terms import check_terms, glossary_lines, proposed_terms, terms_not_agreed

LAND = "- {id: land, word: land, says: To finish a delivery., avoid: [merge, check run]}\n"


def snap(terms: str, **more: str) -> Snapshot:
    return build(packaged(), {"glossary/terms.yml": terms, **more})


def problems(snapshot: Snapshot) -> set[tuple[object, str]]:
    return {(f.problem, str(f.address)) for f in check_terms(snapshot)}


def test_term_has_says_or_of() -> None:
    both = snap("- {id: a, word: a, says: x., of: glossary/term/b}\n- {id: b, word: b}\n"
                "- {id: c, word: c, of: glossary/term/b}\n")
    assert problems(both) == {(Problem.ONE_OF, "glossary/term/a"), (Problem.ONE_OF, "glossary/term/b"),
                              (Problem.WRONG_TYPE, "glossary/term/a"), (Problem.WRONG_TYPE, "glossary/term/c")}
    assert problems(snap(LAND)) == set()


def test_word_clash() -> None:
    clash = snap(LAND + "- {id: land2, word: Land, says: x.}\n- {id: m, word: Merge, says: y.}\n")
    assert problems(clash) == {(Problem.WORD_CLASH, "glossary/term/land2"), (Problem.WORD_CLASH, "glossary/term/land")}


def test_avoided_word_outside_backticks() -> None:
    kb = snap(LAND, **{"product/app/decisions.yml": "- {id: q, question: Should we merge it?}\n",
                       "product/app/actors.yml": "- {id: ok, says: The `merge` button and a check  run., nature: human}\n"
                                           "- {id: check-run, says: Fine., nature: human}\n"
                                           "- {id: quoted, says: \"`check run` and merging and run check.\", nature: human}\n"})
    found = {str(f.address): f.detail for f in check_terms(kb) if f.problem is Problem.AVOIDED_WORD}
    assert "product/app/actor/check-run" in found and "product/app/actor/ok" in found
    assert "product/app/actor/quoted" not in found
    assert "glossary/term/land" not in found


def test_term_must_be_agreed() -> None:
    kb = snap(LAND + "- {id: x, word: x, says: y.}\n")
    agreed = {Address("", "glossary", (("term", "land"),))}
    assert [str(f.address) for f in terms_not_agreed(kb, agreed)] == ["glossary/term/x"]
    assert terms_not_agreed(kb, lambda _: True) == []


def test_proposed_term_blocks_landing() -> None:
    kb = snap(LAND)
    found = proposed_terms(kb, {Address("", "glossary", (("term", "land"),))})
    assert [f.problem for f in found] == [Problem.PROPOSED_TERM]
    assert proposed_terms(kb, set()) == []


def test_glossary_lines_group_terms() -> None:
    kb = snap(LAND + "- {id: x, word: X, says: The commit., group: Land, distinct: [O]}\n")
    assert glossary_lines(kb) == ["land: To finish a delivery.", "  avoid: merge; check run", "Land:", "  X: The commit.",
                                  "    distinct: O"]
