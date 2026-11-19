"""What a value must be for each field type. Every function returns the problems, none raises."""

from collections.abc import Callable, Collection, Mapping
from datetime import datetime

from ogy.kinds import FieldSpec, FieldType
from ogy.model import Problem, parse_address
from ogy.ontology import Ontology

type Found = list[tuple[Problem, str]]
HEX = frozenset("0123456789abcdef")
FINGERPRINT_LENGTH = 12


def _texts(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _time(value: object) -> bool:
    """A date, a time and a UTC offset: a date alone, or a time without an offset, is not one."""
    if isinstance(value, datetime):
        return value.tzinfo is not None
    if not isinstance(value, str) or "T" not in value:
        return False
    try:
        return datetime.fromisoformat(value).tzinfo is not None
    except ValueError:
        return False


def _uri(spec: FieldSpec, value: object) -> bool:
    if not isinstance(value, str):
        return False
    scheme, colon, rest = value.partition(":")
    return bool(colon) and scheme in spec.schemes and bool(rest)


def _expr(value: object) -> bool:
    return isinstance(value, dict) and isinstance(value.get("text"), str) and set(value) <= {"text", "reads"} and (
        "reads" not in value or _texts(value["reads"]))


def _number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _simple(spec: FieldSpec, value: object) -> bool:
    checks: dict[FieldType, Callable[[object], bool]] = {
        FieldType.TEXT: lambda item: isinstance(item, str),
        FieldType.LINK: lambda item: isinstance(item, str),
        FieldType.TEXTS: _texts,
        FieldType.LINKS: _texts,
        FieldType.NUMBER: _number,
        FieldType.FLAG: lambda item: isinstance(item, bool),
        FieldType.ENUM: lambda item: isinstance(item, str) and item in spec.of,
        FieldType.URI: lambda item: _uri(spec, item),
        FieldType.TIME: _time,
        FieldType.EXPR: _expr,
    }
    return checks[spec.type](value) if spec.type in checks else False


def _expected(spec: FieldSpec) -> str:
    match spec.type:
        case FieldType.ENUM:
            return f"one of {list(spec.of)}"
        case FieldType.URI:
            return f"a uri with a scheme from {list(spec.schemes)}"
        case FieldType.TIME:
            return "a date, a time and a UTC offset (2026-11-12T10:05:00+01:00)"
        case FieldType.EXPR:
            return "a mapping {text, reads}"
        case _:
            return str(spec.type)


def sets_problems(ontology: Ontology, value: object) -> Found:
    """`{address: {field: value} | null}`: the kind comes from the address, so each field is that kind's, typed as it declares."""
    if not isinstance(value, dict):
        return [(Problem.WRONG_TYPE, "is a mapping of address to fields or null")]
    found: Found = []
    for key, fields in value.items():
        address = parse_address(key, ontology) if isinstance(key, str) else None
        kind = ontology.get(address.kind) if address else None
        if kind is None:
            found.append((Problem.WRONG_TYPE, f"{key!r} is not an address"))
        elif fields is None:
            continue
        elif not isinstance(fields, dict):
            found.append((Problem.WRONG_TYPE, f"{key} is a mapping of fields or null"))
        else:
            found += [(problem, f"{key}: {detail}") for problem, detail in
                      fields_problems(ontology, ontology.specs(kind), fields, partial=True, old=kind.old_names)]
    return found


AGREED_HASH = "hash"  # the key of an agreement that holds the fingerprint agreed to


def agreed_keys(ontology: Ontology) -> frozenset[str]:
    """The keys of an agreement: the settling kind's answer `at`, `where` and `said`, and the hash. Only a person agrees, so
    who agreed is not a key."""
    settler = ontology.settling_kind()
    names = settler.settling if settler else None
    return frozenset({AGREED_HASH, *((names.at, names.where, names.said) if names else ())})


def _answer_spec(ontology: Ontology, name: str) -> FieldSpec | None:
    """A field of the settling kind's answer: an agreement's `at` and `where` are typed as an answer's."""
    settler = ontology.settling_kind()
    answer = ontology.get(settler.settling.answer) if settler and settler.settling else None
    return answer.fields.get(name) if answer else None


def agreed_problems(ontology: Ontology, value: object) -> Found:
    """`{at, where, said, hash}` (in the settling kind's names): a person's yes in a review round, `hash` the fingerprint agreed to."""
    settler = ontology.settling_kind()
    names = settler.settling if settler else None
    if names is None:
        return [(Problem.WRONG_TYPE, "is no field: the ontology has no settling kind to name its keys")]
    shape = f"{{{names.at}, {names.where}, {names.said}, {AGREED_HASH}: {FINGERPRINT_LENGTH} hex}}"
    if not isinstance(value, dict) or set(value) != agreed_keys(ontology):
        return [(Problem.WRONG_TYPE, f"is {shape}")]
    fingerprint, said = value[AGREED_HASH], value[names.said]
    found: Found = [] if isinstance(fingerprint, str) and len(fingerprint) == FINGERPRINT_LENGTH and set(fingerprint) <= HEX else [
        (Problem.WRONG_TYPE, f"{AGREED_HASH} is {FINGERPRINT_LENGTH} hex")]
    found += [] if isinstance(said, str) and said.strip() else [
        (Problem.WRONG_TYPE, f"{names.said} is a short paraphrase of what the person said")]
    for name in (names.at, names.where):
        spec = _answer_spec(ontology, name)
        if spec is not None and not _simple(spec, value[name]):
            found.append((Problem.WRONG_TYPE, f"{name} is {_expected(spec)}"))
    return found


def value_problems(ontology: Ontology, spec: FieldSpec, value: object) -> Found:
    match spec.type:
        case FieldType.SETS:
            return sets_problems(ontology, value)
        case FieldType.AGREED:
            return agreed_problems(ontology, value)
        case _:
            return [] if _simple(spec, value) else [(Problem.WRONG_TYPE, f"is {_expected(spec)}")]


def fields_problems(ontology: Ontology, specs: Mapping[str, FieldSpec], data: Mapping[str, object], known: Collection[str] = (),
                    *, partial: bool = False, old: Mapping[str, str | None] | None = None) -> Found:
    """Unknown fields, values of the wrong type and, unless `partial`, missing required fields; `known` are part keys, `old` the
    names the kind renamed or dropped (`Kind.old_names`), which `ogy migrate` rewrites."""
    found: Found = []
    for name, value in data.items():
        spec = specs.get(name)
        if "?" in name:
            found.append((Problem.BAD_KEY, f"{name}: no key contains `?`"))
        elif spec is None:
            if old and name in old:
                now = old[name]
                found.append((Problem.NEEDS_MIGRATION, f"{name} is now {now}: run `ogy migrate`" if now else
                              f"{name} was dropped from the kind: run `ogy migrate`"))
            elif name in ontology.declared.reserved.computed:
                found.append((Problem.STORED_STATE, f"{name} is computed, see `ogy show`"))
            elif name not in known:
                found.append((Problem.UNKNOWN_FIELD, name))
        else:
            found += [(problem, f"{name} {detail}") for problem, detail in value_problems(ontology, spec, value)]
    if not partial:
        found += [(Problem.MISSING_FIELD, name) for name, spec in specs.items() if spec.required and name not in data]
    return found
