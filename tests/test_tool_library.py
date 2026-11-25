"""The tool library: one knowledge base that holds every kind of the software ontology and fills nearly every field, with its
findings and its work written down. Every kind file change runs it: a new kind or field is exercised here or listed in
`UNEXERCISED` with why, and a change to what the checks or the work make of the entries shows in the expected sets.

It was written through ogy (put, answer, reply, remove; the built lines by `built.stamp`) in a scratch repository, then a
built entry, a rule and a source changed: so the work holds every status a worktree can show."""

from pathlib import Path

from ogy.base import read_ledgers
from ogy.built import read_source
from ogy.check import check
from ogy.kinds import Holds
from ogy.ontology import packaged
from ogy.receipts import Status, work_left
from ogy.snapshot import Snapshot, load
from ogy.source import WorktreeSource

ROOT = Path(__file__).parent / "fixtures" / "tool-library"
P, S = "product/lending", "software/lending"
BORROW = f"{P}/workflow/borrow/step"
UNBUILT = [  # D15: no step, handler or quantity, and an entity only with transitions (tool has none)
    f"{P}/rule/agent-decides-fee-details",
    f"{P}/rule/at-most-max-loans",
    f"{P}/rule/fees-round-up",
    f"{P}/rule/tools-are-checked-on-return",
    f"{BORROW}/ask/choice/leave",
    f"{BORROW}/ask/timeout",
    f"{BORROW}/record/case/full",
    f"{BORROW}/record/case/otherwise",
    f"{BORROW}/standing/case/otherwise",
    f"{BORROW}/standing/case/owes",
    f"{P}/workflow/close-loan/step/close/case/otherwise",
    f"{P}/workflow/notify/step/send/case/ok",
    f"{P}/workflow/notify/step/send/case/otherwise",
    f"{P}/workflow/remind/step/call/case/otherwise",
    f"{P}/workflow/remind/step/call/case/sent",
    f"{S}/interface/borrow-cli",
    f"{S}/setting/remind-every",
    f"{S}/rule/one-reminder-a-day",
    f"{S}/dependency/mailer/workaround/slow-at-night",
    f"{S}/interface/leave-button",
    f"{S}/interface/loans-report",
]
WORK = {
    *((address, Status.UNBUILT) for address in UNBUILT),
    (f"{P}/entity/loan", Status.CHANGED),  # its sentence changed after it was built
    (f"{P}/rule/late-fee-is-per-day", Status.CHANGED),
    (f"{P}/rule/late-fee-is-per-day", Status.CODE_CHANGED),  # late_fee() changed since the rule was captured from it
    (f"{BORROW}/ask/choice/borrow", Status.CHANGED),  # the rule it is held to (`by`) changed
    (f"{S}/interface/borrow-page", Status.CHANGED),  # held to that rule (`satisfies`, a content input)
    (f"{S}/setting/smtp-host", Status.CHANGED),  # `ogy migrate` dropped its `default` and `used_by`
    (f"{P}/rule/old-reminder-rule", Status.REMOVED),
    # it tells the mail relay, a program: its failed case is the no-answer path, no rule says whether a repeat is safe
    (f"{P}/workflow/notify/step/send/case/ok", "no-answer-path"),
    # unused: nothing satisfies or is constrained by the rule; nothing links to the setting; no effect fires the transition
    *(
        (address, "unused")
        for address in (
            f"{P}/entity/loan/transition/return",
            f"{P}/rule/agent-decides-fee-details",
            f"{P}/rule/fees-round-up",
            f"{S}/setting/remind-every",
            f"{S}/setting/smtp-host",
        )
    ),
}
# kind.field -> why this knowledge base leaves it empty
UNEXERCISED: dict[str, str] = {
    "proposal.at": "stamped only on a proposal written to an answered decision; the fixture asks none again (test_reply.py does)",
}


def read() -> tuple[Snapshot, WorktreeSource]:
    source = WorktreeSource(ROOT, "docs/kb")
    return load(source, packaged()), source


def test_the_tool_library_has_no_findings_even_for_a_land() -> None:
    snapshot, source = read()
    assert [str(item) for item in check(snapshot, source, landing=True)] == []


def test_its_work_is_the_work_written_down() -> None:
    snapshot, source = read()
    ledger = {item.id: item for ledger in read_ledgers(source)[0].values() for item in ledger.items}
    found = {(item.address, item.status) for item in work_left(snapshot, read_source(source)[0], source.repo_file, ledger)}
    assert found == WORK


def filled(snapshot: Snapshot) -> set[str]:
    """Every `kind.field` some entry sets, the items of list parts (answers, effects) and the common fields included."""
    found: set[str] = set()
    for address, entry in snapshot.entries.items():
        kind = snapshot.kind_of(address)
        found |= {f"{kind.kind}.{name}" for name, value in entry.fields.items() if value is not None}
        for part in snapshot.ontology.parts_of(kind.kind):
            items = entry.fields.get(part.key or "") if part.holding is Holds.LIST else None
            found |= {
                f"{part.kind}.{name}" for item in (items if isinstance(items, list) else []) if isinstance(item, dict) for name in item
            }
    return found


def test_every_kind_and_field_is_exercised_or_listed() -> None:
    snapshot, _ = read()
    ontology, found = snapshot.ontology, filled(snapshot)
    assert set(ontology.kinds) - {name.split(".")[0] for name in found} == set()
    wanted = {f"{name}.{field}" for name, kind in ontology.kinds.items() for field in kind.fields}
    assert sorted(wanted - found - set(UNEXERCISED)) == []
    assert sorted(set(UNEXERCISED) & found) == []  # a field the fixture now fills leaves the list
    assert set(ontology.common) <= {name.split(".")[1] for name in found}  # title, src, because, proof, agreed
