"""`ogy kinds <kind>` with its guidance, and `ogy kinds --map`: the ontology on one screen."""

from pathlib import Path

from tests.conftest import ogy

from ogy import cli
from ogy.kindmap import map_lines
from ogy.ontology import Ontology


def test_every_shipped_kind_says_how_to_decide(ontology: Ontology) -> None:
    short = {name: len((kind.guidance or "").split()) for name, kind in ontology.kinds.items()}
    assert [name for name, words in short.items() if not 0 < words <= 60] == []


def test_a_kind_prints_about_guidance_and_fields(repo: Path) -> None:
    code, lines = ogy(repo, "kinds", "actor")
    assert code == cli.OK and lines[0].startswith("actor: whoever") and lines[1].startswith("  guidance: Different permitted actions")
    assert "    nature: enum, one of human|ai|program, required" in lines


def test_the_map_is_one_line_per_kind_grouped_by_layer(ontology: Ontology) -> None:
    lines = map_lines(ontology)
    named = {line.split(":")[0].strip().removesuffix("[]") for line in lines[1:lines.index("rules:")] if line.startswith("  ")}
    assert named == set(ontology.kinds)
    assert [line for line in lines if not line.startswith(" ")][1:] == [
        "product and software:", "product:", "software:", "constitution/ (fixed folder):", "rules:"]
    assert "  workflow: !says !trigger(actor|schedule|event|called) schedule->value event->transition !start->step" \
        " realizes->capability by->>rule" in lines
    assert "        effect[]: as above" in lines  # a part of several kinds is written out once
    assert "  workflow: a scheduled workflow names its schedule" in lines
    assert "  case, choice, timeout: a row with an effect has an operation performing it" in lines
    assert 50 <= len(lines) <= 80


def test_the_map_is_a_flag_of_kinds(repo: Path) -> None:
    code, lines = ogy(repo, "kinds", "--map")
    assert code == cli.OK and lines[0].startswith("! required") and "rules:" in lines
