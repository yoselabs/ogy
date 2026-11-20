"""`ogy kinds`: the kinds of an ontology as text, read from the kind files. Nothing is kept: the kind files are the one home."""

from ogy.kinds import FieldSpec, Input, Kind, Picked
from ogy.near import hint
from ogy.ontology import Ontology
from ogy.verdict import NotFound


def _input(given: Input | Picked) -> str:
    """How a link enters the build hash, as words: `content`, `address`, or what of its targets it picks."""
    if isinstance(given, Input):
        return str(given)
    return f"fields {'|'.join(given.fields)}" if given.fields else f"addresses of its {'|'.join(given.parts)}"


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
    if spec.input is not None:
        detail.append("build input: " + _input(spec.input))
    return f"    {name}: {', '.join(detail)}"


def _facts(kind: Kind) -> list[str]:
    where = [str(kind.shape)]
    if kind.file:
        where.append(f"file {kind.file}")
    if kind.part_of:
        where.append(f"part of {'|'.join(kind.part_of)} under key {kind.key} (holds {kind.holding})")
    if kind.area:
        where.append(f"only in the folder {kind.area}")
    if kind.shared:
        where.append("also in the area shared, when two areas use it")
    if kind.moved_from:
        where.append(f"moved from {kind.moved_from} (`ogy migrate`)")
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
    if kind.input:
        lines.append(f"  build input: {', '.join(f'{name} {_input(given)}' for name, given in kind.input.items())}")
    if kind.input_from:
        found = (f"what links here by {name}, its {_input(given)}" for name, given in kind.input_from.items())
        lines.append(f"  build input from: {', '.join(found)}")
    return lines


def _rules(kind: Kind) -> list[str]:
    lines = [f"  exactly one of: {', '.join(group)}" for group in kind.exactly_one_of]
    for need in kind.requires:
        lines.append(f"  requires{' ' + need.condition if need.condition else ''}: {need.error}")
    if kind.one_part:
        lines.append(f"  exactly one {kind.one_part.kind} with {kind.one_part.field}: {kind.one_part.equals}")
    lines += [f"  was: {kind.was.kind} (`ogy migrate`)"] if kind.was else []
    lines += [f"  renamed: {old} is now {new} (`ogy migrate`)" for old, new in kind.renamed.items()]
    lines += [f"  revalued: {field} {old} is now {', '.join(f'{k} {v}' for k, v in now.items())} (`ogy migrate`)"
              for field, values in kind.revalued.items() for old, now in values.items()]
    lines += [f"  folded: {field} held a part, now its {inner} (`ogy migrate`)" for field, inner in kind.folded.items()]
    return lines + [f"  dropped: {old} (`ogy migrate`)" for old in kind.dropped]


def _likeness(kind: Kind) -> list[str]:
    return [f"  {word}: {text}" for word, text in (("like", kind.like), ("unlike", kind.unlike)) if text]


def likeness_lines(ontology: Ontology) -> list[str]:
    """One line per kind that says what mainstream notion it matches and which of the same name it does not mean."""
    found = [f"  {name}: " + "; ".join(f"{word} {text}" for word, text in (("like", kind.like), ("unlike", kind.unlike)) if text)
             for name, kind in sorted(ontology.kinds.items()) if kind.like or kind.unlike]
    return ["kinds, like and unlike:", *found] if found else []


def kinds_lines(ontology: Ontology, only: str | None = None) -> list[str]:
    """Every kind, or the one named (NotFound with near misses when the ontology has none of that name)."""
    if only is not None and only not in ontology.kinds:
        raise NotFound(f"no kind {only}" + hint(only, ontology.kinds))
    lines: list[str] = []
    for name, kind in sorted(ontology.kinds.items()):
        if only not in (None, name):
            continue
        lines += [f"{name}: {kind.about}", *([f"  guidance: {kind.guidance}"] if kind.guidance else []), *_likeness(kind), *_facts(kind)]
        if kind.fields:
            lines += ["  fields:", *(_field(field, spec) for field, spec in kind.fields.items())]
        lines += [*_rules(kind), ""]
    return lines[:-1]
