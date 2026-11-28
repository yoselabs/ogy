"""The reasons of the ontology's kinds and fields (decision software/ontology/decision/kind-reasons, answered
because-key-computed): a kind file names, with `because`, the decisions or principles behind a kind and behind each field.
`ogy kinds --unreasoned` prints those that name none: the worklist of principle earned-on-a-real-case. A tracker item for an
answer that changes a kind file closes when a kind file cites that decision (decision decision-items-close)."""

lazy from ogy.ontology import Ontology

__all__ = ["cited", "unreasoned"]


def unreasoned(ontology: Ontology) -> list[str]:
    """`<kind>` and `<kind>.<field>` for every kind and field that names no reason, in kind order."""
    found: list[str] = []
    for name, kind in sorted(ontology.kinds.items()):
        if not kind.because:
            found.append(name)
        found += [f"{name}.{field}" for field, spec in sorted(kind.fields.items()) if not spec.because]
    return found


def cited(ontology: Ontology) -> set[str]:
    """Every address a kind or a field names as its reason."""
    found = {text for kind in ontology.kinds.values() for text in kind.because}
    return found | {text for kind in ontology.kinds.values() for spec in kind.fields.values() for text in spec.because}
