"""Tests for the removed ledger."""

import dataclasses
import datetime
from pathlib import Path

import pytest

from ogy import removed
from ogy.removed import Item, Parent

SHA, HASH = "a" * 40, "b" * 12
HOME = "product/land"
STEP = "product/land/workflow/land/step/summarize"


def make(id: str = STEP, **over: object) -> Item:
    parts = id.split("/")
    parent = Parent("/".join(parts[:-2]), "steps", 12) if len(parts) > 4 else None
    base = Item(id, parts[-2], parent, None, "Facts of the land are shown.", "product/land/decision/d1", None,
                datetime.datetime(2026, 11, 18, 9, 12, tzinfo=datetime.timezone(datetime.timedelta(hours=1))),
                SHA, HASH, "v5", {"says": "Facts of the land are shown.", "then": "reported"})
    return dataclasses.replace(base, **over)


def ok(_: Item) -> list[str]:
    return []


def test_append_and_read_roundtrip(tmp_path: Path) -> None:
    removed.append(tmp_path, HOME, make(), ok)
    removed.append(tmp_path, HOME, make("product/land/decision/d2", why=None), ok)
    ledgers, problems = removed.read_all(tmp_path)
    assert problems == []
    assert list(ledgers[HOME].items) == [make(), make("product/land/decision/d2", why=None)]
    assert (tmp_path / "product/land/removed.yml").read_text().startswith("format: 1\nitems:\n")


def test_new_id_in_removed_is_refused(tmp_path: Path) -> None:
    removed.append(tmp_path, HOME, make(), ok)
    with pytest.raises(removed.RemovedError) as caught:
        removed.append(tmp_path, HOME, make(), ok)
    assert caught.value.problems[0].code == "id-reused"
    live = [STEP, STEP + "/part/x", "product/land/workflow/other"]
    items = removed.read_all(tmp_path)[0][HOME].items
    assert [p.address for p in removed.find_reuse(items, live)] == [STEP, STEP + "/part/x"]


def test_part_under_removed_id_is_refused() -> None:
    entity = make("product/land/workflow/land")
    assert [p.code for p in removed.find_reuse([entity], ["product/land/workflow/land/step/new"])] == ["id-reused"]


def test_removed_envelope_is_strict(tmp_path: Path) -> None:
    raw = removed._raw(make())
    assert removed.check_envelope(raw, HOME) == []
    assert removed.check_envelope({**raw, "extra": 1}, HOME)[0].code == "bad-removed"
    assert removed.check_envelope({**raw, "kind": "case"}, HOME)
    assert removed.check_envelope({**raw, "parent": None}, HOME)
    assert removed.check_envelope({**raw, "at": "2026-11-18T09:12:00"}, HOME)
    assert removed.check_envelope({**raw, "hash": "xyz"}, HOME)
    assert removed.check_envelope(raw, "product/other")
    with pytest.raises(removed.RemovedError):
        removed.append(tmp_path, HOME, make(hash="xyz"), ok)


def test_unknown_removed_format(tmp_path: Path) -> None:
    (tmp_path / HOME).mkdir(parents=True)
    (tmp_path / "product/land/removed.yml").write_text("format: 2\nitems: []\n")
    ledgers, problems = removed.read_all(tmp_path)
    assert ledgers == {} and problems[0].code == "bad-removed"


def test_removal_without_item() -> None:
    items = [make("product/land/workflow/land")]
    base = ["product/land/workflow/land", "product/land/workflow/land/step/a", "product/land/workflow/gone", "product/land/workflow/keep"]
    problems = removed.check_unrecorded(base, ["product/land/workflow/keep"], items)
    assert [p.address for p in problems] == ["product/land/workflow/gone"]


def test_removed_item_may_not_change(tmp_path: Path) -> None:
    removed.append(tmp_path, HOME, make(), ok)
    base = removed.read_all(tmp_path)[0][HOME]
    removed.append(tmp_path, HOME, make("product/land/decision/d2"), ok)
    grown = removed.read_all(tmp_path)[0][HOME]
    assert removed.check_append_only(base, grown, HOME) == []
    edited = dataclasses.replace(grown, items=(make(said="changed"), *grown.items[1:]))
    assert removed.check_append_only(base, edited, HOME)[0].code == "edited-append-only"
    assert removed.check_append_only(base, None, HOME)
    assert removed.check_append_only(base, dataclasses.replace(base, format=2), HOME)


def test_agreed_entry_needs_why_as_an_address_and_plain_words_do_for_the_rest() -> None:
    yes = {"says": "Facts of the land are shown.", "agreed": {"at": "2026-11-12T10:00:00+01:00", "where": "ai:x", "from": "human",
                                                              "said": "Fine", "hash": HASH}}
    agreed = make(why=None, snapshot=yes)
    items = [agreed, make("product/land/decision/d2", why="product/land/decision/gone")]
    assert {p.address for p in removed.check_why(items, ["product/land/decision/d1"])} == {STEP, "product/land/decision/d2"}
    plain = make(why="we no longer lend tools", snapshot=yes)
    assert [p.address for p in removed.check_why([plain], [])] == [STEP]  # plain words for what a person agreed to
    assert removed.check_why([make(why="we no longer lend tools")], []) == []
    assert removed.is_address("product/land/decision/d1") and not removed.is_address("we no longer lend") and not removed.is_address(None)
    assert removed.check_why([make(why=None)], []) == []
    assert removed.check_why([make()], ["product/land/decision/d1"]) == []
    assert removed.check_why([make(why="product/land/decision/d2"), make("product/land/decision/d2", why="product/land/decision/d2")],
                             []) == []


def test_replaced_by_chain_reaches_live_entry() -> None:
    a = make("product/land/workflow/a", replaced_by="product/land/workflow/b")
    b = make("product/land/workflow/b", replaced_by="product/land/workflow/c")
    assert removed.check_replacements([a, b], ["product/land/workflow/c"]) == []
    assert len(removed.check_replacements([a, b], [])) == 2
    cycle = make("product/land/workflow/c", replaced_by="product/land/workflow/a")
    a_to_c = dataclasses.replace(a, replaced_by="product/land/workflow/c")
    assert removed.check_replacements([a_to_c, cycle], [])[0].code == "broken-link"
    dead = make("product/land/workflow/d", replaced_by="product/land/workflow/a")
    assert removed.check_replacements([dead, make("product/land/workflow/a")], [])


def test_snapshot_checked_only_when_appended(tmp_path: Path) -> None:
    with pytest.raises(removed.RemovedError) as caught:
        removed.append(tmp_path, HOME, make(), lambda i: ["hash differs"])
    assert caught.value.problems[0].code == "bad-snapshot"
    assert not (tmp_path / "product/land/removed.yml").exists()


def test_old_snapshot_is_never_rechecked() -> None:
    def refuse(_: Item) -> list[str]:
        return ["nope"]

    old, new = make(), make("product/land/decision/d2")
    problems = removed.check_new_snapshots([old, new], {old.id}, refuse)
    assert [p.address for p in problems] == [new.id]


def test_link_to_removed_names_the_replacement() -> None:
    gone = make("product/land/workflow/a", replaced_by="product/land/workflow/b")
    problems = removed.check_links([("product/land/rule/r", "product/land/workflow/a"), ("product/land/rule/r",
                                                                                         "product/land/workflow/z")], [gone])
    assert len(problems) == 1 and "product/land/decision/d1" in problems[0].detail and "product/land/workflow/b" in problems[0].detail


def test_search_by_words_and_parent() -> None:
    entity = make("product/land/workflow/land", said="Land it", parent=None)
    s2 = make("product/land/workflow/land/step/b", said="Second step", parent=Parent("product/land/workflow/land", "steps", 2))
    s1 = make("product/land/workflow/land/step/a", said="First step", parent=Parent("product/land/workflow/land", "steps", 1))
    sub = make("product/land/workflow/land/step/a/case/x", said="deep", parent=Parent("product/land/workflow/land/step/a", "cases", 0))
    items = [entity, s2, s1, sub]
    assert removed.search(items, words=["STEP", "first"]) == [s1]
    assert removed.search(items, parent="product/land/workflow/land") == [s1, s2, sub]
    assert removed.search(items, words=[HOME]) == items
