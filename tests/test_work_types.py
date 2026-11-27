"""`ogy work` for a person: three types, discover (the why), design (a gap in the description) and build (to implement or
prove), each entry once, under its earliest type (decision software/cli/decision/work-types)."""

import json
lazy from pathlib import Path

from tests.test_writes import w

from ogy import cli, ops
from ogy.target import Target
from ogy.workcause import work_type
lazy from ogy.receipts import Work

CAPABILITY = "product/app/capability/lend"
RULE = "product/app/rule/one-loan"


def test_work_is_listed_by_type_and_each_entry_once_under_its_earliest(repo: Path) -> None:
    decision = {
        "address": "product/app/decision/loans",
        "question": "One loan at a time?",
        "options": {"one": {"label": "One", "sets": {RULE: {"says": "A member holds one loan at a time."}}}},
        "proposal": {"chose": "one", "why": "simple"},
    }
    capability = {"address": CAPABILITY, "says": "A member borrows a tool.", "because": ["product/app/decision/loans"]}
    code, lines = w(repo, "put", json.dumps([decision, {"address": RULE, "says": "A member holds one loan at a time."}, capability]))
    assert code == cli.OK, lines
    lines = w(repo, "work", "product")[1]
    heads = [line for line in lines if line.split(" (")[0] in ("discover", "design", "build")]
    assert [head.split(" ")[0] for head in heads] == ["discover", "design", "build"], heads
    design, build = lines.index(heads[1]), lines.index(heads[2])
    assert any(line.startswith(f"unrealized: {CAPABILITY}") for line in lines[:design])
    assert any(line.startswith(f"unused: {RULE}") for line in lines[design:build])
    assert not any(RULE in line for line in lines[build:])  # unbuilt too, but shown once: under design, its earliest type
    assert any(line.startswith("unbuilt: product/app/interface/page") for line in lines[build:])
    flat = ops.run_work(Target(repo), "product").value  # the agents' table keeps every row
    assert {str(item.status) for item in flat if item.address == RULE} == {"unused", "unbuilt"}


def test_a_row_set_by_no_decision_goes_under_the_decision_it_cites(repo: Path) -> None:
    """Decision software/cli/decision/work-cause-reads-because: `because` names the cause when no decision sets the entry."""
    options, proposal = {"yes": {"label": "Yes"}}, {"chose": "yes", "why": "w"}
    decision = {"address": "product/app/decision/loans", "question": "Lend?", "options": options, "proposal": proposal}
    capability = {"address": CAPABILITY, "says": "A member borrows a tool.", "because": ["product/app/decision/loans"]}
    code, lines = w(repo, "put", json.dumps([decision, capability]))
    assert code == cli.OK, lines
    lines = w(repo, "work", "product")[1]
    head = next(index for index, line in enumerate(lines) if line.startswith("by product/app/decision/loans"))
    assert lines[head + 1].startswith(f"unrealized: {CAPABILITY}"), lines[head : head + 3]


def test_a_row_is_typed_by_the_direction_of_its_rule(repo: Path) -> None:
    """Decision software/cli/decision/work-types, type-from-rule: a capability with no goal above is the why missing; the same
    capability with no workflow below is design."""
    code, lines = w(repo, "put", json.dumps([{"address": CAPABILITY, "says": "A member borrows a tool.", "src": ["code:app.py#lend"]}]))
    assert code == cli.OK, lines
    types = {(item.status, ops_type) for item, ops_type in _typed(repo) if item.address == CAPABILITY}
    assert types == {("unrealized", "discover"), ("no-workflow", "design")}


def _typed(repo: Path) -> list[tuple[Work, str]]:
    target = Target(repo)
    snapshot = target.read()[1]
    return [(item, work_type(snapshot, item)) for item in ops.run_work(target, "product").value]
