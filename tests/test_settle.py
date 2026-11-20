"""Decisions settle entries: the option in force, checks D2, D4 to D6 and D10, agreement, labels and the review queue."""

from pathlib import Path

from tests.conftest import entry

from ogy.check import check
from ogy.model import Problem
from ogy.ontology import Ontology, packaged
from ogy.settle import check_decisions, decisions
from ogy.snapshot import Snapshot, build, load
from ogy.source import WorktreeSource
from ogy.status import Agreement, Label, Status, agreement, evidence, label, queue, status

V5 = Path(__file__).parent / "fixtures"
ONTOLOGY = packaged()
VALUES = "- {id: fee, says: The fee., is: 2, unit: EUR}\n- {id: wait, says: The wait., is: 3, unit: days}\n"
OPTIONS = "  one: {label: One, sets: {product/app/quantity/fee: {is: 1}}}\n  two: {label: Two, sets: {product/app/quantity/fee: {is: 2}}}\n"
GUESS = "proposal: {chose: two, why: because}\n"
FEE = "product/app/quantity/fee"
ACTORS = "- {id: member, says: A person who borrows., nature: human}\n"


def decision(options: str = OPTIONS, guess: str = GUESS, answers: str = "", name: str = "fee") -> dict[str, str]:
    body = f"question: How much?\noptions:\n{options}{guess}"
    return {f"product/app/decision/{name}.yml": body + (f"answers:\n{answers}" if answers else "")}


def answer(at: str, chose: str, who: str = "human", more: str = "") -> str:
    return f"  - {{chose: {chose}, said: Two please, at: '{at}', where: 'ai:claude/1#2'{more}}}\n"  # who: computed from delegated


def snap(*parts: dict[str, str], values: str = VALUES) -> Snapshot:
    files = {"product/app/actors.yml": ACTORS, "product/app/quantities.yml": values}
    for part in parts:
        files.update(part)
    return build(ONTOLOGY, files)


def problems(snapshot: Snapshot) -> set[tuple[str, str]]:
    return {(str(item.problem), str(item.address)) for item in check_decisions(snapshot, WorktreeSource(V5, ""))}


def agreed(fingerprint: str, at: str = "2026-11-12T10:00:00+01:00") -> str:
    return f"agreed: {{at: '{at}', where: 'ai:claude/1', said: Fine, hash: '{fingerprint}'}}"


def fee_hash(values: str = VALUES) -> str:
    base = snap(values=values)
    found = base.resolve(FEE)
    assert found is not None
    return base.fingerprint(found)


def test_good_decision_has_no_findings() -> None:
    first = snap(decision())
    answered = snap(decision(answers=answer("2026-11-12T10:00:00+01:00", "two")))
    assert problems(first) == set() and problems(answered) == set()


def test_options_set_the_same_slots() -> None:
    options = OPTIONS + "  three: {label: Three, sets: {product/app/quantity/wait: {is: 1}}}\n"
    assert problems(snap(decision(options))) == {("uneven-options", "product/app/decision/fee")}
    fields = OPTIONS + "  three: {label: Three, sets: {product/app/quantity/fee: {says: x}}}\n"
    assert problems(snap(decision(fields))) == {("uneven-options", "product/app/decision/fee")}


def test_sets_may_say_absent() -> None:
    options = OPTIONS + "  no: {label: No, sets: {product/app/quantity/fee: null}}\n"
    assert problems(snap(decision(options))) == set()


def test_one_decision_per_slot() -> None:
    other = decision(name="fee2")
    assert problems(snap(decision(), other)) == {("two-homes", "product/app/decision/fee2")}
    absent = decision("  no: {label: No, sets: {product/app/quantity/fee: null}}\n", "proposal: {chose: no, why: x}\n", name="gone")
    wait = decision(OPTIONS.replace("fee", "wait").replace("is: 1", "is: 3").replace("is: 2", "is: 3"), name="wait")
    assert problems(snap(decision(), wait)) == set()
    assert ("two-homes", "product/app/decision/gone") in problems(snap(decision(), absent))


def test_newest_answer_by_its_time() -> None:
    answers = answer("2026-11-12T10:00:00+01:00", "two") + answer("2026-11-13T10:00:00+01:00", "one")
    force = decisions(snap(decision(answers=answers)))[0].in_force
    assert force is not None and force.option == "one" and force.by_answer
    swapped = answer("2026-11-14T10:00:00+01:00", "two") + answer("2026-11-13T10:00:00+01:00", "one")
    found = decisions(snap(decision(answers=swapped)))[0].in_force
    assert found is not None and found.option == "two"
    guessed = decisions(snap(decision()))[0].in_force
    assert guessed is not None and guessed.option == "two" and not guessed.by_answer


def test_equal_at_is_an_error() -> None:
    answers = answer("2026-11-12T10:00:00+01:00", "two") + answer("2026-11-12T10:00:00+01:00", "two")
    assert ("equal-at", "product/app/decision/fee") in problems(snap(decision(answers=answers)))


def test_entry_must_equal_option_in_force() -> None:
    assert problems(snap(decision(), values="- {id: fee, says: The fee., is: 1, unit: EUR}\n")) == {
        ("not-in-force", "product/app/decision/fee")
    }


def test_absent_in_force_means_no_entry() -> None:
    no = decision("  no: {label: No, sets: {product/app/quantity/fee: null}}\n", "proposal: {chose: no, why: x}\n")
    assert problems(snap(no)) == {("not-in-force", "product/app/decision/fee")}
    assert problems(snap(no, values="- {id: wait, says: The wait., is: 3, unit: days}\n")) == set()
    assert problems(snap(decision(), values="- {id: wait, says: The wait., is: 3, unit: days}\n")) == {
        ("not-in-force", "product/app/decision/fee")
    }


def test_unanswered_decision_needs_a_guess() -> None:
    assert problems(snap(decision(guess=""))) == {("no-guess", "product/app/decision/fee")}


def test_an_answer_chooses_the_option_and_agrees_to_no_sentence() -> None:
    silent = snap(decision(answers=answer("2026-11-12T10:00:00+01:00", "two")))
    assert problems(silent) == set() and status(silent, entry(silent, FEE)) is Status.NOBODY
    no = decision(
        OPTIONS + "  no: {label: No, sets: {product/app/quantity/fee: null}}\n", answers=answer("2026-11-12T10:00:00+01:00", "no")
    )
    assert problems(snap(no, values="- {id: wait, says: x, is: 3, unit: days}\n")) == set()


def test_problem_names_are_the_spec_names() -> None:
    names = {item.value for item in Problem}
    assert {"uneven-options", "two-homes", "equal-at", "not-in-force", "bad-delegation", "no-guess"} <= names and "bad-quote" not in names


def agreed_kb(fingerprint: str | None = None) -> Snapshot:
    stamp = agreed(fingerprint or fee_hash())
    return snap(values=f"- {{id: fee, says: The fee., is: 2, unit: EUR, {stamp}}}\n- {{id: wait, says: The wait., is: 3, unit: days}}\n")


def test_status_question_waiting() -> None:
    snapshot = snap(decision())
    assert status(snapshot, entry(snapshot, FEE)) is Status.QUESTION


def test_status_decided_by_you() -> None:
    snapshot = agreed_kb()
    assert agreement(snapshot, entry(snapshot, FEE)) is Agreement.AGREED
    assert status(snapshot, entry(snapshot, FEE)) is Status.BY_YOU


def test_status_changed_since_agreed() -> None:
    snapshot = agreed_kb("000000000000")
    assert agreement(snapshot, entry(snapshot, FEE)) is Agreement.CHANGED
    assert status(snapshot, entry(snapshot, FEE)) is Status.CHANGED
    snapshot = agreed_kb()
    assert status(snapshot, entry(snapshot, FEE)) is Status.BY_YOU and evidence_findings(snapshot) == set()


def test_status_decided_by_ai() -> None:
    snapshot = snap()
    assert status(snapshot, entry(snapshot, FEE)) is Status.NOBODY and label(snapshot, entry(snapshot, FEE)) is Label.AI


def test_label_follows_src() -> None:
    def labelled(src: str) -> Label:
        values = f"- {{id: fee, says: The fee., is: 2, unit: EUR, src: {src}}}\n"
        snapshot = snap(values=values)
        return label(snapshot, entry(snapshot, FEE))

    answered = snap(decision(answers=answer("2026-11-12T10:00:00+01:00", "two")))
    assert label(answered, entry(answered, FEE)) is Label.WORDS
    assert labelled('["code:src/a.py#f", "doc:docs/a.md#x"]') is Label.DOCS
    assert labelled('["code:src/a.py#f"]') is Label.CODE
    assert labelled("[]") is Label.AI


def test_an_answered_entry_names_the_choice_and_its_code_source() -> None:
    values = '- {id: fee, says: The fee., is: 2, unit: EUR, src: ["code:src/a.py#f"]}\n'
    snapshot = snap(decision(answers=answer("2026-11-12T10:00:00+01:00", "two")), values=values)
    shown = evidence(snapshot, entry(snapshot, FEE))
    assert shown == "You chose two in product/app/decision/fee; from code: code:src/a.py#f"


def test_only_ai_decided_entries_are_cards() -> None:
    values = '- {id: fee, says: The fee., is: 2, unit: EUR, src: ["code:src/a.py#f"]}\n- {id: wait, says: The wait., is: 3, unit: days}\n'
    cards = queue(snap(values=values))
    assert [(card.kind, str(card.address)) for card in cards if card.address.kind == "quantity"] == [("yes", "product/app/quantity/wait")]
    assert "product/app/actor/member" in {str(card.address) for card in cards}
    cards = queue(agreed_kb())
    assert FEE not in {str(card.address) for card in cards}


def test_queue_lists_questions_first_and_at_most_seven() -> None:
    many = "".join(f"- {{id: v{n}, says: S{n}., is: {n}, unit: days}}\n" for n in range(10))
    cards = queue(snap(decision(), values=VALUES + many))
    assert len(cards) == 7 and cards[0].kind == "question" and cards[1].kind == "yes"


def test_example_tool_library_is_settled(ontology: Ontology) -> None:
    source = WorktreeSource(V5, "example-tool-library")
    snapshot = load(source, ontology)
    fee = snapshot.resolve("product/library/quantity/late-fee")
    assert check_decisions(snapshot, source) == [] and fee is not None
    assert status(snapshot, fee) is Status.BY_YOU
    assert queue(snapshot) == []  # the owner agreed to the owner actor


def test_example_ogy_kb_newest_answer_is_in_force(ontology: Ontology) -> None:
    source = WorktreeSource(V5, "example-ogy-kb")
    snapshot = load(source, ontology)
    force = decisions(snapshot)[0].in_force
    assert check_decisions(snapshot, source) == [] and force is not None and force.option == "ledger"


def test_an_answer_note_and_paraphrase_are_outside_the_fingerprint() -> None:
    plain = answer("2026-11-12T10:00:00+01:00", "two")
    noted = answer("2026-11-12T10:00:00+01:00", "two", more=", note: for now").replace("Two please", "Two for now")
    one, two = snap(decision(answers=plain)), snap(decision(answers=noted))
    address = one.resolve("product/app/decision/fee")
    assert address is not None and one.fingerprint(address) == two.fingerprint(address)
    assert decisions(two)[0].answers[0].note == "for now" and decisions(two)[0].in_force.note == "for now"  # type: ignore[union-attr]


def test_a_guess_that_rests_on_the_owner_keeps_a_paraphrase() -> None:
    heard = decision(guess="proposal: {chose: two, why: because, heard: Two seems right}\n")
    assert problems(snap(heard)) == set() and decisions(snap(heard))[0].heard is not None
    quoted = decision(guess="proposal: {chose: two, why: because, heard: {message: product/app/message/a, quote: Two}}\n")
    found = {(str(i.problem), str(i.address)) for i in check(snap(quoted), WorktreeSource(V5, ""))}
    assert ("wrong-type", "product/app/decision/fee/proposal") in found  # a paraphrase is one line of text, never a quote


def test_an_agent_answers_only_under_a_persons_answer() -> None:
    gave = (
        "question: Who decides the fee?\noptions:\n  agent: {label: The agent, sets: {product/app/quantity/wait: {is: 3}}}\n"
        "proposal: {chose: agent, why: x}\n"
    )
    person = {"product/app/decision/fees-delegated.yml": gave + "answers:\n" + answer("2026-11-11T10:00:00+01:00", "agent")}
    nobody = {"product/app/decision/fees-delegated.yml": gave}
    delegated = ", delegated: product/app/decision/fees-delegated"
    ok = snap(decision(answers=answer("2026-11-13T10:00:00+01:00", "two", "ai", delegated)), person)
    assert problems(ok) == set() and decisions(ok)[0].in_force.delegated  # type: ignore[union-attr]
    bad = {("bad-delegation", "product/app/decision/fee")}
    assert problems(snap(decision(answers=answer("2026-11-13T10:00:00+01:00", "two", "ai", delegated)), nobody)) == bad


def evidence_findings(snapshot: Snapshot) -> set[tuple[str, str]]:
    """No-evidence findings: a person's yes is evidence of its own."""
    return {
        (str(i.problem), str(i.address))
        for i in check(snapshot, WorktreeSource(V5, ""))
        if i.problem is Problem.NO_EVIDENCE and str(i.address) == FEE
    }


def test_a_question_card_reads_alone_with_why_and_what_each_option_makes_true() -> None:
    body = decision()
    path = next(iter(body))
    body[path] = body[path].replace("question: How much?\n", "question: How much?\ncontext: Members asked for a lower fee.\n")
    card = queue(snap(body))[0]
    assert card.context == "Members asked for a lower fee."
    assert dict(zip((key for key, _ in card.options), card.then, strict=True)) == {"two": (f"{FEE}: is = 2",), "one": (f"{FEE}: is = 1",)}
