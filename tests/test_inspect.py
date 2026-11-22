"""S1: lossless inspection of the tool library and ogy's own knowledge base."""

import json
from collections import Counter
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

import any_yaml
import pytest

from ogy.inspect import InspectionRequest, inspect
from ogy.kinds import Holds
from ogy.links import link_items, resolve
from ogy.ontology import packaged
from ogy.snapshot import build

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "tests/fixtures/tool-library/docs/kb"


def plain(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    return value


def read(root):
    files = {path.relative_to(root).as_posix(): path.read_text() for path in sorted(root.rglob("*.yml"))}
    return build(packaged(), files), files


def authored(entry, ontology, files):
    """Locate the original YAML value independently of the snapshot reader."""
    value = any_yaml.load(files[entry.path])
    kind = ontology.get(entry.address.path[0][0])
    if isinstance(value, list):
        value = next(item for item in value if item["id"] == entry.address.path[0][1])
        value = {key: item for key, item in value.items() if key != "id"}
    for name, key in entry.address.path[1:]:
        kind = ontology.get(name)
        assert isinstance(value, dict)
        value = value[kind.key]
        if kind.holding is Holds.MAP:
            assert isinstance(value, dict)
            value = value[key]
    assert isinstance(value, dict)
    return {
        key: item
        for key, item in value.items()
        if key not in {part.key for part in ontology.parts_of(kind.kind) if part.holding is not Holds.LIST}
    }


@pytest.mark.parametrize("root", [LIBRARY, ROOT / "docs/kb"], ids=["tool-library", "ogy"])
def test_every_entry_part_link_and_authored_value_survives(root):
    """Given either KB, inspection conserves entries, list parts and link occurrences and round-trips YAML fields."""
    snapshot, files = read(root)
    document = json.loads(json.dumps(inspect(snapshot), allow_nan=False))
    entries = document["entries"]
    assert Counter(item["address"] for item in entries) == Counter(str(address) for address in snapshot.entries)
    expected_parts, expected_relations = [], []
    for address, entry in sorted(snapshot.entries.items()):
        record = next(item for item in entries if item["address"] == str(address))
        assert record["fields"] == plain(authored(entry, snapshot.ontology, files))
        assert record["fields"] == plain(dict(entry.fields))
        assert (record["kind"], record["key"], record["layer"], record["area"]) == (
            address.kind,
            address.key,
            address.layer,
            address.area,
        )
        kind = snapshot.kind_of(address)
        assert record["sentence_field"] == (kind.sentence or {"absent": "not-declared"})
        if kind.sentence in entry.fields:
            assert record["sentence"] == plain(entry.fields[kind.sentence])
        descriptor = document["ontology"]["kinds"][kind.kind]
        assert descriptor["fields"] == plain({name: spec.model_dump(mode="json") for name, spec in kind.fields.items()})
        assert descriptor["parts"] == sorted(part.kind for part in snapshot.ontology.parts_of(kind.kind))
        for part in sorted(snapshot.ontology.parts_of(kind.kind), key=lambda item: item.kind):
            values = entry.fields.get(part.key or "")
            if part.holding is Holds.LIST and isinstance(values, list):
                for index, value in enumerate(values):
                    locator = {"owner": str(address), "field": part.key, "index": index}
                    expected_parts.append((locator, part.kind, plain(value)))
        for item in link_items(snapshot.ontology, entry):
            target = resolve(snapshot.ontology, snapshot.entries, address, item).target
            expected_relations.append((str(address), item.field, item.text, str(target) if target else None))
    assert [(part["locator"], part["kind"], part["fields"]) for part in document["parts"]] == expected_parts
    assert Counter(
        (rel["owner"], rel["field"], rel["value"], rel["target"] if isinstance(rel["target"], str) else None)
        for rel in document["relations"]
    ) == Counter(expected_relations)
    assert all(rel["direction"] == "outgoing" for rel in document["relations"])
    by_address = {str(address): entry for address, entry in snapshot.entries.items()}
    for relation in document["relations"]:
        value = dict(by_address[relation["owner"]].fields)
        for hop in relation["path"]:
            assert isinstance(value, (dict, list))
            value = value[hop]
        assert plain(value) == relation["value"]
    assert all(part["address"] == {"absent": "unaddressable-part"} for part in document["parts"])
    assert not snapshot.findings


@pytest.mark.parametrize("root", [LIBRARY, ROOT / "docs/kb"], ids=["tool-library", "ogy"])
def test_same_content_has_byte_identical_inspection(root):
    """Given independent snapshots of identical content, inspection serializes byte identically regardless of map order."""
    first, files = read(root)
    second = build(packaged(), dict(reversed(list(files.items()))))
    second.entries = {
        address: replace(entry, fields=dict(reversed(list(entry.fields.items()))))
        for address, entry in reversed(list(second.entries.items()))
    }
    second.ontology.kinds = {
        name: kind.model_copy(update={"fields": dict(reversed(list(kind.fields.items())))})
        for name, kind in reversed(list(second.ontology.kinds.items()))
    }
    assert (
        json.dumps(inspect(first), ensure_ascii=False, allow_nan=False).encode()
        == json.dumps(
            inspect(second),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    )


def test_absence_identity_and_version_are_explicit_and_content_sensitive():
    """Unknown source identities stay absent; all authored facts and ontology declarations affect the version."""
    snapshot = build(packaged(), {"product/app/quantities.yml": "- {id: fee, says: Fee., is: 2, unit: EUR}\n"})
    original = inspect(snapshot)
    assert original["snapshot"]["revision"] == {"absent": "not-in-snapshot"}
    assert original["snapshot"]["tree"] == {"absent": "not-in-snapshot"}
    record = original["entries"][0]
    assert record["title"] == {"absent": "unset"}
    assert record["source"]["line"] == {"absent": "not-in-snapshot"}
    assert "title" not in record["fields"]
    assert original["snapshot"]["version"] == inspect(snapshot)["snapshot"]["version"]
    changed = build(packaged(), {"product/app/quantities.yml": "- {id: fee, says: Fee., is: 3, unit: EUR}\n"})
    assert inspect(changed)["snapshot"]["version"] != original["snapshot"]["version"]
    changed.ontology.declared = changed.ontology.declared.model_copy(update={"harms": ("new-harm",)})
    assert inspect(changed)["snapshot"]["ontology"] != original["snapshot"]["ontology"]
    assert inspect(snapshot) == original


def test_relations_keep_expression_effect_row_and_duplicate_occurrence_identity():
    """Expressions and repeated effects on one target retain their own field, row and occurrence witnesses."""
    snapshot = build(
        packaged(),
        {
            "product/app/actors.yml": "- {id: member, says: Member., nature: human}\n",
            "product/app/workflow/borrow.yml": (
                "says: Borrow.\nstart: ask\nsteps:\n  ask:\n    says: Ask.\n    reads: [product/app/actor/member]\n"
                "    choices:\n      go:\n        label: Go\n        then: missing\n"
                "        effects: [&effect {do: tell, on: product/app/actor/member}, *effect]\n"
                "      stop: {label: Stop, when: {text: 'member is ready', reads: [product/app/actor/member]}}\n"
            ),
        },
    )
    document = inspect(snapshot)
    effects = [rel for rel in document["relations"] if rel["field"] == "on"]
    assert len(effects) == 2
    assert [rel["source"]["index"] for rel in effects] == [0, 1]
    assert all(rel["source"]["owner"].endswith("/choice/go") for rel in effects)
    expression = next(rel for rel in document["relations"] if rel["field"] == "when")
    assert expression["path"] == ["when", "reads", 0]
    missing = next(rel for rel in document["relations"] if rel["value"] == "missing")
    assert missing["target"] == {"absent": "dangling-link"}
    assert len({json.dumps(rel["witness"], sort_keys=True) for rel in document["relations"]}) == len(document["relations"])


def test_layer_request_preserves_boundary_relations_and_full_snapshot_version():
    """Selecting a layer keeps outgoing links to other layers and identifies the complete input snapshot."""
    snapshot, _ = read(LIBRARY)
    whole = inspect(snapshot)
    selected = inspect(snapshot, request=InspectionRequest(layer="software"))
    assert selected["snapshot"] == whole["snapshot"]
    assert all(entry["layer"] == "software" for entry in selected["entries"])
    assert any(rel["target"].startswith("product/") for rel in selected["relations"] if isinstance(rel["target"], str))
    with pytest.raises(ValueError, match="layer"):
        inspect(snapshot, request=InspectionRequest(layer="invented"))


def test_authored_null_unknown_fields_and_yaml_timestamps_are_not_guessed():
    """Given fields outside the ontology and YAML time values, inspection retains them and reports reader findings."""
    snapshot = build(
        packaged(),
        {
            "product/app/decision/choose.yml": (
                "question: Choose?\ntitle: null\nextra: {day: 2026-11-22, enabled: false, count: 0}\n"
                "answers: [{chose: a, said: Pick a., at: 2026-11-22T10:00:00+01:00, where: 'ai:test/1'}]\n"
                "options: {a: {label: A, sets: {product/app/quantity/fee: null}}}\n"
                "proposal: {chose: a, why: A reason., heard: A paraphrase.}\n"
            ),
            "stray.txt": "not an entry",
        },
    )
    document = json.loads(json.dumps(inspect(snapshot), allow_nan=False))
    decision = next(entry for entry in document["entries"] if entry["kind"] == "decision")
    assert decision["title"] is None
    assert "title" not in decision["absent_fields"]
    assert decision["fields"]["extra"] == {"day": "2026-11-22", "enabled": False, "count": 0}
    answer = next(part for part in document["parts"] if part["kind"] == "answer")
    assert answer["fields"]["at"] == "2026-11-22T10:00:00+01:00"
    assert answer["absent_fields"]["delegated"] == {"absent": "unset"}
    assert document["findings"][0]["problem"] == "bad-path"
    document["entries"][0]["fields"].clear()
    assert any(entry.fields for entry in snapshot.entries.values())
