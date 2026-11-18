"""`ogy kinds`: the kinds of an ontology as text, read from the kind files. Nothing is kept: the kind files are the one home."""

from ogy.kinds import FieldSpec, Kind
from ogy.near import hint
from ogy.ontology import Ontology
from ogy.verdict import NotFound


def _field(name: str, spec: FieldSpec) -> str:
    detail = [str(spec.type)]
    if spec.to:
        detail.append("-> " + "|".join(spec.to))
    if spec.of:
        detail.append("one of " + "|".join(spec.of))
    if spec.schemes:
        detail.append("schemes " + "|".join(spec.schemes))
    detail += [word for word, on in (("required", spec.required), ("note", spec.note)) if on]
    if spec.harm:
        detail.append("harm if wrong: " + "|".join(spec.harm))
    return f"    {name}: {', '.join(detail)}"


def _facts(kind: Kind) -> list[str]:
    where = [str(kind.shape)]
    if kind.file:
        where.append(f"file {kind.file}")
    if kind.part_of:
        where.append(f"part of {'|'.join(kind.part_of)} under key {kind.key} (holds {kind.holding})")
    if kind.area:
        where.append(f"only in the folder {kind.area}")
    flags = [text for text, on in (("in every area", kind.every_area), ("never asked", not kind.asked),
                                   ("needs proof", kind.needs_proof), ("must be agreed", kind.must_be_agreed),
                                   ("append only", kind.append_only), ("settles entries", kind.settling is not None),
                                   ("is a flow", kind.flow is not None)) if on]
    lines = [f"  lives: {', '.join(where)}"]
    if kind.layers:
        lines.append(f"  layers: {', '.join(kind.layers)}")
    if flags:
        lines.append(f"  is: {', '.join(flags)}")
    if kind.harm:
        lines.append(f"  harm if wrong: {', '.join(kind.harm)}")
    return lines


def _rules(kind: Kind) -> list[str]:
    lines = [f"  exactly one of: {', '.join(group)}" for group in kind.exactly_one_of]
    for need in kind.requires:
        when = f" when {need.if_set} is set" if need.if_set else f" when it has a {need.if_part}" if need.if_part else ""
        lines.append(f"  requires{when}: {need.error}")
    if kind.one_part:
        lines.append(f"  exactly one {kind.one_part.kind} with {kind.one_part.field}: {kind.one_part.equals}")
    return lines


def kinds_lines(ontology: Ontology, only: str | None = None) -> list[str]:
    """Every kind, or the one named (NotFound with near misses when the ontology has none of that name)."""
    if only is not None and only not in ontology.kinds:
        raise NotFound(f"no kind {only}" + hint(only, ontology.kinds))
    lines: list[str] = []
    for name, kind in sorted(ontology.kinds.items()):
        if only not in (None, name):
            continue
        lines += [f"{name}: {kind.about}", *_facts(kind)]
        if kind.fields:
            lines += ["  fields:", *(_field(field, spec) for field, spec in kind.fields.items())]
        lines += [*_rules(kind), ""]
    return lines[:-1]
