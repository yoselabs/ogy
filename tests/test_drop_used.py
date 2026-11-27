"""An answer that takes away an entry others link to is recorded at once; each entry that still links to it is work
(software/writes/decision/answer-that-removes-used-entries, option record-then-work)."""

import json
lazy from pathlib import Path

import pytest
from tests.conftest import commit
from tests.test_writes import w

from ogy import cli, ops
from ogy.target import Target

GOAL = "product/shop/goal/know-before-visit"
OTHER = "product/shop/goal/find-a-pet"
CAPABILITY = "product/shop/capability/show-stock"
DECISION = "product/shop/decision/stock-goal"
SAYS = "A customer knows before a visit whether a pet can still be bought."
OPTIONS = {"keep": {"label": "Keep it", "sets": {GOAL: {"says": SAYS}}}, "drop": {"label": "Drop it", "sets": {GOAL: None}}}
SAID = ["--said", "the stock goal", "--where", "ai:test/1"]
ROW = f"links to an entry said no to: {CAPABILITY} "


def answered(repo: Path, option: str, hour: int) -> tuple[int, list[str]]:
    return w(repo, "answer", DECISION, option, *SAID, "--at", f"2026-11-25T{hour:02}:00:00+01:00")


@pytest.fixture
def shop(repo: Path) -> Path:
    """The pet shop: the owner said yes to the stock goal, then a capability was written that realizes it."""
    area = {"address": "product/shop/area/shop", "says": "The pet shop's storefront."}
    decision = {"address": DECISION, "question": "Keep the stock goal?", "options": OPTIONS, "proposal": {"chose": "keep", "why": "asked"}}
    other = {"address": OTHER, "says": "A customer finds a pet to buy.", "because": [DECISION]}
    code, lines = w(repo, "put", json.dumps([area, decision, {"address": GOAL, "says": SAYS}, other]))
    assert code == cli.OK, lines
    assert answered(repo, "keep", 10)[0] == cli.OK
    capability = {"address": CAPABILITY, "says": "A customer sees which pets are in stock.", "realizes": [GOAL], "because": [DECISION]}
    code, lines = w(repo, "put", json.dumps(capability))
    assert code == cli.OK, lines
    return repo


@pytest.mark.parametrize("committed", [False, True], ids=["born-since-the-base", "in-the-base"])
def test_dropping_a_goal_a_capability_realizes_is_recorded_and_the_capability_is_work(shop: Path, committed: bool) -> None:
    if committed:
        commit(shop, "the shop")
    code, lines = answered(shop, "drop", 11)
    assert code == cli.OK, lines
    assert (
        "chose: drop" in (shop / f"docs/kb/{DECISION}.yml").read_text()
        and "know-before-visit" not in (shop / "docs/kb/product/shop/goals.yml").read_text()
    )
    flat = ops.run_work(Target(shop)).value  # the agents' table: the person's view shows the capability once, under its why
    rows = [item for item in flat if item.address == CAPABILITY and str(item.status) == ROW.split(":", 1)[0]]
    assert rows and rows[0].note.endswith(f"realizes: {GOAL} (no in {DECISION})"), flat
    assert w(shop, "check") == (cli.OK, ["ok"])  # work, not a finding: a hand over is not blocked


def test_the_work_leaves_when_the_link_is_re_pointed(shop: Path) -> None:
    assert answered(shop, "drop", 11)[0] == cli.OK
    code, lines = w(shop, "put", json.dumps({"address": CAPABILITY, "realizes": [OTHER]}))
    assert code == cli.OK, lines
    assert not any(line.startswith(ROW) for line in w(shop, "work", "product")[1])


def test_a_hand_remove_still_refuses_while_an_entry_links_to_it(shop: Path) -> None:
    code, lines = w(shop, "remove", GOAL, "--why", "plain words")
    assert code == cli.REFUSED and any(f"{CAPABILITY} links to {GOAL}" in line for line in lines), lines


def test_a_link_to_an_address_nobody_said_no_to_is_still_a_finding(shop: Path) -> None:
    code, lines = w(shop, "put", json.dumps({"address": CAPABILITY, "realizes": ["product/shop/goal/never-was"]}))
    assert code == cli.REFUSED and any("dangling-link" in line for line in lines), lines
