"""An answered decision whose answer sets no entry is work until something cites it (decision
software/cli/decision/answered-uncited-is-work, answered computed): a kind file, an entry's `because`, or code, the text
"decision <address>" in a docstring (decision software/cli/decision/where-a-code-answer-lands, answered code-cites)."""

from collections.abc import Callable, Mapping

from tests.conftest import Kb

from ogy.citations import code_suffixes, in_code, uncited

type Make = Callable[[Mapping[str, str | None] | None], Kb]

ASKED = "product/app/decision/how"
DECISION = """\
question: How?
options:
  quick: {label: Quickly}
proposal: {chose: quick, why: Fast.}
answers: [{chose: quick, said: Quickly, at: '2026-11-12T10:05:00+01:00', where: 'ai:x'}]
"""


def test_an_answer_that_sets_nothing_is_work_until_cited(kb: Make) -> None:
    made = kb({"product/app/decision/how.yml": DECISION})
    assert [str(item) for item in uncited(made.snapshot, set())] == [ASKED]
    assert uncited(made.snapshot, {ASKED}) == []  # code cites it
    cited = kb({"product/app/decision/how.yml": DECISION, "product/app/pains.yml": f"- {{id: slow, says: Slow., because: [{ASKED}]}}\n"})
    assert uncited(cited.snapshot, set()) == []  # an entry cites it


def test_an_unanswered_decision_is_no_citation_work(kb: Make) -> None:
    made = kb({"product/app/decision/how.yml": DECISION.split("answers:", 1)[0]})
    assert uncited(made.snapshot, set()) == []


def test_code_cites_a_decision_only_in_a_docstring(kb: Make) -> None:
    texts = {
        "a.py": f'"""Reads it (decision {ASKED}, answered quick)."""\n',
        "b.py": "# decision product/app/decision/other\nx = 'decision product/app/decision/third'\n",
    }
    assert in_code(texts) == {ASKED}
    assert code_suffixes(kb(None).snapshot) == (".py",)
