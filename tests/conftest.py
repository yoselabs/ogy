"""Small knowledge bases written into a temporary folder, read with the software ontology."""

import shutil
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

import pytest
from git_porcelain import run_git

from ogy import cli
from ogy.check import check
from ogy.declared import Declared
from ogy.model import Problem
from ogy.ontology import Ontology, packaged
from ogy.snapshot import Snapshot, load
from ogy.source import KB_DIR, WorktreeSource

SOURCE = "code:app.py#lend"  # the repository fixture's one Python file
CODE = "def lend():\n    return True\n"
AGREED = "{at: '2026-11-12T10:05:00+01:00', where: 'ai:claude/1', said: Members sign in, hash: 000000000000}"
SIGN_IN = """\
says: A member is signed in.
because: [product/app/decision/sign-in]
start: ask
steps:
  ask:
    says: The member asks.
    actor: product/app/actor/member
    choices:
      go: {label: Sign in, then: done}
ends:
  done: {result: success, says: The member is signed in.}
"""

AREAS: dict[str, str] = {
    "product/app/area.yml": "says: What members of the tool library do.\n",
    "software/app/area.yml": "says: The pages and operations that serve the members.\n",
    "product/shared/area.yml": "says: What two areas of the product use.\n",
}
GOOD: dict[str, str] = {
    **AREAS,
    "product/app/actors.yml": "- {id: member, says: A person who borrows., nature: human}\n",
    "product/app/workflow/sign-in.yml": SIGN_IN,
    "software/app/interface/sign-in-page.yml": (
        "says: The sign-in page.\nform: web\nserves: [product/app/workflow/sign-in/step/ask]\nbecause: [product/app/decision/sign-in]\n"),
    "product/app/decision/sign-in.yml": (
        "question: Do members sign in?\noptions:\n  members: {label: Members sign in}\n  anyone: {label: Anyone borrows}\n"
        "proposal: {chose: members, why: Loans need a member.}\n"
        "answers: [{chose: members, said: Members sign in, at: '2026-11-12T10:05:00+01:00', where: 'ai:claude/1'}]\n"),
}


@dataclass
class Kb:
    """A knowledge base on disk: its snapshot and the findings of `ogy check`."""

    snapshot: Snapshot
    source: WorktreeSource

    def repo(self) -> Path:
        """The same files as a repository the command line reads: its knowledge base is the folder `docs/kb` under it."""
        home = self.source.root.with_name(self.source.root.name + "-repo")
        shutil.copytree(self.source.root, home / KB_DIR)
        return home

    def findings(self, evidence: bool = False, landing: bool = False, started: bool = False) -> set[tuple[Problem, str]]:
        """The findings; `no-evidence` only with `evidence=True` and `never-started` (nothing starts a workflow) only with
        `started=True`, so a test of one rule does not carry a `src` on every entry or a root for every workflow."""
        found = check(self.snapshot, self.source, landing=landing)
        hidden = {problem for problem, shown in ((Problem.NO_EVIDENCE, evidence), (Problem.NEVER_STARTED, started)) if not shown}
        return {(item.problem, str(item.address) if item.address else item.path) for item in found if item.problem not in hidden}


def declared(*layers: str) -> Declared:
    """The software ontology's `ontology.yml`, with other layers when given: for a few kinds written in a test."""
    found = packaged().declared
    return found.model_copy(update={"layers": layers}) if layers else found


@pytest.fixture
def ontology() -> Ontology:
    return packaged()


@pytest.fixture
def kb(tmp_path: Path, ontology: Ontology) -> Callable[[Mapping[str, str | None] | None], Kb]:
    """`kb(changes)` writes the good base with `{path: text}` added or replaced (`None` leaves a file out), and reads it."""

    def make(changes: Mapping[str, str | None] | None = None) -> Kb:
        wanted = {**GOOD, **(changes or {})}
        for rel, text in wanted.items():
            if text is not None:
                (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
                (tmp_path / rel).write_text(text)
        source = WorktreeSource(tmp_path, "")
        return Kb(load(source, ontology), source)

    return make


IDENTITY = ("-c", "user.name=ogy-test", "-c", "user.email=test@ogy.invalid", "-c", "commit.gpgsign=false")
FILES = {
    **{f"docs/kb/{rel}": text for rel, text in AREAS.items()},
    "app.py": CODE,
    "docs/kb/product/app/actors.yml": "- {id: member, says: A person who borrows., nature: human, src: ['code:app.py#lend']}\n",
    "docs/kb/product/app/quantities.yml": "- {id: fee, says: The fee., is: 2, unit: EUR, src: ['code:app.py#lend']}\n",
    "docs/kb/software/app/interface/page.yml": (
        "says: The page.\nform: web\nserves: [product/app/workflow/borrow/step/ask]\nsrc: ['code:app.py#lend']\n"),
    "docs/kb/product/app/workflow/borrow.yml": """\
says: A tool is lent.
src: ['code:app.py#lend']
start: ask
steps:
  ask:
    says: The member asks.
    actor: product/app/actor/member
    choices:
      go:
        label: Borrow
        then: done
        effects: [{do: tell, "on": product/app/actor/member}]
    timeout: {after: product/app/quantity/fee, then: done}
ends:
  done: {result: success, says: The tool is lent.}
""",
    "docs/kb/software/app/handler/lend.yml": (
        "says: Lends.\nperforms: [product/app/workflow/borrow/step/ask/choice/go]\nsrc: ['code:app.py#lend']\n"),
}


def commit(repo: Path, message: str) -> str:
    run_git(repo, *IDENTITY, "add", "-A")
    run_git(repo, *IDENTITY, "commit", "-q", "-m", message)
    return run_git(repo, "rev-parse", "HEAD").strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    run_git(tmp_path, "init", "-q", "-b", "main")
    for rel, text in FILES.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    commit(tmp_path, "first")
    return tmp_path


def ogy(repo: Path, *argv: str) -> tuple[int, list[str]]:
    return cli.run(["--repo", str(repo), *argv])
