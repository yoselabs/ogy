"""`ogy init`: make a repository ready for ogy. Every step is idempotent and merges; nothing is clobbered.

Writes `ogy.yml` (the ontology, and the land branch: `--land`, else the remote's default branch; with neither it refuses), the
knowledge-base folder with the (empty) lists of its fixed folders and the entry of the shared area of the first layer, the
ontology's agents block (its `agents.md`) as a marked block in AGENTS.md (and CLAUDE.md when it exists), the ogy server in
`.mcp.json` and Claude Code deny rules for editing the folder by hand, and the entries the ontology starts with (its
`starts.yml`), unless removed. Every name in them comes from the ontology folder."""

import json
import shutil
from dataclasses import dataclass
lazy from pathlib import Path

import any_yaml
from atomic_io import atomic_write_text
from git_porcelain import RealRepo, config_get, git_dir, symbolic_ref
from managed_region import replace_region

from ogy import config, removed
from ogy.edit import Editor
from ogy.kinds import Shape
from ogy.model import Address, parse_address
from ogy.ontology import DEFAULT_ONTOLOGY, Ontology, named
from ogy.source import KB_DIR
from ogy.verdict import RefusalError

START, END = "<!-- BEGIN OGY -->", "<!-- END OGY -->"
HOOKS_DIR = ".githooks"
HOOK = """\
#!/bin/sh
# Written by `ogy init`: `ogy hook` checks the commit this hook guards, with the landing checks on a land.
exec {ogy} hook {name} "$@"
"""
HOOKS = ("pre-commit", "pre-push")
SERVER = {"command": "uvx", "args": ["--from", "git+https://github.com/yoselabs/ogy", "ogy", "mcp"]}
CHECKOUT = ["run", "--frozen", "--no-sync", "python", "-I", "-m", "ogy"]  # ogy's own repository runs the code in front of it
PUBLISHED = "uvx --from git+https://github.com/yoselabs/ogy ogy"


class InitRefusedError(RefusalError):
    """A file ogy would change cannot be read, or the flags contradict `ogy.yml`."""

    prefix = "not set up: "


@dataclass(frozen=True)
class Initialised:
    ontology: str
    kb: str
    written: list[str]  # the files created or changed, relative to the repository


def _settings(repo: Path, ontology: str | None) -> str:
    held = config.read(repo).ontology
    if ontology is not None and held is not None and ontology != held:
        msg = f"{config.CONFIG_FILE} already says ontology: {held}, not {ontology}"
        raise InitRefusedError(msg)
    return ontology or held or DEFAULT_ONTOLOGY


NO_REMOTE_LAND = (
    "no remote names its default branch, so the land branch is not guessed: run `ogy init --land <branch>` "
    "(or `git remote set-head origin --auto`, then `ogy init`)"
)


def _land(repo: Path, given: str | None) -> str | None:
    """The land branch `ogy.yml` keeps: the one it names, else `--land`, else the remote's default branch (`origin/HEAD`); None
    outside a Git repository. Refuses (InitRefusedError) a `--land` that contradicts `ogy.yml` and a repository whose remote names
    no default branch: the branch checked out may be a feature branch, so it is never taken."""
    try:
        held: str | None = config.land(repo)
    except config.NoLandError:
        held = None
    if given is not None and held is not None and given != held:
        msg = f"{config.CONFIG_FILE} already says land: {held}, not {given}"
        raise InitRefusedError(msg)
    if held is not None or given is not None or git_dir(repo) is None:
        return held or given
    remote = symbolic_ref(repo, "refs/remotes/origin/HEAD")
    if remote is None:
        raise InitRefusedError(NO_REMOTE_LAND)
    return remote.removeprefix("refs/remotes/origin/")


def _config(repo: Path, name: str, land: str | None, written: list[str]) -> None:
    """`ogy.yml` with the ontology when there is no file, and the land branch when it names none; every other key is kept."""
    held = config.read(repo)
    kept = {key: value for key in config.KEYS if (value := getattr(held, key)) is not None}
    data = dict(kept) if (repo / config.CONFIG_FILE).exists() else {"ontology": name}
    if land is not None:
        data["land"] = land
    if data != kept or not (repo / config.CONFIG_FILE).exists():
        _put(repo, config.CONFIG_FILE, any_yaml.dump(data), written)


def starts(ontology: Ontology) -> dict[str, str]:
    """The files a new knowledge base starts with: each fixed folder's list, empty, and the entry of the shared area of the
    first layer."""
    found = {f"{kind.area}/{kind.file}": "[]\n" for kind in ontology.kinds.values() if kind.area and kind.shape is Shape.LIST}
    area = ontology.area_kind()
    if area is not None and ontology.layers:
        found[f"{ontology.layers[0]}/{ontology.shared}/{area.file}"] = any_yaml.dump(ontology.shared_fields())
    return found


def _put(repo: Path, rel: str, text: str, written: list[str]) -> None:
    path = repo / rel
    if not path.exists() or path.read_text() != text:
        atomic_write_text(path, text)
        written.append(rel)


def is_ogy_repo(repo: Path) -> bool:
    """ogy's own repository: its commands run the checkout, never a published copy."""
    return (repo / "src/ogy/__main__.py").is_file()


def invocation(repo: Path) -> str:
    """How a person or an agent runs ogy in this repository: `just ogy` in ogy's own, `ogy` when it is on PATH, else through uvx."""
    if is_ogy_repo(repo):
        return "just ogy"
    return "ogy" if shutil.which("ogy") else PUBLISHED


def _server(repo: Path) -> dict[str, object]:
    return {"command": "uv", "args": [*CHECKOUT, "mcp"]} if is_ogy_repo(repo) else dict(SERVER)


def block(repo: Path, ontology: Ontology, body: str) -> str:
    """`body` with the ontology's agents block (its `agents.md`) in the marked region; unchanged when the ontology has none."""
    if ontology.agents is None:
        return body
    return replace_region(body, ontology.agents.format(ogy=invocation(repo)), start_marker=START, end_marker=END)


def _block(repo: Path, ontology: Ontology, rel: str, written: list[str]) -> None:
    path = repo / rel
    _put(repo, rel, block(repo, ontology, path.read_text() if path.exists() else ""), written)


def _hook(repo: Path, written: list[str]) -> None:
    """The tracked hooks that run `ogy hook` (`ogy.hooks`), and `core.hooksPath` pointing at them."""
    for name in HOOKS:
        rel = f"{HOOKS_DIR}/{name}"
        _put(repo, rel, HOOK.format(ogy=invocation(repo), name=name), written)
        (repo / rel).chmod(0o755)
    if git_dir(repo) is not None and config_get(repo, "core.hooksPath") != HOOKS_DIR:
        RealRepo(repo).run(repo, "config", "core.hooksPath", HOOKS_DIR)
        written.append("git config core.hooksPath")


def _json(repo: Path, rel: str) -> dict[str, object]:
    path = repo / rel
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        msg = f"{rel} is not JSON ({error}); fix it and run again"
        raise InitRefusedError(msg) from error
    if not isinstance(data, dict):
        msg = f"{rel} is not a JSON object"
        raise InitRefusedError(msg)
    return data


def _dump(data: dict[str, object]) -> str:
    return json.dumps(data, indent=2) + "\n"


def _mapping(data: dict[str, object], key: str, rel: str) -> dict[str, object]:
    found = data.setdefault(key, {})
    if not isinstance(found, dict):
        msg = f"{rel}: {key} is not an object"
        raise InitRefusedError(msg)
    return found


def _mcp(repo: Path, written: list[str]) -> None:
    data = _json(repo, ".mcp.json")
    servers = _mapping(data, "mcpServers", ".mcp.json")
    if servers.get("ogy") in (None, SERVER):  # an entry the person wrote is theirs; the published default is not
        servers["ogy"] = _server(repo)
    _put(repo, ".mcp.json", _dump(data), written)


def _deny(repo: Path, written: list[str]) -> None:
    rel = ".claude/settings.json"
    data = _json(repo, rel)
    deny = _mapping(data, "permissions", rel).setdefault("deny", [])
    if not isinstance(deny, list):
        msg = f"{rel}: permissions.deny is not a list"
        raise InitRefusedError(msg)
    wide = f"/{KB_DIR}/**"
    folder = f"/{KB_DIR}/**/*.yml"  # the YAML only: a README beside it is for people to edit
    deny[:] = [rule for rule in deny if rule not in (f"Edit({wide})", f"Write({wide})")]  # what an earlier init wrote
    deny.extend(rule for rule in (f"Edit({folder})", f"Write({folder})") if rule not in deny)
    _put(repo, rel, _dump(data), written)


def init(repo: Path, ontology: str | None = None, land: str | None = None) -> Initialised:
    """Set `repo` up; run again to repair it. Refuses (InitRefusedError, OntologyError) before writing when it cannot go on."""
    name = _settings(repo, ontology)
    landing = _land(repo, land)
    kinds = named(name, repo)
    written: list[str] = []
    for rel in (".mcp.json", ".claude/settings.json"):
        _json(repo, rel)  # an unreadable file refuses before anything is written
    _config(repo, name, landing, written)
    for rel, text in starts(kinds).items():
        if not (repo / KB_DIR / rel).exists():
            atomic_write_text(repo / KB_DIR / rel, text)
            written.append(f"{KB_DIR}/{rel}")
    for address, fields in missing_starts(repo, kinds):
        Editor(repo, KB_DIR, kinds).put(address, fields)
        written.append(str(address))
    _block(repo, kinds, "AGENTS.md", written)
    if (repo / "CLAUDE.md").exists():
        _block(repo, kinds, "CLAUDE.md", written)
    _mcp(repo, written)
    _deny(repo, written)
    _hook(repo, written)
    return Initialised(name, KB_DIR, written)


def missing_starts(repo: Path, ontology: Ontology) -> list[tuple[Address, dict[str, object]]]:
    """The entries the ontology starts a knowledge base with (its `starts.yml`) that are not there and were never removed:
    init adds them, unagreed; an entry the owner removed is never added again."""
    snapshot = Editor(repo, KB_DIR, ontology).snapshot()
    ledgers, _ = removed.read_all(repo / KB_DIR)
    gone = {item.id for ledger in ledgers.values() for item in ledger.items}
    found: list[tuple[Address, dict[str, object]]] = []
    for record in ontology.starts:
        address = parse_address(str(record.get("address", "")), ontology)
        if address is not None and address not in snapshot.entries and str(address) not in gone:
            found.append((address, {key: value for key, value in record.items() if key != "address"}))
    return found


def doctor(repo: Path) -> list[str]:
    """`init --check`: what is not set up in this repository, one line each, and how to mend it; empty when it is all in place.
    Writes nothing and refuses nothing: a file it cannot read is a line too."""
    lines: list[str] = []
    if not (repo / config.CONFIG_FILE).is_file():
        lines.append(f"missing {config.CONFIG_FILE}: run `ogy init`")
    elif git_dir(repo) is not None:
        try:
            config.land(repo)
        except config.NoLandError as error:
            lines.append(str(error))
    ontology = named(config.read(repo).ontology or DEFAULT_ONTOLOGY, repo)
    lines.extend(f"missing {KB_DIR}/{rel}: run `ogy init`" for rel in starts(ontology) if not (repo / KB_DIR / rel).is_file())
    lines.extend(f"missing {address}: run `ogy init`" for address, _ in missing_starts(repo, ontology))
    for rel in ("AGENTS.md", "CLAUDE.md"):
        path = repo / rel
        if rel == "AGENTS.md" or path.exists():
            have = path.read_text() if path.exists() else ""
            if block(repo, ontology, have) != have:
                lines.append(f"{rel} has no current ogy block: run `ogy init`")
    lines.extend(
        f"missing {HOOKS_DIR}/{name} (runs `ogy hook {name}`): run `ogy init`" for name in HOOKS if not (repo / HOOKS_DIR / name).is_file()
    )
    if (
        all((repo / HOOKS_DIR / name).is_file() for name in HOOKS)
        and git_dir(repo) is not None
        and config_get(repo, "core.hooksPath") != HOOKS_DIR
    ):
        lines.append(f"git does not use {HOOKS_DIR}: run `ogy init`")
    try:
        server = _mapping(_json(repo, ".mcp.json"), "mcpServers", ".mcp.json").get("ogy")
        deny = _mapping(_json(repo, ".claude/settings.json"), "permissions", ".claude/settings.json").get("deny")
    except InitRefusedError as error:
        return [*lines, str(error)]
    if server is None:
        lines.append(".mcp.json has no ogy server: run `ogy init`")
    elif is_ogy_repo(repo) and server != _server(repo):
        lines.append(".mcp.json runs the published ogy, not this checkout: delete its ogy entry and run `ogy init`")
    rules = [f"Edit(/{KB_DIR}/**/*.yml)", f"Write(/{KB_DIR}/**/*.yml)"]
    if not isinstance(deny, list) or any(rule not in deny for rule in rules):
        lines.append(f".claude/settings.json does not deny editing {KB_DIR}/**/*.yml: run `ogy init`")
    return lines
