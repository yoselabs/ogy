"""Conditional requirements (`if_equals`, `needs_field`, `without`), `choice.when` and `attr.derived`, as the kind files declare."""

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

import pytest
from tests.conftest import SIGN_IN, declared

from ogy.model import Address, Problem
from ogy.ontology import OntologyError, parse_kinds
from ogy.receipts import work_left
lazy from ogy.snapshot import Snapshot

if TYPE_CHECKING:
    from conftest import Kb

type Make = Callable[[Mapping[str, str | None] | None], Kb]

LOAN = """\
says: A loan.
attributes:
  member: {of: product/app/entity/loan}
  days: {type: number}
  late: {type: flag, derived: {text: days is over the limit, reads: [days, product/app/actor/member]}}
"""
STEP = """\
says: S.
start: ask
steps:
  ask:
    actor: product/app/actor/member
    choices:
      go: {label: Go, then: done, when: {text: the member is late, reads: [product/app/actor/member]}}
      stay: {label: Stay, then: done, effects: [{do: write, "on": product/app/entity/loan/attribute/days}]}
ends:
  done: {result: success, says: D.}
"""
PAGE = "says: The page.\nform: web\nserves: [product/app/workflow/ask/step/ask]\naccepts: [product/app/entity/loan]\n"
SERVED = {
    "product/app/interface/ask-page.yml": PAGE,
    "software/app/handler/write.yml": "says: Writes.\nperforms: [product/app/workflow/ask/step/ask/choice/stay]\n",
    "product/app/entity/loan.yml": LOAN,
}


def unmet(kb: Make, changes: Mapping[str, str | None]) -> set[str]:
    return {where for problem, where in kb(changes).findings() if problem is Problem.UNMET}


def left(kb: Make, changes: Mapping[str, str | None], status: str) -> set[str]:
    """The entries with work of `status`, once the files hold no fault: a later layer missing is work, never a fault."""
    made = kb(changes)
    assert not {where for problem, where in made.findings() if problem is Problem.UNMET}
    return {item.address for item in work_left(made.snapshot, {}, _no_file) if item.status == status}


def test_the_good_files_meet_every_requirement(kb: Make) -> None:
    assert kb({**SERVED, "product/app/workflow/ask.yml": STEP}).findings() == set()


def test_an_actor_step_keeps_one_choice_without_when(kb: Make) -> None:
    both = STEP.replace("stay: {label: Stay,", "stay: {label: Stay, when: {text: never},")
    assert unmet(kb, {**SERVED, "product/app/workflow/ask.yml": both}) == {"product/app/workflow/ask/step/ask"}


@pytest.mark.parametrize(
    "effect",
    [
        '{do: write, "on": product/app/entity/loan/attribute/late}',  # a derived attribute is never written
        '{do: tell, "on": product/app/entity/loan}',
        '{do: move, "on": product/app/entity/loan}',
    ],
)
def test_an_effect_names_what_its_do_acts_on(kb: Make, effect: str) -> None:
    flow = STEP.replace('{do: write, "on": product/app/entity/loan/attribute/days}', effect)
    assert unmet(kb, {**SERVED, "product/app/workflow/ask.yml": flow}) == {"product/app/workflow/ask/step/ask/choice/stay"}


def test_a_derived_attribute_has_no_max_and_never_is_optional(kb: Make) -> None:
    loan = LOAN.replace("derived:", "optional: true, derived:")
    assert unmet(kb, {**SERVED, "product/app/entity/loan.yml": loan}) == {"product/app/entity/loan/attribute/late"}


def test_an_attribute_has_a_type_or_names_what_it_holds(kb: Make) -> None:
    loan = LOAN.replace("{of: product/app/entity/loan}", "{many: true}")
    found = kb({**SERVED, "product/app/entity/loan.yml": loan}).findings()
    assert (Problem.ONE_OF, "product/app/entity/loan/attribute/member") in found
    plain = LOAN.replace("{of: product/app/entity/loan}", "{type: text, many: true}")  # a list of plain values
    assert not kb({**SERVED, "product/app/entity/loan.yml": plain}).findings() - kb({**SERVED}).findings()


def test_an_attribute_nothing_writes_or_accepts_is_never_written(kb: Make) -> None:
    page = PAGE.replace("accepts: [product/app/entity/loan]\n", "")
    flow = {**SERVED, "product/app/interface/ask-page.yml": page, "product/app/workflow/ask.yml": STEP}
    assert left(kb, flow, "unwritten") == {"product/app/entity/loan/attribute/member"}  # days is written, late derived
    accepted = page + "accepts: [product/app/entity/loan/attribute/member]\n"
    assert left(kb, {**flow, "product/app/interface/ask-page.yml": accepted}, "unwritten") == set()
    created = STEP.replace(
        '"on": product/app/entity/loan/attribute/days}',
        '"on": product/app/entity/loan/attribute/days}, {do: create, "on": product/app/entity/loan}',
    )
    assert left(kb, {**flow, "product/app/workflow/ask.yml": created}, "unwritten") == set()  # creating the entity writes its facts
    told = STEP.replace(
        '"on": product/app/entity/loan/attribute/days}',
        '"on": product/app/entity/loan/attribute/days}, {do: delete, "on": product/app/entity/loan}',
    )
    assert left(kb, {**flow, "product/app/workflow/ask.yml": told}, "unwritten") == {"product/app/entity/loan/attribute/member"}


PAY = """\
says: A fee is paid.
start: charge
steps:
  charge:
    says: The product asks the payment provider to charge the member.
    cases:
      otherwise: {then: done, effects: [{do: tell, "on": product/app/actor/provider}]}
ends:
  done: {result: success, says: Paid.}
"""
PAYING = {
    "product/app/actors.yml": "- {id: member, says: A person who borrows., nature: human}\n"
    "- {id: provider, says: The payment provider., nature: program}\n",
    "product/app/workflow/pay.yml": PAY,
    "software/app/handler/charge.yml": "says: Charges.\nperforms: [product/app/workflow/pay/step/charge/case/otherwise]\n",
}
CARDS = "says: The card network.\nrealizes: product/app/actor/provider\n"


def test_a_row_that_tells_a_program_actor_is_performed_by_a_handler_using_a_dependency_realizing_it(kb: Make) -> None:
    """A party the business deals with lives in product whatever its nature (decision actor-layers): a product row tells it,
    a software handler performing the row uses the dependency that realizes it."""
    case = "product/app/workflow/pay/step/charge/case/otherwise"
    assert left(kb, PAYING, "unhandled") == {case}
    assert left(kb, {**PAYING, "software/app/dependency/cards.yml": CARDS}, "unhandled") == {case}  # nobody uses it for this row
    used = PAYING["software/app/handler/charge.yml"] + "uses: [software/app/dependency/cards]\n"
    assert left(kb, {**PAYING, "software/app/dependency/cards.yml": CARDS, "software/app/handler/charge.yml": used}, "unhandled") == set()
    person = PAYING["product/app/actors.yml"].replace("program", "human")  # only a program actor is realized by a dependency
    assert left(kb, {**PAYING, "product/app/actors.yml": person}, "unhandled") == set()


def test_a_product_entry_never_names_a_software_one(kb: Make) -> None:
    bot = {"software/app/actors.yml": "- {id: bot, says: A scheduler., nature: program}\n"}  # an actor is outside the product
    assert (Problem.BAD_LAYER, "software/app/actor/bot") in kb(bot).findings()  # decision actor-layers: product only
    told = PAY.replace("product/app/actor/provider", "software/app/dependency/cards")  # a product row never tells a dependency
    found = kb({**PAYING, "product/app/workflow/pay.yml": told, "software/app/dependency/cards.yml": CARDS}).findings()
    assert (Problem.LAYER_DIRECTION, "product/app/workflow/pay/step/charge/case/otherwise") in found


def test_an_entity_needs_proof_only_with_transitions(kb: Make) -> None:
    """D15: `needs_proof: {if_part: transition}`; a step, a handler and a quantity need none."""
    lifecycle = LOAN + "states:\n  out: {says: Out.}\ntransitions:\n  lend: {to: out}\n"
    plain, held = kb(SERVED).snapshot, kb({**SERVED, "product/app/entity/loan.yml": lifecycle}).snapshot
    loan = "product/app/entity/loan"
    assert not plain.needs_proof(at(plain, loan)) and held.needs_proof(at(held, loan))
    assert not any(plain.needs_proof(at(plain, text)) for text in ("software/app/handler/write", "product/app/workflow/sign-in/step/ask"))


def at(snapshot: Snapshot, text: str) -> Address:
    found = snapshot.resolve(text)
    assert found is not None, text
    return found


HEAD = "kind: thing\nabout: x\nlayers: [product]\nshape: file\nfields:\n  a: {type: enum, of: [x, y]}\n  b: {}\n"


@pytest.mark.parametrize(
    ("requires", "message"),
    [
        ("{if_equals: {field: c, value: x}, needs_field: b, error: e}", "if_equals names no field c"),
        ("{if_equals: {field: a, value: [x, z]}, needs_field: b, error: e}", "z is no member of a"),
        ("{if_equals: {field: a, value: x}, needs_field: c, error: e}", "needs_field names no field c"),
        ("{needs_field: b, kinds: [thing], error: e}", "not both"),
        ("{error: e}", "not both"),
        ("{kinds: [thing], without: [c], error: e}", "without names c"),
        ("{if_set: a, if_equals: {field: a, value: x}, needs_field: b, error: e}", "not both"),
        ("{if_unset: c, needs_field: b, error: e}", "if_unset names no field c"),
        ("{kinds: [thing], or_paths: [[b]], error: e}", "further paths beside a path"),
        ("{kinds: [thing], same: true, error: e}", "comes back to the entry"),
        ("{if_set: a, if_reaches: [b], kinds: [thing], path: [b], error: e}", "not both"),
        ("{kinds: [thing], path: [b], work: true, error: e}", "names its status"),
    ],
)
def test_the_loader_refuses_a_requirement_that_names_nothing(requires: str, message: str) -> None:
    with pytest.raises(OntologyError, match=message):
        parse_kinds({"kinds/thing.yml": HEAD + f"requires:\n  - {requires}\n"}, declared("product"))


@pytest.mark.parametrize(
    ("page", "problem"),
    [
        ("says: P.\nform: cli\nserves: [product/app/workflow/ask/step/ask]\n", Problem.UNMET),  # a command line says how it is invoked
        ("says: P.\nform: web\naccepts: [product/app/entity/loan]\n", Problem.UNMET),  # what accepts input serves a step
        ("says: P.\nform: web\noffers: [product/app/workflow/ask/step/ask/choice/go]\n", Problem.UNMET),
        ("says: P.\nform: web\nserves: [product/app/workflow/ask/step/ask]\nallows: [product/app/actor/member]\n", Problem.UNMET),
        ("says: P.\nform: web\nserves: []\n", Problem.WRONG_TYPE),  # an empty list would read as set
        ("says: P.\nform: web\nincludes: [product/app/interface/card]\n", Problem.LINK_CYCLE),
    ],
)
def test_an_interface_is_checked_by_its_form_and_what_it_serves(kb: Make, page: str, problem: Problem) -> None:
    card = "says: A card.\nform: web\nshows: [product/app/entity/loan]\nincludes: [product/app/interface/extra]\n"
    flow = {
        **SERVED,
        "product/app/workflow/ask.yml": STEP,
        "product/app/interface/card.yml": card,
        "product/app/interface/extra.yml": page,
    }
    assert (problem, "product/app/interface/extra") in kb(flow).findings()
    shows = "says: The loans.\nform: file\nshows: [product/app/entity/loan]\nallows: [product/app/actor/member]\n"
    assert kb({**flow, "product/app/interface/extra.yml": shows}).findings() == set()  # only shows: it may serve no step


def _no_file(path: str, rev: str | None = None) -> str | None:
    return None


def test_a_capability_that_realizes_no_goal_is_work_named_in_yaml(kb: Make) -> None:
    """Owner: a capability realizes a goal. Until the goal is written it is work (`status: unrealized`), not a finding."""
    lone = kb({"product/app/capabilities.yml": "- {id: lend, says: Members borrow.}\n"})
    assert lone.findings() == set()
    assert [(item.address, item.status) for item in work_left(lone.snapshot, {}, _no_file) if item.status == "unrealized"] == [
        ("product/app/capability/lend", "unrealized"),
        ("product/app/workflow/sign-in", "unrealized"),  # the repository's workflow realizes no capability either
    ]
    goal = {
        "product/app/goals.yml": "- {id: tools, says: Members get tools.}\n",
        "product/app/capabilities.yml": "- {id: lend, says: Members borrow., realizes: [product/app/goal/tools]}\n",
    }
    assert not [item for item in work_left(kb(goal).snapshot, {}, _no_file) if item.status == "unrealized" and "capability" in item.address]


CONFIRM = """\
says: An order is confirmed.
start: confirm
steps:
  confirm:
    says: The shop asks PayRight to take the payment.
    cases:
      otherwise: {then: paid, effects: [{do: tell, "on": software/app/dependency/payright}]}
ends:
  paid: {result: success, says: Paid.}
"""
SHOP = {
    "software/app/workflow/confirm-order.yml": CONFIRM,
    "software/app/dependency/payright.yml": "says: PayRight, the card service the shop asks to take a payment.\n",
}
ROW = "software/app/workflow/confirm-order/step/confirm/case/otherwise"
WAIT = """\
  wait:
    says: The shop waits for PayRight's answer.
    cases:
      answered: {order: 1, then: paid, when: {text: PayRight answered paid, reads: [software/app/dependency/payright]}}
      otherwise: {then: unpaid}
"""
UNPAID = "  unpaid: {result: failure, says: Not paid; confirming again is safe.}\n"
ONCE = "says: A repeat charge is safe; PayRight is asked by order id first.\n"


def owed(kb: Make, changes: Mapping[str, str | None]) -> list[str]:
    """What the row still owes for its no-answer path: the messages of its `no-answer-path` work."""
    made = kb(changes)
    assert not {where for problem, where in made.findings() if problem is Problem.UNMET}
    return sorted(item.note for item in work_left(made.snapshot, {}, _no_file) if item.address == ROW and item.status == "no-answer-path")


def test_a_row_that_tells_an_outside_system_owes_a_no_answer_path_until_it_has_one(kb: Make) -> None:
    """Misfit M4 is no third result: the outside system may not answer. The row owes a path for that (a timeout, or a case
    ending in failure, on its step or the step it leads to) and a rule it satisfies on whether a repeat is safe."""
    assert len(owed(kb, SHOP)) == 2
    made = kb(SHOP)  # forward paths only: the row's own layer owes it (ogy.owing)
    assert {item.owed_by for item in work_left(made.snapshot, {}, _no_file) if item.status == "no-answer-path"} == {""}
    waits = CONFIRM.replace("then: paid, effects", "then: wait, effects").replace("ends:\n", WAIT + "ends:\n") + UNPAID
    pathed = owed(kb, {**SHOP, "software/app/workflow/confirm-order.yml": waits})
    assert len(pathed) == 1 and "repeat" in pathed[0]  # the no-answer path is there; the repeat rule is not
    held = waits.replace("effects: [", "satisfies: [software/app/rule/charge-once], effects: [")
    assert owed(kb, {**SHOP, "software/app/workflow/confirm-order.yml": held, "software/app/rule/charge-once.yml": ONCE}) == []
    succeeds = held.replace("otherwise: {then: unpaid}", "otherwise: {then: paid}")  # no failure end: no path for no answer
    assert len(owed(kb, {**SHOP, "software/app/workflow/confirm-order.yml": succeeds, "software/app/rule/charge-once.yml": ONCE})) == 1


def test_a_row_that_tells_a_program_actor_owes_a_no_answer_path_and_one_that_tells_a_person_does_not(kb: Make) -> None:
    case = "product/app/workflow/pay/step/charge/case/otherwise"
    assert left(kb, PAYING, "no-answer-path") == {case}
    person = PAYING["product/app/actors.yml"].replace("program", "human")
    assert left(kb, {**PAYING, "product/app/actors.yml": person}, "no-answer-path") == set()


def test_a_capability_no_workflow_realizes_is_work(kb: Make) -> None:
    """The kind guidance said it in prose only: a capability is named before its workflows and a workflow realizes it.
    Until the workflow is written, the capability is work, never a finding."""
    goal = {"product/app/goals.yml": "- {id: tools, says: Members get tools.}\n"}
    lend = {**goal, "product/app/capabilities.yml": "- {id: lend, says: Members borrow., realizes: [product/app/goal/tools]}\n"}
    assert left(kb, lend, "no-workflow") == {"product/app/capability/lend"}
    realized = SIGN_IN.replace("start: ask\n", "start: ask\nrealizes: product/app/capability/lend\n")
    assert left(kb, {**lend, "product/app/workflow/sign-in.yml": realized}, "no-workflow") == set()


def test_a_goal_no_capability_realizes_is_work(kb: Make) -> None:
    """Decision goal-realized-by-capability (answer work, the sibling of no-workflow): a goal is written before the capabilities
    that realize it, so until one does it is work, never a finding."""
    goal = {"product/app/goals.yml": "- {id: tools, says: Members get tools.}\n"}
    assert left(kb, goal, "no-capability") == {"product/app/goal/tools"}
    lend = {**goal, "product/app/capabilities.yml": "- {id: lend, says: Members borrow., realizes: [product/app/goal/tools]}\n"}
    assert left(kb, lend, "unused") == set()


def test_an_attribute_may_name_an_actor_and_not_a_goal(kb: Make) -> None:
    """Decision attribute-of-actor: who it was (the member who borrowed) is an attribute that names the actor."""
    who = LOAN.replace("member: {of: product/app/entity/loan}", "member: {of: product/app/actor/member}")
    assert kb({**SERVED, "product/app/entity/loan.yml": who}).findings() == kb(SERVED).findings()  # nothing new
    goal = LOAN.replace("member: {of: product/app/entity/loan}", "member: {of: product/app/goal/lend}")
    found = kb({**SERVED, "product/app/goals.yml": "- {id: lend, says: Members borrow tools.}\n", "product/app/entity/loan.yml": goal})
    assert (Problem.LINK_KIND, "product/app/entity/loan/attribute/member") in found.findings()


def test_an_attribute_no_interface_shows_and_nothing_reads_is_unread(kb: Make) -> None:
    """Decision software/ontology/decision/attribute-nothing-reads, answered unread-is-work: shown by an interface (it or its
    entity), or read by a condition or a derived value."""
    flow = {**SERVED, "product/app/workflow/ask.yml": STEP}
    loan = "product/app/entity/loan/attribute"
    assert left(kb, flow, "unread") == {f"{loan}/member", f"{loan}/late"}  # days is read by the derived late
    shown = {**flow, "product/app/interface/ask-page.yml": PAGE + f"shows: [{loan}/late]\n"}
    assert left(kb, shown, "unread") == {f"{loan}/member"}
    assert left(kb, {**flow, "product/app/interface/ask-page.yml": PAGE + "shows: [product/app/entity/loan]\n"}, "unread") == set()
