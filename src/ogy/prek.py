"""A repository's prek config (`.pre-commit-config.yaml`). When there is one, prek owns the Git hooks: `ogy init` merges one
pre-commit entry that runs `ogy hook pre-commit` into it and leaves `core.hooksPath` alone (the decision
software/setup/decision/init-hook-owner). The pre-push check stays in the repository's own gate entry, because a gate kit may
allow no other pre-push hook beside it, so init adds none and the doctor asks for none."""

lazy from pathlib import Path

import any_yaml

CONFIGS = (".pre-commit-config.yaml", ".pre-commit-config.yml")
RUNS = "ogy hook pre-commit"


class PrekConfigError(ValueError):
    """The prek config is not YAML, or not of the shape prek reads (a mapping whose `repos` is a block list)."""


def config_file(repo: Path) -> str | None:
    """The prek config of `repo`, relative to it; None when it has none."""
    return next((rel for rel in CONFIGS if (repo / rel).exists()), None)


def runs_ogy(rel: str, text: str) -> bool:
    """Whether a hook in the config runs `ogy hook pre-commit` (ogy's own runs it as `just ogy hook pre-commit`)."""
    try:
        data = any_yaml.load(text)
    except any_yaml.YAMLError as error:
        msg = f"{rel} is not YAML ({error}); fix it and run again"
        raise PrekConfigError(msg) from error
    repos = data.get("repos") if isinstance(data, dict) else None
    if not isinstance(repos, list):
        msg = f"{rel}: repos is not a list"
        raise PrekConfigError(msg)
    hooks = [hook for repo in repos if isinstance(repo, dict) for hook in repo.get("hooks") or [] if isinstance(hook, dict)]
    return any(RUNS in str(hook.get("entry", "")) for hook in hooks)


def merged(rel: str, text: str, ogy: str) -> str:
    """`text` with a local pre-commit hook that runs `<ogy> hook pre-commit` added as the last repo; unchanged when one runs it.
    Comments and order are kept. Raises PrekConfigError on a config prek could not read."""
    if runs_ogy(rel, text):
        return text
    hook = {
        "id": "ogy",
        "name": "ogy check",
        "entry": f"{ogy} hook pre-commit",
        "language": "system",
        "always_run": True,
        "pass_filenames": False,
        "stages": ["pre-commit"],
    }
    try:
        return any_yaml.append_item(text, "repos", {"repo": "local", "hooks": [hook]})
    except (TypeError, ValueError) as error:
        msg = f"{rel}: repos is not a block list ({error})"
        raise PrekConfigError(msg) from error
