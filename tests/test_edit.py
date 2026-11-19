"""Editing by address, the author's comments, YAML 1.2 and the fingerprint."""

from pathlib import Path

import any_yaml
import pytest

from ogy.edit import Editor
from ogy.model import Address
from ogy.ontology import Ontology, packaged

WORKFLOW = """\
# Why this exists: the owner, 2026-11-16.
says: A tool is lent.  # the one sentence
start: ask
steps:
  ask:
    says: The member asks.
    choices:
      go: {label: Borrow, then: done}
ends:
  done: {result: success, says: Lent.}
"""
FLOW = Address("product", "app", (("workflow", "borrow"),))
ASK = FLOW.part("step", "ask")


@pytest.fixture
def editor(tmp_path: Path) -> Editor:
    (tmp_path / "docs/kb/product/app/workflow").mkdir(parents=True)
    (tmp_path / "docs/kb/product/app/workflow/borrow.yml").write_text(WORKFLOW)
    (tmp_path / "docs/kb/product/app/quantities.yml").write_text("- {id: fee, says: The fee., is: 2, unit: EUR}\n")
    return Editor(tmp_path, "docs/kb", packaged())


def test_put_adds_entity_list_item_and_parts(editor: Editor) -> None:
    editor.put(Address("product", "app", (("actor", "member"),)), {"says": "A person.", "nature": "human"})
    editor.put(Address("product", "app", (("quantity", "late"),)), {"says": "Late.", "is": 1, "unit": "days"})
    editor.put(ASK.part("timeout"), {"after": "product/app/quantity/late", "then": "done"})
    editor.put(ASK.part("choice", "stay"), {"label": "Stay", "then": "done"})
    snapshot = editor.snapshot()
    assert {str(address) for address in snapshot.entries} >= {
        "product/app/actor/member", "product/app/quantity/late", "product/app/workflow/borrow/step/ask/timeout",
        "product/app/workflow/borrow/step/ask/choice/stay"}
    assert snapshot.entries[Address("product", "app", (("quantity", "late"),))].path == "product/app/quantities.yml"
    assert snapshot.findings == []


def test_update_sets_and_removes_fields(editor: Editor) -> None:
    fee = Address("product", "app", (("quantity", "fee"),))
    editor.update(fee, {"is": 3})
    assert editor.snapshot().entries[fee].fields["is"] == 3
    editor.update(fee, {"unit": None})
    assert "unit" not in editor.snapshot().entries[fee].fields
    editor.update(ASK.part("choice", "go"), {"label": "Take it"})
    assert editor.snapshot().entries[ASK.part("choice", "go")].fields["label"] == "Take it"


def test_remove_deletes_the_entry_wherever_it_lives(editor: Editor) -> None:
    editor.remove(ASK.part("choice", "go"))
    editor.remove(Address("product", "app", (("quantity", "fee"),)))
    entries = editor.snapshot().entries
    assert ASK.part("choice", "go") not in entries and Address("product", "app", (("quantity", "fee"),)) not in entries and ASK in entries
    editor.remove(FLOW)
    assert not (editor.root / "docs/kb/product/app/workflow/borrow.yml").exists()


def test_edits_keep_the_authors_comments(editor: Editor) -> None:
    editor.update(FLOW, {"says": "A tool is lent for a week."})
    text = (editor.root / "docs/kb/product/app/workflow/borrow.yml").read_text()
    assert text.startswith("# Why this exists: the owner, 2026-11-16.\n")
    assert "says: A tool is lent for a week. # the one sentence" in text


def test_yaml_1_2_reads_on_as_a_word() -> None:
    assert any_yaml.load("on: a member presses cancel\n") == {"on": "a member presses cancel"}


def test_fingerprint_follows_fields_that_are_not_notes(editor: Editor, ontology: Ontology) -> None:
    fee = Address("product", "app", (("quantity", "fee"),))
    before = editor.snapshot().fingerprint(fee)
    editor.update(fee, {"title": "The late fee", "src": ["code:src/x.py#fee"], "proof": None})
    assert editor.snapshot().fingerprint(fee) == before
    editor.update(fee, {"is": 5})
    assert editor.snapshot().fingerprint(fee) != before
    meaning = editor.snapshot().fingerprint(fee)
    editor.update(fee, {"proof": ["tests/test_fee.py::test_fee"]})
    snapshot = editor.snapshot()
    assert snapshot.fingerprint(fee) == meaning  # a new proof never sends the entry back to the owner
    assert snapshot.build_hash(fee) != snapshot.build_hash(fee, proofs=False)  # but it is work for the built record


def test_a_parent_fingerprint_follows_its_unkeyed_parts_and_declared_paths(editor: Editor) -> None:
    go = ASK.part("choice", "go")
    before = editor.snapshot().fingerprint(go)
    editor.update(go, {"effects": [{"do": "tell", "on": "product/app/actor/member"}]})
    after = editor.snapshot().fingerprint(go)
    assert after != before
    editor.update(go, {"effects": [{"do": "write", "on": "product/app/actor/member"}]})
    assert editor.snapshot().fingerprint(go) not in {before, after}


def test_a_rule_holder_stales_nothing_and_a_pin_makes_the_rule_suspect(editor: Editor) -> None:
    rule, mailer = Address("software", "app", (("rule", "one-mail"),)), Address("software", "app", (("dependency", "mailer"),))
    editor.put(rule, {"says": "One mail a day."})
    editor.put(mailer, {"says": "Sends mail.", "pin": "smtplib 1"})
    before = editor.snapshot()
    editor.update(FLOW, {"satisfies": [str(rule)]})  # a workflow held to it: neither changes
    editor.update(mailer, {"satisfies": [str(rule)]})  # a pinned external held to it: only the rule changes
    held = editor.snapshot()
    assert held.build_hash(FLOW) == before.build_hash(FLOW) and held.build_hash(mailer) == before.build_hash(mailer)
    assert held.build_hash(rule) != before.build_hash(rule)
    editor.update(mailer, {"pin": "smtplib 2"})
    assert editor.snapshot().build_hash(rule) not in {before.build_hash(rule), held.build_hash(rule)}
    editor.update(mailer, {"satisfies": None})
    assert editor.snapshot().build_hash(rule) == before.build_hash(rule)  # a path that reaches nothing leaves it as it was
    assert editor.snapshot().fingerprint(rule) == before.fingerprint(rule)  # a pin never changes the rule's meaning
