"""The built record: stamps, work left, removal work, sourced changes."""

from pathlib import Path

import pytest

from ogy import built
from ogy.built import BuiltError, Line

SRC = "product/library/values.yml"
FEE = "product/library/value/late-fee"


def line(own: str = "1d8551a51abd", deps: dict[str, str] | None = None, covers: tuple[str, ...] = (),
         sourced: dict[str, str] | None = None) -> Line:
    return Line(own, deps or {}, covers, sourced or {})


def test_stamp_writes_one_flow_line_per_address_sorted(tmp_path: Path) -> None:
    built.stamp(tmp_path, SRC, "product/library/value/b", line("1234", covers=("src/a.py",), sourced={"code:x": "ff"}))
    built.stamp(tmp_path, SRC, FEE, line(deps={"product/library/value/b": "1234"}))
    text = (tmp_path / "built" / SRC).read_text()
    b_line, fee_line = text.splitlines()
    assert fee_line.startswith(f"{FEE}: {{own: 1d8551a51abd, deps: {{product/library/value/b: '1234'}}")
    assert b_line == "product/library/value/b: {own: '1234', deps: {}, covers: [src/a.py], sourced: {code:x: ff}}"
    assert built.read(tmp_path, SRC)["product/library/value/b"].covers == ("src/a.py",)


def test_unstamp_deletes_line_and_empty_file(tmp_path: Path) -> None:
    built.stamp(tmp_path, SRC, FEE, line())
    built.stamp(tmp_path, SRC, "product/library/value/b", line("bb"))
    built.unstamp(tmp_path, SRC, FEE)
    assert list(built.read(tmp_path, SRC)) == ["product/library/value/b"]
    built.unstamp(tmp_path, SRC, "product/library/value/b")
    assert not (tmp_path / "built" / SRC).exists()


def test_work_left_reads_the_built_record() -> None:
    record = {"a": line("1", deps={"d": "x"}), "b": line("2"), "c": line("3", deps={"d": "x"}), "ok": line("4")}
    current = {"a": ("1", {"d": "y"}), "b": ("9", {}), "c": ("3", {"d": "x"}), "new": ("5", {}), "ok": ("4", {})}
    assert built.work_left(record, current) == {"a": "input changed", "b": "changed", "new": "unbuilt"}


def test_removed_entry_is_work_until_line_deleted(tmp_path: Path) -> None:
    built.stamp(tmp_path, SRC, FEE, line())
    record = built.read_all(tmp_path)
    assert built.removal_work(record, ["product/library/value/other"]) == [FEE]
    built.unstamp(tmp_path, SRC, FEE)
    assert built.removal_work(built.read_all(tmp_path), ["product/library/value/other"]) == []


def test_changed_symbol_is_reported() -> None:
    record = {FEE: line(sourced={"src/fee.py::fee": "aa", "doc:a.md#fee": "bb"})}
    now = {FEE: {"src/fee.py::fee": "zz", "doc:a.md#fee": "bb"}}
    assert built.sourced_changes(record, now) == {FEE: ["src/fee.py::fee"]}


def test_changed_doc_section_is_reported() -> None:
    record = {FEE: line(sourced={"doc:a.md#fee": "bb"})}
    assert built.sourced_changes(record, {FEE: {"doc:a.md#fee": "cc"}}) == {FEE: ["doc:a.md#fee"]}
    assert built.sourced_changes(record, {FEE: {"doc:a.md#fee": "bb"}}) == {}


@pytest.mark.parametrize("text", [
    "a: {own: x}\n",
    "a: {own: 1, deps: {}, covers: [], sourced: {}}\n",
    "a: {own: x, deps: {}, covers: [], sourced: {}}\na: {own: y, deps: {}, covers: [], sourced: {}}\n",
    "- a\n",
])
def test_bad_built_line(tmp_path: Path, text: str) -> None:
    path = tmp_path / "built" / SRC
    path.parent.mkdir(parents=True)
    path.write_text(text)
    with pytest.raises(BuiltError):
        built.read(tmp_path, SRC)


def test_address_in_two_files_is_an_error(tmp_path: Path) -> None:
    built.stamp(tmp_path, SRC, FEE, line())
    built.stamp(tmp_path, "library/other.yml", FEE, line())
    with pytest.raises(BuiltError):
        built.read_all(tmp_path)
