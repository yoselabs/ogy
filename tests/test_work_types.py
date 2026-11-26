"""`ogy work` for a person: three types, discover (the why), design (a gap in the description) and build (to implement or
prove), each entry once, under its earliest type (decision software/cli/decision/work-types)."""

import json
lazy from pathlib import Path

from tests.test_writes import w

from ogy import cli, ops
from ogy.target import Target

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
