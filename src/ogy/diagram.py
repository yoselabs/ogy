"""`ogy diagram <workflow address>`: a Mermaid flowchart generated from the entries on demand, never committed."""

import re

from ogy.flowcheck import graph, link
lazy from ogy.kinds import Flow
lazy from ogy.model import Address
lazy from ogy.snapshot import Snapshot


def node(address: Address) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", "_".join(f"{kind}_{key}" for kind, key in address.path[-2:]))


def label(snapshot: Snapshot, row: Address, flow: Flow) -> str:
    fields = snapshot.entries[row].fields
    when = fields.get(flow.when)
    text = snapshot.sentence(row) or (when.get("text") if isinstance(when, dict) else None) or row.key or row.kind
    return str(text).replace('"', "'")


def mermaid(snapshot: Snapshot, flow: Flow, container: Address) -> list[str]:
    g = graph(snapshot, flow, container)
    lines = ["flowchart TD"]
    lines.extend(f'  start(("start")) --> {node(start)}' for start in link(snapshot, container, flow.start))
    for step in g.steps:
        shape = f'{node(step)}[["{step.key}"]]' if snapshot.entries[step].fields.get(flow.calls) else f'{node(step)}["{step.key}"]'
        lines.append(f"  {shape}")
        lines.extend(f"  {node(step)} --> {node(target)}" for target in link(snapshot, step, flow.then))
        for kind in (flow.choice, flow.case, flow.timeout):
            for row in g.rows[step][kind]:
                lines.extend(
                    f'  {node(step)} -- "{label(snapshot, row, flow)}" --> {node(target)}' for target in link(snapshot, row, flow.then)
                )
    lines.extend(f'  {node(end)}(("{end.key}"))' for end in g.ends)
    return lines
