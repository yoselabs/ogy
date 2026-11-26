"""A goal owes its reason: a principle or a decision it cites with `because`, or the decision that sets it. One with neither,
as a goal read from code starts, is discover work (decision software/ontology/decision/reason-is-owed)."""

import json
lazy from pathlib import Path

from tests.test_writes import w

from ogy import cli, ops
from ogy.target import Target

BARE, CITES, SET = "product/app/goal/bare", "product/app/goal/cites", "product/app/goal/set"
WHY = "product/app/decision/why"


def test_a_goal_with_no_reason_is_discover_work_and_one_with_a_reason_is_not(repo: Path) -> None:
    decision = {
        "address": WHY,
        "question": "Why lend tools?",
        "options": {"share": {"label": "Neighbours share", "sets": {SET: {"says": "Neighbours share tools."}}}},
        "proposal": {"chose": "share", "why": "the pain"},
    }
    records = [
        decision,
        {"address": SET, "says": "Neighbours share tools."},
        {"address": BARE, "says": "Tools are found.", "src": ["code:app.py#lend"]},  # read from code: no reason
        {"address": CITES, "says": "Tools come back.", "because": [WHY]},
    ]
    code, lines = w(repo, "put", json.dumps(records))
    assert code == cli.OK, lines
    owed = {item.address for item in ops.run_work(Target(repo), "product").value if str(item.status) == "no-reason"}
    assert owed == {BARE}
    lines = w(repo, "work", "product")[1]
    heads = [index for index, line in enumerate(lines) if line.split(" (")[0] in ("discover", "design", "build")]
    assert lines[heads[0]].startswith("discover (")  # the why: discover, the first type
    end = heads[1] if len(heads) > 1 else len(lines)
    assert any(line.startswith(f"no-reason: {BARE}") for line in lines[heads[0] : end])
