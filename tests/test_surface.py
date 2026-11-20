"""The command surface: flags before or after the verb, help on everything, find, near misses, status, and what an agent is given."""

import asyncio
import json
lazy from pathlib import Path

import pytest
from fastmcp.exceptions import ToolError
from git_porcelain import run_git
from tests.conftest import AGREED, commit, ogy
from verb_cli.testing import assert_help_tree

from ogy import cli
from ogy.mcp_server import build


def test_the_global_flags_work_before_and_after_the_verb(repo: Path) -> None:
    before = ogy(repo, "--rev", "HEAD", "show", "product/app/quantity/fee")
    assert before[0] == cli.OK
    assert cli.run(["show", "product/app/quantity/fee", "--repo", str(repo), "--rev", "HEAD"]) == before
    assert cli.run(["--repo", str(repo), "show", "product/app/quantity/fee", "--rev", "HEAD"]) == before
    assert cli.run(["check", "--repo", str(repo), "--rev", "."]) == (cli.OK, ["ok"])


def test_remove_does_not_ask_for_a_rev(repo: Path) -> None:
    code, _ = ogy(repo, "--rev", "HEAD", "remove", "software/app/handler/lend", "--why", "not needed")
    assert code == cli.OK and not (repo / "docs/kb/software/app/handler/lend.yml").exists()


def test_every_command_and_option_explains_itself() -> None:
    assert_help_tree(cli.parser())


def test_the_renamed_commands_are_gone_and_the_new_ones_are_there(repo: Path) -> None:
    for old in ("context", "work-left", "spec", "removed"):
        with pytest.raises(SystemExit):
            cli.parser().parse_args([old])
    for name in ("find", "status", "kinds", "work", "dropped"):
        assert cli.parser().parse_args([name, *(["x"] if name == "find" else [])]).command == name


def test_the_mcp_descriptions_are_the_commands_own() -> None:
    tools = {tool.name: tool.description or "" for tool in asyncio.run(build().list_tools())}
    assert "usage:" not in " ".join(tools.values()) and tools["find"].startswith("search live and removed entries")


def test_find_lists_live_and_removed_entries_as_a_table(repo: Path) -> None:
    ogy(repo, "remove", "software/app/handler/lend", "--why", "not needed")
    code, lines = ogy(repo, "find", "app")
    assert code == cli.OK and any(line.startswith("product/app/quantity/fee   quantity") for line in lines)
    assert any(line.startswith("software/app/handler/lend   handler   removed") for line in lines)
    assert [line.split("   ")[0] for line in ogy(repo, "find", "--removed")[1]] == ["software/app/handler/lend"]
    assert [line.split("   ")[0] for line in ogy(repo, "find", "--kind", "quantity")[1]] == ["product/app/quantity/fee"]
    assert ogy(repo, "find", "nothing-like-it") == (cli.OK, ["nothing found"])
    assert ogy(repo, "find", "--kind", "quantty")[0] == cli.NOT_FOUND


def test_find_by_parent_lists_the_parts(repo: Path) -> None:
    _, lines = ogy(repo, "find", "--parent", "product/app/workflow/borrow")
    assert {line.split("   ")[0] for line in lines} == {"product/app/workflow/borrow/step/ask", "product/app/workflow/borrow/end/done"}


def test_a_miss_offers_near_addresses(repo: Path) -> None:
    code, lines = ogy(repo, "show", "product/app/quantity/fe")
    assert code == cli.NOT_FOUND and lines[0].startswith("no entry product/app/quantity/fe (did you mean product/app/quantity/fee")
    assert "did you mean product/app/quantity/fee" in ogy(repo, "put", '{"address": "value/fee", "is": 3}')[1][0]
    assert "did you mean product/app/decision" not in ogy(repo, "show", "product/app/actor/membr")[1][0]
    assert "did you mean product/app/actor/member" in ogy(repo, "show", "product/app/actor/membr")[1][0]


def test_status_counts_an_area_and_saves_nothing(repo: Path) -> None:
    code, lines = ogy(repo, "status")
    assert code == cli.OK and lines[0].startswith("product/app   ")
    assert "findings: 0 (ogy check)" in lines and "work left: 3 (ogy work)" in lines  # D15: the row, the timeout and the page
    assert ogy(repo, "status", "app") == (code, lines)
    assert ogy(repo, "status", "ap")[1] == ["no layer or area ap (did you mean app?)"]
    assert not (repo / ".git/ogy-rounds").exists()


def test_check_work_and_review_take_an_area(repo: Path) -> None:
    assert ogy(repo, "check", "app") == (cli.OK, ["ok"])
    assert ogy(repo, "work", "app")[0] == cli.FINDINGS
    assert ogy(repo, "review", "app")[0] == cli.OK
    for command in ("check", "work", "review"):
        assert ogy(repo, command, "nope")[0] == cli.NOT_FOUND


def test_work_takes_a_layer_so_the_business_sees_its_own_gaps(repo: Path) -> None:
    every = ogy(repo, "work")[1]
    product, software = ogy(repo, "work", "product")[1], ogy(repo, "work", "software")[1]
    assert any("product/" in line for line in product) and not any("software/" in line for line in product)
    assert not any("product/" in line for line in software)
    assert ogy(repo, "work", "product/app")[1] == product and len(every) >= len(product)


def test_an_agent_gets_a_table_with_its_header_even_when_empty(repo: Path) -> None:
    assert cli.run(["--repo", str(repo), "find", "zzz"], agent=True) == (cli.OK, ["address\tkind\tstate\tsays\tnote"])
    assert cli.run(["--repo", str(repo), "dropped"], agent=True) == (cli.OK, ["why\taddress"])
    assert cli.run(["--repo", str(repo), "check"], agent=True)[1] == ["problem\tpath\taddress\tdetail"]


def test_an_agent_gets_records_and_no_python_reprs(repo: Path) -> None:
    code, lines = cli.run(["--repo", str(repo), "show", "software/app/handler/lend"], agent=True)
    text = "\n".join(lines)
    assert code == cli.OK and "address: software/app/handler/lend" in text and "performs:" in text
    assert "['" not in text and "{'" not in text
    assert "['" not in "\n".join(ogy(repo, "show", "software/app/handler/lend")[1])
    assert "findings: 0" in "\n".join(cli.run(["--repo", str(repo), "status"], agent=True)[1])


def test_a_refusal_is_a_tool_error_over_mcp(repo: Path) -> None:
    with pytest.raises(ToolError, match="did you mean product/app/quantity/fee"):
        asyncio.run(build().call_tool("show", {"repo": str(repo), "address": "product/app/quantity/fe"}))


def test_review_and_check_take_a_layer_and_a_changed_card_shows_what_changed(repo: Path) -> None:
    """Fable's blocker 4: `review product` and `check product` were `no area product` (exit 4)."""
    assert ogy(repo, "--rev", ".", "check", "product")[0] == cli.OK
    assert ogy(repo, "--rev", ".", "check", "software/app")[0] == cli.OK
    round_id = ogy(repo, "--rev", ".", "review", "product")[1][0].split()[-1]
    code, lines = ogy(repo, "--rev", ".", "reply", "yes all", "--said", "All of it", "--where", "ai:claude/1", "--round", round_id)
    assert code == cli.OK, lines
    commit(repo, "agreed")
    flow = repo / "docs/kb/product/app/workflow/borrow.yml"
    flow.write_text(flow.read_text().replace("The member asks.", "The member begs."))
    commit(repo, "edited")
    code, lines = ogy(repo, "--rev", ".", "review", "product")
    assert code == cli.OK and "   since you agreed: step/ask: says: The member asks. -> The member begs." in lines, lines


OLD_YES = AGREED.replace("000000000000", "'a1b2c3d4e5f6'")  # a hash the kinds of its day took: no rehash today matches it
LONG = "A tool is lent to a member who asks for it, names the day it is wanted and waits for the lender to say yes."


def test_since_you_agreed_reads_the_commit_that_wrote_the_yes_and_shows_where_a_long_value_differs(repo: Path) -> None:
    """Fable's review, problem 3: the commit that wrote the yes holds the version agreed to. A difference past the first 60
    characters is shown, not cut off. A hash no version rehashes to (taken under older kinds) is read whole."""
    flow = repo / "docs/kb/product/app/workflow/borrow.yml"
    text = flow.read_text()
    flow.write_text(text.replace("says: A tool is lent.\n", f"says: A tool is lent.\nagreed: {OLD_YES}\n", 1))
    commit(repo, "agreed under older kinds")
    lines = ogy(repo, "--rev", ".", "review", "product")[1]
    assert "   since you agreed: no commit holds the version agreed to (2 read): read it whole" in lines, lines
    flow.write_text(text.replace("The member asks.", LONG))
    round_id = ogy(repo, "--rev", ".", "review", "product")[1][0].split()[-1]
    code, lines = ogy(repo, "--rev", ".", "reply", "yes all", "--said", "All of it", "--where", "ai:claude/1", "--round", round_id)
    assert code == cli.OK, lines
    commit(repo, "agreed")
    flow.write_text(flow.read_text().replace("to say yes.", "to say no."))
    commit(repo, "edited")
    lines = ogy(repo, "--rev", ".", "review", "product")[1]
    said = [line for line in lines if line.startswith("   since you agreed: step/ask: says:")]
    assert said == ["   since you agreed: step/ask: says: ...waits for the lender to say yes. -> ...waits for the lender to say no."], lines


def test_since_you_agreed_never_diffs_against_text_nobody_agreed_to(repo: Path) -> None:
    """Fable's second review, problem 2: a yes and an edit in one commit. That commit holds the stored hash but not the version
    agreed to (rehashed, it differs), so the card is read whole, before the next edit and after it."""
    round_id = ogy(repo, "--rev", ".", "review", "product")[1][0].split()[-1]
    code, lines = ogy(repo, "--rev", ".", "reply", "yes all", "--said", "All of it", "--where", "ai:claude/1", "--round", round_id)
    assert code == cli.OK, lines
    flow = repo / "docs/kb/product/app/workflow/borrow.yml"
    flow.write_text(flow.read_text().replace("The member asks.", "The member begs."))
    commit(repo, "agreed and edited")
    whole = "   since you agreed: step/ask: no commit holds the version agreed to (2 read): read it whole"
    lines = ogy(repo, "--rev", ".", "review", "product")[1]
    assert whole in lines and not any("as agreed" in line for line in lines), lines
    flow.write_text(flow.read_text().replace("The member begs.", "The member pleads."))
    commit(repo, "edited again")
    lines = ogy(repo, "--rev", ".", "review", "product")[1]
    assert not any("begs" in line for line in lines if "since you agreed" in line), lines
    assert "   since you agreed: step/ask: no commit holds the version agreed to (3 read): read it whole" in lines, lines


def test_a_half_workflow_commits_on_a_branch_and_landing_refuses_it(repo: Path) -> None:
    """Fable's blocker 8: an end no step reaches yet and a workflow nothing starts are a layer not finished, not a fault."""
    run_git(repo, "checkout", "-q", "-b", "later")
    half = {
        "address": "product/app/workflow/remind",
        "says": "A late borrower is reminded.",
        "src": ["code:app.py#lend"],
        "start": "send",
        "steps": {"send": {"says": "The library sends a reminder.", "cases": {"otherwise": {"then": "sent"}}}},
        "ends": {"sent": {"result": "success", "says": "Sent."}, "ignored": {"result": "failure", "says": "Ignored."}},
    }
    code, lines = ogy(repo, "put", json.dumps(half))
    assert code == cli.OK, lines
    commit(repo, "half a workflow")
    assert ogy(repo, "--rev", ".", "check")[0] == cli.OK
    code, lines = ogy(repo, "--rev", ".", "check", "--landing")
    assert code == cli.FINDINGS and {line.split(":")[0] for line in lines} == {"end-unreached", "never-started"}, lines
