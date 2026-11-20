"""`ogy migrate` merges two kinds into one: the new kind lists the old ones (`was: [...]`), their entries move into its folder,
each old kind's own field names follow (`was.renamed`), every address is rewritten and what was agreed or built stays current.
Two entries that would become one are refused until one is moved to a new id."""

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import any_yaml
import pytest
from tests.conftest import commit
from tests.test_migrate import build_hash, fingerprint

from ogy import built, ops, writes
from ogy.model import Problem, parse_address
from ogy.ontology import Ontology, OntologyError, packaged, parse_kinds
from ogy.target import Target
from ogy.writes import WriteRefused

PAGE, CLI, OLD = "software/app/view/page", "software/app/command/lend", "software/app/view/old"
NEW_PAGE, NEW_CLI = "software/app/interface/page", "software/app/interface/lend"
SERVES = "serves: [product/app/workflow/borrow/step/ask]\nsrc: ['code:app.py#lend']\n"
BEFORE = Path(__file__).parent / "fixtures" / "before-interface"  # view.yml and command.yml as they were before the merge
SHIPPED = files("ogy").joinpath("ontologies", "software", "kinds")


def _texts(was: str | None = None) -> dict[str, str]:
    """The shipped kinds; with `was`, interface's `was:` block replaced by it."""
    texts = {f"kinds/{item.name}": item.read_text() for item in SHIPPED.iterdir()}
    if was is not None:
        head, rest = texts["kinds/interface.yml"].split("about:", 1)
        texts["kinds/interface.yml"] = "kind: interface\n" + was + "about:" + rest
        assert head.startswith("kind: interface\nwas:")
    return texts


def unmerged() -> Ontology:
    """The software kinds as they were before view and command merged into interface."""
    texts = {rel: text.replace("[interface]", "[view, command]").replace("[interface, ", "[view, command, ").replace(
        ", interface]", ", view, command]")
             for rel, text in _texts().items() if rel != "kinds/interface.yml"}
    texts |= {f"kinds/{item.name}": item.read_text() for item in BEFORE.iterdir()}
    return parse_kinds(texts, packaged().declared)


@dataclass(frozen=True)
class Unmerged(Target):
    def kinds(self) -> Ontology:
        return unmerged()


@pytest.fixture
def before(repo: Path) -> str:
    """A view and a command agreed and built, a decision that sets the view, a removed view in the ledger: committed."""
    target, kb = Unmerged(repo), repo / "docs/kb"
    (kb / "software/app/interface/page.yml").rename(kb / "software/app/interface/view.tmp")
    (kb / "software/app/view").mkdir(parents=True)
    (kb / "software/app/interface/view.tmp").rename(kb / f"{PAGE}.yml")
    (kb / "software/app/interface").rmdir()
    (kb / f"{PAGE}.yml").write_text((kb / f"{PAGE}.yml").read_text().replace("form: web\n", ""))
    (kb / "software/app/command").mkdir(parents=True)
    (kb / f"{CLI}.yml").write_text(f"says: Lend from the command line.\ninvoked_as: ogy lend\n{SERVES}")
    (kb / f"{OLD}.yml").write_text(f"says: The old page.\n{SERVES}")
    (kb / "software/app/decision").mkdir(parents=True)
    (kb / "software/app/decision/page.yml").write_text(
        f"question: Is the page plain?\noptions:\n  plain: {{label: Plain, sets: {{{PAGE}: {{says: The page.}}}}}}\n"
        "proposal: {chose: plain, why: Simple.}\n")
    ops.run_remove(target, OLD, why="not needed")
    writes.agree(target, writes.said("Yes", "ai:claude/1", None), [PAGE, CLI])
    for text in (PAGE, CLI):
        built.stamp(kb, target.read()[1].entries[parse_address(text, target.kinds())].path, text, built.Line(build_hash(target, text)))
    assert not ops.run_check(target).value
    return commit(repo, "before the merge")


def test_migrate_merges_two_kinds_and_keeps_what_was_agreed_and_built(repo: Path, before: str) -> None:
    target, kb = Target(repo), repo / "docs/kb"
    found = {(item.problem, item.path) for item in ops.run_check(target).value}
    assert {(Problem.NEEDS_MIGRATION, f"{PAGE}.yml"), (Problem.NEEDS_MIGRATION, f"{CLI}.yml")} <= found
    ledger = (kb / "software/app/removed.yml").read_text()
    lines = ops.run_migrate(target).value.lines()
    assert f"moved {CLI}.yml to {NEW_CLI}.yml (a kind was renamed)" in lines
    assert not (kb / "software/app/view").exists() and not (kb / "software/app/command").exists()
    assert NEW_PAGE in (kb / "software/app/decision/page.yml").read_text()  # the address follows the entry
    assert (kb / "software/app/removed.yml").read_text() == ledger and OLD in ledger  # a ledger keeps the names its items had
    assert not ops.run_check(target).value
    entries = target.read()[1].entries
    cli = entries[parse_address(NEW_CLI, target.kinds())].fields
    assert cli["form"] == "cli" and cli["invoked_as"] == "ogy lend"  # the command's default, its own field kept
    assert entries[parse_address(NEW_PAGE, target.kinds())].fields["form"] == "web"  # the view's default
    for text in (NEW_PAGE, NEW_CLI):
        assert entries[parse_address(text, target.kinds())].fields["agreed"]["hash"] == fingerprint(target, text)
    work = {item.address for item in ops.run_work(target).value}
    assert NEW_PAGE not in work and NEW_CLI not in work  # built, and still built: a merge is no work
    assert ops.run_migrate(target).value.lines() == ["nothing to migrate"]
    commit(repo, "merged")
    assert not ops.run_check(Target(repo, rev="HEAD"), base=before).value  # the base read through the merge: nothing lost


def test_a_view_and_a_command_of_one_id_are_refused_until_one_moves(repo: Path, before: str) -> None:
    kb = repo / "docs/kb"
    (kb / "software/app/command/page.yml").write_text(f"says: The page as a command.\ninvoked_as: ogy page\n{SERVES}")
    commit(repo, "a command of the view's id")
    why = (f"software/app/command/page and {PAGE} would both become {NEW_PAGE}: `ogy move` one of them to a new id first, "
           "with the ogy version (its kinds) from before the merge")
    found = {(item.problem, item.path, item.detail) for item in ops.run_check(Target(repo)).value}
    assert (Problem.NEEDS_MIGRATION, f"{PAGE}.yml", why) in found
    assert (Problem.NEEDS_MIGRATION, "software/app/command/page.yml", why) in found
    with pytest.raises(WriteRefused) as refused:
        ops.run_migrate(Target(repo))
    assert refused.value.reasons == [f"needs-migration: {why}"]
    assert (kb / f"{PAGE}.yml").is_file() and (kb / f"{CLI}.yml").is_file()  # nothing moved
    assert (kb / "built" / f"{PAGE}.yml").is_file()


HOW = """\
question: How is a tool lent from the command line?
options:
  lend: {label: ogy lend, sets: {software/app/command/lend: {invoked_as: ogy lend}}}
proposal: {chose: lend, why: Short.}
"""


def test_a_removed_command_is_read_under_the_merged_kind(repo: Path, before: str) -> None:
    """The ledger keeps `command/gone`; read as `interface/gone` it covers its removal since an older base and still forbids
    the id. A decision's `sets` gives the command's fields under the interface's names."""
    kb, gone = repo / "docs/kb", "software/app/command/gone"
    (kb / f"{gone}.yml").write_text(f"says: Gone.\ninvoked_as: ogy gone\n{SERVES}")
    (kb / "software/app/decision/how.yml").write_text(HOW)
    early = commit(repo, "a command that goes")
    ops.run_remove(Unmerged(repo), gone, why="not needed")
    commit(repo, "removed")
    ops.run_migrate(Target(repo))
    commit(repo, "merged")
    how = any_yaml.load((kb / "software/app/decision/how.yml").read_text())
    assert isinstance(how, dict) and how["options"]["lend"]["sets"] == {NEW_CLI: {"invoked_as": "ogy lend"}}
    assert gone in (kb / "software/app/removed.yml").read_text()
    assert not ops.run_check(Target(repo, rev="HEAD"), base=early).value
    decided = kb / "software/app/decision/page.yml"
    decided.write_text(decided.read_text().replace(NEW_PAGE, "software/app/interface/gone"))
    found = {(item.problem, str(item.address or item.path)) for item in ops.run_check(Target(repo, rev=".")).value}
    assert found == {(Problem.NOT_IN_FORCE, "software/app/decision/page")}  # as a sets key to any removed entry, one finding
    (kb / "software/app/interface/gone.yml").write_text(f"says: Back.\nform: cli\ninvoked_as: ogy gone\n{SERVES}")
    found = {(item.problem, str(item.address or item.path)) for item in ops.run_check(Target(repo, rev=".")).value}
    assert (Problem.ID_REUSED, "software/app/interface/gone") in found


def test_a_merge_keeps_one_file_per_entry_and_renames_into_fields() -> None:
    renamed = "was: [{kind: view}, {kind: command, renamed: {invoked_as: shape}}]\n"
    with pytest.raises(OntologyError, match="was command renamed invoked_as to shape, which is no field"):
        parse_kinds(_texts(renamed), packaged().declared)
    with pytest.raises(OntologyError, match="was command renamed says, which is still a field"):
        parse_kinds(_texts(renamed.replace("invoked_as: shape", "says: form")), packaged().declared)
    some = _texts("was: [{kind: view}, {kind: command, renamed: {invoked_as: form}}]\n")
    picked = {**some, "kinds/step.yml": some["kinds/step.yml"] + "input_from: {serves: {fields: [form]}}\n"}
    with pytest.raises(OntologyError, match="form, which interface took from only some of the kinds"):
        parse_kinds(picked, packaged().declared)
    with pytest.raises(OntologyError, match="was view, as another kind was"):
        parse_kinds(_texts("was: [{kind: view}, {kind: view}]\n"), packaged().declared)
