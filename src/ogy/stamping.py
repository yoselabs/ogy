"""The test run writes the built lines (decision software/ontology/decision/built-line-writer, answered test-run-writes).

A pytest plugin, registered as `ogy` (entry point `pytest11`) and inert until `--ogy-stamp` is given. Before the tests run it
reads the knowledge base of the repository pytest runs in; at the end it writes a built line for every entry that needs a
proof and whose every proof item passed in this run: its build hash as read before the tests ran and the receipts of its `src`
now. An entry with a proof that failed, was skipped, was expected to fail or did not run is left as it is: a partial run never
deletes a line. No command writes a line, so a line always comes from a run.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, runtime_checkable
lazy from pathlib import Path

from ogy import built, evidence
from ogy import config as settings
from ogy.model import link_values
from ogy.ontology import DEFAULT_ONTOLOGY
from ogy.target import Target
from ogy.writes import locked

if TYPE_CHECKING:
    from ogy.model import Address
    from ogy.snapshot import Snapshot
    from ogy.source import Source

OPTION = "--ogy-stamp"

__all__ = ["OPTION", "Outcomes", "Run", "passed_proofs", "stamp_passed"]


# The parts of pytest's objects the hooks read: ogy does not import pytest, which only loads this module as a plugin.
class _Report(Protocol):
    nodeid: str
    when: str
    passed: bool


@runtime_checkable
class _Reporter(Protocol):
    def write_line(self, line: str) -> None: ...


class _Plugins(Protocol):
    def get_plugin(self, name: str) -> object | None: ...
    def register(self, plugin: object, name: str) -> object: ...


class _Config(Protocol):
    rootpath: Path
    pluginmanager: _Plugins

    def getoption(self, name: str) -> object: ...


class _Session(Protocol):
    config: _Config


class _Parser(Protocol):
    def addoption(self, *names: str, **options: str) -> None: ...


@dataclass
class Outcomes:
    """What each test reported, by its id without parameters (`tests/test_fee.py::test_late_fee_per_day`)."""

    passed: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)

    def add(self, nodeid: str, *, ok: bool) -> None:
        (self.passed if ok else self.failed).add(nodeid.split("[", 1)[0])

    def green(self) -> set[str]:
        """Tests that passed and never failed, skipped or were expected to fail, in any phase or parameter."""
        return self.passed - self.failed


def passed_proofs(snapshot: Snapshot, green: set[str]) -> list[Address]:
    """The entries that need a proof and whose proof items all passed (an entry with no proof item is never built)."""
    name = snapshot.ontology.roles.proof
    return [
        address
        for address in sorted(snapshot.entries)
        if snapshot.needs_proof(address)
        and (items := link_values(snapshot.entries[address].fields.get(name)))
        and all(item in green for item in items)
    ]


def _line(snapshot: Snapshot, source: Source, address: Address) -> built.Line:
    schemes = snapshot.ontology.declared.evidence
    links = link_values(snapshot.entries[address].fields.get(snapshot.ontology.roles.src))
    receipts = {link: evidence.receipt(link, source.repo_file, schemes) for link in links}
    return built.Line(snapshot.build_hash(address), (), {link: hash_ for link, hash_ in receipts.items() if hash_ is not None})


def stamp_passed(target: Target, before: tuple[Source, Snapshot], green: set[str]) -> list[Address]:
    """Write the line of every entry whose proofs all passed, under the write lock; returns their addresses."""
    source, snapshot = before
    done = passed_proofs(snapshot, green)
    root = target.repo / target.kb
    with locked(target, "stamp"):
        for address in done:
            built.stamp(root, snapshot.entries[address].path, str(address), _line(snapshot, source, address))
    return done


@dataclass
class Run:
    """One stamping test session: the knowledge base as read before the tests ran, and what each test reported."""

    target: Target
    before: tuple[Source, Snapshot]
    outcomes: Outcomes = field(default_factory=Outcomes)

    def pytest_runtest_logreport(self, report: _Report) -> None:
        if report.when == "call" or not report.passed:  # a failed or skipped setup or teardown fails the test too
            self.outcomes.add(report.nodeid, ok=report.passed and not hasattr(report, "wasxfail"))

    def pytest_sessionfinish(self, session: _Session) -> None:
        done = stamp_passed(self.target, self.before, self.outcomes.green())
        reporter = session.config.pluginmanager.get_plugin("terminalreporter")
        if isinstance(reporter, _Reporter):
            reporter.write_line(f"ogy: wrote {len(done)} built line(s)")


def pytest_addoption(parser: _Parser) -> None:
    parser.addoption(OPTION, action="store_true", help="write the built line of every knowledge base entry whose proofs all passed")


def pytest_configure(config: _Config) -> None:
    if config.getoption(OPTION):
        root = Path(config.rootpath)
        target = Target(root, ontology=config_ontology(root))
        config.pluginmanager.register(Run(target, target.read()), "ogy-stamp-run")


def config_ontology(root: Path) -> str:
    return settings.read(root).ontology or DEFAULT_ONTOLOGY
