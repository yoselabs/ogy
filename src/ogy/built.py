"""The built record: what each entry was when its proof last passed (loader-changes section 5).

One file per source file, `<kb>/built/<source path>` (`built/library/values.yml` for `library/values.yml`), a YAML mapping
with one flow-style line per address, sorted by address. Only this module writes it. Everything here takes plain data
(addresses, fingerprint strings, dicts and the knowledge base root); finding an address's source file is the caller's."""

import dataclasses
from typing import TYPE_CHECKING
lazy from pathlib import Path

import any_yaml
from atomic_io import atomic_write_text

from ogy.model import Finding, Problem
lazy from ogy.source import Source

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

BUILT = "built"
_KEYS = {"own", "covers", "sourced"}
_DROPPED = {"deps"}  # keys a built line no longer has: the file is `needs-migration` until `ogy migrate` writes it without them

__all__ = [
    "BUILT",
    "BuiltError",
    "Line",
    "read",
    "read_all",
    "read_source",
    "removal_work",
    "sourced_changes",
    "stamp",
    "unstamp",
    "work_left",
    "write",
]


class BuiltError(ValueError):
    """A built file whose shape is wrong or that writes an address twice (B5), or whose line holds a key of its own (S4)."""

    def __init__(self, message: str, problem: Problem = Problem.BAD_BUILT) -> None:
        super().__init__(message)
        self.problem = problem


@dataclasses.dataclass(frozen=True)
class Line:
    own: str
    covers: tuple[str, ...] = ()
    sourced: Mapping[str, str] = dataclasses.field(default_factory=dict)
    dropped: tuple[str, ...] = dataclasses.field(default=(), compare=False)  # old keys the line still holds (`ogy migrate`)


def path_of(kb: Path, source: str) -> Path:
    return kb / BUILT / source


def _strings(value: object, where: str) -> dict[str, str]:
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        msg = f"{where}: expected a mapping of strings"
        raise BuiltError(msg)
    return dict(value)


def _line(address: str, raw: object, where: str) -> Line:
    if isinstance(raw, dict) and set(raw) - _KEYS - _DROPPED:
        msg = f"{where}: {address} has keys of its own: {sorted(set(raw) - _KEYS - _DROPPED)}"
        raise BuiltError(msg, Problem.STORED_STATE)
    if not isinstance(raw, dict) or set(raw) - _DROPPED != _KEYS:
        msg = f"{where}: {address} needs exactly {sorted(_KEYS)}"
        raise BuiltError(msg)
    covers = raw["covers"]
    if not isinstance(raw["own"], str) or not isinstance(covers, list) or not all(isinstance(c, str) for c in covers):
        msg = f"{where}: {address} has a wrong own or covers"
        raise BuiltError(msg)
    return Line(raw["own"], tuple(covers), _strings(raw["sourced"], where), tuple(sorted(set(raw) & _DROPPED)))


def parse(text: str, where: str) -> dict[str, Line]:
    """The lines of one built file's text. Raises BuiltError for a bad line or a repeated address."""
    try:
        data = any_yaml.load(text)
    except any_yaml.YAMLError as error:  # a repeated key is a YAML error
        msg = f"{where}: {error}"
        raise BuiltError(msg) from error
    if data is None:
        return {}
    if not isinstance(data, dict):
        msg = f"{where}: expected a mapping of address to line"
        raise BuiltError(msg)
    return {str(address): _line(str(address), raw, where) for address, raw in data.items()}


def read(kb: Path, source: str) -> dict[str, Line]:
    """The lines of one built file; no file is no lines. Raises BuiltError for a bad line or a repeated address."""
    path = path_of(kb, source)
    return parse(path.read_text(encoding="utf-8"), f"{BUILT}/{source}") if path.is_file() else {}


def read_source(source: Source) -> tuple[dict[str, Line], list[Finding]]:
    """Every line of every built file of a commit or the worktree, and a finding for each file that does not read."""
    record: dict[str, Line] = {}
    found: list[Finding] = []
    prefix = BUILT + "/"
    paths = sorted(path for path in source.listing() if path.startswith(prefix) and path.endswith(".yml"))
    for path, text in source.read(paths).items():
        try:
            lines = parse(text, path)
        except BuiltError as error:
            found.append(Finding(error.problem, path, str(error)))
            continue
        found += [Finding(Problem.BAD_BUILT, path, f"{address} is written twice") for address in lines if address in record]
        if old := sorted({key for line in lines.values() for key in line.dropped}):
            found.append(
                Finding(
                    Problem.NEEDS_MIGRATION, path, f"its lines hold {', '.join(old)}, which built lines no longer have: run `ogy migrate`"
                )
            )
        record.update(lines)
    return record, found


def read_all(kb: Path) -> dict[str, Line]:
    """Every line of every built file, by address; an address in two files is an error."""
    record: dict[str, Line] = {}
    root = kb / BUILT
    for file in sorted(root.rglob("*")) if root.is_dir() else ():
        if not file.is_file():
            continue
        for address, line in read(kb, file.relative_to(root).as_posix()).items():
            if address in record:
                msg = f"{BUILT}: {address} is written twice"
                raise BuiltError(msg)
            record[address] = line
    return record


def _record(line: Line) -> dict[str, object]:
    return {"own": line.own, "covers": list(line.covers), "sourced": dict(sorted(line.sourced.items()))}


def write(kb: Path, source: str, lines: Mapping[str, Line]) -> None:
    """Write the lines of one built file (none: delete it)."""
    path = path_of(kb, source)
    if not lines:
        path.unlink(missing_ok=True)
        return
    atomic_write_text(path, any_yaml.flow_lines({a: _record(lines[a]) for a in lines}))


def stamp(kb: Path, source: str, address: str, line: Line) -> None:
    """The proof of `address` passed: write its line into the built file of its source file."""
    lines = read(kb, source)
    lines[address] = line
    write(kb, source, lines)


def unstamp(kb: Path, source: str, address: str) -> None:
    """The removal of `address` was delivered: delete its line (and the file when it was the last one)."""
    lines = read(kb, source)
    if lines.pop(address, None) is not None:
        write(kb, source, lines)


def work_left(record: Mapping[str, Line], current: Mapping[str, str]) -> dict[str, str]:
    """B1. `current` maps each `needs_proof` address to its build hash now (its meaning, proofs and declared inputs).
    Returns {address: "unbuilt" | "changed"} for the entries that are work."""
    work: dict[str, str] = {}
    for address, own in sorted(current.items()):
        line = record.get(address)
        if line is None:
            work[address] = "unbuilt"
        elif line.own != own:
            work[address] = "changed"
    return work


def removal_work(record: Mapping[str, Line], entries: Iterable[str]) -> list[str]:
    """B2. Addresses with a line and no entry (`entries`: every address of the snapshot); unstamp deletes the line."""
    alive = set(entries)
    return sorted(address for address in record if address not in alive)


def sourced_changes(record: Mapping[str, Line], now: Mapping[str, Mapping[str, str]]) -> dict[str, list[str]]:
    """B3. `now` maps an address to {link: hash now}. Returns {address: [link, ...]} for the stamped links whose hash
    differs; a link starting `doc:` is a document change, any other a code change (the caller labels the text)."""
    changed: dict[str, list[str]] = {}
    for address, line in sorted(record.items()):
        links = [link for link, hash_ in line.sourced.items() if address in now and now[address].get(link) != hash_]
        if links:
            changed[address] = sorted(links)
    return changed
