"""Checks against the base commit: two snapshots, the base and now."""

import dataclasses
import datetime as dt
from collections.abc import Callable, Mapping

from tests.conftest import GOOD, Kb

from ogy.base import check_base, read_ledgers
from ogy.removed import Item, Ledger
from ogy.snapshot import Snapshot, build
lazy from ogy.ontology import Ontology

type MakeKb = Callable[[Mapping[str, str | None] | None], Kb]

DECISION = """\
question: Which way?
options:
  a: {says: A}
answers:
  - {chose: a, said: A please, at: '2026-11-12T10:00:00+01:00', where: 'bd:x'}
"""
GONE = "product/app/actors.yml"


def snap(ontology: Ontology, changes: Mapping[str, str | None] | None = None) -> Snapshot:
    """A knowledge base held in memory: the good one with `{path: text}` added, replaced or (None) left out."""
    files = {**GOOD, **(changes or {})}
    return build(ontology, {path: text for path, text in files.items() if text is not None})


def removal(address: str) -> Item:
    when = dt.datetime(2026, 11, 18, tzinfo=dt.UTC)
    return Item(address, address.split("/")[-2], None, None, None, None, None, when, "a" * 40, "b" * 12, "v5", {})


def kinds(base: Snapshot, snapshot: Snapshot, **ledgers: Ledger) -> set[tuple[str, str]]:
    found = check_base(snapshot, base, ledgers)
    return {(str(f.problem), str(f.address)) for f in found}


def test_append_only_rejects_edit_and_removal(ontology: Ontology) -> None:
    base = snap(ontology, {"product/app/decision/d1.yml": DECISION})
    added = DECISION + "  - {chose: a, said: A again, at: '2026-11-13T10:00:00+01:00', where: 'bd:x'}\n"
    edited = DECISION.replace("A please", "B please")
    dropped = DECISION.replace("answers:\n", "answers: []\n").split("  - {")[0]
    assert kinds(base, snap(ontology, {"product/app/decision/d1.yml": added})) == set()
    assert kinds(base, snap(ontology, {"product/app/decision/d1.yml": edited})) == {("edited-append-only", "product/app/decision/d1")}
    assert kinds(base, snap(ontology, {"product/app/decision/d1.yml": dropped})) == {("edited-append-only", "product/app/decision/d1")}


def test_id_removed_is_removal_work(ontology: Ontology) -> None:
    base = snap(ontology, {"product/app/interface/other.yml": "says: Other.\n"})
    now = snap(ontology, {"product/app/interface/other.yml": None})
    assert kinds(base, now) == {("removed-unrecorded", "product/app/interface/other")}


def test_removal_without_item(ontology: Ontology) -> None:
    base = snap(ontology, {"product/app/workflow/sign-in.yml": None})
    assert kinds(base, snap(ontology, {"product/app/workflow/sign-in.yml": None, "product/app/interface/sign-in-page.yml": None})) == {
        ("removed-unrecorded", "product/app/interface/sign-in-page")
    }
    # a recorded removal, and a part covered by its entity's item, are fine
    full, now = snap(ontology), snap(ontology, {"product/app/workflow/sign-in.yml": None, "product/app/interface/sign-in-page.yml": None})
    ledger = Ledger("product/app", 1, (removal("product/app/workflow/sign-in"), removal("product/app/interface/sign-in-page")))
    assert kinds(full, now, app=ledger) == set()


def test_removed_item_may_not_change(ontology: Ontology) -> None:
    now = snap(ontology)
    old = Ledger("product/app", 1, (removal("product/app/quantity/a"), removal("product/app/quantity/b")))
    appended = Ledger("product/app", 1, (*old.items, removal("product/app/quantity/c")))
    edited = Ledger("product/app", 1, (dataclasses.replace(old.items[0], said="x"), old.items[1]))
    assert check_base(now, now, {"product/app": appended}, {"product/app": old}) == []
    found = check_base(now, now, {"product/app": edited}, {"product/app": old})
    assert [str(f.problem) for f in found] == ["edited-append-only"]
    assert [str(f.problem) for f in check_base(now, now, {}, {"product/app": old})] == ["edited-append-only"]


def test_read_ledgers_reads_removed_files(kb: MakeKb) -> None:
    text = (
        "format: 1\nitems:\n  - {id: product/app/quantity/a, kind: quantity, parent: null, title: null, said: null, why: null,"
        " replaced_by: null, at: '2026-11-18T09:12:00+01:00', last_seen: "
        + "a" * 40
        + ", hash: "
        + "b" * 12
        + ", ontology: v5, snapshot: {says: A}}\n"
    )
    ledgers, problems = read_ledgers(kb({"product/app/removed.yml": text}).source)
    assert problems == []
    assert [item.id for item in ledgers["product/app"].items] == ["product/app/quantity/a"]
    unknown, problems = read_ledgers(kb({"product/app/removed.yml": "format: 9\nitems: []\n"}).source)
    assert unknown == {} and [item.code for item in problems] == ["bad-removed"]


def test_a_kind_the_ontology_renamed_is_followed_and_nothing_else_may_change(ontology: Ontology) -> None:
    other = "question: Who?\noptions:\n  a: {label: A, sets: {}}\nproposal: {chose: a, why: x}\n"
    delegated = DECISION.replace("where: 'bd:x'", "where: 'bd:x', delegated: product/app/decision/d2")
    retired = delegated.replace("/decision/d2", "/question/d2")  # a kind this ontology no longer has
    base = snap(ontology, {"product/app/decision/d1.yml": retired})
    now = {"product/app/decision/d1.yml": delegated, "product/app/decision/d2.yml": other}
    assert kinds(base, snap(ontology, now)) == set()
    changed = {**now, "product/app/decision/d1.yml": delegated.replace("A please", "B please")}
    assert kinds(base, snap(ontology, changed)) == {("edited-append-only", "product/app/decision/d1")}
