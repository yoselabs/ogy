"""Service tokens are tested only in isolated fixture repositories and fake state directories."""

import os

import pytest

from ogy.verdict import RefusalError
from ogy.web.token import resolve_token


def test_token_rotates_by_default_and_stability_requires_explicit_opt_in(repo, monkeypatch):
    """Given restarts, the token rotates unless the owner explicitly asks to retain it."""
    monkeypatch.delenv("OGY_SERVE_STABLE_TOKEN", raising=False)
    first = resolve_token(repo)
    second = resolve_token(repo)
    assert first != second
    monkeypatch.setenv("OGY_SERVE_STABLE_TOKEN", "1")
    assert resolve_token(repo) == second
    assert (repo / ".git/ogy/server.token").stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("mode", [0o644, 0o666])
def test_loose_existing_token_is_refused_before_reuse(repo, monkeypatch, mode):
    """Given an exposed token, opting into stability cannot silently reuse it."""
    monkeypatch.setenv("OGY_SERVE_STABLE_TOKEN", "1")
    resolve_token(repo)
    (repo / ".git/ogy/server.token").chmod(mode)
    with pytest.raises(RefusalError, match="0600"):
        resolve_token(repo)


def test_nested_directory_uses_private_external_state_not_ancestor_git(repo, tmp_path_factory, monkeypatch):
    """Given a child folder of a Git repository, credentials live outside its worktree."""
    state = tmp_path_factory.mktemp("state")
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    nested = repo / "nested"
    nested.mkdir()
    resolve_token(nested)
    path = next(state.rglob("server.token"))
    assert path.is_relative_to(state) and not path.is_relative_to(repo)
    assert path != repo / ".git/ogy/server.token"
    assert path.parent.stat().st_mode & 0o777 == 0o700
    assert not (nested / ".ogy").exists()


def test_symlink_or_wrong_owner_token_is_refused(repo, monkeypatch):
    """Given an attacker-controlled credential file, the server refuses it before reading."""
    resolve_token(repo)
    path = repo / ".git/ogy/server.token"
    target = path.with_name("other")
    path.replace(target)
    path.symlink_to(target)
    with pytest.raises(RefusalError, match="private regular"):
        resolve_token(repo)
    path.unlink()
    target.replace(path)
    monkeypatch.setattr(os, "getuid", lambda: path.stat().st_uid + 1)
    with pytest.raises(RefusalError, match="owned"):
        resolve_token(repo)


def test_existing_git_metadata_can_hold_the_private_token(repo):
    """Given review history already created ogy's metadata, starting the server preserves that directory."""
    folder = repo / ".git/ogy"
    folder.mkdir(mode=0o755)
    assert resolve_token(repo)
    assert folder.stat().st_mode & 0o777 == 0o755
    assert (folder / "server.token").stat().st_mode & 0o777 == 0o600
