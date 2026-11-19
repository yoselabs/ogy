"""`ogy kinds --map`: the whole ontology on one screen. One line per kind, grouped by the layers it may live in, its parts
indented under it; then the rules the kind files declare, as sentences. Read from the kind files; nothing is kept."""

from ogy.kinds import FieldSpec, FieldType, Flow, Holds, Kind, Shape
from ogy.ontology import Ontology

LEGEND = ("! required, -> one link, ->> many links (an expression: the links it reads), [] a list part, (a|b) enum members, "
          "indentation = part of; every kind also takes ")
MANY = frozenset({FieldType.LINKS, FieldType.EXPR})


def _field(name: str, spec: FieldSpec) -> str:
    text = ("!" if spec.required else "") + name
    if spec.of:
        text += f"({'|'.join(spec.of)})"
    if spec.to:
        text += ("->>" if spec.type in MANY else "->") + "|".join(spec.to)
    return text


def _line(kind: Kind, depth: int) -> str:
    mark = "[]" if kind.shape is Shape.INLINE and kind.holding is Holds.LIST else ""
    fields = " ".join(_field(name, spec) for name, spec in kind.fields.items())
    return f"{'  ' * depth}{kind.kind}{mark}:" + (f" {fields}" if fields else "")


def _tree(ontology: Ontology, kind: Kind, depth: int, shown: set[str]) -> list[str]:
    """The kind's line and its parts below it; a part already shown under another parent is named, not repeated."""
    if kind.kind in shown:
        return [f"{'  ' * depth}{kind.kind}{'[]' if kind.holding is Holds.LIST else ''}: as above"]
    shown.add(kind.kind)
    lines = [_line(kind, depth)]
    for part in ontology.parts_of(kind.kind):
        lines += _tree(ontology, part, depth + 1, shown)
    return lines


def _groups(ontology: Ontology) -> list[tuple[str, list[Kind]]]:
    """Top kinds by where they live: each combination of layers in the ontology's order, then each fixed folder."""
    top = [kind for _, kind in sorted(ontology.kinds.items()) if kind.shape is not Shape.INLINE]
    order = sorted({kind.layers for kind in top if kind.layers}, key=lambda layers: [ontology.layers.index(item) for item in layers])
    order.sort(key=lambda layers: (ontology.layers.index(layers[0]), -len(layers)))
    groups = [(" and ".join(layers), [kind for kind in top if kind.layers == layers]) for layers in order]
    folders = sorted({kind.area for kind in top if kind.area})
    return groups + [(f"{folder}/ (fixed folder)", [kind for kind in top if kind.area == folder]) for folder in folders]


def _rules(ontology: Ontology) -> list[str]:
    """Every rule the kind files declare, as a sentence; one sentence several kinds declare is written once."""
    said: dict[str, list[str]] = {}
    for name, kind in sorted(ontology.kinds.items()):
        sentences = [f"exactly one of {', '.join(group)}" for group in kind.exactly_one_of]
        sentences += [need.error for need in kind.requires]
        if kind.one_part is not None:
            sentences.append(f"exactly one {kind.one_part.kind} with {kind.one_part.field}: {kind.one_part.equals}")
        for sentence in sentences:
            said.setdefault(sentence, []).append(name)
    return [f"  {', '.join(names)}: {sentence}" for sentence, names in said.items()]


def _flow_rules(name: str, flow: Flow) -> list[str]:
    """The fixed checks a `flow:` turns on (see `flowcheck`), in the names that kind file gives."""
    return [f"  {name} (flow): an actor {flow.step} offers {flow.choice}s (maybe a {flow.timeout}) and nothing else; a system "
            f"{flow.step} has {flow.case}s or one `{flow.then}`; a calling {flow.step} continues by {flow.case}s",
            f"  {name} (flow): a system {flow.step} has one `{flow.otherwise}` {flow.case} without `{flow.when}`; every other "
            f"{flow.case} has `{flow.when}` and its own `{flow.order}`",
            f"  {name} (flow): every {flow.step} is reached from `{flow.start}` and reaches an {flow.end} or a hand-off; every "
            f"{flow.end} is reached",
            f"  {name} (flow): a calling {flow.step} names every {flow.end} of its callee in `{flow.covers}`",
            f"  {name} (flow): the {' and '.join(item + 's' for item in flow.servers)} serving a {flow.step} offer every "
            f"{flow.choice} between them",
            f"  {name} (flow): every {name} is started: an {flow.actor} on its first {flow.step}, a "
            f"{' or '.join(flow.roots)}, or led to from a started {name}"]


def map_lines(ontology: Ontology) -> list[str]:
    lines, shown = [LEGEND + ", ".join(ontology.common)], set[str]()
    for title, kinds in _groups(ontology):
        lines.append(f"{title}:")
        for kind in kinds:
            lines += _tree(ontology, kind, 1, shown)
    flows = [line for name, kind in sorted(ontology.kinds.items()) if kind.flow for line in _flow_rules(name, kind.flow)]
    return [*lines, "rules:", *_rules(ontology), *flows]
