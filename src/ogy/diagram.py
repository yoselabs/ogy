"""`ogy diagram <workflow address>`: a Mermaid flowchart generated from the entries on demand, never committed."""

import re

from ogy.flowcheck import graph, link
from ogy.kinds import Flow
from ogy.model import Address
from ogy.snapshot import Snapshot


def node(address: Address) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", "_".join(f"{kind}_{key}" for kind, key in address.path[-2:]))


def label(snapshot: Snapshot, row: Address, flow: Flow) -> str:
    fields = snapshot.entries[row].fields
    when = fields.get(flow.when)
    text = fields.get("label") or (when.get("text") if isinstance(when, dict) else None) or row.key or row.kind
    return str(text).replace('"', "'")


def mermaid(snapshot: Snapshot, flow: Flow, container: Address) -> list[str]:
    g = graph(snapshot, flow, container)
    lines = ["flowchart TD"]
    for start in link(snapshot, container, flow.start):
        lines.append(f'  start(("start")) --> {node(start)}')
    for step in g.steps:
        shape = f'{node(step)}[["{step.key}"]]' if snapshot.entries[step].fields.get(flow.calls) else f'{node(step)}["{step.key}"]'
        lines.append(f"  {shape}")
        for target in link(snapshot, step, flow.then):
            lines.append(f"  {node(step)} --> {node(target)}")
        for kind in (flow.choice, flow.case, flow.timeout):
            for row in g.rows[step][kind]:
                for target in link(snapshot, row, flow.then):
                    lines.append(f'  {node(step)} -- "{label(snapshot, row, flow)}" --> {node(target)}')
    for end in g.ends:
        lines.append(f'  {node(end)}(("{end.key}"))')
    return lines
