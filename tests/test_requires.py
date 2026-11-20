"""Conditional requirements (`if_equals`, `needs_field`, `without`), `choice.when` and `attr.derived`, as the kind files declare."""

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
from tests.conftest import SIGN_IN, declared

from ogy.model import Problem
from ogy.ontology import OntologyError, parse_kinds

if TYPE_CHECKING:
    from conftest import Kb

type Make = Callable[[dict[str, str | None] | None], Kb]

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
SERVED = {"software/app/interface/ask-page.yml": PAGE,
          "software/app/handler/write.yml": "says: Writes.\nperforms: [product/app/workflow/ask/step/ask/choice/stay]\n",
          "product/app/entity/loan.yml": LOAN}


def unmet(kb: Make, changes: dict[str, str | None]) -> set[str]:
    return {where for problem, where in kb(changes).findings() if problem is Problem.UNMET}


def test_the_good_files_meet_every_requirement(kb: Make) -> None:
    assert kb({**SERVED, "product/app/workflow/ask.yml": STEP}).findings() == set()


def test_an_actor_step_keeps_one_choice_without_when(kb: Make) -> None:
    both = STEP.replace("stay: {label: Stay,", "stay: {label: Stay, when: {text: never},")
    assert unmet(kb, {**SERVED, "product/app/workflow/ask.yml": both}) == {"product/app/workflow/ask/step/ask"}


@pytest.mark.parametrize("effect", [
    '{do: write, "on": product/app/entity/loan/attribute/late}',  # a derived attribute is never written
    '{do: tell, "on": product/app/entity/loan}',
    '{do: transition, "on": product/app/entity/loan}',
])
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
    flow = {**SERVED, "software/app/interface/ask-page.yml": page, "product/app/workflow/ask.yml": STEP}
    assert unmet(kb, flow) == {"product/app/entity/loan/attribute/member"}  # days is written, late derived
    accepted = page + "accepts: [product/app/entity/loan/attribute/member]\n"
    assert unmet(kb, {**flow, "software/app/interface/ask-page.yml": accepted}) == set()
    created = STEP.replace('"on": product/app/entity/loan/attribute/days}', '"on": product/app/entity/loan/attribute/days}, '
                           '{do: create, "on": product/app/entity/loan}')
    assert unmet(kb, {**flow, "product/app/workflow/ask.yml": created}) == set()  # creating the entity writes its facts
    told = STEP.replace('"on": product/app/entity/loan/attribute/days}', '"on": product/app/entity/loan/attribute/days}, '
                        '{do: delete, "on": product/app/entity/loan}')
    assert unmet(kb, {**flow, "product/app/workflow/ask.yml": told}) == {"product/app/entity/loan/attribute/member"}


PAY = """\
says: A fee is paid.
start: charge
steps:
  charge:
    says: The product asks the payment provider to charge the member.
    cases:
      otherwise: {then: done, effects: [{do: tell, "on": software/app/actor/provider}]}
ends:
  done: {result: success, says: Paid.}
"""
PAYING = {"software/app/actors.yml": "- {id: provider, says: The payment provider., nature: program}\n",
          "software/app/workflow/pay.yml": PAY,
          "software/app/handler/charge.yml": "says: Charges.\nperforms: [software/app/workflow/pay/step/charge/case/otherwise]\n"}
CARDS = "says: The card network.\nrealizes: software/app/actor/provider\n"


def test_a_row_that_tells_a_program_actor_is_performed_by_a_handler_using_a_dependency_realizing_it(kb: Make) -> None:
    case = "software/app/workflow/pay/step/charge/case/otherwise"
    assert unmet(kb, PAYING) == {case}
    assert unmet(kb, {**PAYING, "software/app/dependency/cards.yml": CARDS}) == {case}  # nobody uses it for this row
    used = PAYING["software/app/handler/charge.yml"] + "uses: [software/app/dependency/cards]\n"
    assert unmet(kb, {**PAYING, "software/app/dependency/cards.yml": CARDS, "software/app/handler/charge.yml": used}) == set()
    person = PAYING["software/app/actors.yml"].replace("program", "human")  # only a program actor is realized by a dependency
    assert unmet(kb, {**PAYING, "software/app/actors.yml": person}) == set()


def test_a_product_entry_never_names_a_software_one(kb: Make) -> None:
    flow = SIGN_IN.replace("actor: product/app/actor/member", "actor: software/app/actor/bot")
    bot = {"software/app/actors.yml": "- {id: bot, says: A scheduler., nature: program}\n", "product/app/workflow/sign-in.yml": flow}
    assert (Problem.LAYER_DIRECTION, "product/app/workflow/sign-in/step/ask") in kb(bot).findings()


HEAD = "kind: thing\nabout: x\nlayers: [product]\nshape: file\nfields:\n  a: {type: enum, of: [x, y]}\n  b: {}\n"


@pytest.mark.parametrize(("requires", "message"), [
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
    ("{kinds: [thing], path: [b], status: x, error: e}", "only a requirement that is work names its status"),
])
def test_the_loader_refuses_a_requirement_that_names_nothing(requires: str, message: str) -> None:
    with pytest.raises(OntologyError, match=message):
        parse_kinds({"kinds/thing.yml": HEAD + f"requires:\n  - {requires}\n"}, declared("product"))


@pytest.mark.parametrize(("page", "problem"), [
    ("says: P.\nform: cli\nserves: [product/app/workflow/ask/step/ask]\n", Problem.UNMET),  # a command line says how it is invoked
    ("says: P.\nform: web\naccepts: [product/app/entity/loan]\n", Problem.UNMET),  # what accepts input serves a step
    ("says: P.\nform: web\noffers: [product/app/workflow/ask/step/ask/choice/go]\n", Problem.UNMET),
    ("says: P.\nform: web\nserves: [product/app/workflow/ask/step/ask]\nallows: [product/app/actor/member]\n", Problem.UNMET),
    ("says: P.\nform: web\nserves: []\n", Problem.WRONG_TYPE),  # an empty list would read as set
    ("says: P.\nform: web\nincludes: [software/app/interface/card]\n", Problem.LINK_CYCLE),
])
def test_an_interface_is_checked_by_its_form_and_what_it_serves(kb: Make, page: str, problem: Problem) -> None:
    card = "says: A card.\nform: web\nshows: [product/app/entity/loan]\nincludes: [software/app/interface/extra]\n"
    flow = {**SERVED, "product/app/workflow/ask.yml": STEP, "software/app/interface/card.yml": card,
            "software/app/interface/extra.yml": page}
    assert (problem, "software/app/interface/extra") in kb(flow).findings()
    shows = "says: The loans.\nform: file\nshows: [product/app/entity/loan]\nallows: [product/app/actor/member]\n"
    assert kb({**flow, "software/app/interface/extra.yml": shows}).findings() == set()  # only shows: it may serve no step
