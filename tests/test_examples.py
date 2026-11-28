"""The example knowledge bases, read-only: each loads and its check finds nothing but terms awaiting the owner's yes.

Built here: decision software/ontology/decision/taskloop-fit-fixture."""

import re
from pathlib import Path
from typing import override

import pytest

from ogy.check import check
from ogy.model import Problem
from ogy.ontology import packaged
from ogy.snapshot import load
from ogy.source import WorktreeSource

V5 = Path(__file__).parent / "fixtures"


CODE_LINK = re.compile(r"code:([^#\"\]\s]+)#(\w+)(?:\.(\w+))?")
PROOF_LINK = re.compile(r"([\w./-]+\.py)::(\w+)(?:::(\w+))?")  # a proof names a test: path::function or path::Class::method


class Stand(WorktreeSource):
    """An example captured from another repository (the task loop) names code this one does not hold: every `code:` link
    names a stand-in file that defines its symbol, and every proof a stand-in test, so the links are read as they were when the
    example was written."""

    @override
    def repo_file(self, path: str, rev: str | None = None) -> str | None:
        symbols: dict[str, set[str]] = {}
        for text in self.root_texts().values():
            for found in (*CODE_LINK.finditer(text), *PROOF_LINK.finditer(text)):
                if found[1] == path:
                    symbols.setdefault(found[2], set()).update([found[3]] if found[3] else [])
        methods = {name: "".join(f"    def {m}(self): ...\n" for m in sorted(members)) for name, members in symbols.items()}
        defined = [f"class {name}:\n{body}" if body else f"def {name}(): ..." for name, body in methods.items()]
        return "\n".join(defined) if defined else None

    def root_texts(self) -> dict[str, str]:
        return self.read(self.listing())


def findings(folder: str, root: Path = V5, source: WorktreeSource | None = None, *, landing: bool = True) -> set[tuple[Problem, str]]:
    source = source or WorktreeSource(root, folder)
    return {(item.problem, str(item.address)) for item in check(load(source, packaged()), source, landing=landing)}


AWAITING = {Problem.TERM_NOT_AGREED}  # a term waits for the owner's yes: an error only when a land is asked for


EXAMPLES = Path(__file__).parent.parent / "examples"  # reference cases written through ogy (decision reference-cases)


@pytest.mark.parametrize(
    ("root", "folder"),
    [(V5, "example-tool-library"), (EXAMPLES / "task-loop", "docs/kb"), (EXAMPLES / "pet-shop", "docs/kb")],
    ids=["tool-library", "task-loop", "pet-shop"],
)
def test_an_example_loads_and_finds_nothing_but_terms_awaiting_the_owner(root: Path, folder: str) -> None:
    """Decision software/ontology/decision/taskloop-fit-fixture (replace): an example pins that it loads and that `check` finds
    nothing but terms awaiting the owner's yes; no entry counts and no exact addresses, so it may grow."""
    source = Stand(root, folder)
    assert load(source, packaged()).entries
    assert {problem for problem, _ in findings(folder, root, source)} <= AWAITING
    assert not findings(folder, root, source, landing=False)
