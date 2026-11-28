"""`ogy.yml` at the repository root: the defaults of the flags (a flag on the command line overrides it), and the land
branch `ogy init` records (`land`: its `--land`, else the remote's default branch), which no other command sets and nothing guesses.
`cites` lists the repository paths (a folder ends in `/`) whose text ogy reads for the citation "decision <address>", whatever
their language (decision software/cli/decision/citations-outside-python, answered entry-or-declared-file)."""

from dataclasses import dataclass
lazy from pathlib import Path

import any_yaml
from settings_base import resolve_config_path

from ogy.verdict import UnusableError

CONFIG_FILE = "ogy.yml"
CONFIG_ENV = "OGY_CONFIG"  # points at another file; the repository's own is the default
KEYS = ("ontology", "rev", "land", "cites")
NO_LAND = f"{CONFIG_FILE} names no land branch (`land:`): run `ogy init`"


class ConfigError(UnusableError):
    """`ogy.yml` cannot be read as settings."""

    prefix = "bad settings: "


class NoLandError(UnusableError):
    """`ogy.yml` names no land branch, so no update can be told to be a land."""


@dataclass(frozen=True)
class Config:
    """What the file sets; None for a key it does not hold."""

    ontology: str | None = None
    rev: str | None = None
    land: str | None = None  # the branch a land updates and a branch is checked against
    cites: tuple[str, ...] = ()  # the paths read for citations; none: no file cites a decision


def path_of(repo: Path) -> Path | None:
    """The settings file in use: `$OGY_CONFIG`, else `<repo>/ogy.yml`; None when there is none."""
    return resolve_config_path(CONFIG_ENV, repo / CONFIG_FILE)


def read(repo: Path) -> Config:
    path = path_of(repo)
    if path is None:
        return Config()
    try:
        return parse(path.read_text(), str(path))
    except (OSError, UnicodeDecodeError) as error:
        msg = f"{path}: {error}"
        raise ConfigError(msg) from error


def parse(text: str, path: str = CONFIG_FILE) -> Config:
    """The settings one `ogy.yml` text sets (a commit's own, for a read of that commit)."""
    try:
        data = any_yaml.load(text)
    except any_yaml.YAMLError as error:
        msg = f"{path}: {error}"
        raise ConfigError(msg) from error
    if data is None:
        return Config()
    if not isinstance(data, dict):
        msg = f"{path} is a mapping of settings"
        raise ConfigError(msg)
    unknown = sorted(str(key) for key in data if key not in KEYS)
    if unknown:
        msg = f"{path}: unknown setting {', '.join(unknown)} (known: {', '.join(KEYS)})"
        raise ConfigError(msg)
    cites = data.pop("cites", None) or []
    bad = sorted(key for key, value in data.items() if not isinstance(value, str))
    bad += ["cites"] if not isinstance(cites, list) or not all(isinstance(item, str) for item in cites) else []
    if bad:
        msg = f"{path}: {', '.join(bad)} must be text (cites: a list of paths)"
        raise ConfigError(msg)
    return Config(**data, cites=tuple(cites))


def land(repo: Path) -> str:
    """The land branch `ogy.yml` names; refuses (NoLandError) when it names none. Every reader of `land` goes through it (the
    hooks, the merge base a check and a removal compare against, init and its doctor), so none falls back to a guess."""
    found = read(repo).land
    if found is None:
        raise NoLandError(NO_LAND)
    return found
