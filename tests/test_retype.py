"""`ogy migrate` follows a kind the ontology renamed (`was:`): its entries move to the new folder, file or key, every address
that names them is rewritten, and what was agreed or built stays current."""

import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import pytest
from tests.conftest import commit
from tests.test_migrate import DECISION, build_hash, fingerprint

from ogy import built, ops, writes
from ogy.model import Problem, parse_address
from ogy.ontology import Ontology, OntologyError, packaged, parse_kinds
from ogy.target import Target

FEE, LEND, GO = "product/app/value/fee", "software/app/operation/lend", "product/app/workflow/borrow/step/ask/choice/go"
NEW_LEND, NEW_GO = "software/app/handler/lend", "product/app/workflow/borrow/step/ask/pick/go"
# operation (one file each) becomes handler, actor (a list file) becomes role, the part choice (key choices) becomes pick (picks)
RENAMES = {"operation": ("handler", "was: {kind: operation}\n"),
           "actor": ("role", "was: {kind: actor, file: actors.yml}\n"),
           "choice": ("pick", "was: {kind: choice, key: choices}\n")}


def _texts(renames: dict[str, tuple[str, str]]) -> dict[str, str]:
    texts = {}
    for item in files("ogy").joinpath("ontologies", "software", "kinds").iterdir():
        text, name = item.read_text(), item.name.removesuffix(".yml")
        for old, (new, _) in renames.items():
            text = re.sub(rf"(?<!: )\b{old}\b(?!:)", new, text)  # a link target or a path hop; never a field name
            text = text.replace(f"kind: {old}\n", f"kind: {new}\n").replace(f"  {old}: {old} ", f"  {old}: {new} ")  # a flow name
        text = text.replace("file: actors.yml", "file: roles.yml").replace("key: choices", "key: picks")
        new, was = renames.get(name, (name, ""))
        texts[f"kinds/{new}.yml"] = text + was
    return texts


def renamed() -> Ontology:
    return parse_kinds(_texts(RENAMES), packaged().declared)


@dataclass(frozen=True)
class Renamed(Target):
    def kinds(self) -> Ontology:
        return renamed()


@pytest.fixture
def before(repo: Path) -> str:
    """The fee, the operation and the choice agreed, the fee and the choice built: committed."""
    target = Target(repo)
    (repo / "docs/kb/product/app/decision/fee.yml").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/kb/product/app/decision/fee.yml").write_text(DECISION)
    writes.agree(target, writes.said("Yes", "ai:claude/1", None), [FEE, LEND, GO])
    for text in (FEE, GO):
        built.stamp(repo / "docs/kb", target.read()[1].entries[parse_address(text, target.kinds())].path, text,
                    built.Line(build_hash(target, text), {LEND: build_hash(target, LEND)} if text == GO else {}))
    assert not ops.run_check(target).value
    return commit(repo, "before the kind rename")


def test_a_renamed_kind_is_found_until_migrated(repo: Path, before: str) -> None:
    found = {(item.problem, item.path) for item in ops.run_check(Renamed(repo)).value}
    for path in ("product/app/actors.yml", "software/app/operation/lend.yml", "product/app/workflow/borrow.yml"):
        assert (Problem.NEEDS_MIGRATION, path) in found


def test_migrate_moves_the_entries_and_keeps_what_was_agreed_and_built(repo: Path, before: str) -> None:
    target = Renamed(repo)
    lines = ops.run_migrate(target).value.lines()
    assert "moved software/app/operation/lend.yml to software/app/handler/lend.yml (a kind was renamed)" in lines
    assert not (repo / "docs/kb/product/app/actors.yml").exists() and (repo / "docs/kb/product/app/roles.yml").is_file()
    assert "picks:" in (repo / "docs/kb/product/app/workflow/borrow.yml").read_text()
    assert NEW_GO in (repo / "docs/kb/software/app/handler/lend.yml").read_text()  # the link follows the part
    assert not ops.run_check(target).value
    entries = target.read()[1].entries
    for text in (NEW_LEND, NEW_GO, FEE):
        assert entries[parse_address(text, target.kinds())].fields["agreed"]["hash"] == fingerprint(target, text)
    work = {item.address for item in ops.run_work(target).value}
    assert FEE not in work and NEW_GO not in work  # built, and still built: a rename is no work
    assert ops.run_migrate(target).value.lines() == ["nothing to migrate"]


def test_the_base_is_read_under_the_new_kind_names(repo: Path, before: str) -> None:
    ops.run_migrate(Renamed(repo))
    commit(repo, "migrated")
    assert not ops.run_check(Renamed(repo, rev="HEAD"), base=before).value  # nothing lost, no edited answer


def test_an_old_kind_name_is_no_kind_any_more() -> None:
    with pytest.raises(OntologyError, match="handler: was decision, which is still a kind"):
        parse_kinds(_texts({"operation": ("handler", "was: {kind: decision}\n")}), packaged().declared)
