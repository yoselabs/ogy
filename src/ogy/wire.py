"""Results for an agent (over MCP): a table in lean-wire TSV with its header even when it is empty, or one record as YAML.

People read `ogy.render`. No result is computed here."""

import any_yaml
from lean_wire import encode_tsv

from ogy.render import plain
lazy from ogy.find import Found
lazy from ogy.graph import Impact
lazy from ogy.model import Finding
lazy from ogy.overview import Overview
lazy from ogy.receipts import Work
lazy from ogy.review import Dropped
lazy from ogy.semdiff import SemanticDiff
lazy from ogy.show import Shown

type Row = dict[str, str]


def _table(rows: list[Row], columns: list[str]) -> list[str]:
    return [encode_tsv(rows, columns=columns).rstrip("\n")]


def _record(data: dict[str, object]) -> list[str]:
    """The non-empty entries of `data`, as YAML."""
    return [any_yaml.dump({key: value for key, value in data.items() if value not in ("", None, [], {})}).rstrip("\n")]


def findings(found: list[Finding]) -> list[str]:
    return _table(
        [{"problem": str(f.problem), "path": f.path, "address": str(f.address or ""), "detail": f.detail} for f in found],
        ["problem", "path", "address", "detail"],
    )


def work(found: list[Work]) -> list[str]:
    return _table(
        [{"status": str(w.status), "address": w.address, "now": w.build_hash, "built": w.built or "", "note": w.note} for w in found],
        ["status", "address", "now", "built", "note"],
    )


def anchors(found: list[tuple[str, str, int]]) -> list[str]:
    return _table([{"anchor": a, "heading": h, "level": str(n)} for a, h, n in found], ["anchor", "heading", "level"])


def entries(found: list[Found]) -> list[str]:
    return _table(
        [{"address": f.address, "kind": f.kind, "state": f.state, "says": f.says, "note": f.note} for f in found],
        ["address", "kind", "state", "says", "note"],
    )


def impact(found: Impact) -> list[str]:
    groups = (("reaches", found.reaches), ("reached_by", found.reached_by))
    rows = [{"direction": direction, "address": str(a)} for direction, group in groups for a in sorted(group)]
    return _table(rows, ["direction", "address"])


def dropped(found: Dropped) -> list[str]:
    groups = (
        ("proposal says no, nobody has seen it", found.proposed_no),
        ("removed with no why", found.unexplained),
        ("removed with plain words", found.plain_why),
        ("answer with a note", found.noted),
        ("answer given under a delegation", found.delegated),
    )
    rows = [{"why": why, "address": str(a)} for why, group in groups for a in group]
    return _table(rows, ["why", "address"])


def diff(found: SemanticDiff) -> list[str]:
    rows: list[Row] = []
    for c in found.changes:
        rows += [
            {"address": str(c.address), "change": str(c.change), "field": i.name, "old": plain(i.old), "new": plain(i.new)}
            for i in c.fields
        ] or [{"address": str(c.address), "change": str(c.change)}]
    return _table(rows, ["address", "change", "field", "old", "new"])


def status(found: Overview) -> list[str]:
    areas = {
        h.area: {
            "questions": h.questions,
            "answered": h.answered,
            "decided_by_ai": h.ai,
            "from_docs": h.docs,
            "from_code": h.code,
            "decided_by_you": h.you,
            "changed": h.changed,
        }
        for h in found.areas
    }
    return _record(
        {
            "areas": areas,
            "waiting_for_you": found.waiting,
            "findings": found.findings,
            "work_left": found.work,
            "dropped": found.dropped,
            **({} if found.coverage is None else {"kinds_without_entries": {k: list(v) for k, v in found.coverage.items()}}),
        }
    )


def show(found: Shown) -> list[str]:
    if found.context is None:
        decided = found.decided_in
        return _record(
            {
                "address": str(found.address),
                "exists": False,
                "decided_no_in": str(decided.decision) if decided else "",
                "decided_by": decided.by if decided else "",
            }
        )
    around, decided, built = found.context, found.decided_in, found.built
    return _record(
        {
            "address": str(found.address),
            "path": around.entry.path,
            "fingerprint": around.fingerprint,
            "fields": dict(around.entry.fields),
            "parents": [str(a) for a in around.parents],
            "parts": [str(a) for a in around.parts],
            "links": [{"field": e.field, "to": str(e.address)} for e in around.links],
            "referenced_by": [{"field": e.field, "from": str(e.address)} for e in around.referenced_by],
            "status": str(found.status or ""),
            "label": str(found.label or ""),
            "agreed": {"at": found.agreed.at.isoformat(), "where": found.agreed.where, "said": found.agreed.said} if found.agreed else "",
            "decided_in": {"decision": str(decided.decision), "in_force": decided.option or "", "by": decided.by, "note": decided.note}
            if decided
            else "",
            "came_from": list(found.came_from),
            "through_decision": found.through_decision,
            "settles": list(found.settles),
            "built": {
                "file": found.built_file,
                "own": built.own,
                "covers": list(built.covers),
                "current": built.own == found.build_hash,
                "work": [f"{w.status} {w.note}".strip() for w in found.work],
            }
            if built
            else "",
        }
    )
