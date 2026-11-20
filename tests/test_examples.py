"""The three v5 example knowledge bases, read-only: the acceptance test of every step of the v5 loader plan."""

import re
from pathlib import Path
from typing import override

from ogy.check import check
from ogy.model import Problem
from ogy.ontology import packaged
from ogy.snapshot import load
from ogy.source import WorktreeSource

V5 = Path(__file__).parent / "fixtures"


CODE_LINK = re.compile(r"code:([^#\"\]\s]+)#(\w+)(?:\.(\w+))?")


class Stand(WorktreeSource):
    """The fit was captured from the task-loop repository, which this one does not hold: every `code:` link names a stand-in
    file that defines its symbol, so the links are read as they were when the fit was written."""

    @override
    def repo_file(self, path: str, rev: str | None = None) -> str | None:
        symbols: dict[str, set[str]] = {}
        for text in self.root_texts().values():
            for found in CODE_LINK.finditer(text):
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


def test_example_tool_library_has_no_findings() -> None:
    assert findings("example-tool-library") == set()


def test_taskloop_fit_has_only_expected_findings() -> None:
    terms = {"claim", "land", "squash", "target-tip", "gate", "checked-commit"}
    expected = {(Problem.TERM_NOT_AGREED, f"product/shared/term/{word}") for word in terms}
    assert findings("taskloop-fit/kb", source=Stand(V5, "taskloop-fit/kb")) == expected
    assert not {
        item
        for item in findings("taskloop-fit/kb", source=Stand(V5, "taskloop-fit/kb"), landing=False)
        if item[0] is Problem.TERM_NOT_AGREED
    }  # waiting for the owner, an error only when a land is asked for


def test_taskloop_fit_reads_every_part_with_a_slash_address() -> None:
    """The owner cut the land workflow (35 links from product into software) to re-capture it after stage 3 (bead
    ogy-yy9.75), and with it what only it used: the handlers close, deliver, squash, validate and hold-after-land, the
    interface step-land, the workflow round-land that called it, the entity land-candidate and the three decisions that set
    their fields."""
    snapshot = load(WorktreeSource(V5, "taskloop-fit/kb"), packaged())
    assert len(snapshot.entries) == 47
    assert snapshot.resolve("product/land/workflow/land") is None and snapshot.resolve("software/land/dependency/origin") is not None
