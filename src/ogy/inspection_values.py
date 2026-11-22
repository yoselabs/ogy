"""Tagged, reversible JSON values for inspection of YAML outside JSON's value space."""

from __future__ import annotations

import base64
import math
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

# Any: invalid authored YAML is open data, including non-string mapping keys.
type Value = dict[str, Any]
MARKER = "\x00ogy"


class _Tagged(dict[str, Any]):
    """Transport metadata distinguished from authored dictionaries until final encoding."""


def tagged(kind: str, value: object) -> Value:
    return _Tagged({MARKER: {"type": kind, "value": value}})


def plain(value: object) -> object:
    """Preserve mapping order and scalar types, escaping authored marker keys."""
    if isinstance(value, _Tagged):
        return value
    if isinstance(value, (date, datetime)):
        return tagged(type(value).__name__, value.isoformat())
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) or key == MARKER for key in value):
            return tagged("mapping", [[plain(key), plain(item)] for key, item in value.items()])
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return _extended(value)


def _extended(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return tagged("float", repr(value)) if isinstance(value, float) and not math.isfinite(value) else value
    if isinstance(value, (set, frozenset)):
        return tagged("set", [plain(item) for item in sorted(value, key=repr)])
    if isinstance(value, bytes):
        return tagged("binary", base64.b64encode(value).decode("ascii"))
    return tagged("unsupported", type(value).__name__)


def problems(value: object, path: str = "$", ancestors: frozenset[int] = frozenset()) -> list[str]:
    """Find non-JSON YAML values without coercing keys or losing their locations."""
    if id(value) in ancestors:
        return [f"{path}: recursive YAML alias"]
    ancestors = ancestors | {id(value)}
    if isinstance(value, Mapping):
        found = [f"{path}: non-text or reserved mapping key" for key in value if not isinstance(key, str) or key == MARKER]
        return found + [issue for key, item in value.items() for issue in problems(item, f"{path}.{key}", ancestors)]
    if isinstance(value, (list, tuple)):
        return [issue for index, item in enumerate(value) for issue in problems(item, f"{path}[{index}]", ancestors)]
    if isinstance(value, (set, frozenset, bytes)) or (isinstance(value, float) and not math.isfinite(value)):
        return [f"{path}: YAML {type(value).__name__} requires an inspection marker"]
    return []
