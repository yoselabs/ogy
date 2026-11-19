"""The glossary checks T1-T6 and the terminal listing."""

from collections.abc import Callable

from tests.conftest import Kb

from ogy.model import Address, Problem
from ogy.ontology import packaged
from ogy.snapshot import Snapshot, build
from ogy.terms import check_terms, glossary_lines, proposed_terms, terms_not_agreed

type Make = Callable[[dict[str, str | None] | None], Kb]
LAND = "- {id: land, word: land, says: To finish a delivery., avoid: [merge, check run]}\n"


def snap(terms: str, **more: str) -> Snapshot:
    return build(packaged(), {"product/shared/glossary.yml": terms, **more})


def problems(snapshot: Snapshot) -> set[tuple[object, str]]:
    return {(f.problem, str(f.address)) for f in check_terms(snapshot)}


def test_a_term_says_one_line_of_under_15_words(kb: Make) -> None:
    long = "- {id: a, word: a, says: " + " ".join(["word"] * 15) + "}\n- {id: b, word: b, says: \"One.\\nTwo.\"}\n"
    assert problems(snap(long)) == {(Problem.TERM_TOO_LONG, "product/shared/term/a"), (Problem.TERM_TOO_LONG, "product/shared/term/b")}
    assert problems(snap(LAND)) == set()
    old = "- {id: fee, word: fee, of: product/app/quantity/fee, distinct: [a price], group: Money, example: x, borrowed: 'https://x.org'}\n"
    found = kb({"product/app/glossary.yml": old}).findings()
    assert {problem for problem, _ in found} == {Problem.NEEDS_MIGRATION, Problem.MISSING_FIELD}  # `ogy migrate`, then a `says`
    assert not kb({"product/app/glossary.yml": "- {id: fee, word: fee, says: What a loan costs.}\n"}).findings(evidence=True)


def test_word_clash() -> None:
    clash = snap(LAND + "- {id: land2, word: Land, says: x.}\n- {id: m, word: Merge, says: y.}\n")
    assert problems(clash) == {(Problem.WORD_CLASH, "product/shared/term/land2"), (Problem.WORD_CLASH, "product/shared/term/land")}


def test_avoided_word_outside_backticks() -> None:
    kb = snap(LAND, **{"product/app/decisions.yml": "- {id: q, question: Should we merge it?}\n",
                       "product/app/actors.yml": "- {id: ok, says: The `merge` button and a check  run., nature: human}\n"
                                           "- {id: check-run, says: Fine., nature: human}\n"
                                           "- {id: quoted, says: \"`check run` and merging and run check.\", nature: human}\n"})
    found = {str(f.address): f.detail for f in check_terms(kb) if f.problem is Problem.AVOIDED_WORD}
    assert "product/app/actor/check-run" in found and "product/app/actor/ok" in found
    assert "product/app/actor/quoted" not in found
    assert "product/shared/term/land" not in found


def test_term_must_be_agreed() -> None:
    kb = snap(LAND + "- {id: x, word: x, says: y.}\n")
    agreed = {Address("product", "shared", (("term", "land"),))}
    assert [str(f.address) for f in terms_not_agreed(kb, agreed)] == ["product/shared/term/x"]
    assert terms_not_agreed(kb, lambda _: True) == []


def test_proposed_term_blocks_landing() -> None:
    kb = snap(LAND)
    found = proposed_terms(kb, {Address("product", "shared", (("term", "land"),))})
    assert [f.problem for f in found] == [Problem.PROPOSED_TERM]
    assert proposed_terms(kb, set()) == []


def test_glossary_lines_print_the_shared_terms_then_each_area() -> None:
    kb = snap(LAND, **{"software/app/glossary.yml": "- {id: x, word: X, says: The commit.}\n",
                       "software/shared/glossary.yml": "- {id: y, word: Y, says: A run.}\n"})
    assert glossary_lines(kb) == ["product/shared:", "  land: To finish a delivery.", "    avoid: merge; check run",
                                  "software/shared:", "  Y: A run.", "software/app:", "  X: The commit."]


def test_a_decision_may_not_give_the_words_of_an_agreed_term() -> None:
    def kb(sets: str, agreed: bool = True) -> Snapshot:
        stamp = "{at: '2026-11-12T10:00:00+01:00', where: 'ai:claude/1', said: Yes, hash: 'aaaaaaaaaaaa'}"
        term = f"- {{id: land, word: land, says: To finish.{', agreed: ' + stamp if agreed else ''}}}\n"
        decision = f"question: Q?\noptions:\n  a: {{label: A, sets: {{{sets}}}}}\nproposal: {{chose: a, why: x}}\n"
        return snap(term, **{"product/app/decision/q.yml": decision})
    reworded = "product/shared/term/land: {says: To end.}"
    assert (Problem.AGREED_TERM_IN_SETS, "product/app/decision/q") in problems(kb(reworded))
    assert not {p for p, _ in problems(kb("product/shared/term/land: null"))} & {Problem.AGREED_TERM_IN_SETS}
    assert not {p for p, _ in problems(kb(reworded, agreed=False))} & {Problem.AGREED_TERM_IN_SETS}  # a new word may be proposed
    assert (Problem.AGREED_TERM_IN_SETS, "product/app/decision/q") in problems(kb("product/shared/term/land: {avoid: [end]}"))
