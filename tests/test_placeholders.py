"""Every `<name>` of an interface's `invoked_as` is one of its inputs, and every input is a `<name>` of it (decisions
software/ontology/decision/inputs-that-are-no-fact, answered declared-inputs, and
software/ontology/decision/command-inputs-are-accepted, answered checked); what it accepts is the `of` of its inputs
(decision software/ontology/decision/input-carries-fact, answered input-of)."""

from collections.abc import Callable, Mapping

from tests.conftest import Kb

from ogy.model import Problem

type Make = Callable[[Mapping[str, str | None] | None], Kb]

CLI = "says: Shows one.\nform: cli\ninvoked_as: app show <address> [--rev <rev>]\n"
INPUTS = "inputs:\n  address: {says: The entry shown.}\n  rev: {says: The commit read., optional: true}\n"


def placeholders(kb: Make, text: str) -> set[str]:
    return {where for problem, where in kb({"product/app/interface/show.yml": text}).findings() if problem is Problem.UNMATCHED_PLACEHOLDER}


def test_each_placeholder_is_an_input_and_each_input_a_placeholder(kb: Make) -> None:
    assert placeholders(kb, CLI + INPUTS) == set()
    assert placeholders(kb, CLI) == {"product/app/interface/show"}  # <address> and <rev> are no inputs
    assert placeholders(kb, CLI.replace(" [--rev <rev>]", "") + INPUTS) == {"product/app/interface/show"}  # rev is no <rev>
    spaced = CLI.replace("<address>", "<address or area>") + INPUTS
    assert placeholders(kb, spaced) == {"product/app/interface/show"}  # a name with a space is no input id


def test_an_interface_without_invoked_as_names_any_inputs(kb: Make) -> None:
    web = "says: A page.\nform: web\ninputs:\n  note: {says: What the member writes.}\n"
    assert placeholders(kb, web) == set()


def test_accepts_gives_way_to_the_inputs(kb: Make) -> None:
    old = "says: A page.\nform: web\naccepts: [product/app/entity/loan]\n"
    assert Problem.NEEDS_MIGRATION in {problem for problem, _ in kb({"product/app/interface/show.yml": old}).findings()}
