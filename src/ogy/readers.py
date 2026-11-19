"""`ogy kinds --readers`: what reads each field of each kind. A field nothing reads is text in a field's clothes
(principle rigid-where-checked: a field names the check that reads it).

Most readers come from the kind files themselves: the fingerprint (when something compares it), the paths of `requires`
and `fingerprint.also`, `exactly_one_of` and `one_part`, the names `flow:` and `settling:` give, link resolution and impact
(every link, links and expr field), and the review rank (`harm`). The checks and printers that read a field by its name follow
from the roles the kinds declare (`named`): the sentence, the glossary, the printed-first kind, the settling names. `ogy show`
prints every field and is no reader."""

from collections.abc import Iterable

from ogy.kinds import ANY, LINKING, Flow, Holds, Kind, Requirement
from ogy.ontology import Ontology

AVOIDED, REVIEW, GLOSSARY = "check avoided-word", "printer review", "printer glossary"


def named(ontology: Ontology) -> dict[str, set[str]]:
    """field, or kind.field -> the checks and printers that read it by name, from the roles the kinds declare."""
    found: dict[str, set[str]] = {name: {AVOIDED} for name in ontology.texts()}  # the avoided-word check reads every text field

    def add(key: str, *readers: str) -> None:
        found.setdefault(key, set()).update(readers)

    for kind in ontology.kinds.values():
        if kind.sentence is not None:
            add(kind.sentence, AVOIDED, REVIEW, *(["check duplicate-says"] if ontology.carded(kind) else []))
        if kind.flow is not None and (row := ontology.get(kind.flow.choice)) is not None and row.sentence:
            add(f"{row.kind}.{row.sentence}", "printer diagram")
        if (names := kind.settling) is not None:
            add(f"{names.guess}.{names.why}", AVOIDED, REVIEW)
        if (printed := kind.printed_first) is not None and printed.also:
            add(f"{kind.kind}.{printed.also}", AVOIDED, GLOSSARY)
        if (glossary := kind.glossary) is not None:
            add(f"{kind.kind}.{glossary.word}", "check word-clash", GLOSSARY)
            add(f"{kind.kind}.{kind.sentence}", "check term-too-long", GLOSSARY)
            add(f"{kind.kind}.{glossary.avoid}", AVOIDED, "check word-clash", GLOSSARY)
    return found

type Reads = dict[tuple[str, str], set[str]]


def _mark(found: Reads, kind: str, field: str, reader: str, kinds: dict[str, Kind]) -> None:
    if kind in kinds and field in kinds[kind].fields:
        found.setdefault((kind, field), set()).add(reader)


def _walk(found: Reads, kinds: dict[str, Kind], start: str, hops: Iterable[str], reader: str) -> set[str]:
    """Mark the fields a link path reads from `start`; the kinds a final `=@fingerprint` reaches."""
    current = {start}
    for hop in hops:
        if hop.startswith("=@"):
            return current if hop == "=@fingerprint" else set()
        if hop.startswith("/"):
            current = {hop[1:]}
        elif hop.startswith("="):
            for kind in current:
                _mark(found, kind, hop[1:], reader, kinds)
            break
        elif hop.startswith("<-"):
            name = hop[2:]
            current = {k for k, kind in kinds.items() if name in kind.fields and {*current, ANY} & set(kind.fields[name].to)}
            for kind in current:
                _mark(found, kind, name, reader, kinds)
        else:
            for kind in current:
                _mark(found, kind, hop, reader, kinds)
            current = {t for k in current if hop in kinds[k].fields for t in kinds[k].fields[hop].to}
            current = set(kinds) if ANY in current else current
    return set()


def _requirement(found: Reads, kinds: dict[str, Kind], name: str, need: Requirement) -> None:
    """Its condition's field, the field it needs, its path and the `without` fields of the kinds it reaches."""
    for field in (need.if_set, need.if_equals.field if need.if_equals else None, need.needs_field):
        if field:
            _mark(found, name, field, "requires", kinds)
    _walk(found, kinds, name, need.path, "requires")
    for target in need.kinds:
        for field in need.without:
            _mark(found, target, field, "requires", kinds)


def _flow(found: Reads, kinds: dict[str, Kind], container: str, flow: Flow) -> None:
    rows = (flow.choice, flow.case, flow.timeout)
    wanted = [(container, flow.start), *((container, field) for field in flow.roots), *((k, flow.then) for k in (flow.step, *rows)),
              (flow.step, flow.actor), (flow.step, flow.calls), (flow.case, flow.covers), (flow.case, flow.when),
              (flow.case, flow.order), *((k, field) for k in flow.servers for field in (flow.serves, flow.offers)),
              (flow.guard, flow.guarded), (flow.guard, flow.denied)]
    for kind, field in wanted:
        _mark(found, kind, field, "flow", kinds)


def _settling(found: Reads, kinds: dict[str, Kind]) -> None:
    for kind in kinds.values():
        if (names := kind.settling) is not None:
            heard = next((k.kind for k in kinds.values() if k.is_part(names.guess) and k.key == names.heard), "")
            wanted = [(names.option, names.sets), (names.guess, names.chose), (names.guess, names.value), (heard, names.said),
                      *((names.answer, f) for f in (names.chose, names.said, names.at, names.where, names.note,
                                                    names.delegated))]
            for part, field in wanted:
                _mark(found, part, field, "settling", kinds)


def _compared(ontology: Ontology, reached: set[str]) -> set[str]:
    """The kinds whose fingerprint the work or an agreement compares: built (needs proof), agreed (asked, with a sentence),
    reached by a path; a list or one part is inside its parent's. Telling a move from a loss compares every fingerprint, for
    identity, not meaning: it is no reader."""
    kinds = ontology.kinds
    own = {n for n, k in kinds.items() if k.needs_proof or (k.asked and ontology.carded(k)) or k.must_be_agreed or n in reached}
    inside = {n for n, k in kinds.items() if k.holding in (Holds.LIST, Holds.ONE) and k.part_of and set(k.part_of) & own}
    return own | inside | ({n for n, k in kinds.items() if k.holding is Holds.ONE and set(k.part_of) & inside})


def readers(ontology: Ontology) -> dict[tuple[str, str], list[str]]:
    """`(kind, field)` -> the sorted names of what reads it, for every field of every kind (empty: nothing does)."""
    kinds, found, reached = ontology.kinds, {}, set()
    for name, kind in kinds.items():
        for need in kind.requires:
            _requirement(found, kinds, name, need)
        for path in (*kind.fingerprint.also, *kind.fingerprint.reached):
            reached |= _walk(found, kinds, name, path, "fingerprint path")
        for group in kind.exactly_one_of:
            for field in group:
                _mark(found, name, field, "exactly_one_of", kinds)
        if kind.one_part is not None:
            _mark(found, kind.one_part.kind, kind.one_part.field, "one_part", kinds)
        if kind.flow is not None:
            _flow(found, kinds, name, kind.flow)
    _settling(found, kinds)
    compared, by_name = _compared(ontology, reached), named(ontology)
    for name, kind in kinds.items():
        for field, spec in kind.fields.items():
            extra = [item for item in (*by_name.get(field, ()), *by_name.get(f"{name}.{field}", ())) if kind.asked or item != REVIEW]
            extra += ["fingerprint"] if not spec.note and name in compared else []
            extra += ["links and impact"] if spec.type in LINKING else []
            extra += ["review rank (harm)"] if spec.harm else []
            found.setdefault((name, field), set()).update(extra)
    return {key: sorted(value) for key, value in sorted(found.items())}


def readers_lines(ontology: Ontology, only: str | None = None) -> list[str]:
    """One line per field, `kind.field: reader, ...`, then the fields nothing reads and those only the fingerprint reads (a change
    to them is work, but no check reads them)."""
    found = {key: value for key, value in readers(ontology).items() if only in (None, key[0])}
    lines = [f"{kind}.{field}: {', '.join(names) or 'nothing'}" for (kind, field), names in found.items()]
    idle = [f"{kind}.{field}" for (kind, field), names in found.items() if not names]
    stale = [f"{kind}.{field}" for (kind, field), names in found.items() if names == ["fingerprint"]]
    return [*lines, "", f"read by nothing ({len(idle)}): {', '.join(idle) or 'none'}",
            f"read only by the fingerprint ({len(stale)}): {', '.join(stale) or 'none'}"]
