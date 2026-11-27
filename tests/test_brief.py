"""One work item's brief, `ogy work <address>` (decision software/cli/decision/work-brief, answered work-address): the why above it
walked only up (parents, `because`, `realizes`), never sideways along `then`; the decisions that set it or anything above it;
one hop around it by field; its proof and built state. A layer or an area still lists the work left."""

import json
lazy from pathlib import Path

from tests.conftest import SOURCE
from tests.test_writes import w

from ogy import cli

A = "product/app"
PAIN, GOAL, CAP, WF = f"{A}/pain/tools-sit-idle", f"{A}/goal/tools-shared", f"{A}/capability/lend-tools", f"{A}/workflow/lend"
ROW, END, PAGE, WHY = f"{WF}/step/ask/choice/go", f"{WF}/end/lent", f"{A}/interface/lend-page", f"{A}/decision/how-to-lend"


def _chain(repo: Path) -> None:
    cap = {"says": "Members borrow tools.", "realizes": [GOAL]}
    records = [
        {"address": PAIN, "says": "Tools sit idle in sheds."},
        {"address": GOAL, "says": "Neighbours share tools.", "because": [PAIN], "src": [SOURCE]},
        {
            "address": WHY,
            "question": "How do members borrow?",
            "options": {"page": {"label": "A page", "sets": {CAP: cap}}},
            "proposal": {"chose": "page", "why": "Simplest."},
        },
        {"address": CAP, **cap},
        {
            "address": WF,
            "says": "A member borrows a tool.",
            "src": [SOURCE],
            "realizes": CAP,
            "start": "ask",
            "steps": {
                "ask": {
                    "says": "The member asks for a tool.",
                    "actor": f"{A}/actor/member",
                    "choices": {"go": {"label": "Borrow", "then": "lent"}},
                }
            },
            "ends": {"lent": {"result": "success", "says": "The tool is lent."}},
        },
        {"address": PAGE, "says": "The lending page.", "form": "web", "serves": [f"{WF}/step/ask"], "src": [SOURCE]},
    ]
    code, lines = w(repo, "put", json.dumps(records))
    assert code == cli.OK, lines


def _parts(lines: list[str]) -> dict[str, list[str]]:
    parts: dict[str, list[str]] = {}
    now = "entry"
    for line in lines:
        if line.endswith(":") and not line.startswith(" "):
            now = line[:-1]
        elif line.strip():
            parts.setdefault(now, []).append(line.strip())
    return parts


def test_the_brief_of_a_row_reads_the_why_above_the_decision_and_one_hop_around(repo: Path) -> None:
    _chain(repo)
    code, lines = w(repo, "work", ROW)
    assert code == cli.FINDINGS, lines  # the row is unbuilt: work is left
    parts = _parts(lines)
    assert parts["entry"][0] == f"brief of {ROW} (choice)"
    assert any(line.startswith(f"unbuilt  {ROW}") for line in parts["work"])
    why = [line.split()[1] for line in parts["why"]]
    assert why == [f"{WF}/step/ask", WF, CAP, GOAL, PAIN]  # nearest first, up only
    assert END not in why  # `then` leads on, not up
    assert parts["decided by"] == [f"decision  {WHY}  How do members borrow?"]
    assert any(line.startswith(f"then  {END}") for line in parts["links out"])
    assert any(line.startswith(f"serves  {PAGE}") for line in parts["linked from"])  # the page serves the row's step
    assert parts["built"] == ["no line"]


def test_an_area_still_lists_the_work_and_a_missing_address_says_what_is_near(repo: Path) -> None:
    _chain(repo)
    code, lines = w(repo, "work", A)
    assert code == cli.FINDINGS and not lines[0].startswith("brief of"), lines
    code, lines = w(repo, "work", f"{A}/capability/lend-tool")
    assert code == cli.NOT_FOUND, lines
    assert CAP in "\n".join(lines)
