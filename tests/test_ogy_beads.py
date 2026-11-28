"""The bd runner (tools/ogy_beads.py, decision software/cli/decision/work-to-tracker): it plans create, rewrite and close from
`ogy work --tracker` and the open beads labelled ogy-work, never touches a bead without the label, and writes only with --apply."""

import json
lazy from pathlib import Path

import pytest
from beads_client import Bd, Bead
from beads_client.testing import Script
from tests.conftest import SOURCE, commit
from tests.test_writes import w
from tools.ogy_beads import (
    ADDRESS,
    DECIDED,
    DECISION,
    FINGERPRINT,
    LABEL,
    OPTION,
    Action,
    Answer,
    Item,
    apply,
    main,
    plan,
    plan_decided,
    read_items,
)

from ogy import cli

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
        ([_item(A)], [_bead("t-1", A), Bead("t-3", labels=(LABEL,))], [("close", "", "t-3")]),  # its metadata write failed
    ],
    ids=["create", "rewrite", "current", "close", "unlabelled", "mixed", "no-address"],
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


def test_main_shows_the_plan_and_writes_only_with_apply(repo: Path) -> None:
    rule = {"address": A, "says": "It holds.", "src": [SOURCE]}
    assert w(repo, "put", json.dumps([rule]))[0] == cli.OK
    commit(repo, "a rule")  # the runner reads HEAD
    shown = Script().say("[]").say("[]")  # bd list of ogy-work, then of ogy-decision: none yet
    assert main(["--repo", str(repo)], Bd("test", exe="bd", run=shown)) == 0
    assert [call[3] for call in shown.calls] == ["list", "list"]  # show only: nothing written
    creates = len(plan(read_items(repo, "HEAD"), []))
    applied = Script().say("[]").say("[]")
    for index in range(creates):
        applied.say(json.dumps({"id": f"t-{index}"})).say()  # create answers its id, the metadata update nothing
    assert main(["--repo", str(repo), "--apply"], Bd("test", exe="bd", run=applied)) == 0
    assert [call[3] for call in applied.calls] == ["list", "list", *["create", "update"] * creates]


def test_the_runner_answers_help_and_refuses_an_unknown_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """ADR 0025: `tools/ogy_beads.py --help` prints its usage and changes nothing; an unknown flag exits 2."""
    with pytest.raises(SystemExit) as helped:
        main(["--help"], Bd("test", exe="bd", run=Script()))
    assert helped.value.code == 0 and "--apply" in capsys.readouterr().out
    with pytest.raises(SystemExit) as refused:
        main(["--no-such-flag"], Bd("test", exe="bd", run=Script()))
    assert refused.value.code == 2


D1, D2 = "software/ontology/decision/one", "software/ontology/decision/two"


def _decided(id_: str, decision: str, option: str = "a", labels: tuple[str, ...] = (DECIDED,)) -> Bead:
    return Bead(id_, labels=labels, metadata={DECISION: decision, OPTION: option})


@pytest.mark.parametrize(
    ("beads", "cites", "answers", "wanted"),
    [
        ([_decided("t-1", D1)], {D1}, {D1: Answer("a", "A")}, [("close", D1, "t-1")]),  # a kind file cites it: done
        ([_decided("t-1", D1)], set(), {D1: Answer("b", "B")}, [("rewrite", D1, "t-1")]),  # answered again with another option
        ([_decided("t-1", D1)], set(), {D1: Answer("a", "A")}, []),  # current, not yet built
        ([_decided("t-1", D1, labels=())], {D1}, {}, []),  # without the label it is never touched
        ([_decided("t-1", D1), _decided("t-2", D2)], {D2}, {D1: Answer("a", "A"), D2: Answer("a", "A")}, [("close", D2, "t-2")]),
    ],
    ids=["cited", "re-answered", "current", "unlabelled", "mixed"],
)
def test_a_decision_bead_closes_when_a_kind_file_cites_it_and_follows_a_new_answer(
    beads: list[Bead], cites: set[str], answers: dict[str, Answer], wanted: list[tuple[str, str, str]]
) -> None:
    """Decision software/cli/decision/decision-items-close (computed-close)."""
    assert [(action.kind, action.key, action.bead) for action in plan_decided(beads, cites, answers)] == wanted
