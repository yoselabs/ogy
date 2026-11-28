"""A pain: what goes wrong for the people the product serves, one sentence a person agrees to by its own card, never by
`yes all`. A goal that cites a pain has its reason only once a person agreed to that pain (decision
product/capture/decision/pain-kind)."""

import json
lazy from pathlib import Path

from tests.test_reply import r, round_of, status
from tests.test_writes import w

from ogy import cli, ops
from ogy.target import Target

PAIN, GOAL = "product/app/pain/no-tools", "product/app/goal/tools-at-hand"


def _owed(repo: Path) -> set[str]:
    return {item.address for item in ops.run_work(Target(repo), "product").value if str(item.status) == "no-reason"}


def test_a_pain_is_a_reason_only_once_a_person_agreed_to_it_by_its_own_card(repo: Path) -> None:
    pain = {"address": PAIN, "says": "Members buy a tool they need once a year."}
    goal = {"address": GOAL, "says": "Members borrow the tools they need.", "because": [PAIN], "src": ["code:app.py#lend"]}
    code, lines = w(repo, "put", json.dumps([pain, goal]))
    assert code == cli.OK, lines
    assert GOAL in _owed(repo)  # a guessed pain is no reason yet
    shown = w(repo, "review")[1]
    label = next(line.split(".")[0] for line in shown if line[:1].isdigit() and PAIN in line)
    code, lines = r(repo, "yes all", "--round", round_of(shown))
    assert f"{PAIN} is agreed only by its own card" in "\n".join(lines), lines
    assert "nobody agreed" in status(repo, PAIN) and GOAL in _owed(repo)
    shown = w(repo, "review")[1]
    label = next(line.split(".")[0] for line in shown if line[:1].isdigit() and PAIN in line)
    code, lines = r(repo, f"yes {label}", "--round", round_of(shown))
    assert code == cli.OK, lines
    assert "decided by you" in status(repo, PAIN) and GOAL not in _owed(repo)


def test_a_pain_nothing_answers_is_a_row_until_a_goal_or_decision_cites_it(repo: Path) -> None:
    """Decision software/ontology/decision/pain-owes-a-follower: computed, never marked."""
    assert w(repo, "put", json.dumps([{"address": PAIN, "says": "Members buy a tool they need once a year."}]))[0] == cli.OK
    unused = {item.address for item in ops.run_work(Target(repo), "product").value if str(item.status) == "unanswered"}
    assert PAIN in unused
    goal = {"address": GOAL, "says": "Members borrow the tools they need.", "because": [PAIN], "src": ["code:app.py#lend"]}
    assert w(repo, "put", json.dumps([goal]))[0] == cli.OK
    unused = {item.address for item in ops.run_work(Target(repo), "product").value if str(item.status) == "unanswered"}
    assert PAIN not in unused
