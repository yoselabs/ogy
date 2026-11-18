"""Field types, common fields, requirements and flow checks."""

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from ogy.model import Problem

if TYPE_CHECKING:
    from conftest import Kb

type Make = Callable[[dict[str, str | None] | None], Kb]

VALUES = "- {id: fee, says: The fee., is: 2, unit: EUR}\n- {id: wait, says: The wait., is: 3, unit: days}\n"
CALLEE = ("says: Callee.\ntrigger: called\nstart: only\nsteps:\n  only:\n    cases:\n"
          "      a: {order: 1, when: {text: x}, then: good}\n      otherwise: {then: bad}\n"
          "ends:\n  good: {result: success, says: G.}\n  bad: {result: failure, says: B.}\n")


def only(found: set[tuple[Problem, str]], problem: Problem) -> set[str]:
    return {where for kind, where in found if kind is problem}


def stamp(at: str = "2026-11-12T10:05:00+01:00", where: str = "ai:claude/1#2", who: str = "human", fingerprint: str = "ca3445729b96",
          said: str = "Yes") -> str:
    return f"{{at: '{at}', where: '{where}', from: {who}, said: '{said}', hash: '{fingerprint}'}}"


def agreed(value: str | None = None, **given: str) -> dict[str, str | None]:
    """The member actor with a person's yes on it (`agreed`)."""
    return {"product/app/actors.yml": f"- {{id: member, says: A person., nature: human, agreed: {value or stamp(**given)}}}\n"}


def test_good_base_has_no_findings(kb: Make) -> None:
    assert kb(None).findings() == set()


def test_unknown_field_and_missing_field(kb: Make) -> None:
    found = kb({"product/app/actors.yml": "- {id: member, colour: red}\n"}).findings()
    assert found == {(Problem.UNKNOWN_FIELD, "product/app/actor/member"), (Problem.MISSING_FIELD, "product/app/actor/member")}


def test_enum_value_outside_of_is_wrong_type(kb: Make) -> None:
    found = kb({"product/app/actors.yml": "- {id: member, says: x, nature: robot}\n"}).findings()
    assert found == {(Problem.WRONG_TYPE, "product/app/actor/member")}


@pytest.mark.parametrize(("where", "ok"), [("ai:claude/1#2", True), ("jira:LIB-4", True), ("https://x.test", False),
                                           ("ai:", False), ("slack:x", False), ("noscheme", False)])
def test_uri_scheme_must_be_listed(kb: Make, where: str, ok: bool) -> None:
    assert (kb(agreed(where=where)).findings() == set()) is ok


@pytest.mark.parametrize(("at", "ok"), [("2026-11-12T10:05:00+01:00", True), ("2026-11-12T10:05:00", False), ("2026-11-12", False),
                                        ("2026-11-12T10:05:00Z", True), ("later", False)])
def test_time_needs_date_time_and_offset(kb: Make, at: str, ok: bool) -> None:
    assert (kb(agreed(at=at)).findings() == set()) is ok


def test_number_is_a_yaml_number_not_text(kb: Make) -> None:
    found = kb({"product/app/values.yml": '- {id: fee, says: The fee., is: "2", unit: EUR}\n'}).findings()
    assert found == {(Problem.WRONG_TYPE, "product/app/value/fee")}


def when(text: str, reads: str) -> dict[str, str | None]:
    flow = ("says: S.\ntrigger: actor\nstart: sys\nsteps:\n  sys:\n    cases:\n"
            f"      go: {{order: 1, when: {{text: {text}, reads: {reads}}}, then: done}}\n"
            "      otherwise: {then: done}\nends:\n  done: {result: success, says: D.}\n")
    return {"product/app/workflow/sys.yml": flow}


def test_expr_reads_are_checked_links(kb: Make) -> None:
    assert kb({**when("the fee", "[product/app/value/fee]"), "product/app/values.yml": VALUES}).findings() == set()
    found = kb({**when("the fee", "[product/app/value/nothing, product/app/actor/member]"), "product/app/values.yml": VALUES}).findings()
    assert (Problem.DANGLING_LINK, "product/app/workflow/sys/step/sys/case/go") in found
    assert (Problem.LINK_KIND, "product/app/workflow/sys/step/sys/case/go") in found


def test_expr_text_is_not_parsed(kb: Make) -> None:
    assert kb({**when('"2 >= ((( and or"', "[]"), "product/app/values.yml": VALUES}).findings() == set()


DECISION = """\
question: How much?
options:
  one: {label: Two, sets: {product/app/value/fee: {is: 2}}}
  none: {label: None, sets: {product/app/value/fee: null}}
guess: {chose: one, why: Small.}
"""


def test_sets_names_declared_fields_of_real_entries(kb: Make) -> None:
    base = {"product/app/values.yml": VALUES, "product/app/decision/fee.yml": DECISION}
    assert kb(base).findings() == set()
    wrong = DECISION.replace("{is: 2}", "{is: low, colour: red}").replace("product/app/value/fee: null", "nothing/at/all: null")
    found = kb({**base, "product/app/decision/fee.yml": wrong}).findings()
    assert only(found, Problem.WRONG_TYPE) == {"product/app/decision/fee/option/one", "product/app/decision/fee/option/none"}
    assert only(found, Problem.UNKNOWN_FIELD) == {"product/app/decision/fee/option/one"}


def test_sets_may_say_absent_and_name_entries_that_do_not_exist_yet(kb: Make) -> None:
    unborn = DECISION.replace("product/app/value/fee", "product/app/value/new-fee").replace("chose: one", "chose: none")
    assert kb({"product/app/values.yml": VALUES, "product/app/decision/fee.yml": unborn}).findings() == set()


def test_guess_has_one_of_chose_or_value(kb: Make) -> None:
    both = DECISION.replace("guess: {chose: one,", "guess: {chose: one, value: {product/app/value/fee: {is: 2}},")
    assert only(kb({"product/app/values.yml": VALUES, "product/app/decision/fee.yml": both}).findings(),
                Problem.ONE_OF) == {"product/app/decision/fee/guess"}


def test_agreed_entry_shape(kb: Make) -> None:
    assert kb(agreed()).findings() == set()
    for bad in (agreed(fingerprint="short"), agreed(who="ai"), agreed(said=" "),
                agreed("{at: '2026-11-12T10:05:00+01:00', hash: ca3445729b96}"),
                agreed("{product/app/actor/member: {shown: A, hash: ca3445729b96}}")):
        assert only(kb(bad).findings(), Problem.WRONG_TYPE) == {"product/app/actor/member"}


def test_common_fields(kb: Make) -> None:
    changed = {"product/app/actors.yml": "- {id: member, title: Member, says: x, nature: human, src: [], agreed: "
                                         + stamp() + ", because: [product/app/workflow/sign-in], proof: [tests/t.py::test_a]}\n"}
    assert kb(changed).findings() == set()
    wrong = {"product/app/actors.yml":
             "- {id: member, says: x, nature: human, src: one, because: [product/app/workflow/nothing], layer: product}\n"}
    found = kb(wrong).findings()
    assert {problem for problem, _ in found} == {Problem.WRONG_TYPE, Problem.DANGLING_LINK, Problem.UNKNOWN_FIELD,
                                                 Problem.BAD_SRC}  # `layer` is no field: the folder is the layer


def test_the_folder_is_the_layer_and_the_kind_says_which_layers_it_may_appear_in(kb: Make) -> None:
    both = {"software/app/values.yml": VALUES, "product/app/decision/fee.yml": DECISION, "software/app/decision/fee.yml": DECISION}
    assert only(kb(both).findings(), Problem.BAD_LAYER) == set()  # a value and a decision may be in either layer
    actor = "- {id: member, says: A person., nature: human}\n"
    view = "says: The page.\nserves: [product/app/workflow/sign-in/step/ask]\n"
    found = kb({"software/app/actors.yml": actor, "product/app/view/page.yml": view}).findings()
    assert only(found, Problem.BAD_LAYER) == {"software/app/actor/member", "product/app/view/page"}


def test_requirement_applies_when_part_present(kb: Make) -> None:
    plain = CALLEE.replace("called", "actor")
    effect = plain.replace("a: {order: 1,", "a: {order: 1, effects: [{do: tell, \"on\": product/app/actor/member, value: hi}],")
    assert only(kb({"product/app/workflow/callee.yml": effect}).findings(),
                Problem.UNMET) == {"product/app/workflow/callee/step/only/case/a"}
    assert only(kb({"product/app/workflow/callee.yml": plain}).findings(), Problem.UNMET) == set()
    operation = "says: Sends.\nperforms: [product/app/workflow/callee/step/only/case/a]\n"
    assert kb({"product/app/workflow/callee.yml": effect, "software/app/operation/send.yml": operation}).findings() == set()


def test_actor_step_with_one_timeout(kb: Make) -> None:
    flow = ("says: S.\ntrigger: actor\nstart: ask\nsteps:\n  ask:\n    actor: product/app/actor/member\n"
            "    choices:\n      go: {label: Go, then: done}\n")
    flow += "    timeout: {after: product/app/value/wait, then: done}\nends:\n  done: {result: success, says: D.}\n"
    base = {"product/app/workflow/sign-in.yml": flow, "product/app/values.yml": VALUES}
    assert kb(base).findings() == set()
    system = flow.replace("    actor: product/app/actor/member\n    choices:\n      go: {label: Go, then: done}\n", "    then: done\n")
    assert only(kb({**base, "product/app/workflow/sign-in.yml": system}).findings(),
                Problem.STEP_SHAPE) == {"product/app/workflow/sign-in/step/ask"}


def calling(covers: str) -> dict[str, str | None]:
    flow = ("says: C.\ntrigger: actor\nstart: call\nsteps:\n  call:\n    calls: product/app/workflow/callee\n    cases:\n"
            f"      a: {{covers_ends: {covers}, then: done}}\nends:\n  done: {{result: success, says: D.}}\n")
    return {"product/app/workflow/caller.yml": flow, "product/app/workflow/callee.yml": CALLEE}


def test_calling_step_covers_every_callee_end(kb: Make) -> None:
    both = "[product/app/workflow/callee/end/good, product/app/workflow/callee/end/bad]"
    assert kb(calling(both)).findings() == set()
    found = kb(calling("[product/app/workflow/callee/end/good]")).findings()
    assert found == {(Problem.UNCOVERED_END, "product/app/workflow/caller/step/call")}


def test_called_workflow_needs_a_caller(kb: Make) -> None:
    alone = kb({"product/app/workflow/callee.yml": CALLEE}).findings()
    assert alone == {(Problem.ORPHAN, "product/app/workflow/callee")}
    assert kb(calling("[product/app/workflow/callee/end/good, product/app/workflow/callee/end/bad]")).findings() == set()


def cases(first: str, second: str) -> dict[str, str | None]:
    flow = ("says: S.\ntrigger: actor\nstart: sys\nsteps:\n  sys:\n    cases:\n"
            f"      a: {{{first}, when: {{text: a}}, then: done}}\n      b: {{{second}, when: {{text: b}}, then: done}}\n"
            "      otherwise: {then: done}\nends:\n  done: {result: success, says: D.}\n")
    return {"product/app/workflow/sys.yml": flow}


def test_cases_are_ordered_by_data(kb: Make) -> None:
    assert kb(cases("order: 1", "order: 2")).findings() == set()
    assert only(kb(cases("order: 1", "order: 1")).findings(), Problem.STEP_SHAPE) == {"product/app/workflow/sys/step/sys"}
    assert only(kb(cases("order: 1", "label: x")).findings(), Problem.UNKNOWN_FIELD) == {"product/app/workflow/sys/step/sys/case/b"}
    no_otherwise = cases("order: 1", "order: 2")["product/app/workflow/sys.yml"].replace("      otherwise: {then: done}\n", "")
    assert only(kb({"product/app/workflow/sys.yml": no_otherwise}).findings(), Problem.STEP_SHAPE) == {"product/app/workflow/sys/step/sys"}


def test_unreachable_step_and_unreached_end(kb: Make) -> None:
    flow = ("says: S.\ntrigger: actor\nstart: a\nsteps:\n  a: {then: done}\n  lost: {then: done}\n"
                           "ends:\n  done: {result: success, says: D.}\n  never: {result: failure, says: N.}\n")
    found = kb({"product/app/workflow/w.yml": flow}).findings()
    assert found == {(Problem.UNREACHABLE, "product/app/workflow/w/step/lost"), (Problem.END_UNREACHED, "product/app/workflow/w/end/never")}


def test_guard_else_reaches_an_end(kb: Make) -> None:
    flow = ("says: S.\ntrigger: actor\nstart: a\nsteps:\n  a: {then: done}\nends:\n  done: {result: success, says: D.}\n"
            "  denied: {result: failure, says: N.}\n")
    guard = "says: Allowed.\n\"on\": product/app/workflow/w/step/a\nwhen: {text: ok}\nelse: product/app/workflow/w/end/denied\n"
    assert kb({"product/app/workflow/w.yml": flow, "product/app/guard/g.yml": guard}).findings() == set()
