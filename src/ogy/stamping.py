"""The test run writes the built lines (decision software/ontology/decision/built-line-writer, answered test-run-writes).

A pytest plugin, registered as `ogy` (entry point `pytest11`) and inert until `--ogy-stamp` is given. Before the tests run it
reads the knowledge base of the repository pytest runs in; at the end it writes a built line for every entry that needs a
proof and whose every proof item passed in this run: its build hash as read before the tests ran and the receipts of its `src`
now; it deletes the line of an entry one of whose proofs failed, so a red test never leaves its entry built. An entry whose
proof was skipped, was expected to fail or did not run is left as it is: a partial run deletes no line. No command writes a
line, so a line always comes from a run. Under pytest-xdist only the controller writes.
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

__all__ = ["OPTION", "Outcomes", "Run", "failed_proofs", "passed_proofs", "stamp_passed"]


# The parts of pytest's objects the hooks read: ogy does not import pytest, which only loads this module as a plugin.
class _Report(Protocol):
    nodeid: str
    when: str
    passed: bool
    failed: bool


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
    skipped: set[str] = field(default_factory=set)  # skipped or expected to fail: neither proves nor breaks

    def add(self, report: _Report) -> None:
        test = report.nodeid.split("[", 1)[0]
        if report.failed:
            self.failed.add(test)
        elif not report.passed or hasattr(report, "wasxfail"):
            self.skipped.add(test)
        elif report.when == "call":
            self.passed.add(test)

    def green(self) -> set[str]:
        """Tests that passed and never failed, were skipped or were expected to fail, in any phase or parameter."""
        return self.passed - self.failed - self.skipped


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


def failed_proofs(snapshot: Snapshot, red: set[str]) -> list[Address]:
    """The entries that need a proof and one of whose proof items failed in this run."""
    name = snapshot.ontology.roles.proof
    return [
        address
        for address in sorted(snapshot.entries)
        if snapshot.needs_proof(address) and any(item in red for item in link_values(snapshot.entries[address].fields.get(name)))
    ]


def stamp_passed(target: Target, before: tuple[Source, Snapshot], outcomes: Outcomes) -> tuple[list[Address], list[Address]]:
    """Under the write lock, write the line of every entry whose proofs all passed and delete the line of every entry one of
    whose proofs failed: a red test never leaves its entry built. Returns both lists."""
    source, snapshot = before
    done, broken = passed_proofs(snapshot, outcomes.green()), failed_proofs(snapshot, outcomes.failed)
    root = target.repo / target.kb
    with locked(target, "stamp"):
        for address in done:
            built.stamp(root, snapshot.entries[address].path, str(address), _line(snapshot, source, address))
        for address in broken:
            built.unstamp(root, snapshot.entries[address].path, str(address))
    return done, broken


@dataclass
class Run:
    """One stamping test session: the knowledge base as read before the tests ran, and what each test reported."""

    target: Target
    before: tuple[Source, Snapshot]
    outcomes: Outcomes = field(default_factory=Outcomes)

    def pytest_runtest_logreport(self, report: _Report) -> None:
        self.outcomes.add(report)  # a failed setup or teardown fails the test too

    def pytest_sessionfinish(self, session: _Session) -> None:
        done, broken = stamp_passed(self.target, self.before, self.outcomes)
        reporter = session.config.pluginmanager.get_plugin("terminalreporter")
        if isinstance(reporter, _Reporter):
            reporter.write_line(f"ogy: wrote {len(done)} built line(s), deleted {len(broken)} of entries whose proof failed")


def pytest_addoption(parser: _Parser) -> None:
    parser.addoption(OPTION, action="store_true", help="write the built line of every knowledge base entry whose proofs all passed")


def pytest_configure(config: _Config) -> None:
    # Under pytest-xdist only the controller records and writes: it receives every worker's reports; a worker has `workerinput`.
    if config.getoption(OPTION) and not hasattr(config, "workerinput"):
        root = Path(config.rootpath)
        target = Target(root, ontology=config_ontology(root))
        config.pluginmanager.register(Run(target, target.read()), "ogy-stamp-run")


def config_ontology(root: Path) -> str:
    return settings.read(root).ontology or DEFAULT_ONTOLOGY
