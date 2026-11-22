"""Private service credentials: fresh by default, stable only by explicit environment opt-in."""

from __future__ import annotations

import os
import secrets
import stat
from pathlib import Path

from content_digest import digest_text
from git_porcelain import RealRepo, git_dir

from ogy.verdict import RefusalError


def token_path(repo: Path) -> Path:
    """Use this repository's Git metadata, never an ancestor's or the worktree itself."""
    repo = repo.resolve()
    folder = git_dir(repo)
    if folder is not None and (repo / ".git").exists():
        return folder / "ogy/server.token"
    state = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    worktree = repo
    if folder is not None:
        found = RealRepo(repo, ambient=os.environ).try_run(repo, "rev-parse", "--show-toplevel")
        if found.rc == 0:
            worktree = Path(found.out.strip()).resolve()
    if not state.is_absolute() or state.resolve().is_relative_to(worktree):
        message = "XDG_STATE_HOME must be absolute and outside the served worktree"
        raise RefusalError(message)
    return state / "ogy" / digest_text(str(repo), length=64) / "server.token"


def _private(info: os.stat_result, mode: int, *, directory: bool = False) -> bool:
    shape = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    return shape and info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == mode


def resolve_token(repo: Path) -> str:
    """Publish a fresh 0600 header token, or reuse it with OGY_SERVE_STABLE_TOKEN=1."""
    path = token_path(repo)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.parent.lstat()
    mode = stat.S_IMODE(info.st_mode)
    # Existing review metadata may be readable; only external state needs an exactly 0700 directory.
    expected = mode if (repo.resolve() / ".git").exists() and not mode & 0o022 else 0o700
    if not _private(info, expected, directory=True):
        message = "service token directory must be owned by this user and private (external state needs mode 0700)"
        raise RefusalError(message)
    previous = None
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        pass
    except OSError as error:
        message = "service token must be a private regular file"
        raise RefusalError(message) from error
    else:
        try:
            with os.fdopen(fd, encoding="ascii") as stream:
                if not _private(os.fstat(stream.fileno()), 0o600):
                    message = "service token must be owned by this user with mode 0600"
                    raise RefusalError(message)
                previous = stream.read(257).strip()
        except UnicodeDecodeError as error:
            message = "invalid service token encoding"
            raise RefusalError(message) from error
        if not previous or len(previous) > 256 or not previous.isascii():
            message = "invalid service token"
            raise RefusalError(message)
    if previous is not None and os.environ.get("OGY_SERVE_STABLE_TOKEN") == "1":
        return previous
    token = secrets.token_urlsafe(32)
    temporary = path.with_name(f".server-{secrets.token_hex(12)}")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="ascii") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(token + "\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return token
