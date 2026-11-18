"""Addresses, paths, parts and local keys."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from tests.conftest import GOOD

from ogy.layout import locate, path_for
from ogy.model import Address, Problem, parse_address
from ogy.ontology import Ontology

if TYPE_CHECKING:
    from conftest import Kb

type Make = Callable[[dict[str, str | None] | None], Kb]


def test_entity_path_is_its_address(kb: Make, ontology: Ontology) -> None:
    snapshot = kb(None).snapshot
    address = Address("product", "app", (("workflow", "sign-in"),))
    assert snapshot.entries[address].path == "product/app/workflow/sign-in.yml" == path_for(ontology.kinds["workflow"], address.home,
                                                                                            "sign-in")
    assert str(address) == "product/app/workflow/sign-in" and address.home == "product/app"


def test_list_file_named_by_kind(kb: Make, ontology: Ontology) -> None:
    snapshot = kb(None).snapshot
    assert snapshot.entries[Address("product", "app", (("actor", "member"),))].path == "product/app/actors.yml"
    assert path_for(ontology.kinds["actor"], "product/app", "member") == "product/app/actors.yml"


def test_unknown_file_is_bad_path(kb: Make) -> None:
    bad = ("product/app/notes.yml", "product/app/deep/er/x.yml", "product/app/step/x.yml")
    found = kb(dict.fromkeys(bad, "x: 1\n")).findings()
    assert found == {(Problem.BAD_PATH, path) for path in bad}


def test_the_layer_level_cannot_be_skipped(kb: Make) -> None:
    """The ontology declares `<layer>/<area>/<kind>/<id>`; the area or the kind at the top, or an unknown layer, is `bad-path`."""
    value = "- {id: fee, says: The fee., is: 2, unit: EUR}\n"
    flow = GOOD["product/app/workflow/sign-in.yml"]
    skipped = {"app/values.yml": value, "app/workflow/sign-in-2.yml": flow, "workflow/sign-in-3.yml": flow, "values.yml": value,
               "tech/app/values.yml": value, "product/values.yml": value, "product/workflow/sign-in-4.yml": flow}
    found = kb(skipped).findings()
    assert {(problem, path) for problem, path in found if problem is Problem.BAD_PATH} == {(Problem.BAD_PATH, path) for path in skipped}


def test_a_bad_path_says_what_is_wanted(ontology: Ontology) -> None:
    assert "no layer (product, software)" in str(locate(ontology, "app/workflow/x.yml"))
    assert "holds areas" in str(locate(ontology, "product/values.yml"))
    assert locate(ontology, "product/app/values.yml") is not None and not isinstance(locate(ontology, "product/app/values.yml"), str)


def test_reserved_files_are_not_entry_files(kb: Make) -> None:
    assert kb({"built/app/actors.yml": "{}\n", "product/app/removed.yml": "format: 1\nitems: []\n"}).findings() == set()
    assert (Problem.BAD_PATH, "kinds/x.yml") in kb({"kinds/x.yml": "kind: x\n"}).findings()


def test_kind_fixed_to_one_area(kb: Make) -> None:
    terms = "- {id: land, word: land, says: To finish.}\n"
    assert kb({"product/shared/glossary.yml": terms}).findings(landing=True) == {(Problem.TERM_NOT_AGREED, "product/shared/term/land")}
    assert (Problem.BAD_PATH, "product/app/terms.yml") in kb({"product/app/terms.yml": terms}).findings()


def test_parts_nest_and_get_slash_addresses(kb: Make) -> None:
    snapshot = kb(None).snapshot
    step = Address("product", "app", (("workflow", "sign-in"), ("step", "ask")))
    go = step.part("choice", "go")
    assert str(go) == "product/app/workflow/sign-in/step/ask/choice/go"
    assert go in snapshot.entries and snapshot.entries[go].path == "product/app/workflow/sign-in.yml"
    assert go.parent() == step and snapshot.resolve("product/app/workflow/sign-in/end/done") is not None
    assert parse_address(str(go), snapshot.ontology) == go


def test_inline_holds_map_list_one(kb: Make) -> None:
    flow = SIGN_IN_CHANGED
    snapshot = kb({"product/app/workflow/sign-in.yml": flow}).snapshot
    choice = Address("product", "app", (("workflow", "sign-in"), ("step", "ask"), ("choice", "go")))
    timeout = Address("product", "app", (("workflow", "sign-in"), ("step", "ask"), ("timeout", "")))
    assert timeout in snapshot.entries and str(timeout) == "product/app/workflow/sign-in/step/ask/timeout"
    assert snapshot.resolve(str(timeout)) == timeout
    assert snapshot.entries[choice].fields["effects"] == [{"do": "tell", "on": "product/app/actor/member"}]
    assert not any(address.kind == "effect" for address in snapshot.entries)


def test_local_key_resolves_to_sibling_part(kb: Make) -> None:
    snapshot = kb(None).snapshot
    go = Address("product", "app", (("workflow", "sign-in"), ("step", "ask"), ("choice", "go")))
    assert snapshot.links.forward(go, "then") == {Address("product", "app", (("workflow", "sign-in"), ("end", "done")))}


def test_local_key_ambiguous_between_step_and_end(kb: Make) -> None:
    both = SIGN_IN_CHANGED.replace("ends:\n", "  done: {says: Also.}\nends:\n")
    found = kb({"product/app/workflow/sign-in.yml": both}).findings()
    assert (Problem.AMBIGUOUS_LINK, "product/app/workflow/sign-in/step/ask/choice/go") in found


def test_short_link_form_is_rejected(kb: Make) -> None:
    changed = SIGN_IN_CHANGED.replace("actor: product/app/actor/member", "actor: actor/member")
    found = kb({"product/app/workflow/sign-in.yml": changed}).findings()
    assert (Problem.BAD_LINK, "product/app/workflow/sign-in/step/ask") in found


def test_names_are_kebab_case(kb: Make) -> None:
    renamed = SIGN_IN_CHANGED.replace("  ask:", "  Ask:").replace("start: ask", "start: Ask")
    assert (Problem.BAD_NAME, "product/app/workflow/sign-in/step/Ask") in kb({"product/app/workflow/sign-in.yml": renamed}).findings()
    assert (Problem.BAD_PATH, "product/Bad/actors.yml") in kb({"product/Bad/actors.yml": "[]\n"}).findings()


def test_duplicate_id_in_list_file(kb: Make) -> None:
    twice = "- {id: member, says: A, nature: human}\n- {id: member, says: B, nature: ai}\n"
    found = kb({"product/app/actors.yml": twice}).snapshot.findings
    assert [(item.problem, str(item.address)) for item in found] == [(Problem.DUPLICATE_ID, "product/app/actor/member")]


def test_locate_is_pure(ontology: Ontology) -> None:
    assert locate(ontology, "product/app/value/x.yml") == "no entity kind 'value'"
    assert "no layer" in str(locate(ontology, "notes.txt"))  # no file is ignored


SIGN_IN_CHANGED = """\
says: A member is signed in.
trigger: actor
start: ask
steps:
  ask:
    says: The member asks.
    actor: product/app/actor/member
    choices:
      go:
        label: Sign in
        then: done
        effects:
          - {do: tell, "on": product/app/actor/member}
    timeout: {after: product/app/value/wait, then: done}
ends:
  done: {result: success, says: The member is signed in.}
"""


def test_every_file_under_the_knowledge_base_is_accounted_for(kb: Make) -> None:
    stray = ("README.md", "product/app/notes.txt", "product/app/data.json", "product/app/message/x.md", "glossary/notes.md",
             "tools/x.yml", "product/removed.yml", "product/app/value/deep/er.yml", "glossary/removed.yml")
    found = kb({**dict.fromkeys(stray, "x\n"), "product/app/removed.yml": "format: 1\nitems: []\n",
                "built/anything.json": "{}\n"}).findings()
    assert {path for problem, path in found if problem is Problem.BAD_PATH} == set(stray)


def test_an_area_entry_is_its_area_yml_and_its_id_is_the_folder(kb: Make, ontology: Ontology) -> None:
    snapshot = kb(None).snapshot
    address = Address("product", "app", (("area", "app"),))
    assert snapshot.entries[address].path == "product/app/area.yml" == path_for(ontology.kinds["area"], "product/app", "app")
    assert snapshot.entries[address].fields == {"says": "What members of the tool library do."}


def test_an_area_folder_without_its_area_yml_is_missing_entry_and_a_fixed_folder_is_no_area(kb: Make) -> None:
    found = kb({"product/app/area.yml": None, "software/loans/values.yml": "- {id: fee, says: The fee., is: 2, unit: EUR}\n",
                "product/shared/glossary.yml": "- {id: fee, word: fee, says: What a loan costs.}\n"}).findings()
    assert {item for item in found if item[0] is Problem.MISSING_ENTRY} == {
        (Problem.MISSING_ENTRY, "product/app/area/app"), (Problem.MISSING_ENTRY, "software/loans/area/loans")}
