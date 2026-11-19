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

FEE, LEND, GO = "product/app/quantity/fee", "software/app/handler/lend", "product/app/workflow/borrow/step/ask/choice/go"
NEW_LEND, NEW_GO = "software/app/worker/lend", "product/app/workflow/borrow/step/ask/pick/go"
# handler (one file each) becomes worker, actor (a list file) becomes role, the part choice (key choices) becomes pick (picks)
RENAMES = {"handler": ("worker", "was: {kind: handler}\n"),
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
        kept = "".join(line for line in text.splitlines(keepends=True) if not (was and line.startswith("was:")))
        texts[f"kinds/{new}.yml"] = kept + was  # the kind's old name: the one it had before this rename
    return texts


def renamed() -> Ontology:
    return parse_kinds(_texts(RENAMES), packaged().declared)


@dataclass(frozen=True)
class Renamed(Target):
    def kinds(self) -> Ontology:
        return renamed()


@pytest.fixture
def before(repo: Path) -> str:
    """The fee, the handler and the choice agreed, the fee and the choice built: committed."""
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
    for path in ("product/app/actors.yml", "software/app/handler/lend.yml", "product/app/workflow/borrow.yml"):
        assert (Problem.NEEDS_MIGRATION, path) in found


def test_migrate_moves_the_entries_and_keeps_what_was_agreed_and_built(repo: Path, before: str) -> None:
    target = Renamed(repo)
    lines = ops.run_migrate(target).value.lines()
    assert "moved software/app/handler/lend.yml to software/app/worker/lend.yml (a kind was renamed)" in lines
    assert not (repo / "docs/kb/product/app/actors.yml").exists() and (repo / "docs/kb/product/app/roles.yml").is_file()
    assert "picks:" in (repo / "docs/kb/product/app/workflow/borrow.yml").read_text()
    assert NEW_GO in (repo / "docs/kb/software/app/worker/lend.yml").read_text()  # the link follows the part
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
    with pytest.raises(OntologyError, match="worker: was decision, which is still a kind"):
        parse_kinds(_texts({"handler": ("worker", "was: {kind: decision}\n")}), packaged().declared)


LOAN = """\
says: A loan.
src: ['code:app.py#lend']
attributes:
  member: {says: Who borrows., type: one, of: product/app/entity/loan}
  notes: {says: What the desk wrote., type: list}
  due: {says: When it is due., type: time}
"""
HEARD = DECISION.replace("proposal: {chose: two, why: Small.}", "proposal: {chose: two, why: Small., heard: {said: Two seems fair}}")


def test_migrate_rewrites_the_values_a_kind_reshaped(repo: Path) -> None:
    """attribute type one, list and time, and a proposal's heard part, are rewritten; what was agreed stays agreed."""
    target, member = Target(repo), "product/app/entity/loan/attribute/member"
    (repo / "docs/kb/product/app/entity").mkdir(parents=True)
    (repo / "docs/kb/product/app/entity/loan.yml").write_text(LOAN)
    (repo / "docs/kb/product/app/decision").mkdir(parents=True)
    (repo / "docs/kb/product/app/decision/fee.yml").write_text(HEARD)
    writes.agree(target, writes.said("Yes", "ai:claude/1", None), [member])
    base = commit(repo, "before the values changed")
    found = {(item.problem, str(item.address)) for item in ops.run_check(target).value}
    assert (Problem.NEEDS_MIGRATION, member) in found and (Problem.NEEDS_MIGRATION, "product/app/decision/fee/proposal") in found
    ops.run_migrate(target)
    assert not ops.run_check(target).value
    entries = target.read()[1].entries
    fields = {key: entries[parse_address(f"product/app/entity/loan/attribute/{key}", target.kinds())].fields
              for key in ("member", "notes", "due")}
    assert "type" not in fields["member"] and fields["notes"]["many"] is True and fields["due"]["type"] == "datetime"
    assert fields["member"]["agreed"]["hash"] == fingerprint(target, member)  # the owner's yes still holds
    assert entries[parse_address("product/app/decision/fee/proposal", target.kinds())].fields["heard"] == "Two seems fair"
    commit(repo, "migrated")
    assert not ops.run_check(Target(repo, rev="HEAD"), base=base).value
