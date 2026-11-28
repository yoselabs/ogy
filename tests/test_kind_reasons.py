"""Kind files name their reasons (decision software/ontology/decision/kind-reasons, answered because-key-computed): a kind and a
field may carry `because`; `ogy kinds --unreasoned` prints those that name none; every reason a shipped kind file names is an entry
of ogy's own knowledge base."""

import shutil
from pathlib import Path

from tests.test_writes import w

from ogy import cli
from ogy.kindreasons import cited
from ogy.ontology import packaged
from ogy.snapshot import load
from ogy.source import WorktreeSource

SHIPPED = Path(__file__).parent.parent / "src" / "ogy" / "ontologies" / "software"
KB = Path(__file__).parent.parent / "docs" / "kb"


def test_unreasoned_lists_a_kind_and_a_field_until_their_kind_file_names_a_reason(repo: Path) -> None:
    shutil.copytree(SHIPPED, repo / "onto" / "software")
    code, lines = w(repo, "--ontology", "onto/software", "kinds", "--unreasoned")
    assert code == cli.OK and "enum" in lines and "enum.says" in lines, lines
    kind = repo / "onto" / "software" / "kinds" / "enum.yml"
    text = kind.read_text().replace("kind: enum\n", "kind: enum\nbecause: [product/capture/decision/pain-kind]\n", 1)
    kind.write_text(text.replace("  says: {required: true}", "  says: {required: true, because: [product/capture/decision/pain-kind]}"))
    code, lines = w(repo, "--ontology", "onto/software", "kinds", "--unreasoned")
    assert code == cli.OK and "enum" not in lines and "enum.says" not in lines, lines


def test_every_reason_a_shipped_kind_file_names_is_an_entry_of_ogys_knowledge_base() -> None:
    snapshot = load(WorktreeSource(KB.parent.parent, "docs/kb"), packaged())
    missing = sorted(text for text in cited(packaged()) if snapshot.resolve(text) is None)
    assert missing == [], missing
