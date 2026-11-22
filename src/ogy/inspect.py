"""Lossless, read-only inspection document, schema version 2.
schema: integer transport contract version.
request: explicit layer selection; null means the complete snapshot.
snapshot.content: SHA-256 of resolved entries and reader findings, not a Git tree.
snapshot.ontology: SHA-256 of the resolved ontology descriptor document.
snapshot.version: SHA-256 of both identities; compare after reloading under the write lock.
snapshot.revision/tree: absent, since Snapshot retains neither source identity.
ontology: declared metadata, kind descriptors, starts and agent instructions.
ontology.kinds: exact kind definitions plus parts and effective link field names.
entries: one record per addressable entry or part, sorted by address.
entries.fields: all authored fields, including list parts, without renamed keys.
parts: one indexed record per unaddressable list item; fields mirror its owner slot.
relations: one outgoing record per authored link occurrence, including unresolved links.
relations.witness: owner and field path; source identifies the entry or list item.
absent: reserved typed envelope, distinct from authored mappings and null; dates/times are tagged ISO text.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from typing import TYPE_CHECKING, Any, cast

from content_digest import digest

from ogy.inspection_values import plain as _plain
from ogy.inspection_values import tagged
from ogy.kinds import Holds
from ogy.links import LinkItem, link_items, resolve

if TYPE_CHECKING:
    from ogy.kinds import Kind
    from ogy.model import Entry
    from ogy.snapshot import Snapshot

# Authored fields are open, ontology-defined JSON shapes, including unknown fields on invalid snapshots.
type Document = dict[str, Any]


@dataclass(frozen=True)
class InspectionRequest:
    """Select entries in a layer; identities always describe the complete input snapshot."""

    layer: str | None = None


def _absent(reason: str) -> Document:
    return tagged("absent", reason)


def _ontology(snapshot: Snapshot) -> Document:
    ontology = snapshot.ontology
    kinds = {}
    for name, kind in sorted(ontology.kinds.items()):
        kinds[name] = {
            **kind.model_dump(mode="json"),
            "parts": sorted(part.kind for part in ontology.parts_of(name)),
            "link_fields": sorted(field for field, spec in ontology.specs(kind).items() if spec.to),
        }
    return {
        "declared": ontology.declared.model_dump(mode="json"),
        "kinds": kinds,
        "starts": ontology.starts,
        "agents": ontology.agents if ontology.agents is not None else _absent("not-in-ontology"),
    }


def _record(snapshot: Snapshot, entry: Entry, kind: Kind, fields: Mapping[str, object]) -> Document:
    title = snapshot.ontology.roles.title
    return {
        "kind": kind.kind,
        "layer": entry.address.layer,
        "area": entry.address.area,
        "sentence_field": kind.sentence if kind.sentence is not None else _absent("not-declared"),
        "sentence": fields.get(kind.sentence, _absent("unset")) if kind.sentence is not None else _absent("not-declared"),
        "title": fields.get(title, _absent("unset")),
        "fields": dict(fields),
        "absent_fields": {name: _absent("unset") for name in sorted(set(snapshot.ontology.specs(kind)) - fields.keys())},
        "source": {"path": entry.path, "line": _absent("not-in-snapshot")},
    }


def _parts(snapshot: Snapshot, entry: Entry) -> list[Document]:
    parts = []
    for kind in sorted(snapshot.ontology.parts_of(entry.address.kind), key=lambda part: part.kind):
        values = entry.fields.get(kind.key or "")
        if kind.holding is not Holds.LIST or not isinstance(values, list):
            continue
        for index, value in enumerate(values):
            locator = {"owner": str(entry.address), "field": kind.key, "index": index}
            record = _record(snapshot, entry, kind, value) if isinstance(value, Mapping) else {"fields": value}
            parts.append(
                {
                    **record,
                    "kind": kind.kind,
                    "layer": entry.address.layer,
                    "area": entry.address.area,
                    "address": _absent("unaddressable-part"),
                    "key": _absent("unkeyed-part"),
                    "parent": str(entry.address),
                    "locator": locator,
                }
            )
    return parts


def _holder(snapshot: Snapshot, entry: Entry, item: LinkItem) -> tuple[object, list[str | int], Mapping[str, object]]:
    if item.item is None:
        return str(entry.address), [], entry.fields
    for kind in sorted(snapshot.ontology.parts_of(entry.address.kind), key=lambda part: part.kind):
        values = entry.fields.get(kind.key or "")
        if kind.holding is Holds.LIST and isinstance(values, list):
            for index, value in enumerate(values):
                if value is item.item:
                    locator = {"owner": str(entry.address), "field": kind.key, "index": index}
                    return locator, [kind.key or "", index], item.item
    msg = "link item does not belong to its snapshot entry"
    raise ValueError(msg)


def _relations(snapshot: Snapshot, entry: Entry) -> list[Document]:
    # YAML aliases may share a mapping; a list slot, rather than object identity, owns each occurrence.
    rows = {kind.key for kind in snapshot.ontology.parts_of(entry.address.kind) if kind.holding is Holds.LIST}
    entry = replace(
        entry,
        fields={
            name: [dict(item) if isinstance(item, Mapping) else item for item in value]
            if name in rows and isinstance(value, list)
            else value
            for name, value in entry.fields.items()
        },
    )
    relations = []
    occurrences: dict[tuple[str | int, ...], int] = {}
    for item in link_items(snapshot.ontology, entry):
        source, prefix, fields = _holder(snapshot, entry, item)
        path = [*prefix, item.field]
        value = fields.get(item.field)
        if isinstance(value, dict):
            path.append("reads")
            value = value.get("reads")
        if isinstance(value, list):
            key = tuple(path)
            occurrence = occurrences.get(key, 0)
            # link_items ignores non-text list members; the witness still names the authored slot.
            indices = [index for index, found in enumerate(value) if isinstance(found, str)]
            path.append(indices[occurrence])
            occurrences[key] = occurrence + 1
        resolution = resolve(snapshot.ontology, snapshot.entries, entry.address, item)
        relations.append(
            {
                "owner": str(entry.address),
                "source": source,
                "target": str(resolution.target)
                if resolution.target is not None
                else _absent(resolution.problem.value if resolution.problem is not None else "unresolved-link"),
                "field": item.field,
                "direction": "outgoing",
                "value": item.text,
                "path": path,
                "witness": {"owner": str(entry.address), "path": path},
            }
        )
    return sorted(relations, key=lambda relation: (str(relation["source"]), relation["field"], str(relation["path"])))


def inspect(snapshot: Snapshot, *, request: InspectionRequest | None = None) -> Document:
    """Return detached JSON data without I/O, guessed labels, graph derivation or write authority.

    Content identity covers what Snapshot retains, including notes, answers and proposals. Revision, original YAML
    spelling, source line numbers, built records and removed ledgers cannot be recovered from Snapshot. The version is
    an optimistic concurrency token for a future writer, not a review round id or permission to write.
    """
    request = request or InspectionRequest()
    if request.layer is not None and request.layer not in snapshot.ontology.layers:
        msg = f"unknown inspection layer {request.layer!r}"
        raise ValueError(msg)
    ontology = _ontology(snapshot)
    findings = sorted(
        (asdict(item) | {"address": str(item.address) if item.address is not None else None} for item in snapshot.findings),
        key=lambda item: (item["path"], str(item["address"]), item["detail"]),
    )
    identity = {
        "content": digest(
            _plain(
                {
                    "entries": [
                        {"address": str(address), "path": entry.path, "fields": dict(entry.fields)}
                        for address, entry in sorted(snapshot.entries.items())
                    ],
                    "findings": findings,
                }
            ),
            length=64,
        ),
        "ontology": digest(_plain(ontology), length=64),
    }
    entries: list[Document] = []
    parts: list[Document] = []
    relations: list[Document] = []
    for address, entry in sorted(snapshot.entries.items()):
        if request.layer is not None and address.layer != request.layer:
            continue
        entries.append(
            {
                **_record(snapshot, entry, snapshot.kind_of(address), entry.fields),
                "address": str(address),
                "key": address.key,
                "parent": str(address.parent()) if address.parent() is not None else _absent("root-entry"),
            }
        )
        parts.extend(_parts(snapshot, entry))
        relations.extend(_relations(snapshot, entry))
    document = {
        "schema": 2,
        "request": asdict(request),
        "snapshot": {
            **identity,
            "version": digest(identity, length=64),
            "revision": _absent("not-in-snapshot"),
            "tree": _absent("not-in-snapshot"),
        },
        "ontology": ontology,
        "entries": entries,
        "parts": parts,
        "relations": relations,
        "findings": findings,
        "absent": {name: _absent("not-in-snapshot") for name in ("source_text", "built", "removed")},
    }
    return cast("Document", _plain(document))
