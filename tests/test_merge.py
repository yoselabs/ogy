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
WAS = "was: [{kind: view, defaults: {form: page}}, {kind: command, renamed: {invoked_as: form}}]\n"


def _texts(was: str = WAS) -> dict[str, str]:
    """The software kinds with view and command merged into interface: a command's `invoked_as` is the interface's `form`."""
    root, texts = files("ogy").joinpath("ontologies", "software", "kinds"), {}
    for item in root.iterdir():
        text = item.read_text().replace("[view, command]", "[interface]")
        if item.name == "view.yml":
            text = was + text.replace("kind: view\n", "kind: interface\n") + "  form: {required: true}\n"
        if item.name != "command.yml":
            texts[f"kinds/{item.name.replace('view', 'interface')}"] = text
    return texts


def merged() -> Ontology:
    return parse_kinds(_texts(), packaged().declared)


@dataclass(frozen=True)
class Merged(Target):
    def kinds(self) -> Ontology:
        return merged()


@pytest.fixture
def before(repo: Path) -> str:
    """A view and a command agreed and built, a handler that cites the view, a removed view in the ledger: committed."""
    target, kb = Target(repo), repo / "docs/kb"
    (kb / "software/app/command").mkdir(parents=True)
    (kb / f"{CLI}.yml").write_text(f"says: Lend from the command line.\ninvoked_as: ogy lend\n{SERVES}")
    (kb / f"{OLD}.yml").write_text(f"says: The old page.\n{SERVES}")
    handler = kb / "software/app/handler/lend.yml"
    handler.write_text(handler.read_text() + f"because: [{PAGE}]\n")
    ops.run_remove(target, OLD, why="not needed")
    writes.agree(target, writes.said("Yes", "ai:claude/1", None), [PAGE, CLI])
    for text in (PAGE, CLI):
        built.stamp(kb, target.read()[1].entries[parse_address(text, target.kinds())].path, text, built.Line(build_hash(target, text), {}))
    assert not ops.run_check(target).value
    return commit(repo, "before the merge")


def test_migrate_merges_two_kinds_and_keeps_what_was_agreed_and_built(repo: Path, before: str) -> None:
    target, kb = Merged(repo), repo / "docs/kb"
    found = {(item.problem, item.path) for item in ops.run_check(target).value}
    assert {(Problem.NEEDS_MIGRATION, f"{PAGE}.yml"), (Problem.NEEDS_MIGRATION, f"{CLI}.yml")} <= found
    ledger = (kb / "software/app/removed.yml").read_text()
    lines = ops.run_migrate(target).value.lines()
    assert f"moved {CLI}.yml to {NEW_CLI}.yml (a kind was renamed)" in lines
    assert not (kb / "software/app/view").exists() and not (kb / "software/app/command").exists()
    assert NEW_PAGE in (kb / "software/app/handler/lend.yml").read_text()  # the link follows the entry
    assert (kb / "software/app/removed.yml").read_text() == ledger and OLD in ledger  # a ledger keeps the names its items had
    assert not ops.run_check(target).value
    entries = target.read()[1].entries
    cli = entries[parse_address(NEW_CLI, target.kinds())].fields
    assert cli["form"] == "ogy lend" and "invoked_as" not in cli  # the command's own field under the interface's name
    assert entries[parse_address(NEW_PAGE, target.kinds())].fields["form"] == "page"  # the view's default
    for text in (NEW_PAGE, NEW_CLI):
        assert entries[parse_address(text, target.kinds())].fields["agreed"]["hash"] == fingerprint(target, text)
    work = {item.address for item in ops.run_work(target).value}
    assert NEW_PAGE not in work and NEW_CLI not in work  # built, and still built: a merge is no work
    assert ops.run_migrate(target).value.lines() == ["nothing to migrate"]
    commit(repo, "merged")
    assert not ops.run_check(Merged(repo, rev="HEAD"), base=before).value  # the base read through the merge: nothing lost


def test_a_view_and_a_command_of_one_id_are_refused_until_one_moves(repo: Path, before: str) -> None:
    kb = repo / "docs/kb"
    (kb / "software/app/command/page.yml").write_text(f"says: The page as a command.\ninvoked_as: ogy page\n{SERVES}")
    commit(repo, "a command of the view's id")
    why = (f"software/app/command/page and {PAGE} would both become {NEW_PAGE}: `ogy move` one of them to a new id first, "
           "with the ogy version (its kinds) from before the merge")
    found = {(item.problem, item.path, item.detail) for item in ops.run_check(Merged(repo)).value}
    assert (Problem.NEEDS_MIGRATION, f"{PAGE}.yml", why) in found
    assert (Problem.NEEDS_MIGRATION, "software/app/command/page.yml", why) in found
    with pytest.raises(WriteRefused) as refused:
        ops.run_migrate(Merged(repo))
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
    (kb / "product/app/decision").mkdir(parents=True)
    (kb / "product/app/decision/how.yml").write_text(HOW)
    early = commit(repo, "a command that goes")
    ops.run_remove(Target(repo), gone, why="not needed")
    commit(repo, "removed")
    ops.run_migrate(Merged(repo))
    commit(repo, "merged")
    how = any_yaml.load((kb / "product/app/decision/how.yml").read_text())
    assert isinstance(how, dict) and how["options"]["lend"]["sets"] == {NEW_CLI: {"form": "ogy lend"}}
    assert gone in (kb / "software/app/removed.yml").read_text()
    assert not ops.run_check(Merged(repo, rev="HEAD"), base=early).value
    handler = kb / "software/app/handler/lend.yml"
    handler.write_text(handler.read_text().replace(NEW_PAGE, "software/app/interface/gone"))
    found = {(item.problem, str(item.address or item.path)) for item in ops.run_check(Merged(repo, rev=".")).value}
    assert found == {(Problem.DANGLING_LINK, "software/app/handler/lend")}  # as a link to any removed entry, one finding
    (kb / "software/app/interface/gone.yml").write_text(f"says: Back.\nform: ogy gone\n{SERVES}")
    found = {(item.problem, str(item.address or item.path)) for item in ops.run_check(Merged(repo, rev=".")).value}
    assert (Problem.ID_REUSED, "software/app/interface/gone") in found


def test_a_merge_keeps_one_file_per_entry_and_renames_into_fields() -> None:
    with pytest.raises(OntologyError, match="was command renamed invoked_as to shape, which is no field"):
        parse_kinds(_texts(WAS.replace("form", "shape")), packaged().declared)
    with pytest.raises(OntologyError, match="was command renamed says, which is still a field"):
        parse_kinds(_texts(WAS.replace("invoked_as: form", "says: form")), packaged().declared)
    picked = {**_texts(), "kinds/step.yml": _texts()["kinds/step.yml"] + "input_from: {serves: {fields: [form]}}\n"}
    with pytest.raises(OntologyError, match="form, which interface took from only some of the kinds"):
        parse_kinds(picked, packaged().declared)
    with pytest.raises(OntologyError, match="was view, as another kind was"):
        parse_kinds(_texts("was: [{kind: view}, {kind: view}]\n"), packaged().declared)
