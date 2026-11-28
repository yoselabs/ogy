"""A text field that declares `placeholders: <part kind>` (an interface's `invoked_as`) and the parts it names: every `<name>`
in the text is a part of that kind with the id `name`, and every such part is a `<name>` of the text (decisions
software/ontology/decision/inputs-that-are-no-fact, answered declared-inputs, and
software/ontology/decision/command-inputs-are-accepted, answered checked). An entry that leaves the text unset names none."""

import re

from ogy.model import Finding, Problem
lazy from ogy.snapshot import Snapshot
lazy from ogy.source import Source

_NAME = re.compile(r"<([^<>]+)>")  # a name with a space or a bar is no part id: it is reported


def check_placeholders(snapshot: Snapshot, _source: Source | None = None) -> list[Finding]:
    found: list[Finding] = []
    for address, entry in sorted(snapshot.entries.items()):
        for field, spec in snapshot.ontology.specs(snapshot.kind_of(address)).items():
            if spec.placeholders is None or (text := entry.text(field)) is None:
                continue
            named = set(_NAME.findall(text))
            held = {part.path[-1][1] for part in snapshot.links.parts(address, spec.placeholders)}
            found += [
                Finding(Problem.UNMATCHED_PLACEHOLDER, entry.path, f"{field}: <{name}> is no {spec.placeholders} of it", address)
                for name in sorted(named - held)
            ]
            found += [
                Finding(Problem.UNMATCHED_PLACEHOLDER, entry.path, f"{spec.placeholders} {name} is no <{name}> of its {field}", address)
                for name in sorted(held - named)
            ]
    return found
