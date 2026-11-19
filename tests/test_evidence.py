"""Evidence links: `code:` symbols, `doc:` headings by GitHub anchor, and the hashes for `sourced`."""

from pathlib import Path

from ogy.evidence import EvidenceProblem, check_item, check_items, receipt, section_hash, symbol_hash
from ogy.ontology import packaged

SCHEMES = packaged().declared.evidence
CODE = '''
FEE = 3
RATE: float = 0.5
type Money = int
def late_fee(days):
    return days * FEE
class Loan:
    limit = 2
    def renew(self):
        def inner(): pass
'''
DOC = "# Title\n\nintro\n\n## Late `fees`!\n\nbody one\n\n### Detail\n\nd\n\n## Next\n\n```\n# not a heading\n```\n\n## Next\n"


def reader(tmp_path: Path):
    def read(path: str, rev: str | None = None) -> str | None:
        file = tmp_path / path
        return file.read_text() if file.is_file() else None

    return read


def project(tmp_path: Path):
    (tmp_path / "fee.py").write_text(CODE)
    (tmp_path / "notes.md").write_text(DOC)
    (tmp_path / "data.json").write_text("{}")
    return reader(tmp_path)


def test_an_address_is_no_source(tmp_path):
    read = project(tmp_path)
    for item in ("product/library/message/2026-11-12-a41c", "product/library/decision/d4"):
        assert check_item(item, read, SCHEMES).code == "bad-src"


def test_code_link_finds_function_method_constant(tmp_path):
    read = project(tmp_path)
    for symbol in ("late_fee", "Loan", "Loan.renew", "Loan.limit", "FEE", "RATE", "Money"):
        assert check_item(f"code:fee.py#{symbol}", read, SCHEMES) is None, symbol


def test_code_link_to_missing_symbol(tmp_path):
    read = project(tmp_path)
    for item in ("code:fee.py#nope", "code:fee.py#inner", "code:fee.py#Loan.renew.inner", "code:fee.py#Loan.nope"):
        assert check_item(item, read, SCHEMES) == EvidenceProblem("missing-code", item, check_item(item, read, SCHEMES).detail)
    assert check_item("code:gone.py#x", read, SCHEMES).code == "missing-code"


def test_src_targets_only_source_kinds_and_code(tmp_path):
    read = project(tmp_path)
    for item in ("https://example.com/x", "doc:notes.md", "code:fee.py", "code:fee.py#", "code:data.json#x", "code:../x.py#a", "plain"):
        assert check_item(item, read, SCHEMES).code == "bad-src", item


def test_doc_link_needs_file_and_heading(tmp_path):
    read = project(tmp_path)
    assert check_item("doc:abc1234:notes.md#late-fees", read, SCHEMES) is None
    assert check_item("doc:abc1234:notes.md#detail", read, SCHEMES) is None
    assert check_item("doc:abc1234:notes.md#next-1", read, SCHEMES) is None
    assert check_item("doc:abc1234:notes.md#not-a-heading", read, SCHEMES).code == "missing-doc"
    assert check_item("doc:abc1234:gone.md#late-fees", read, SCHEMES).code == "missing-doc"
    assert check_item("doc:abc1234:fee.py#late-fees", read, SCHEMES).code == "missing-doc"


def test_a_doc_link_pins_a_revision(tmp_path):
    read = project(tmp_path)
    for item in ("doc:notes.md#late-fees", "doc:main:notes.md#late-fees", "doc:abc12:notes.md#late-fees"):
        problem = check_item(item, read, SCHEMES)
        assert problem.code == "bad-src" and "pins a Git revision" in problem.detail, item
    seen = []

    def spy(path, rev=None):
        seen.append((path, rev))
        return read(path)

    assert check_item("doc:0123abc:notes.md#late-fees", spy, SCHEMES) is None and seen == [("notes.md", "0123abc")]
    assert receipt("doc:0123abc:notes.md#late-fees", read, SCHEMES) == section_hash(DOC, "late-fees")


def test_check_items_collects_problems(tmp_path):
    read = project(tmp_path)
    assert [p.code for p in check_items(["code:fee.py#FEE", "doc:abc1234:gone.md#a", "x"], read, SCHEMES)] == ["missing-doc", "bad-src"]


def test_section_runs_to_next_heading_of_same_or_higher_level(tmp_path):
    read = project(tmp_path)
    before = receipt("doc:abc1234:notes.md#late-fees", read, SCHEMES)
    assert before == section_hash(DOC, "late-fees")
    assert section_hash(DOC.replace("d\n", "changed\n"), "late-fees") != before
    assert section_hash(DOC.replace("intro", "other"), "late-fees") == before


def test_changed_symbol_changes_receipt(tmp_path):
    read = project(tmp_path)
    before = receipt("code:fee.py#late_fee", read, SCHEMES)
    assert before == symbol_hash(CODE, "late_fee")
    assert symbol_hash(CODE.replace("days * FEE", "days"), "late_fee") != before
    assert symbol_hash(CODE.replace("FEE = 3", "FEE = 4"), "late_fee") == before
    assert receipt("code:fee.py#nope", read, SCHEMES) is None
