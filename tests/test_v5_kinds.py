"""The kind language: what a kind file may say and what the loader refuses."""

from importlib.resources import files

import pytest
from tests.conftest import declared

from ogy.kinds import ONTOLOGY_FILE, FieldType, Holds, Shape
from ogy.model import Address, Entry
from ogy.ontology import OntologyError, packaged, parse_declared, parse_kinds
from ogy.snapshot import fingerprint

ACTOR = "kind: actor\nabout: who uses it\nshape: list\nfile: actors.yml\nlayers: [product]\nfields:\n  nature: {}\n"
LAYERS = ("product", "software")
FIXED = "kind: principle\nabout: x\nshape: list\nfile: principles.yml\narea: glossary\n"
HEAD = "kind: thing\nabout: x\nlayers: [product]\n"
ENTITY = HEAD + "shape: file\n"
PARENT = "kind: parent\nabout: x\nshape: file\nlayers: [product]\n"
SETTLING = (
    "settling: {option: option, answer: answer, guess: guess, heard: heard, sets: sets, chose: chose, value: sets, "
    "said: said, at: at, where: where, note: note, delegated: delegated, context: context, why: why}\n"
)
PART = "kind: part\nabout: x\nshape: inline\nkey: parts\npart_of: parent\n"


def load(*texts: str) -> None:
    kinds = {"kinds/actor.yml": ACTOR}
    for text in texts:
        kinds[f"kinds/{text.split()[1]}.yml"] = text
    parse_kinds(kinds, declared(*LAYERS))


def test_software_kinds_load() -> None:
    ontology = packaged()
    assert len(ontology.kinds) == 29 and "message" not in ontology.kinds
    assert ontology.kinds["term"].area is None and ontology.kinds["principle"].area == "constitution"
    assert {name for name, kind in ontology.kinds.items() if kind.shared} == {"term", "actor", "enum", "area"}
    assert ontology.settling_kind() is ontology.kinds["decision"]
    assert ontology.kinds["effect"].holding is Holds.LIST
    assert ontology.kinds["proposal"].holding is Holds.ONE
    assert ontology.kinds["step"].holding is Holds.MAP


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (ENTITY + "fields:\n  a: {type: enum}\n", "enum fields"),
        (ENTITY + "fields:\n  a: {of: [x]}\n", "enum fields"),
        (ENTITY + "fields:\n  a: {type: uri}\n", "uri fields"),
        (ENTITY + "fields:\n  a: {type: expr}\n", "name target kinds"),
        (ENTITY + "fields:\n  a: {type: link, to: [nobody]}\n", "unknown kind nobody"),
        (ENTITY + "fields:\n  a: {normative: true}\n", "normative"),
        (ENTITY + "delivered: true\n", "delivered"),
        (ENTITY + "subjects: [x]\n", "subjects"),
        (ENTITY + "fields:\n  title: {}\n", "common to every kind"),
        (HEAD + "shape: list\n", "names its file"),
        (ENTITY + "file: things.yml\n", "file belongs to list and single kinds"),
        (HEAD + "shape: list\nfile: actors.yml\n", "also the file of actor"),
        (HEAD + "shape: list\nfile: actor.yml\n", "equals a kind name"),
        (HEAD + "shape: list\nfile: removed.yml\n", "removed ledger"),
        (HEAD.replace("product", "nowhere") + "shape: file\n", "not a layer of the ontology"),
        ("kind: thing\nabout: x\nshape: file\n", "declares the layers it may appear in"),
        (HEAD + "shape: inline\nkey: k\npart_of: actor\n", "a part is in its parent's layer"),
        (ENTITY + "area: glossary\n", "has no layers"),
        (HEAD + "shape: inline\nkey: k\npart_of: nobody\n", "unknown kind nobody"),
        (ENTITY + "holds: list\n", "inline kinds only"),
        (ENTITY + "append_only: true\n", "inline kinds that hold a list"),
        (HEAD + "shape: file\nimmutable: true\n", "immutable"),
        (ENTITY + "area: Not_An_Area\n", "no valid area name"),
        (ENTITY + "area: built\n", "no valid area name"),
        (ENTITY + "fields:\n  status: {}\n", "computed, never stored"),
        (ENTITY + "fields:\n  does: {}\n", "another name for a sentence"),
        (ENTITY + "fields:\n  ok?: {}\n", "no name contains"),
        (ENTITY + "fields:\n  a: {type: enum, of: ['yes?']}\n", "no name contains"),
        (ENTITY + "requires:\n  - {if_set: a, if_part: b, path: [], kinds: [], error: x}\n", "not both"),
        (ENTITY + "requires:\n  - {if_part: nothing, path: [], kinds: [actor], error: x}\n", "no part kind"),
        (ENTITY + "requires:\n  - {path: [], kinds: [actor], says: x}\n", "says"),
        (ENTITY + SETTLING, "settling names no kind"),
        (HEAD + "shape: single\n", "names its file"),
        ("kind: thing\nabout: x\nshape: single\nfile: thing.yml\narea: glossary\n", "belong to kinds that live under a layer"),
        (ENTITY + "must_be_agreed: true\nasked: false\n", "never asked cannot need agreement"),
    ],
)
def test_loader_refuses_inconsistent_kinds(text: str, message: str) -> None:
    with pytest.raises(OntologyError, match=message):
        load(text)


LINK = ENTITY + "fields:\n  a: {type: link, to: [actor], input: %s}\n"


@pytest.mark.parametrize(
    ("texts", "message"),
    [
        ((ENTITY + "fields:\n  a: {input: content}\n",), "only a link or expr field is an input"),
        ((LINK % "address",), "is the meaning already"),
        ((LINK % "{fields: [colour]}",), "picks colour, no field of actor"),
        ((LINK % "{parts: [part]}",), "picks part, no part of actor"),
        ((LINK % "{fields: [nature], parts: [part]}",), "fields or parts, one of them"),
        ((ENTITY + "input: {nothing: content}\n",), "names a common field or a part kind"),
        ((PARENT + "input: {part: {fields: [a]}}\n", PART), "a part is an input whole"),
        ((ENTITY + "input_from: {satisfies: {fields: [pin]}}\n",), "names a link field that leads here"),
        ((ENTITY + "needs_proof: true\nfields:\n  a: {type: link, to: [actor]}\n",), "states its input"),
        ((LINK % "none" + "input: {a: content}\n",), "a field of its own declares its input itself"),
        ((PARENT + "fields:\n  part: {type: link, to: [actor], input: none}\ninput: {part: content}\n", PART), "declares its input itself"),
    ],
)
def test_loader_refuses_inputs_that_read_nothing(texts: tuple[str, ...], message: str) -> None:
    with pytest.raises(OntologyError, match=message):
        load(*texts)


def test_inputs_that_name_what_their_targets_hold_load() -> None:
    load(
        ENTITY + "needs_proof: true\nfields:\n  a: {type: link, to: [actor], input: {fields: [nature]}}\n"
        "  b: {type: link, to: [actor], input: none}\ninput: {satisfies: address, because: address}\n"
    )
    load(PARENT + "input: {part: content}\n", PART)


def test_a_common_link_field_of_a_kind_that_needs_proof_states_its_input() -> None:
    common = declared(*LAYERS)
    because = common.common["because"].model_copy(update={"input": None})
    unstated = common.model_copy(update={"common": {**common.common, "because": because}})
    kinds = {"kinds/actor.yml": ACTOR, "kinds/thing.yml": ENTITY + "needs_proof: true\n"}
    with pytest.raises(OntologyError, match="because: a link field of a kind that needs proof states its input"):
        parse_kinds(kinds, unstated)
    parse_kinds({**kinds, "kinds/thing.yml": ENTITY + "needs_proof: true\ninput: {because: none}\n"}, unstated)


def test_link_has_one_direction() -> None:
    first = HEAD.replace("thing", "first") + "shape: file\nfields:\n  to: {type: link, to: [second]}\n"
    second = HEAD.replace("thing", "second") + "shape: file\nfields:\n  back: {type: links, to: [first]}\n"
    with pytest.raises(OntologyError, match="link to each other"):
        load(first, second)
    load(PARENT + "fields:\n  of: {type: link, to: [part]}\n", PART + "fields:\n  up: {type: link, to: [parent]}\n")


def test_part_kind_with_several_parents() -> None:
    other = PARENT.replace("parent", "other")
    both = PART.replace("part_of: parent", "part_of: [parent, other]")
    ontology = parse_kinds({"kinds/parent.yml": PARENT, "kinds/other.yml": other, "kinds/part.yml": both}, declared(*LAYERS))
    assert [kind.kind for kind in ontology.parts_of("parent")] == ["part"] == [kind.kind for kind in ontology.parts_of("other")]


def test_any_target_accepts_every_kind_and_no_kind_is_named_any() -> None:
    load(ENTITY + "fields:\n  of: {type: link, to: [any]}\n")
    with pytest.raises(OntologyError, match="not be `any`"):
        load("kind: any\nabout: x\nshape: file\n")


def test_list_kind_declares_its_file_once() -> None:
    ontology = packaged()
    files = [kind.file for kind in ontology.kinds.values() if kind.shape is Shape.LIST]
    assert len(files) == len(set(files)) == 8
    assert ontology.file_kind("quantities.yml") is ontology.kinds["quantity"]


def test_a_kind_names_the_layers_it_may_appear_in() -> None:
    kinds = packaged().kinds
    assert packaged().layers == ("product", "software")
    assert kinds["actor"].layers == LAYERS and kinds["interface"].layers == ("software",) and kinds["decision"].layers == LAYERS
    assert kinds["term"].layers == LAYERS and kinds["term"].moved_folder is None


def test_the_ontology_file_declares_the_layers() -> None:
    text = files("ogy").joinpath("ontologies", "software", ONTOLOGY_FILE).read_text()
    assert parse_declared(text).layers == ("product", "software")
    for bad in ("layers: product\n", text + "extra: 1\n", "[a]\n", text.replace("layers: [product, software]", "layers: [1]")):
        with pytest.raises(OntologyError, match=ONTOLOGY_FILE):
            parse_declared(bad)
    for layers, why in (
        ((), "declares no layers"),
        (("Product",), "no valid folder name"),
        (("kinds",), "no valid folder name"),
        (("glossary",), "no valid folder name"),
        (("shared",), "no valid folder name"),
    ):
        with pytest.raises(OntologyError, match=why):
            texts = {"kinds/actor.yml": ACTOR.replace("[product]", "[]"), "kinds/principle.yml": FIXED}
            parse_kinds(texts, declared().model_copy(update={"layers": layers}))


def test_the_ontology_file_names_what_the_engine_reads() -> None:
    found = packaged().declared
    assert found.roles.agreed in found.common and found.harms[0] == "structure" and found.rank(None) == len(found.harms)
    for change, why in (
        ({"asked_alone": ("nope",)}, "asked_alone: nope is no harm"),
        ({"roles": found.roles.model_copy(update={"src": "source"})}, "roles: src names no common field source"),
    ):
        with pytest.raises(OntologyError, match=why):
            parse_kinds({"kinds/actor.yml": ACTOR}, found.model_copy(update=change))
    with pytest.raises(OntologyError, match="harm late is no harm"):
        parse_kinds({"kinds/actor.yml": ACTOR + "  late: {harm: [late]}\n"}, found)


def test_inline_holds_map_list_one() -> None:
    kinds = packaged().kinds
    assert (kinds["step"].holding, kinds["effect"].holding, kinds["timeout"].holding) == (Holds.MAP, Holds.LIST, Holds.ONE)
    assert kinds["effect"].addressable is False and kinds["timeout"].has_id is False and kinds["timeout"].addressable


def test_fields_are_meaning_unless_note() -> None:
    ontology = packaged()
    term = ontology.kinds["term"]
    assert term.fields["word"].type is FieldType.TEXT
    where = Address("product", "shared", (("term", "land"),))
    base = Entry(where, "p", {"word": "land", "says": "to finish", "example": "a"})
    same = Entry(where, "p", {"word": "land", "says": "to finish", "example": "another"})
    other = Entry(where, "p", {"word": "land", "says": "to deliver", "example": "a"})
    assert fingerprint(term, base) == fingerprint(term, same) != fingerprint(term, other)


def test_settling_names_are_checked() -> None:
    decision = HEAD.replace("thing", "decision") + "shape: file\n" + SETTLING.replace("sets: sets", "sets: nothing")
    with pytest.raises(OntologyError, match="settling names no kind option"):
        load(decision)
