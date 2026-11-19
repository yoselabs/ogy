"""`ogy migrate`: a kind file that renames or drops a field declares it, and the entries follow without going stale; a dropped
value comes back to the owner."""

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import pytest
from tests.conftest import commit

from ogy import built, ops, writes
from ogy.model import Problem, parse_address
from ogy.ontology import Ontology, OntologyError, packaged, parse_kinds
from ogy.receipts import Status
from ogy.target import Target

FEE, LEND, GO = "product/app/value/fee", "software/app/operation/lend", "product/app/workflow/borrow/step/ask/choice/go"
TIMEOUT, ASKED = "product/app/workflow/borrow/step/ask/timeout", "product/app/decision/fee"
DECISION = """\
question: How much is the fee?
options:
  two: {label: Two euros, sets: {product/app/value/fee: {is: 2, unit: EUR}}}
guess: {chose: two, why: Small.}
"""
EFFECT = files("ogy").joinpath("ontologies", "software", "kinds", "effect.yml").read_text()
EFFECT_PAIRS = [line + "\n" for line in EFFECT.splitlines() if line.startswith("requires:") or "if_equals: {field: do" in line]
# value.unit becomes `per`, effect.on is dropped, answer.note becomes `hedge` (the paths and names that read them follow);
# a pair whose first text is empty appends the second to the file
CHANGES = {
    "value.yml": [("  unit: {required: true}", "  per: {required: true}"), ("", "renamed: {unit: per}\n")],
    "effect.yml": [('  "on": {type: link, to: [transition, entity, attr, actor, external], required: true}\n', ""),
                   ("dropped: [value]", 'dropped: [value, "on"]'), *((line, "") for line in EFFECT_PAIRS)],
    "answer.yml": [("  note: {note: true}", "  hedge: {note: true}"), ("", "renamed: {note: hedge}\n")],
    "decision.yml": [("settling: {}", "settling: {note: hedge}")],
    "timeout.yml": [('"=unit"', '"=per"')],
}


def changed(changes: dict[str, list[tuple[str, str]]] = CHANGES) -> Ontology:
    root = files("ogy").joinpath("ontologies", "software", "kinds")
    texts = {}
    for item in root.iterdir():
        text = item.read_text()
        for old, new in changes.get(item.name, []):  # an empty `old` appends `new`
            assert old in text, (item.name, old)
            text = text.replace(old, new) if old else text + new
        texts[f"kinds/{item.name}"] = text
    return parse_kinds(texts, packaged().declared)


@dataclass(frozen=True)
class Changed(Target):
    """The repository read with the changed kinds, as a newer ogy would ship them."""

    def kinds(self) -> Ontology:
        return changed()


def fingerprint(target: Target, text: str) -> str:
    snapshot = target.read()[1]
    address = parse_address(text, snapshot.ontology)
    assert address is not None
    return snapshot.fingerprint(address)


def build_hash(target: Target, text: str) -> str:
    snapshot = target.read()[1]
    address = parse_address(text, snapshot.ontology)
    assert address is not None
    return snapshot.build_hash(address)


@pytest.fixture
def before(repo: Path) -> str:
    """The fee and the operation agreed, the fee, the choice and the timeout built, and an answer with a note: committed."""
    target = Target(repo)
    (repo / "docs/kb/product/app/decision/fee.yml").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/kb/product/app/decision/fee.yml").write_text(DECISION)
    ops.run_answer(target, ASKED, "two", "Two is fine", "ai:claude/1", note="for now")
    writes.agree(target, writes.said("Yes", "ai:claude/1", None), [FEE, LEND, GO])
    for text in (FEE, GO, TIMEOUT):
        built.stamp(repo / "docs/kb", target.read()[1].entries[parse_address(text, target.kinds())].path, text,
                    built.Line(build_hash(target, text)))
    assert not ops.run_check(target).value
    return commit(repo, "before the kind change")


def test_a_kind_change_is_found_until_migrated(repo: Path, before: str) -> None:
    found = {(item.problem, str(item.address), item.detail) for item in ops.run_check(Changed(repo)).value}
    assert (Problem.NEEDS_MIGRATION, FEE, "unit is now per: run `ogy migrate`") in found
    assert (Problem.NEEDS_MIGRATION, GO, "effects: on was dropped from the kind: run `ogy migrate`") in found
    assert (Problem.NEEDS_MIGRATION, ASKED, "answers: note is now hedge: run `ogy migrate`") in found


def test_a_rename_keeps_agreements_and_built_lines_current(repo: Path, before: str) -> None:
    target = Changed(repo)
    done = ops.run_migrate(target).value
    assert f"renamed {FEE} unit to per" in done.lines()
    assert not ops.run_check(target).value
    fee = target.read()[1].entries[parse_address(FEE, target.kinds())].fields
    assert fee["per"] == "EUR" and "unit" not in fee
    assert fee["agreed"]["hash"] == fingerprint(target, FEE)  # the owner's yes still holds
    work = {item.address: item.status for item in ops.run_work(target).value}
    assert FEE not in work and TIMEOUT not in work  # a rename is no work
    assert ops.run_migrate(target).value.lines() == ["nothing to migrate"]


def test_a_dropped_value_comes_back_to_the_owner(repo: Path, before: str) -> None:
    target = Changed(repo)
    lines = ops.run_migrate(target).value.lines()
    assert f"dropped {GO} effects.on (it held 'product/app/actor/member'): the owner sees this entry as changed" in lines
    entries = target.read()[1].entries
    go, lend = (entries[parse_address(text, target.kinds())].fields for text in (GO, LEND))
    assert go["agreed"]["hash"] != fingerprint(target, GO)  # changed since the owner agreed
    assert lend["agreed"]["hash"] == fingerprint(target, LEND)  # a changed row it performs is no change of its meaning
    assert {item.address: item.status for item in ops.run_work(target).value}[GO] is Status.CHANGED


def test_the_base_is_read_migrated(repo: Path, before: str) -> None:
    target = Changed(repo)
    ops.run_migrate(target)
    commit(repo, "migrated")
    assert not ops.run_check(Changed(repo, rev="HEAD"), base=before).value  # no edited answer, no lost field


def test_a_rename_names_a_field_of_the_kind() -> None:
    with pytest.raises(OntologyError, match="renamed unit to units, which is no field"):
        changed({"value.yml": [("  unit: {required: true}", "  per: {required: true}"), ("", "renamed: {unit: units}\n")]})
