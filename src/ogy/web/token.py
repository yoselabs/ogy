"""The repository's stable service token location and private file permissions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from asgi_token_gate import stable_token
from git_porcelain import git_dir

if TYPE_CHECKING:
    from pathlib import Path


def resolve_token(repo: Path) -> str:
    folder = git_dir(repo)
    path = (folder / "ogy" if folder is not None else repo / ".ogy") / "server.token"
    token = stable_token(path)
    path.chmod(0o600)
    return token
