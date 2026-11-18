"""The reserved area `shared` of each layer: only the kinds marked `shared` live there, and the old fixed folder `glossary/`
moves there with `ogy migrate`, keeping agreements, links and removed items."""

import json
from collections.abc import Callable
from pathlib import Path

from tests.conftest import Kb, commit, ogy

from ogy import ops, writes
from ogy.model import Problem
from ogy.status import Agreement, agreement
from ogy.target import Target

type Make = Callable[[dict[str, str | None] | None], Kb]
KB = "docs/kb"
TERMS = "- {id: fee, word: fee, says: What a loan costs.}\n- {id: old, word: old fee, says: What a loan cost before.}\n"
NAMES = "question: Name the fee?\noptions:\n  keep: {label: Keep it, sets: {glossary/term/fee: {says: What a loan costs.}}}\n"


def w(repo: Path, *argv: str) -> tuple[int, list[str]]:
    return ogy(repo, "--rev", ".", *argv)


def old_glossary(repo: Path) -> str:
    """The layout before: the fixed folder glossary/ with an agreed term, a removed one and a decision that names the term."""
    (repo / KB / "glossary").mkdir()
    (repo / KB / "glossary/terms.yml").write_text(TERMS)
    (repo / KB / "product/app/decision").mkdir(parents=True)
    (repo / KB / "product/app/decision/names.yml").write_text(NAMES)
    assert w(repo, "answer", "product/app/decision/names", "keep", "--said", "Keep", "--where", "ai:claude/1")[0] == 0
    assert w(repo, "remove", "glossary/term/old", "--why", "product/app/decision/names")[0] == 0
    writes.agree(Target(repo), writes.said("Yes", "ai:claude/1", None), ["glossary/term/fee"])
    return commit(repo, "the old layout")


def test_migrate_moves_the_glossary_folder_to_the_shared_area(repo: Path) -> None:
    base = old_glossary(repo)
    target = Target(repo)
    assert {(item.problem, str(item.address or item.path)) for item in ops.run_check(target).value} == {
        (Problem.NEEDS_MIGRATION, "glossary/term/fee"), (Problem.NEEDS_MIGRATION, "glossary/removed.yml")}
    assert w(repo, "move", "glossary/term/fee", "app")[0] == 3  # migrate first
    lines = ops.run_migrate(target).value.lines()
    assert lines[0] == "moved glossary/term/fee to product/shared/term/fee: `ogy move` it to the area that uses it"
    assert not (repo / KB / "glossary").exists() and (repo / KB / "product/shared/area.yml").is_file()
    assert "id: product/shared/term/old" in (repo / KB / "product/shared/removed.yml").read_text()
    assert "product/shared/term/fee:" in (repo / KB / "product/app/decision/names.yml").read_text()
    snapshot = target.read()[1]
    fee = snapshot.resolve("product/shared/term/fee")
    assert fee is not None and agreement(snapshot, fee) is Agreement.AGREED
    assert not ops.run_check(target).value and ops.run_migrate(target).value.lines() == ["nothing to migrate"]
    commit(repo, "migrated")
    assert not ops.run_check(Target(repo, rev="HEAD"), base=base).value  # the base is read migrated: nothing lost
    assert w(repo, "move", "product/shared/term/fee", "app")[0] == 0
    commit(repo, "the fee is the app's word")
    assert not ops.run_check(Target(repo, rev="HEAD"), base=base).value


def test_only_terms_actors_and_sets_live_in_the_shared_area(kb: Make) -> None:
    shared = {"product/shared/actors.yml": "- {id: owner, says: The owner., nature: human}\n",
              "product/shared/sets.yml": "- {id: colours, says: The colours., members: [red]}\n",
              "product/shared/glossary.yml": "- {id: fee, word: fee, says: What a loan costs.}\n",
              "software/shared/area.yml": "says: What two software areas use.\n",
              "software/shared/actors.yml": "- {id: ci, says: The CI runner., nature: program}\n"}
    assert not {item for item in kb(shared).findings() if item[0] is Problem.BAD_PATH}
    found = kb({"product/shared/values.yml": "- {id: fee, says: The fee., is: 2, unit: EUR}\n"}).findings()
    assert (Problem.BAD_PATH, "product/shared/values.yml") in found


def test_a_move_into_the_shared_area_needs_a_shared_kind(repo: Path) -> None:
    assert w(repo, "put", json.dumps({"address": "product/shared/area/shared", "says": "What two areas use."}))[0] == 0
    code, lines = w(repo, "move", "product/app/value/fee", "shared")
    assert code == 3 and "holds only what two areas use" in lines[0]
    assert w(repo, "move", "product/app/actor/member", "shared")[0] == 0


def test_a_folder_that_holds_only_its_removed_ledger_is_no_area(kb: Make) -> None:
    found = kb({"product/old/removed.yml": "format: 1\nitems: []\n"}).findings()
    assert not {item for item in found if item[0] is Problem.MISSING_ENTRY}
