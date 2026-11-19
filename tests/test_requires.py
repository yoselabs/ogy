"""Conditional requirements (`if_equals`, `needs_field`, `without`), `choice.when` and `attr.derived`, as the kind files declare."""

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
from tests.conftest import declared

from ogy.model import Problem
from ogy.ontology import OntologyError, parse_kinds

if TYPE_CHECKING:
    from conftest import Kb

type Make = Callable[[dict[str, str | None] | None], Kb]

LOAN = """\
says: A loan.
attrs:
  member: {type: one, of: product/app/entity/loan}
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
      stay: {label: Stay, then: done, effects: [{do: write, "on": product/app/entity/loan/attr/days}]}
ends:
  done: {result: success, says: D.}
"""
SERVED = {"software/app/view/ask-page.yml": "says: The page.\nserves: [product/app/workflow/ask/step/ask]\n",
          "software/app/operation/write.yml": "says: Writes.\nperforms: [product/app/workflow/ask/step/ask/choice/stay]\n",
          "product/app/entity/loan.yml": LOAN}


def unmet(kb: Make, changes: dict[str, str | None]) -> set[str]:
    return {where for problem, where in kb(changes).findings() if problem is Problem.UNMET}


def test_the_good_files_meet_every_requirement(kb: Make) -> None:
    assert kb({**SERVED, "product/app/workflow/ask.yml": STEP}).findings() == set()


def test_an_actor_step_keeps_one_choice_without_when(kb: Make) -> None:
    both = STEP.replace("stay: {label: Stay,", "stay: {label: Stay, when: {text: never},")
    assert unmet(kb, {**SERVED, "product/app/workflow/ask.yml": both}) == {"product/app/workflow/ask/step/ask"}


@pytest.mark.parametrize("effect", [
    '{do: write, "on": product/app/entity/loan/attr/late}',  # a derived attribute is never written
    '{do: tell, "on": product/app/entity/loan}',
    '{do: transition, "on": product/app/entity/loan}',
])
def test_an_effect_names_what_its_do_acts_on(kb: Make, effect: str) -> None:
    flow = STEP.replace('{do: write, "on": product/app/entity/loan/attr/days}', effect)
    assert unmet(kb, {**SERVED, "product/app/workflow/ask.yml": flow}) == {"product/app/workflow/ask/step/ask/choice/stay"}


def test_a_derived_attribute_has_no_max_and_one_names_what_it_holds(kb: Make) -> None:
    loan = LOAN.replace("derived:", "optional: true, derived:").replace(", of: product/app/entity/loan", "")
    assert unmet(kb, {**SERVED, "product/app/entity/loan.yml": loan}) == {
        "product/app/entity/loan/attr/late", "product/app/entity/loan/attr/member"}


HEAD = "kind: thing\nabout: x\nlayers: [product]\nshape: entity\nfields:\n  a: {type: enum, of: [x, y]}\n  b: {}\n"


@pytest.mark.parametrize(("requires", "message"), [
    ("{if_equals: {field: c, value: x}, needs_field: b, error: e}", "if_equals names no field c"),
    ("{if_equals: {field: a, value: [x, z]}, needs_field: b, error: e}", "z is no member of a"),
    ("{if_equals: {field: a, value: x}, needs_field: c, error: e}", "needs_field names no field c"),
    ("{needs_field: b, kinds: [thing], error: e}", "not both"),
    ("{error: e}", "not both"),
    ("{kinds: [thing], without: [c], error: e}", "without names c"),
    ("{if_set: a, if_equals: {field: a, value: x}, needs_field: b, error: e}", "not both"),
])
def test_the_loader_refuses_a_requirement_that_names_nothing(requires: str, message: str) -> None:
    with pytest.raises(OntologyError, match=message):
        parse_kinds({"kinds/thing.yml": HEAD + f"requires:\n  - {requires}\n"}, declared("product"))
