"""The board's shell speaks the ontology's words and gives every kind, operation and mark a glyph of its own."""

import re
from pathlib import Path

from ogy.target import Target

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src/ogy/web/static"
LIBRARY = Path(__file__).parent / "fixtures/tool-library"


def glyphs() -> dict[str, dict[str, str]]:
    """The icon table of `model/icons.js`: group name -> glyph name -> path."""
    text = (STATIC / "js/model/icons.js").read_text(encoding="utf-8")
    groups = {}
    for group in ("kinds", "operations", "marks"):
        body = re.search(rf"const {group} = \{{(.*?)\n\}};", text, re.DOTALL)
        assert body, group
        groups[group] = {
            name.strip('"'): path for name, path in re.findall(r'^\s+("?[\w-]+"?):\s+"([^"]+)",?$', body.group(1), re.MULTILINE)
        }
    return groups


def test_no_two_kinds_operations_or_marks_share_a_glyph():
    """Given every glyph the viewer draws, each path is used once: an icon that means three things means nothing."""
    table = glyphs()
    paths = [path for group in table.values() for path in group.values()]
    assert len(paths) > 40
    assert len(paths) == len(set(paths))
    names = [name for group in table.values() for name in group]
    assert len(names) == len(set(names))


def test_every_ontology_kind_has_its_own_glyph():
    """Given the shipped ontologies, a kind without a glyph would be drawn as a blank square."""
    table = glyphs()["kinds"]
    kinds = set(Target(LIBRARY).kinds().kinds)
    assert kinds
    assert sorted(kinds - set(table)) == []
    assert sorted(set(table) - kinds) == []


def test_every_effect_operation_has_a_glyph_that_is_not_a_kind():
    """Given the effect operations of the ontology, each is drawn and none borrows a kind's mark."""
    operations = set(glyphs()["operations"])
    declared = {"create", "delete", "write", "tell", "do-transition"}
    assert operations == declared


def test_the_shell_has_no_inline_colour_and_marks_authored_text():
    """Given the shell modules, colour lives in the stylesheet and KB text is wrapped by one function."""
    shell = [*(STATIC / "js/shell").glob("*.js"), *(STATIC / "js/ui").glob("*.js")]
    assert shell
    for path in shell:
        text = path.read_text(encoding="utf-8")
        assert re.search(r"#[0-9a-fA-F]{3,8}\b", text) is None, path
    assert "data-authored" in (STATIC / "js/ui/authored.js").read_text(encoding="utf-8")
    mention = (STATIC / "js/ui/mention.js").read_text(encoding="utf-8")
    assert 'data-renderer": "mention"' in mention
