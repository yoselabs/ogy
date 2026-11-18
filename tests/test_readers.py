"""`ogy kinds --readers`: what reads each field, from the kind files and the checks that read a field by name."""

from importlib.resources import files
from pathlib import Path

from tests.conftest import ogy

from ogy import cli
from ogy.ontology import Ontology, packaged, parse_kinds
from ogy.readers import readers


def test_the_shipped_fields_name_their_readers(ontology: Ontology) -> None:
    found = readers(ontology)
    assert {"flow", "requires", "links and impact", "fingerprint"} <= set(found[("step", "actor")])
    assert found[("guess", "sets")] == ["exactly_one_of", "settling"]
    assert "fingerprint path" in found[("external", "pin")]  # an operation that uses the external reads its pin
    assert found[("term", "example")] == [] and found[("area", "distinct")] == []
    assert found[("decision", "context")] == ["check avoided-word"]  # a note: outside every fingerprint


def test_a_field_nothing_reads_is_listed(repo: Path) -> None:
    root = files("ogy").joinpath("ontologies", "software", "kinds")
    texts = {f"kinds/{item.name}": item.read_text() for item in root.iterdir()}
    texts["kinds/area.yml"] += "  colour: {note: true}\n"
    assert readers(parse_kinds(texts, packaged().layers))[("area", "colour")] == []
    code, lines = ogy(repo, "kinds", "term", "--readers")
    assert code == cli.OK and "term.example: nothing" in lines and lines[-2].startswith("read by nothing (2): term.borrowed")
