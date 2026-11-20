"""The removed ledgers in `ogy check`: R2 and R4 to R8 on one commit, and the checks against the base commit (C1 to C3, R1, R3, R7)."""

import dataclasses
lazy from collections.abc import Collection

from ogy import removed, removed_moves
from ogy.base import check_base, read_ledgers
from ogy.kindchange import before
from ogy.layout import REMOVED_FILE
from ogy.links import link_items, resolve
from ogy.model import Finding, Problem, home_of, link_values, parse_address
from ogy.removal import known_addresses, snapshot_problems
from ogy.retype import Retype
from ogy.snapshot import Snapshot, load
lazy from ogy.source import Source


def findings_of(problems: list[removed.Problem], snapshot: Snapshot) -> list[Finding]:
    """Ledger problems as findings, placed at the entry when one has that address and else at the home's ledger file."""
    found: list[Finding] = []
    for item in problems:
        address = snapshot.resolve(item.address)
        path = snapshot.entries[address].path if address else f"{home_of(item.address, snapshot.ontology)}/{REMOVED_FILE}"
        found.append(Finding(Problem(item.code), path, item.detail, address))
    return found


def _citers(snapshot: Snapshot, ids: Collection[str]) -> list[tuple[str, str]]:
    """R8: (entry, removed id) for each link, `because` and `src` that names a removed address (and no live entry).
    One that `dangling-link` already reports (a link that resolves nowhere) is left out: one finding each."""
    pairs: list[tuple[str, str]] = []
    for address, entry in snapshot.entries.items():
        reported = {
            item.text
            for item in link_items(snapshot.ontology, entry)
            if resolve(snapshot.ontology, snapshot.entries, address, item).problem is Problem.DANGLING_LINK
        }
        sources = link_values(entry.fields.get(snapshot.ontology.roles.src))
        reported |= {text for text in sources if ":" not in text and parse_address(text, snapshot.ontology)}
        named = [item.text for item in link_items(snapshot.ontology, entry)] + list(sources)
        for text in (text for text in named if text not in reported):
            gone = next((i for i in ids if text == i or text.startswith(i + "/")), None)
            if gone is not None and snapshot.resolve(text) is None:
                pairs.append((str(address), gone))
    return pairs


def named_now(ledgers: dict[str, removed.Ledger], snapshot: Snapshot) -> dict[str, removed.Ledger]:
    """The ledgers read under the kind names now (`ogy.retype`): a ledger file keeps the names its items had, so an item of a
    renamed or merged kind is compared by the address its entry would have now. Nothing is written."""
    rename = Retype(snapshot.ontology).address
    return {
        home: dataclasses.replace(ledger, items=tuple(removed_moves.moved_item(item, rename) for item in ledger.items))
        for home, ledger in ledgers.items()
    }


def check_ledgers(snapshot: Snapshot, source: Source) -> list[Finding]:
    ledgers, problems = read_ledgers(source)
    ledgers = named_now(ledgers, snapshot)
    items = [item for ledger in ledgers.values() for item in ledger.items]
    live = [str(address) for address in snapshot.entries]
    problems += removed.find_reuse(items, live) + removed.check_why(items, known_addresses(snapshot), snapshot.ontology.roles.agreed)
    problems += removed.check_replacements(items, live) + removed.check_links(_citers(snapshot, [i.id for i in items]), items)
    moved = [
        Finding(
            Problem.NEEDS_MIGRATION,
            f"{home}/{REMOVED_FILE}",
            f"{home}/ is no home any more: run `ogy migrate`, which moves its removed items to {new}/{REMOVED_FILE}",
        )
        for home, new in snapshot.ontology.moved_homes().items()
        if home in ledgers
    ]
    return findings_of(problems, snapshot) + moved


def migrated_ledgers(ledgers: dict[str, removed.Ledger], snapshot: Snapshot) -> dict[str, removed.Ledger]:
    """The ledgers as `ogy migrate` writes them: those of a fixed folder a kind moved out of, under the home it moved to."""
    for old, new in snapshot.ontology.moved_homes().items():
        ledgers = removed_moves.rehomed(ledgers, old, new)
    return ledgers


def check_against_base(snapshot: Snapshot, source: Source, base: Snapshot, base_source: Source) -> list[Finding]:
    """C1 to C3 and R1, R3, and R7: an item that is not in the base ledger has a snapshot equal to the entry in the base (an
    item written under an old kind name, to the entry in the base read under the kinds as they were)."""
    written = read_ledgers(source)[0]
    ledgers = named_now(written, snapshot)
    old = named_now(migrated_ledgers(read_ledgers(base_source)[0], snapshot), snapshot)  # the base as `ogy migrate` would write it
    found = check_base(snapshot, base, ledgers, old)
    in_base, rename = {item.id for ledger in old.values() for item in ledger.items}, Retype(snapshot.ontology).address
    new = [item for ledger in written.values() for item in ledger.items if rename(item.id) not in in_base]
    then = load(base_source, before(snapshot.ontology)) if any(rename(item.id) != item.id for item in new) else base
    found += findings_of(
        removed.check_new_snapshots(new, (), lambda item: snapshot_problems(then if rename(item.id) != item.id else base, item)), snapshot
    )
    return found
