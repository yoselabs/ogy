"""The write commands: put and answer; each checked, atomic and under the lock."""

import asyncio
import json
lazy from pathlib import Path

import any_yaml
import pytest
from fastmcp.exceptions import ToolError
from git_porcelain import git_dir
from process_lock import ProcessLock
from tests.conftest import commit, dig, ogy

from ogy import cli, ops
from ogy.mcp_server import build
from ogy.target import Target

OPTIONS = "{one: {label: One, sets: {product/app/quantity/fee: {is: 1}}}, two: {label: Two, sets: {product/app/quantity/fee: {is: 2}}}}"


def w(repo: Path, *argv: str) -> tuple[int, list[str]]:
    return ogy(repo, "--rev", ".", *argv)


def put(repo: Path, address: str, **fields: object) -> tuple[int, list[str]]:
    return w(repo, "put", json.dumps({"address": address, **fields}))


def tree(repo: Path) -> dict[str, str]:
    return {p.relative_to(repo).as_posix(): p.read_text() for p in sorted((repo / "docs/kb").rglob("*.yml"))}


@pytest.fixture
def decided(repo: Path) -> Path:
    code, lines = put(
        repo,
        "product/app/decision/fee-amount",
        question="How much is the fee?",
        options=any_yaml.load(OPTIONS),
        proposal={"chose": "two", "why": "a guess"},
    )
    assert code == cli.OK, lines
    return repo


WAIT = {"says": "The wait.", "is": 3, "unit": "days", "src": ["code:app.py#lend"]}


def test_put_adds_an_entry_that_checks_clean(repo: Path) -> None:
    code, lines = put(repo, "product/app/quantity/wait", **WAIT)
    assert (code, lines) == (cli.OK, ["added product/app/quantity/wait"])
    assert "id: wait" in (repo / "docs/kb/product/app/quantities.yml").read_text()
    assert w(repo, "check")[0] == cli.OK


def test_put_takes_kind_area_and_id_for_an_address(repo: Path) -> None:
    record = json.dumps({"kind": "quantity", "layer": "product", "area": "app", "id": "wait", **WAIT})
    assert w(repo, "put", record) == (cli.OK, ["added product/app/quantity/wait"])


def test_put_takes_an_array_in_one_call_and_changes_what_exists(repo: Path) -> None:
    records = [
        {"address": "product/app/quantity/wait", **WAIT},
        {"address": "product/app/quantity/fee", "is": 5},
        {"address": "product/app/quantity/fee", "title": "A fee"},
    ]
    assert w(repo, "put", json.dumps(records[:2])) == (cli.OK, ["added product/app/quantity/wait", "changed product/app/quantity/fee"])
    text = (repo / "docs/kb/product/app/quantities.yml").read_text()
    assert "is: 5" in text and "The fee." in text  # the fields not named stay
    fee = "product/app/quantity/fee"
    assert put(repo, fee, title="A name")[0] == cli.OK and put(repo, fee, title=None)[0] == cli.OK
    assert "title" not in (repo / "docs/kb/product/app/quantities.yml").read_text() and w(repo, "check") == (cli.OK, ["ok"])


def test_put_reads_yaml_arguments_a_file_and_several_arguments(repo: Path, tmp_path: Path) -> None:
    yaml_text = "- {address: product/app/quantity/wait, says: The wait., is: 3, unit: days, src: [code:app.py#lend]}\n"
    assert w(repo, "put", yaml_text) == (cli.OK, ["added product/app/quantity/wait"])
    file = tmp_path / "more.yml"
    file.write_text("- {address: product/app/quantity/late, says: Late., is: 1, unit: days, src: [code:app.py#lend]}\n")
    two = json.dumps({"address": "product/app/quantity/fee", "is": 9})
    assert w(repo, "put", two, "--file", str(file)) == (cli.OK, ["changed product/app/quantity/fee", "added product/app/quantity/late"])


def test_put_checks_the_batch_together_and_writes_nothing_when_one_is_refused(repo: Path) -> None:
    before = tree(repo)
    good = {"address": "product/app/quantity/wait", **WAIT}
    refusals = [
        {"address": "product/app/quantity/fee", "says": "x", "is": 1, "unit": "EUR", "colour": "red"},  # an unknown field
        {"address": "product/app/quantity/other", "says": "x", "src": ["code:app.py#lend"]},  # required fields missing
        {"address": "product/app/quantity/Bad_Id", **WAIT},
        {"address": "product/app/nothing/x"},
        {"address": "product/app/decision/q", "question": "Q?", "answers": [{"chose": "a"}]},  # answers have their own command
        {"address": "product/app/quantity/fee", "agreed": {"hash": "000000000000"}},  # only reply agrees
        {"address": "product/app/quantity/fee", "is": "many"},
        {"address": "product/app/quantity/none-yet", "is": 1},  # a change to what does not exist is an add: it lacks its fields
        {"address": "product/app/workflow/borrow/step/ask/choice/go/nope/x"},
        {"kind": "quantity", "layer": "product", "area": "app"},
        {"address": "product/app/quantity/wait", "kind": "quantity", "layer": "product", "area": "app", "id": "wait"},
    ]
    for bad in refusals:
        code, lines = w(repo, "put", json.dumps([good, bad]))
        assert code == cli.REFUSED and lines[0].startswith("refused:") and "record 2" in lines[0], (bad, lines)
        assert tree(repo) == before
    assert w(repo, "put", json.dumps([good, good]))[0] == cli.REFUSED and tree(repo) == before  # the same address twice
    assert w(repo, "put")[0] == cli.REFUSED and w(repo, "put", "not: [valid")[0] == cli.REFUSED and tree(repo) == before


def test_a_batch_that_breaks_the_base_is_put_back(repo: Path) -> None:
    before = tree(repo)
    ok = {"address": "product/app/quantity/wait", **WAIT}
    code, lines = w(
        repo,
        "put",
        json.dumps(
            [
                ok,
                {
                    "address": "software/app/interface/page2",
                    "says": "Another page.",
                    "form": "web",
                    "src": ["code:app.py#lend"],
                    "serves": ["product/app/workflow/borrow/step/nowhere"],
                },
            ]
        ),
    )
    assert code == cli.REFUSED and "dangling-link" in lines[0]
    assert tree(repo) == before


def test_a_decision_and_the_entry_its_options_set_arrive_in_one_call(repo: Path) -> None:
    options = {
        "keep": {"label": "Keep", "sets": {"product/app/capability/late-fee": {"says": "A late fee is charged."}}},
        "drop": {"label": "Drop", "sets": {"product/app/capability/late-fee": None}},
    }
    records = [
        {
            "address": "product/app/decision/late-fee-q",
            "question": "Keep the late fee?",
            "options": options,
            "proposal": {"chose": "keep", "why": "built"},
        },
        {"address": "product/app/capability/late-fee", "says": "A late fee is charged.", "src": ["code:app.py#lend"]},
    ]
    assert w(repo, "put", json.dumps(records)) == (
        cli.OK,
        ["added product/app/decision/late-fee-q", "added product/app/capability/late-fee"],
    )
    assert w(repo, "check") == (cli.OK, ["ok"])


def test_put_adds_a_part_under_a_parent_of_the_same_call_and_to_one_that_exists(repo: Path) -> None:
    stay = {"address": "product/app/workflow/borrow/step/ask/choice/stay", "label": "Stay", "then": "product/app/workflow/borrow/end/done"}
    assert w(repo, "put", json.dumps(stay))[0] == cli.OK and "stay" in (repo / "docs/kb/product/app/workflow/borrow.yml").read_text()
    options = {"keep": {"label": "Keep", "sets": {"product/app/quantity/fee": {"is": 2}}}}
    records = [
        {"address": "product/app/decision/q2/proposal", "chose": "keep", "why": "built"},
        # the part comes before its parent: still added after
        {"address": "product/app/decision/q2", "question": "Keep the fee?", "options": options},
    ]
    assert w(repo, "put", json.dumps(records)) == (cli.OK, ["added product/app/decision/q2", "added product/app/decision/q2/proposal"])
    assert w(repo, "check") == (cli.OK, ["ok"])


def test_put_never_reuses_a_removed_id(repo: Path) -> None:
    assert w(repo, "remove", "software/app/handler/lend", "--why", "not needed")[0] == cli.OK
    code, _ = put(
        repo, "software/app/handler/lend", says="x", performs=["product/app/workflow/borrow/step/ask/choice/go"], src=["code:app.py#lend"]
    )
    assert code == cli.REFUSED


def test_new_set_agree_and_message_are_gone(repo: Path) -> None:
    for command in ("new", "set", "agree", "message"):
        with pytest.raises(SystemExit):
            w(repo, command, "x")


SAID = ("--where", "ai:claude/1", "--at", "2026-11-12T10:05:00+01:00")


def test_answer_keeps_a_paraphrase_when_and_where_and_agrees_to_what_it_sets(decided: Path) -> None:
    code, lines = w(decided, "answer", "product/app/decision/fee-amount", "one", "--said", "One euro is enough", *SAID)
    assert code == cli.OK, lines
    assert lines == ["product/app/decision/fee-amount: answered one", "set product/app/quantity/fee"]
    assert "is: 1" in (decided / "docs/kb/product/app/quantities.yml").read_text()
    answers = dig(any_yaml.load((decided / "docs/kb/product/app/decision/fee-amount.yml").read_text()), "answers")
    assert isinstance(answers, list)
    (answered,) = answers
    assert dict(answered) == {"chose": "one", "said": "One euro is enough", "at": "2026-11-12T10:05:00+01:00", "where": "ai:claude/1"}
    assert not list((decided / "docs/kb").rglob("message")) and w(decided, "check") == (cli.OK, ["ok"])
    shown = w(decided, "show", "product/app/quantity/fee")[1]
    assert any("decided by you" in line for line in shown)  # the answer agrees to what the option sets, as its card showed it
    assert "You said (paraphrased): One euro is enough" in w(decided, "show", "product/app/decision/fee-amount")[1]


def test_answer_defaults_to_now_with_an_offset(decided: Path) -> None:
    now = ops.writes.utc_now()
    ops.run_answer(Target(decided, rev="."), "product/app/decision/fee-amount", "one", "One", "ai:claude/1", now=lambda: now)
    assert now.isoformat() in (decided / "docs/kb/product/app/decision/fee-amount.yml").read_text()


def test_answer_note_is_shown_and_listed_by_dropped(decided: Path) -> None:
    kind = "product/app/decision/fee-amount"
    code, lines = w(decided, "answer", kind, "two", "--said", "Two for now", *SAID, "--note", "for now; challenge it later")
    assert code == cli.OK, lines
    assert any("note: for now; challenge it later" in line for line in w(decided, "show", "product/app/quantity/fee")[1])
    assert w(decided, "dropped")[1] == [f"answer with a note (the owner's hedge or condition): {kind}"]
    assert w(decided, "status")[1][-1] == "dropped: 1 (ogy dropped)"
    assert w(decided, "check") == (cli.OK, ["ok"])


def test_answer_refusals_leave_everything_as_it_was(decided: Path) -> None:
    before = tree(decided)
    said = ("--said", "One euro", *SAID)
    for argv in (
        ["product/app/decision/fee-amount", "three", *said],
        ["product/app/decision/none", "one", *said],
        ["product/app/decision/fee-amount", "one", "--said", " ", *SAID],
        ["product/app/decision/fee-amount", "one", "--said", "x", "--where", "nonsense"],
        ["product/app/decision/fee-amount", "one", "--said", "x", "--where", "ai:x", "--at", "2026-11-13"],
        ["product/app/decision/fee-amount", "one", *said, "--delegated", "product/app/decision/fee-amount"],
    ):  # no person's answer
        code, lines = w(decided, "answer", *argv)
        assert code == cli.REFUSED and lines[0].startswith("refused:"), (argv, lines)
    assert tree(decided) == before


def test_an_agent_answers_only_under_a_persons_answer_and_it_is_listed(decided: Path) -> None:
    options = {"agent": {"label": "The agent decides fees", "sets": {"product/app/quantity/fee": {"unit": "EUR"}}}}
    assert (
        put(
            decided,
            "product/app/decision/fees-delegated",
            question="Who decides fees?",
            options=options,
            proposal={"chose": "agent", "why": "asked"},
        )[0]
        == cli.OK
    )
    agent = ("--delegated", "product/app/decision/fees-delegated")
    code, lines = w(decided, "answer", "product/app/decision/fee-amount", "two", "--said", "Two is small", *SAID, *agent)
    assert code == cli.REFUSED and "--delegated" in lines[0]  # the delegation has no person's answer yet
    assert w(decided, "answer", "product/app/decision/fees-delegated", "agent", "--said", "Decide fees for me", *SAID)[0] == cli.OK
    code, lines = w(decided, "answer", "product/app/decision/fee-amount", "one", "--said", "One is small", *SAID, *agent)
    assert code == cli.OK, lines
    text = (decided / "docs/kb/product/app/decision/fee-amount.yml").read_text()
    assert "from:" not in text and "delegated: product/app/decision/fees-delegated" in text
    assert w(decided, "check") == (cli.OK, ["ok"])
    assert any("by AI, for you" in line for line in w(decided, "show", "product/app/quantity/fee")[1])
    assert w(decided, "dropped")[1] == ["answer an agent gave under a delegation (the owner may veto): product/app/decision/fee-amount"]


def test_an_answered_proposal_is_inert_and_a_delegated_answer_is_shown_in_force(decided: Path) -> None:
    options = {"agent": {"label": "The agent decides fees", "sets": {"product/app/quantity/fee": {"unit": "EUR"}}}}
    assert (
        put(
            decided,
            "product/app/decision/fees-delegated",
            question="Who decides fees?",
            options=options,
            proposal={"chose": "agent", "why": "asked"},
        )[0]
        == cli.OK
    )
    assert w(decided, "answer", "product/app/decision/fees-delegated", "agent", "--said", "Decide fees for me", *SAID)[0] == cli.OK
    agent = ("--delegated", "product/app/decision/fees-delegated")
    assert w(decided, "answer", "product/app/decision/fee-amount", "one", "--said", "One is small", *SAID, *agent)[0] == cli.OK
    assert not any("differs" in line for line in w(decided, "dropped")[1])  # the proposal (two) is inert after an answer
    text = "\n".join(w(decided, "review")[1])
    assert "Q1. delegated  product/app/decision/fee-amount" in text and "(recommended)" not in text
    assert "A. One  (in force, an agent's answer under your delegation)" in text and "AI proposal because" not in text
    code, lines = w(decided, "reply", "yes all", "--said", "Fine", "--where", "ai:claude/1", "--at", "2026-11-12T11:00:00+01:00")
    assert code == cli.OK and "product/app/decision/fee-amount answered: one" in lines[0], lines
    assert "delegated" not in "\n".join(w(decided, "review")[1])  # the owner's answer now: no card


def test_answer_that_says_no_removes_the_entry(repo: Path) -> None:
    options = {
        "keep": {"label": "Keep", "sets": {"product/app/capability/late-fee": {"says": "A late fee is charged."}}},
        "drop": {"label": "Drop", "sets": {"product/app/capability/late-fee": None}},
    }
    records = [
        {"address": "product/app/capability/late-fee", "says": "A late fee is charged.", "src": ["code:app.py#lend"]},
        {
            "address": "product/app/decision/late-fee-q",
            "question": "Keep the late fee?",
            "options": options,
            "proposal": {"chose": "keep", "why": "built"},
        },
    ]
    assert w(repo, "put", json.dumps(records))[0] == cli.OK
    commit(repo, "late fee")  # a removal is recorded against what was committed
    code, lines = w(repo, "answer", "product/app/decision/late-fee-q", "drop", "--said", "No late fee", *SAID)
    assert code == cli.OK and "removed product/app/capability/late-fee" in lines, lines
    assert "late-fee" not in (repo / "docs/kb/product/app/capabilities.yml").read_text().replace("late-fee-q", "")
    assert w(repo, "find", "late", "--removed")[1][0].startswith("product/app/capability/late-fee")


def test_a_second_writer_is_refused_while_the_lock_is_held(repo: Path) -> None:
    git = git_dir(repo)
    assert git is not None
    before = tree(repo)
    with ProcessLock.acquire_exclusive(git / "ogy.lock"):
        code, lines = w(repo, "put", json.dumps({"address": "product/app/quantity/fee", "is": 9}))
    assert code == cli.REFUSED and "another ogy write" in lines[0] and tree(repo) == before


def test_writes_work_through_the_mcp_tools(repo: Path) -> None:
    names = {tool.name for tool in asyncio.run(build().list_tools())}
    assert {"put", "answer", "reply"} <= names and not {"new", "set", "agree", "init", "message"} & names
    record = json.dumps([{"address": "product/app/quantity/wait", **WAIT, "says": "- a wait."}])
    result = asyncio.run(build().call_tool("put", {"repo": str(repo), "records": [record]}))
    assert (result.structured_content or {}).get("exit_code") == cli.OK
    assert "- a wait." in (repo / "docs/kb/product/app/quantities.yml").read_text()
    with pytest.raises(ToolError, match="standard input"):
        asyncio.run(build().call_tool("put", {"repo": str(repo), "file": "-"}))


def test_a_put_into_a_new_area_brings_its_area_entry_whose_id_is_the_folder(repo: Path) -> None:
    rule = {"address": "product/loans/rule/late", "says": "A late tool costs a fee.", "src": ["code:app.py#lend"]}
    code, lines = w(repo, "put", json.dumps(rule))
    assert code == cli.REFUSED and "missing-entry" in lines[0] and "product/loans/area/loans" in lines[0]
    wrong = {"address": "product/loans/area/fees", "says": "Fees."}
    code, lines = w(repo, "put", json.dumps([wrong, rule]))
    assert code == cli.REFUSED and "the name of its area" in lines[0]
    code, lines = w(repo, "put", json.dumps([{"address": "product/loans/area/loans", "says": "Loans and their fees."}, rule]))
    assert code == cli.OK and (repo / "docs/kb/product/loans/area.yml").read_text() == "says: Loans and their fees.\n"
    assert w(repo, "check") == (cli.OK, ["ok"]) and "product/loans/area" not in "\n".join(w(repo, "review")[1])


def test_an_answer_removes_a_state_after_the_transition_that_links_to_it(repo: Path) -> None:
    entity = "product/app/entity/loan"
    states = {"open": {"says": "Lent."}, "closed": {"says": "Back."}}
    sets = {f"{entity}/state/closed": {"says": "Back."}, f"{entity}/transition/close": {"to": "closed"}}
    options = {
        "keep": {"label": "Keep", "sets": sets},
        "drop": {"label": "Drop", "sets": {f"{entity}/state/closed": None, f"{entity}/transition/close": None}},
    }
    records = [
        {
            "address": entity,
            "says": "A loan.",
            "src": ["code:app.py#lend"],
            "states": states,
            "transitions": {"close": {"from": ["open"], "to": "closed"}},
        },
        {
            "address": "product/app/decision/loan-close",
            "question": "Do loans close?",
            "options": options,
            "proposal": {"chose": "keep", "why": "built"},
        },
    ]
    code, lines = w(repo, "put", json.dumps(records))
    assert code == cli.OK, lines
    code, lines = w(repo, "answer", "product/app/decision/loan-close", "drop", "--said", "Loans never close", *SAID)
    assert code == cli.OK and f"removed {entity}/state/closed" in lines and f"removed {entity}/transition/close" in lines, lines


def test_a_put_that_drops_parts_needs_a_why_and_records_each(repo: Path) -> None:
    step = "product/app/workflow/borrow/step/ask"
    assert w(repo, "put", json.dumps({"address": f"{step}/choice/skip", "label": "Skip", "then": "done"}))[0] == cli.OK
    commit(repo, "skip")  # a drop is recorded against what was committed
    record = json.dumps({"address": step, "choices": {"go": {"label": "Borrow", "then": "done"}}})
    code, lines = w(repo, "put", record)
    assert code == cli.REFUSED and f"drops {step}/choice/skip" in lines[0] and "--why" in lines[0], lines
    code, lines = w(repo, "put", record, "--why", "Nobody skips")
    assert code == cli.OK, lines
    removed_yml = (repo / "docs/kb/product/app/removed.yml").read_text()
    assert f"{step}/choice/skip" in removed_yml and "Nobody skips" in removed_yml
