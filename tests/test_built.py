"""The built record: stamps, work left, removal work, sourced changes."""

lazy from pathlib import Path

import pytest

from ogy import built
from ogy.built import BuiltError, Line

SRC = "product/library/quantities.yml"
FEE = "product/library/quantity/late-fee"


def line(own: str = "1d8551a51abd", covers: tuple[str, ...] = (), sourced: dict[str, str] | None = None) -> Line:
    return Line(own, covers, sourced or {})


def test_stamp_writes_one_flow_line_per_address_sorted(tmp_path: Path) -> None:
    built.stamp(tmp_path, SRC, "product/library/quantity/b", line("1234", covers=("src/a.py",), sourced={"code:x": "ff"}))
    built.stamp(tmp_path, SRC, FEE, line())
    text = (tmp_path / "built" / SRC).read_text()
    b_line, fee_line = text.splitlines()
    assert fee_line == f"{FEE}: {{own: 1d8551a51abd, covers: [], sourced: {{}}}}"
    assert b_line == "product/library/quantity/b: {own: '1234', covers: [src/a.py], sourced: {code:x: ff}}"
    assert built.read(tmp_path, SRC)["product/library/quantity/b"].covers == ("src/a.py",)


def test_unstamp_deletes_line_and_empty_file(tmp_path: Path) -> None:
    built.stamp(tmp_path, SRC, FEE, line())
    built.stamp(tmp_path, SRC, "product/library/quantity/b", line("bb"))
    built.unstamp(tmp_path, SRC, FEE)
    assert list(built.read(tmp_path, SRC)) == ["product/library/quantity/b"]
    built.unstamp(tmp_path, SRC, "product/library/quantity/b")
    assert not (tmp_path / "built" / SRC).exists()


def test_work_left_reads_the_built_record() -> None:
    record = {"b": line("2"), "ok": line("4")}
    assert built.work_left(record, {"b": "9", "new": "5", "ok": "4"}) == {"b": "changed", "new": "unbuilt"}


def test_an_old_deps_key_reads_and_is_found_until_migrated(tmp_path: Path) -> None:
    path = tmp_path / "built" / SRC
    path.parent.mkdir(parents=True)
    path.write_text(f"{FEE}: {{own: '1', deps: {{d: x}}, covers: [], sourced: {{}}}}\n")
    assert built.read(tmp_path, SRC)[FEE] == line("1")
    built.write(tmp_path, SRC, {FEE: built.Line("1")})
    assert "deps" not in path.read_text()


def test_removed_entry_is_work_until_line_deleted(tmp_path: Path) -> None:
    built.stamp(tmp_path, SRC, FEE, line())
    record = built.read_all(tmp_path)
    assert built.removal_work(record, ["product/library/quantity/other"]) == [FEE]
    built.unstamp(tmp_path, SRC, FEE)
    assert built.removal_work(built.read_all(tmp_path), ["product/library/quantity/other"]) == []


def test_changed_symbol_is_reported() -> None:
    record = {FEE: line(sourced={"src/fee.py::fee": "aa", "doc:a.md#fee": "bb"})}
    now = {FEE: {"src/fee.py::fee": "zz", "doc:a.md#fee": "bb"}}
    assert built.sourced_changes(record, now) == {FEE: ["src/fee.py::fee"]}


def test_changed_doc_section_is_reported() -> None:
    record = {FEE: line(sourced={"doc:a.md#fee": "bb"})}
    assert built.sourced_changes(record, {FEE: {"doc:a.md#fee": "cc"}}) == {FEE: ["doc:a.md#fee"]}
    assert built.sourced_changes(record, {FEE: {"doc:a.md#fee": "bb"}}) == {}


@pytest.mark.parametrize(
    "text",
    [
        "a: {own: x}\n",
        "a: {own: 1, covers: [], sourced: {}}\n",
        "a: {own: x, deps: {}, sourced: {}}\n",
        "a: {own: x, covers: [], sourced: {}}\na: {own: y, covers: [], sourced: {}}\n",
        "- a\n",
    ],
)
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
