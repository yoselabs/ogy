"""Sync bd from `ogy work --tracker` (decision software/cli/decision/work-to-tracker, answered print-and-runner).

The runner outside ogy: ogy prints the work left as items keyed by entry address; this reads them from a commit and the open
beads labelled `ogy-work`, and plans three things: create a bead for an item that has none, rewrite a bead whose fingerprint
differs from the item's, close a bead whose address the work left no longer lists. A bead without the label is never touched.
It shows the plan and changes nothing unless `--apply` is given. A closed bead is not reopened: an item that comes back gets a
new bead (Fable's recommendation; the owner has not decided it).

Usage: `just beads [--rev HEAD] [--apply]`.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from beads_client import Bd, Bead, NewBead

from ogy import cli

LABEL = "ogy-work"
ADDRESS, FINGERPRINT = "ogy_address", "ogy_fingerprint"

type Kind = Literal["create", "rewrite", "close"]


@dataclass(frozen=True)
class Item:
    key: str
    title: str
    fingerprint: str
    brief: str


@dataclass(frozen=True)
class Action:
    kind: Kind
    key: str
    bead: str = ""  # the bead to rewrite or close
    item: Item | None = None


def plan(items: list[Item], beads: list[Bead]) -> list[Action]:
    """What to do so the open ogy beads match the work left: one bead per item, its fingerprint current."""
    held = {str(bead.metadata.get(ADDRESS)): bead for bead in beads if LABEL in bead.labels and bead.metadata.get(ADDRESS)}
    actions: list[Action] = []
    for item in items:
        bead = held.get(item.key)
        if bead is None:
            actions.append(Action("create", item.key, item=item))
        elif str(bead.metadata.get(FINGERPRINT, "")) != item.fingerprint:
            actions.append(Action("rewrite", item.key, bead.id, item))
    keys = {item.key for item in items}
    actions += [Action("close", key, bead.id) for key, bead in sorted(held.items()) if key not in keys]
    # A labelled bead with no address (its metadata write failed after the create) would be duplicated forever: close it.
    lost = [bead for bead in beads if LABEL in bead.labels and not bead.metadata.get(ADDRESS)]
    actions += [Action("close", "", bead.id) for bead in sorted(lost, key=lambda bead: bead.id)]
    return actions


def apply(actions: list[Action], bd: Bd) -> None:
    for action in actions:
        item = action.item
        if action.kind == "close":
            why = f"ogy work no longer lists {action.key}: built or removed" if action.key else "an ogy-work bead with no address"
            bd.close(action.bead, why)
            continue
        if item is None:
            continue
        meta = {ADDRESS: item.key, FINGERPRINT: item.fingerprint}
        if action.kind == "create":
            done = f"ogy work no longer lists {item.key}"
            made = bd.create(NewBead(item.title, description=item.brief, acceptance_criteria=done, labels=(LABEL,)))
            bd.update(made, metadata=meta)
        else:
            bd.update(action.bead, description=item.brief, metadata=meta)


def read_items(repo: Path, rev: str) -> list[Item]:
    _, lines = cli.run(["--repo", str(repo), "--rev", rev, "work", "--tracker"])
    return [Item(raw["key"], raw["title"], raw["fingerprint"], raw["brief"]) for raw in json.loads("\n".join(lines))]


def main(argv: list[str] | None = None, bd: Bd | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ogy-beads", description="Sync bd from ogy work --tracker; shows the plan unless --apply.")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--rev", default="HEAD", help="the commit to read the work left from (default HEAD: what is committed)")
    parser.add_argument("--apply", action="store_true", help="make the changes in bd; without it nothing is written")
    parser.add_argument("--tracker-dir", type=Path, help="the folder whose bd to sync (default: the repository)")
    args = parser.parse_args(argv)
    where = str(args.tracker_dir or args.repo)
    bd = bd or Bd("ogy-beads", cwd=where, env=os.environ)  # find bd on the PATH of the shell that ran it
    actions = plan(read_items(args.repo, args.rev), bd.find(label=LABEL))
    counts = {kind: sum(1 for action in actions if action.kind == kind) for kind in ("create", "rewrite", "close")}
    for action in actions:
        sys.stdout.write(f"{action.kind} {action.bead or '-'} {action.key}\n")
    sys.stdout.write(f"{counts['create']} to create, {counts['rewrite']} to rewrite, {counts['close']} to close\n")
    if args.apply:
        apply(actions, bd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
