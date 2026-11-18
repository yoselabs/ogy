"""`ogy migrate`: the entries follow the renames and drops their kinds declare (see `ogy.kindchange`), in one checked write.

Every old name is rewritten (`kindchange.changes`); an agreement and a built line that were current stay current when only
names changed (`kindchange.Kept`); a dropped field that held a value is printed and its entry's agreement is left, so the
owner sees the entry as changed since agreed. Nothing is recorded: Git keeps the old names."""

from dataclasses import dataclass

from ogy import built
from ogy.edit import Editor
from ogy.kindchange import Change, Kept, changes
from ogy.model import Address
from ogy.snapshot import Snapshot
from ogy.target import Target
from ogy.writes import commit


@dataclass(frozen=True)
class Migrated:
    changes: list[Change]
    agreed: list[Address]  # agreements re-set to the fingerprint after the migration
    built: list[str]  # built lines re-set
    files: list[str]

    def lines(self) -> list[str]:
        if not self.changes:
            return ["nothing to migrate"]
        out = [f"renamed {c.address} {c.field} to {c.new}" if c.new else f"dropped {c.address} {c.field} (it held {c.value!r}): "
               "the owner sees this entry as changed" for c in self.changes]
        out += [f"kept the agreement current: {address}" for address in self.agreed]
        return out + [f"kept the built line current: {text}" for text in self.built]


def _agreements(snapshot: Snapshot, kept: Kept) -> dict[Address, dict[str, object]]:
    found: dict[Address, dict[str, object]] = {}
    for address, entry in snapshot.entries.items():
        agreed = entry.fields.get("agreed")
        given = agreed.get("hash") if isinstance(agreed, dict) else None
        if isinstance(agreed, dict) and isinstance(given, str) and (now := kept.hash(address, given)) not in (None, given):
            found[address] = {**agreed, "hash": now}
    return found


def _built(target: Target, snapshot: Snapshot, kept: Kept) -> list[str]:
    """Re-set the `own` and `deps` hashes of the built lines that only a rename changed."""
    root, done = target.repo / target.kb, []
    for text, line in sorted(built.read_all(root).items()):
        address = snapshot.resolve(text)
        if address is None:
            continue
        own = kept.hash(address, line.own) or line.own
        deps = {dep: (kept.hash(found, given) if (found := snapshot.resolve(dep)) else None) or given for dep, given in line.deps.items()}
        if own != line.own or deps != dict(line.deps):
            built.stamp(root, snapshot.entries[address].path, text, built.Line(own, deps, line.covers, line.sourced))
            done.append(text)
    return done


def migrate(target: Target) -> Migrated:
    """Write the migration of the worktree (the lock is held); refuses, writing nothing, when it leaves a new error."""
    editor = Editor(target.repo, target.kb, target.kinds())
    snapshot = editor.snapshot()
    after, found = changes(snapshot)
    if not found:
        return Migrated([], [], [], [])
    kept = Kept(snapshot)
    agreed = _agreements(snapshot, kept)
    lines: list[str] = []

    def act(ed: Editor) -> None:
        for address, entry in snapshot.entries.items():
            now = {**after.entries[address].fields, **({"agreed": agreed[address]} if address in agreed else {})}
            update = {name: now.get(name) for name in {*entry.fields, *now} if now.get(name) != entry.fields.get(name)}
            if update:
                ed.update(address, update, snap=snapshot)
        lines.extend(_built(target, snapshot, kept))

    touched = sorted({change.address for change in found} | set(agreed))
    files = commit(target, lambda _: touched, act)
    return Migrated(found, sorted(agreed), lines, files)
