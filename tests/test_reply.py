"""`ogy review` keeps its rounds by id; `ogy reply` applies the grammar to the round it answers, keeping a paraphrase, never a quote."""

import asyncio
import json
lazy from pathlib import Path

import any_yaml
import pytest
from fastmcp.exceptions import ToolError
from tests.test_writes import OPTIONS, put, tree, w

from ogy import cli
from ogy import status as status_of
from ogy.mcp_server import build
from ogy.target import Target
lazy from ogy.status import Agreed

WHO = ("--said", "Agreed to the cards", "--where", "ai:claude/1", "--at", "2026-11-12T10:05:00+01:00")


def r(repo: Path, text: str, *more: str) -> tuple[int, list[str]]:
    """The owner's reply as a grammar line, with the agent's paraphrase."""
    return w(repo, "reply", text, *WHO, *more)


def agreed_in(repo: Path) -> dict[str, Agreed]:
    """The entries a person agreed to, with their stamp."""
    return status_of.agreed_in(Target(repo).read()[1])


def round_of(lines: list[str]) -> str:
    return next(line.removeprefix("round ") for line in lines if line.startswith("round r"))


@pytest.fixture
def asked(repo: Path) -> Path:
    """Two sentences decided by AI (cards 1 and 2) and one unanswered decision (Q1), reviewed."""
    code, lines = put(
        repo,
        "product/app/decision/fee-amount",
        question="How much?",
        options=any_yaml.load(OPTIONS),
        proposal={"chose": "two", "why": "a guess"},
    )
    assert code == cli.OK, lines
    for ident, says in (("a-cap", "A member can borrow."), ("b-cap", "A member can return.")):
        assert put(repo, f"product/app/capability/{ident}", says=says, because=["product/app/decision/fee-amount"])[0] == cli.OK
    code, lines = w(repo, "review")
    assert code == cli.OK, lines
    return repo


def status(repo: Path, address: str) -> str:
    return next(line for line in w(repo, "show", address)[1] if line.startswith("status"))


def test_review_numbers_questions_and_cards_and_names_the_round(asked: Path) -> None:
    lines = w(asked, "review")[1]
    text = "\n".join(lines)
    assert "Q1. question  product/app/decision/fee-amount" in text and "A. Two  (recommended)" in text and "B. One" in text
    assert "1. yes  product/app/capability/a-cap" in text and "2. yes  product/app/capability/b-cap" in text
    assert any(line.startswith("round r") for line in lines) and "Reply: yes" in text


def test_reply_agrees_to_every_card_on_the_entry_with_the_paraphrase(asked: Path) -> None:
    code, lines = r(asked, "yes")
    assert code == cli.OK and lines == ["yes: agreed to 4 sentence(s)"], lines
    found = agreed_in(asked)
    assert {"product/app/capability/a-cap", "product/app/capability/b-cap"} <= set(found)
    assert {(item.said, item.where) for item in found.values()} == {("Agreed to the cards", "ai:claude/1")}
    text = (asked / "docs/kb/product/app/capabilities.yml").read_text()
    assert "from:" not in text and "said: Agreed to the cards" in text and "yes" not in text.replace("says", "")
    assert all("decided by you" in status(asked, f"product/app/capability/{k}") for k in ("a-cap", "b-cap"))
    assert w(asked, "check") == (cli.OK, ["ok"])


def test_reply_yes_with_numbers_agrees_to_those_cards(asked: Path) -> None:
    assert r(asked, "yes 2")[0] == cli.OK
    assert set(agreed_in(asked)) == {"product/app/capability/b-cap"}
    assert "nobody agreed" in status(asked, "product/app/capability/a-cap")


def test_reply_changes_a_sentence_and_agrees_to_it(asked: Path) -> None:
    code, lines = r(asked, "1: A member can borrow for 30 days.")
    assert code == cli.OK, lines
    assert "borrow for 30 days." in (asked / "docs/kb/product/app/capabilities.yml").read_text()
    assert "decided by you" in status(asked, "product/app/capability/a-cap")


def test_reply_no_turns_a_sentence_into_a_question(asked: Path) -> None:
    code, lines = w(asked, "reply", "no 1", "--said", "Keep it simpler", "--where", "ai:claude/1")
    assert code == cli.OK and "product/app/decision/reconsider-a-cap" in lines[0], lines
    assert "question waiting" in status(asked, "product/app/capability/a-cap")
    assert "Keep it simpler" in (asked / "docs/kb/product/app/decision/reconsider-a-cap.yml").read_text()
    assert w(asked, "check") == (cli.OK, ["ok"])


def test_reply_chooses_an_option_by_letter_or_key(asked: Path) -> None:
    code, lines = r(asked, "Q1 b")  # the proposal ("two") is A, the other option B
    assert code == cli.OK and lines == ["Q1 b: product/app/decision/fee-amount answered: one"], lines
    assert "is: 1" in (asked / "docs/kb/product/app/quantities.yml").read_text()
    assert w(asked, "check") == (cli.OK, ["ok"])


def test_reply_takes_several_items_at_once(asked: Path) -> None:
    code, lines = r(asked, "yes 1, 2: A member can return a tool., Q1 b, later")
    assert code == cli.OK and len(lines) == 4, lines
    assert "decided by you" in status(asked, "product/app/capability/a-cap") and "decided by you" in status(
        asked, "product/app/capability/b-cap"
    )


def test_a_card_that_changed_since_it_was_shown_is_refused_and_stays(asked: Path) -> None:
    assert put(asked, "product/app/capability/a-cap", says="A member can borrow twice.")[0] == cli.OK
    before = tree(asked)
    code, lines = r(asked, "yes")
    assert code == cli.REFUSED and "changed since it was shown" in lines[0], lines
    assert tree(asked) == before  # nothing applied: nothing is written
    assert "nobody agreed" in status(asked, "product/app/capability/a-cap")
    cards = "\n".join(w(asked, "review")[1])
    assert "product/app/capability/a-cap" in cards and "borrow twice" in cards


def test_other_items_still_apply_when_one_card_is_stale(asked: Path) -> None:
    assert put(asked, "product/app/capability/a-cap", says="A member can borrow twice.")[0] == cli.OK
    code, lines = r(asked, "yes 1, yes 2")
    assert code == cli.FINDINGS and sum(line.startswith("refused") for line in lines) == 1, lines
    assert "decided by you" in status(asked, "product/app/capability/b-cap")


def test_a_reply_that_applies_nothing_writes_nothing(asked: Path) -> None:
    before = tree(asked)
    for text in ("maybe", "yes 9", "Q2 a", "Q1 z", "9: x", "later"):
        code, lines = r(asked, text)
        assert code == (cli.OK if text == "later" else cli.REFUSED), (text, lines)
        assert tree(asked) == before, text
    assert r(asked, " ")[0] == cli.REFUSED and tree(asked) == before


def test_reply_needs_a_round_and_a_paraphrase(repo: Path) -> None:
    code, lines = r(repo, "yes")
    assert code == cli.NOT_FOUND and "no review round" in lines[0]
    with pytest.raises(SystemExit):
        w(repo, "reply", "yes", "--where", "ai:x")
    assert w(repo, "reply", "yes", "--said", " ", "--where", "ai:x", "--round", "r0")[0] == cli.NOT_FOUND


def test_an_agreement_is_only_a_persons(asked: Path) -> None:
    capability = asked / "docs/kb/product/app/capabilities.yml"
    stamp = "  agreed: {at: '2026-11-12T10:05:00+01:00', where: 'ai:x', from: ai, said: Fine, hash: 000000000000}\n"
    capability.write_text(capability.read_text().replace("  says: A member can borrow.\n", "  says: A member can borrow.\n" + stamp))
    assert any("agreed is {at, where, said, hash" in line for line in w(asked, "check")[1])  # no field says who: only a person agrees


def test_rounds_are_kept_by_id_and_a_reply_names_the_round_it_answers(asked: Path) -> None:
    small = round_of(w(asked, "review")[1])
    wide = round_of(w(asked, "review", "--all")[1])
    assert small != wide
    code, lines = r(asked, "yes 1", "--round", small)  # the owner read the 7 cards; a later look-around did not replace them
    assert code == cli.OK and set(agreed_in(asked)) == {"product/app/capability/a-cap"}, lines
    assert r(asked, "yes 1", "--round", "r000000")[0] == cli.NOT_FOUND
    assert r(asked, "yes 1", "--round", "../../x")[0] == cli.NOT_FOUND


def test_a_reply_without_a_round_takes_the_newest_round(asked: Path) -> None:
    assert put(asked, "product/app/capability/a-cap", says="A member can borrow twice.")[0] == cli.OK
    assert w(asked, "review")[0] == cli.OK  # the first round is now stale for card 1; the newest is not
    code, lines = r(asked, "yes 1")
    assert code == cli.OK and set(agreed_in(asked)) == {"product/app/capability/a-cap"}, lines


def test_a_bare_yes_to_a_round_shown_with_all_is_refused(asked: Path) -> None:
    wide = round_of(w(asked, "review", "--all")[1])
    before = tree(asked)
    code, lines = r(asked, "yes", "--round", wide)
    assert code == cli.REFUSED and "--all" in lines[0] and tree(asked) == before
    assert r(asked, "yes 1 2", "--round", wide)[0] == cli.OK  # naming the cards is fine


def test_over_mcp_the_round_is_required(asked: Path) -> None:
    with pytest.raises(ToolError) as error:
        asyncio.run(build().call_tool("reply", {"repo": str(asked), "rev": ".", "text": "yes", "said": "Fine", "where": "ai:x"}))
    assert "name the round" in str(error.value)
    wide = round_of(w(asked, "review")[1])
    done = asyncio.run(
        build().call_tool("reply", {"repo": str(asked), "rev": ".", "text": "yes 1", "said": "Fine", "where": "ai:x", "round": wide})
    )
    assert (done.structured_content or {}).get("exit_code") == cli.OK


def test_review_help_says_it_saves_a_round(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.parser().parse_args(["review", "--help"])
    assert "SAVES the round" in " ".join(capsys.readouterr().out.split())


@pytest.fixture
def heard(repo: Path) -> Path:
    """One question whose proposal rests on what the owner said, paraphrased."""
    cited = {"chose": "two", "why": "the owner leaned to two", "heard": "Two euros seem plenty"}
    code, lines = put(repo, "product/app/decision/fee-amount", question="How much?", options=any_yaml.load(OPTIONS), proposal=cited)
    assert code == cli.OK, lines
    return repo


def test_the_card_of_a_proposal_that_rests_on_the_owner_reads_you_said(heard: Path) -> None:
    text = "\n".join(w(heard, "review")[1])
    assert "You said (paraphrased): Two euros seem plenty. Read as A." in text and "AI guess" not in text


def test_one_yes_records_the_answer_a_proposal_that_rests_on_the_owner_read(heard: Path) -> None:
    assert w(heard, "review")[0] == cli.OK
    code, lines = r(heard, "yes")
    assert code == cli.OK and "product/app/decision/fee-amount answered: two" in lines[0], lines
    text = (heard / "docs/kb/product/app/decision/fee-amount.yml").read_text()
    assert "chose: two" in text and "said: Two euros seem plenty" in text and "from:" not in text
    assert "product/app/decision/fee-amount" not in "\n".join(w(heard, "review")[1])  # the question left the queue
    assert w(heard, "check") == (cli.OK, ["ok"])


def test_yes_to_a_named_question_confirms_only_it_and_a_question_without_words_is_not_confirmed(asked: Path) -> None:
    code, lines = r(asked, "yes Q1")
    assert code == cli.REFUSED and "rests on nothing you said" in lines[0], lines
    assert not (asked / "docs/kb/product/app/decision/fee-amount.yml").read_text().count("answers")
    assert r(asked, "yes")[0] == cli.OK  # a bare yes agrees to the sentences and leaves the question for the owner to choose
    assert "answers" not in (asked / "docs/kb/product/app/decision/fee-amount.yml").read_text()


def test_yes_all_accepts_every_recommendation_with_one_paraphrase(asked: Path) -> None:
    code, lines = w(asked, "reply", "yes all", "--said", "Accepted every recommendation", "--where", "ai:claude/1", "--note", "tentative")
    assert code == cli.OK and "product/app/decision/fee-amount answered: two" in lines[0] and "agreed to 4 sentence(s)" in lines[0], lines
    text = (asked / "docs/kb/product/app/decision/fee-amount.yml").read_text()
    assert "said: Accepted every recommendation" in text and "note: tentative" in text
    assert "decided by you" in status(asked, "product/app/capability/a-cap")
    assert "You said (paraphrased): Accepted every recommendation" in w(asked, "show", "product/app/capability/a-cap")[1]
    assert w(asked, "check") == (cli.OK, ["ok"])


def test_decide_is_yes_all_and_works_in_an_all_round(asked: Path) -> None:
    wide = round_of(w(asked, "review", "--all")[1])
    assert r(asked, "yes", "--round", wide)[0] == cli.REFUSED  # a bare yes stays refused there
    code, lines = r(asked, "decide", "--round", wide)
    assert code == cli.OK and "answered: two" in lines[0], lines


def test_yes_all_reports_a_stale_card_and_applies_the_rest(asked: Path) -> None:
    assert put(asked, "product/app/capability/a-cap", says="A member can borrow twice.")[0] == cli.OK
    code, lines = r(asked, "yes all")
    assert code == cli.OK and "not done: product/app/capability/a-cap changed since it was shown" in lines[0], lines
    assert "nobody agreed" in status(asked, "product/app/capability/a-cap")
    assert "decided by you" in status(asked, "product/app/capability/b-cap")


def test_a_rewritten_card_then_yes_agrees_to_the_others(asked: Path) -> None:
    code, lines = r(asked, "1: A member can borrow for 30 days., yes")
    assert code == cli.OK and not any("refused" in line or "changed since" in line for line in lines), lines
    assert all("decided by you" in status(asked, f"product/app/capability/{k}") for k in ("a-cap", "b-cap"))


def test_a_workflow_is_one_card_and_one_yes_agrees_to_its_parts(repo: Path) -> None:
    lines = w(repo, "review")[1]
    head = next(line for line in lines if line.endswith("product/app/workflow/borrow") or "product/app/workflow/borrow  (" in line)
    label = head.split(".")[0]
    assert not any("product/app/workflow/borrow/step/" in line for line in lines if line[:1].isdigit())  # parts are not cards
    text = "\n".join(lines)
    assert "one yes agrees to" in text and "- step/ask:" in text
    code, out = r(repo, f"{label}: A new sentence.", "--round", round_of(lines))
    assert code != cli.OK and "lists" in "\n".join(out), out
    assert r(repo, f"yes {label}", "--round", round_of(lines))[0] == cli.OK
    assert "decided by you" in status(repo, "product/app/workflow/borrow/step/ask")


def test_a_bare_question_needs_no_proposal_and_is_answered_in_words(repo: Path) -> None:
    """Fable's blocker 6: a decision with no options is a question as it is; with options, the proposal stays required."""
    q = "product/app/decision/wallets"
    code, lines = w(repo, "put", json.dumps({"address": q, "question": "Do we accept wallets?"}))
    assert code == cli.OK, lines
    assert w(repo, "check")[0] == cli.OK
    shown = w(repo, "review")[1]
    assert f"Q1. question  {q}" in shown and "   Answer in words: Q1: <your words>" in shown, shown
    code, lines = r(repo, "yes all", "--round", round_of(shown))
    assert code == cli.OK and lines[-1].endswith(f"not done: {q} has no options: answer it in words (Q1: <your words>)"), lines
    code, lines = r(repo, "Q1: only cards for now", "--round", round_of(shown))
    assert code == cli.OK and lines[-1].endswith("has no option yet: add one that says it (`put`), then `answer` it with a paraphrase")
    options = {"address": q, "options": {"yes": {"label": "Yes"}, "no": {"label": "No"}}}
    code, lines = w(repo, "put", json.dumps(options))
    assert code == cli.REFUSED and "no-proposal" in lines[0], lines
