"""`ogy move`: an entry changes area and keeps its id, its agreements and its answers; every address follows it in the same
write and nothing is recorded: `check --base` tells the move from a loss."""

import asyncio
import json
from pathlib import Path

import pytest
from tests.conftest import commit, ogy

from ogy import cli
from ogy.mcp_server import build
from ogy.model import parse_address
from ogy.moves import detect
from ogy.ontology import packaged
from ogy.snapshot import Snapshot
from ogy.snapshot import build as snapshot_build
from ogy.target import Target

STEP = "product/app/workflow/borrow/step/ask"
KB = "docs/kb"


def w(repo: Path, *argv: str) -> tuple[int, list[str]]:
    return ogy(repo, "--rev", ".", *argv)


@pytest.fixture(autouse=True)
def areas(repo: Path) -> None:
    """The areas the tests move into hold their area.yml, as every area must."""
    for area in ("loans", "people", "other"):
        assert w(repo, "put", json.dumps({"address": f"product/{area}/area/{area}", "says": f"The {area}."}))[0] == cli.OK
    commit(repo, "areas")


def agreed(repo: Path) -> None:
    """The owner says `yes all` to the review: the workflow and its parts are agreed."""
    round_id = w(repo, "review")[1][0].split()[-1]
    code, lines = w(repo, "reply", "yes all", "--said", "Agreed to all", "--where", "ai:claude/1", "--round", round_id)
    assert code == cli.OK, lines
    commit(repo, "agreed")


def status(repo: Path, address: str) -> str:
    return next(line for line in w(repo, "show", address)[1] if line.startswith("status"))


def tree(repo: Path) -> dict[str, str]:
    return {p.relative_to(repo).as_posix(): p.read_text() for p in sorted((repo / KB).rglob("*.yml"))}


def fingerprint(repo: Path, address: str) -> str:
    snapshot = Target(repo).read()[1]
    found = parse_address(address, snapshot.ontology)
    assert found is not None
    return snapshot.fingerprint(found)


def base_findings(repo: Path) -> list[str]:
    return w(repo, "check", "--base", "HEAD")[1]


def test_move_keeps_the_fingerprint_and_the_agreement_and_records_nothing(repo: Path) -> None:
    agreed(repo)
    before, printed = status(repo, STEP), fingerprint(repo, "product/app/workflow/borrow")
    assert "decided by you" in before
    code, lines = w(repo, "move", "product/app/workflow/borrow", "product/loans")
    assert code == cli.OK and lines == ["moved product/app/workflow/borrow to product/loans/workflow/borrow"], lines
    assert not (repo / KB / "product/app/workflow/borrow.yml").exists() and (repo / KB / "product/loans/workflow/borrow.yml").exists()
    assert fingerprint(repo, "product/loans/workflow/borrow") == printed  # the address is outside the fingerprint
    assert status(repo, "product/loans/workflow/borrow/step/ask") == before
    assert w(repo, "show", STEP)[0] == cli.NOT_FOUND  # the old address is gone, not forwarded
    assert not list((repo / KB).rglob("removed.yml"))
    assert w(repo, "check") == (cli.OK, ["ok"]) and base_findings(repo) == ["ok"]


def test_move_rewrites_every_address_and_no_words(repo: Path) -> None:
    agreed(repo)
    before = tree(repo)
    assert w(repo, "move", "product/app/workflow/borrow", "product/loans")[0] == cli.OK
    after = tree(repo)
    assert not any("product/app/workflow" in text for text in after.values())  # every link: one write
    assert "product/loans/workflow/borrow/step/ask" in after[f"{KB}/software/app/interface/page.yml"]
    page = f"{KB}/software/app/interface/page.yml"  # its link and the hash of its agreement changed, no word
    assert [line for line in after[page].splitlines() if "said" in line] == [line for line in before[page].splitlines() if "said" in line]


def test_check_against_the_base_tells_a_move_from_a_loss(repo: Path) -> None:
    agreed(repo)
    assert w(repo, "move", "product/app/workflow/borrow", "product/loans")[0] == cli.OK
    assert base_findings(repo) == ["ok"]
    moved = repo / KB / "product/loans/workflow/borrow.yml"
    moved.write_text(moved.read_text().replace("A tool is lent.", "A tool is given."))  # moved and changed: still a move
    assert base_findings(repo) == ["ok"]
    moved.unlink()
    assert any(line.startswith("removed-unrecorded") for line in base_findings(repo))


def test_a_move_then_an_edit_across_two_commits_is_a_move_and_reads_changed(repo: Path) -> None:
    agreed(repo)
    assert w(repo, "move", "product/app/workflow/borrow", "product/loans")[0] == cli.OK
    commit(repo, "moved")
    moved = repo / KB / "product/loans/workflow/borrow.yml"
    moved.write_text(moved.read_text().replace("A tool is lent.", "A tool is given.").replace("The member asks.", "The member begs."))
    commit(repo, "edited")
    assert w(repo, "check", "--base", "HEAD~2")[1] == ["ok"]  # the id arrived once: a move, whatever its fingerprint
    assert "changed since you agreed" in status(repo, "product/loans/workflow/borrow/step/ask")


def test_an_actor_moves_and_the_steps_that_name_it_stay_agreed(repo: Path) -> None:
    agreed(repo)
    before = status(repo, STEP)
    with pytest.raises(SystemExit):
        w(repo, "move", "product/app/actor/member", "product/people", "--why", "x")  # a move has no why: Git keeps the record
    assert w(repo, "move", "product/app/actor/member", "product/people")[0] == cli.OK
    assert "actor: product/people/actor/member" in tree(repo)[f"{KB}/product/app/workflow/borrow.yml"]
    assert not (repo / KB / "product/app/actors.yml").exists()  # the emptied list file is gone
    assert status(repo, STEP) == before  # the step's fingerprint changed with its actor link; its agreement followed
    assert w(repo, "check") == (cli.OK, ["ok"]) and base_findings(repo) == ["ok"]


def test_a_decision_moves_and_what_cites_it_follows(repo: Path) -> None:
    sets = {"keep": {"label": "Keep", "sets": {"product/app/quantity/fee": {"is": 2}}}}
    decision = {"address": "product/app/decision/fee", "question": "Keep the fee?", "options": sets,
                "proposal": {"chose": "keep", "why": "g"}}
    assert w(repo, "put", json.dumps(decision))[0] == cli.OK
    code, lines = w(repo, "remove", "software/app/interface/page", "--why", "product/app/decision/fee")
    assert code == cli.OK, lines
    commit(repo, "removed")
    findings = w(repo, "check")  # the step no view serves now: the move adds nothing to it
    assert w(repo, "move", "product/app/decision/fee", "product/people")[0] == cli.OK
    assert "why: product/people/decision/fee" in (repo / KB / "software/app/removed.yml").read_text()  # the ledger follows
    assert w(repo, "check") == findings and base_findings(repo) == findings[1]


def test_the_layer_may_change_when_the_kind_allows_it_and_is_refused_when_it_does_not(repo: Path) -> None:
    before = tree(repo)
    goals = repo / KB / "product/app/goals.yml"
    goals.write_text("- {id: lend, says: Members borrow tools., src: ['code:app.py#lend']}\n")
    quantities = repo / KB / "product/app/quantities.yml"
    quantities.write_text(quantities.read_text() + "- {id: spare, says: Spare tools., is: 1, unit: tool, src: ['code:app.py#lend']}\n")
    commit(repo, "a goal")
    before = tree(repo)
    code, lines = w(repo, "move", "product/app/goal/lend", "software/app")
    assert code == cli.REFUSED and "goal may live in the layers" in lines[0] and tree(repo) == before
    assert w(repo, "move", "software/app/interface/page", "product/app")[0] == cli.REFUSED  # a view is software only
    assert w(repo, "move", "product/app/quantity/fee", "software/app")[0] == cli.REFUSED  # a product timeout waits on it
    assert w(repo, "move", "product/app/quantity/spare", "software/app")[0] == cli.OK
    assert (repo / KB / "software/app/quantities.yml").exists() and w(repo, "check") == (cli.OK, ["ok"])


def test_a_move_is_refused_when_the_target_exists_or_was_removed(repo: Path) -> None:
    other = repo / KB / "product/other/actors.yml"
    other.parent.mkdir(parents=True, exist_ok=True)
    other.write_text("- {id: member, says: Another person., nature: human, src: ['code:app.py#lend']}\n")
    before = tree(repo)
    code, lines = w(repo, "move", "product/app/actor/member", "product/other")
    assert code == cli.REFUSED and "exists" in lines[0] and tree(repo) == before
    for argv in (["product/app/actor/member", "product/app"], ["product/app/actor/member", "product/a/b/c"],
                 [STEP, "product/loans"], ["product/shared/term/land", "product/loans"]):
        assert w(repo, "move", *argv)[0] in (cli.REFUSED, cli.USAGE, cli.NOT_FOUND), argv
    assert tree(repo) == before
    fee = "- {id: fee, says: Another fee., is: 1, unit: EUR, src: ['code:app.py#lend']}\n"
    (repo / KB / "product/other/quantities.yml").write_text(fee)
    assert w(repo, "remove", "product/other/quantity/fee", "--why", "not wanted")[0] == cli.OK
    code, lines = w(repo, "move", "product/app/quantity/fee", "product/other")
    assert code == cli.REFUSED and "never reused" in lines[0]


def test_move_works_through_the_mcp_tools(repo: Path) -> None:
    assert "move" in {tool.name for tool in asyncio.run(build().list_tools())}
    result = asyncio.run(build().call_tool("move", {"repo": str(repo), "address": "product/app/quantity/fee", "area": "product/loans"}))
    assert (result.structured_content or {}).get("exit_code") == cli.OK and (repo / KB / "product/loans/quantities.yml").exists()
    with pytest.raises(Exception, match="area"):
        asyncio.run(build().call_tool("move", {"repo": str(repo), "address": "product/loans/quantity/fee"}))


def test_an_entry_a_decision_in_force_sets_can_move_and_the_answer_still_counts(repo: Path) -> None:
    sets = {n: {"label": n, "sets": {"product/app/quantity/fee": {"is": i}}} for i, n in ((1, "one"), (2, "two"))}
    decision = {"address": "product/app/decision/fee", "question": "How much?", "options": sets, "proposal": {"chose": "two", "why": "g"}}
    assert w(repo, "put", json.dumps(decision))[0] == cli.OK
    code, lines = w(repo, "answer", "product/app/decision/fee", "one", "--said", "One", "--where", "ai:x",
                    "--at", "2026-11-12T10:05:00+01:00")
    assert code == cli.OK, lines
    commit(repo, "answered")
    dropped = w(repo, "dropped")
    code, lines = w(repo, "move", "product/app/quantity/fee", "product/loans")
    assert code == cli.OK, lines
    text = (repo / KB / "product/app/decision/fee.yml").read_text()
    assert "product/loans/quantity/fee" in text and "product/app/quantity/fee" not in text
    assert "is: 1" in (repo / KB / "product/loans/quantities.yml").read_text()
    assert w(repo, "check") == (cli.OK, ["ok"]) and base_findings(repo) == ["ok"]
    assert w(repo, "dropped") == dropped  # a move drops nothing


def test_a_move_into_an_area_without_its_area_entry_is_refused_and_the_area_entry_stays(repo: Path) -> None:
    before = tree(repo)
    code, lines = w(repo, "move", "product/app/quantity/fee", "product/elsewhere")
    assert code == cli.REFUSED and "missing-entry" in lines[0] and "product/elsewhere/area/elsewhere" in lines[0] and tree(repo) == before
    code, lines = w(repo, "move", "product/app/area/app", "product/loans")
    assert code == cli.REFUSED and "does not move" in lines[0]


def test_the_fingerprint_breaks_a_tie_between_two_of_one_kind_and_id() -> None:
    def kb(**areas: str) -> Snapshot:
        return snapshot_build(packaged(), {f"product/{area}/actors.yml": f"- {{id: member, says: {says}, nature: human}}\n"
                                           for area, says in areas.items()})
    base, now = kb(app="A member.", other="Another member."), kb(loans="Another member.", people="A member.")
    found = detect(base, now)
    assert {str(old): str(new) for old, new in found.items()} == {
        "product/app/actor/member": "product/people/actor/member", "product/other/actor/member": "product/loans/actor/member"}
    assert detect(base, kb(loans="A changed member.", people="Another changed member.")) == {}  # no fingerprint matches: a loss


def test_a_rename_gives_a_new_id_every_link_follows_and_check_base_tells_it_from_a_loss(repo: Path) -> None:
    agreed(repo)
    assert w(repo, "move", "product/app/actor/member", "product/app/actor/borrower")[0] == cli.OK
    assert w(repo, "show", "product/app/actor/borrower")[0] == cli.OK and w(repo, "show", "product/app/actor/member")[0] == cli.NOT_FOUND
    assert "product/app/actor/borrower" in tree(repo)[f"{KB}/product/app/workflow/borrow.yml"]
    assert "decided by you" in status(repo, STEP)
    assert not list((repo / KB).rglob("removed.yml"))
    assert w(repo, "check") == (cli.OK, ["ok"]) and base_findings(repo) == ["ok"]
    assert w(repo, "move", "product/app/actor/borrower", "product/app/workflow/borrower")[0] != cli.OK  # the kind stays
