"""The bd runner (tools/ogy_beads.py, decision software/cli/decision/work-to-tracker): it plans create, rewrite and close from
`ogy work --tracker` and the open beads labelled ogy-work, never touches a bead without the label, and writes only with --apply."""

import json

import pytest
from beads_client import Bd, Bead
from beads_client.testing import Script
from tools.ogy_beads import ADDRESS, FINGERPRINT, LABEL, Action, Item, apply, plan

A, B, C = "product/app/rule/a", "product/app/rule/b", "product/app/rule/c"


def _item(key: str, fingerprint: str = "f1") -> Item:
    return Item(key, f"unbuilt: {key}", fingerprint, f"brief of {key}")


def _bead(id_: str, key: str, fingerprint: str = "f1", labels: tuple[str, ...] = (LABEL,)) -> Bead:
    return Bead(id_, labels=labels, metadata={ADDRESS: key, FINGERPRINT: fingerprint})


@pytest.mark.parametrize(
    ("items", "beads", "wanted"),
    [
        ([_item(A)], [], [("create", A, "")]),  # a work item with no bead
        ([_item(A, "f2")], [_bead("t-1", A)], [("rewrite", A, "t-1")]),  # its entry changed
        ([_item(A)], [_bead("t-1", A)], []),  # current: nothing to do
        ([], [_bead("t-1", A)], [("close", A, "t-1")]),  # built or removed: the work left no longer lists it
        ([], [_bead("t-9", B, labels=("other",))], []),  # a bead without the label is never touched
        ([_item(A), _item(C)], [_bead("t-2", B)], [("create", A, ""), ("create", C, ""), ("close", B, "t-2")]),
    ],
    ids=["create", "rewrite", "current", "close", "unlabelled", "mixed"],
)
def test_the_plan_makes_the_open_ogy_beads_match_the_work_left(
    items: list[Item], beads: list[Bead], wanted: list[tuple[str, str, str]]
) -> None:
    assert [(action.kind, action.key, action.bead) for action in plan(items, beads)] == wanted


def test_apply_creates_with_the_label_then_writes_the_address_and_fingerprint() -> None:
    script = Script().say(json.dumps({"id": "t-5"}))
    bd = Bd("test", exe="bd", run=script)
    apply([Action("create", A, item=_item(A)), Action("close", B, "t-2")], bd)
    create, update, close = (call[3:] for call in script.calls)  # past `bd --actor test`
    assert create[0] == "create" and LABEL in create
    assert update[:2] == ["update", "t-5"] and json.loads(update[update.index("--metadata") + 1]) == {ADDRESS: A, FINGERPRINT: "f1"}
    assert close[:2] == ["close", "t-2"]
