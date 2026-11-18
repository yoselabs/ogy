"""`ogy.yml` at the repository root: the defaults of the flags. A flag on the command line overrides it."""

from dataclasses import dataclass
from pathlib import Path

import any_yaml
from settings_base import resolve_config_path

from ogy.verdict import Unusable

CONFIG_FILE = "ogy.yml"
CONFIG_ENV = "OGY_CONFIG"  # points at another file; the repository's own is the default
KEYS = ("ontology", "rev")


class ConfigError(Unusable):
    """`ogy.yml` cannot be read as settings."""

    prefix = "bad settings: "


@dataclass(frozen=True)
class Config:
    """What the file sets; None for a key it does not hold."""

    ontology: str | None = None
    rev: str | None = None


def path_of(repo: Path) -> Path | None:
    """The settings file in use: `$OGY_CONFIG`, else `<repo>/ogy.yml`; None when there is none."""
    return resolve_config_path(CONFIG_ENV, repo / CONFIG_FILE)


def read(repo: Path) -> Config:
    path = path_of(repo)
    if path is None:
        return Config()
    try:
        data = any_yaml.load(path.read_text())
    except (any_yaml.YAMLError, OSError, UnicodeDecodeError) as error:
        raise ConfigError(f"{path}: {error}") from error
    if data is None:
        return Config()
    if not isinstance(data, dict):
        raise ConfigError(f"{path} is a mapping of settings")
    unknown = sorted(str(key) for key in data if key not in KEYS)
    if unknown:
        raise ConfigError(f"{path}: unknown setting {', '.join(unknown)} (known: {', '.join(KEYS)})")
    bad = sorted(key for key, value in data.items() if not isinstance(value, str))
    if bad:
        raise ConfigError(f"{path}: {', '.join(bad)} must be text")
    return Config(**data)


