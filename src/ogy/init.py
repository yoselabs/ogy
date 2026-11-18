"""`ogy init`: make a repository ready for ogy. Every step is idempotent and merges; nothing is clobbered.

Writes `ogy.yml`, the knowledge-base folder with its constitution folder and the area `shared` of the first layer, a marked
block in AGENTS.md (and CLAUDE.md when it exists), the ogy server in `.mcp.json` and Claude Code deny rules for editing the
folder by hand."""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import any_yaml
from atomic_io import atomic_write_text
from git_porcelain import RealRepo, config_get, git_dir
from managed_region import replace_region

from ogy import config
from ogy.kinds import SHARED_AREA
from ogy.layout import SHARED_SAYS
from ogy.ontology import packaged
from ogy.source import KB_DIR
from ogy.verdict import Refusal

START, END = "<!-- BEGIN OGY -->", "<!-- END OGY -->"
CONSTITUTION_FILE = "constitution/principles.yml"
SHARED_FILE = f"product/{SHARED_AREA}/area.yml"  # the shared area of the first layer, with its own entry
STARTS = {CONSTITUTION_FILE: "[]\n", SHARED_FILE: any_yaml.dump({"says": SHARED_SAYS})}  # what a new knowledge base starts with
HOOKS_DIR = ".githooks"
HOOK = """\
#!/bin/sh
# Written by `ogy init`: check the knowledge base as staged for this commit.
git diff --cached --quiet -- docs/kb && exit 0
tree=$(git write-tree) || exit 1
parent=$(git rev-parse -q --verify HEAD)
commit=$(git commit-tree "$tree" ${{parent:+-p $parent}} -m staged) || exit 1
exec {ogy} --rev "$commit" check
"""
SERVER = {"command": "uvx", "args": ["--from", "git+https://github.com/yoselabs/ogy", "ogy", "mcp"]}
CHECKOUT = ["run", "--frozen", "--no-sync", "python", "-I", "-m", "ogy"]  # ogy's own repository runs the code in front of it
PUBLISHED = "uvx --from git+https://github.com/yoselabs/ogy ogy"
BLOCK = """\
## Knowledge base (ogy)

The requirements knowledge base is the folder `docs/kb/`: `constitution/`, `product/<area>/` and `software/<area>/`, nothing else
at its top. Each layer has the area `shared` (`product/shared/`): only the terms, actors and sets that two of its areas use live
there; everything else lives in the area that owns it. Change it only through ogy (CLI or MCP); never edit its YAML by hand.
- Run `{ogy} glossary` first, before reading code or writing a sentence: it prints the constitution (the principles every decision is
  judged against; cite one with `because`), then the glossary: the shared terms, then each area's (`<layer>/<area>/glossary.yml`);
  `{ogy} glossary <layer>/<area>` prints one area's terms with the shared ones it reads. Read both; use the words it prints. A term
  is `word`, `says` (one line of under 15 words) and `avoid`, nothing else; it needs no source. A word one area uses goes in that
  area's glossary, one that two areas use in the `shared` area of their layer. `{ogy} status` shows where things
  stand; `{ogy} find <words>` searches live and removed entries (search before you propose); `{ogy} show <address>` reads one.
- Before you create an entry of a kind, read `{ogy} kinds <kind>`: what it is, its guidance (when to use it rather than its
  neighbours: an actor, a lifecycle state or an attribute; `by` holds an entry to a rule, `because` cites a principle or a decision
  as the reason) and its fields. `{ogy} kinds --map` prints the whole ontology on one screen, with its rules.
- Add and change entries with ONE command, `{ogy} put`: one or many records, JSON or YAML, as arguments, `--file` or standard input
  (`{ogy} put '[{{"address": "<layer>/<area>/<kind>/<id>", "says": "..."}}]'`). An address that exists is changed (`"field": null` removes a
  field), a new one is added; the whole call is checked together (a decision may come with the entries its options set) and written whole
  or not at all. A choice goes in with `{ogy} answer`, a reply to a review round with `{ogy} reply "<grammar line>"`;
  `{ogy} remove --why` always says why (a decision address, or plain words); remove only when a requirement changes,
  never to reorganise. To change an entry's area use `{ogy} move <address> <area>` (`<layer>/<area>` to change the layer too): the id
  and the owner's agreements stay, every address follows in the same write, and nothing is recorded (Git keeps it); never remove
  and put again.
- A newer ogy may rename or drop a field of a kind, or move a kind out of a fixed folder (the kind file says `renamed: {{old: new}}`,
  `dropped: [...]` or `moved_from: <folder>/<file>`); `{ogy} check` then reports `needs-migration`. Run `{ogy} migrate`, never a hand
  edit: it renames and moves in one write and keeps the owner's agreements and the built lines current; a dropped field that held a
  value is printed, and that entry comes back to the owner as changed. What it moved lands in `product/shared`: `{ogy} move` each
  entry to the area that uses it.
- Reads see the worktree by default (`--rev .`); CI reads a commit with `{ogy} --rev HEAD check`. The flags `--repo --rev --ontology`
  go before or after the command: `{ogy} show <address> --rev HEAD`.
- Every write is checked; fix what it refuses. Run `{ogy} check` before you hand over: every finding is an error, there are no
  warnings. Exit codes: 0 ok, 1 findings, 2 usage, 3 refused, 4 not found.
- Every area folder holds its `area.yml` (`says`: what the area covers; `distinct`: what belongs in a neighbouring area); a put
  into a new area brings it in the same call. The first actor is the person:
  `{ogy} put '[{{"address": "product/<area>/area/<area>", "says": "..."}}, {{"address": "product/<area>/actor/human", "says": "...",
  "nature": "human"}}]'`
  (an actor needs no evidence).
- ogy stores no messages and no quotes. When the owner speaks, record the answer at once with a short paraphrase:
  `{ogy} answer <decision> <option> --said "<one plain line>" --where ai:<agent>/<session-id>` (`--note` for a hedge or condition), or
  `{ogy} reply "<grammar line>" --said "..." --where ...` for a review round (`from: human`: only a person agrees). Show each
  paraphrase to the owner in the read-back. A guess that rests on what the owner said carries a paraphrase (`guess.heard: {{said}}`),
  so the review reads "You said (paraphrased): .... Read as B." and one yes records the answer.
- Never answer for the owner. Only when the owner said "decide on my behalf" for a scope (an answer `from: human` of a decision),
  answer with `{ogy} answer ... --from ai --delegated <that decision>`; `{ogy} dropped` lists those answers, and you list them to the
  owner at session end."""


class InitRefused(Refusal):
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
        raise InitRefused(f"{config.CONFIG_FILE} already says ontology: {held}, not {ontology}")
    return ontology or held or "software"


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


def _block(repo: Path, rel: str, written: list[str]) -> None:
    path = repo / rel
    body = path.read_text() if path.exists() else ""
    _put(repo, rel, replace_region(body, BLOCK.format(ogy=invocation(repo)), start_marker=START, end_marker=END), written)


def _hook(repo: Path, written: list[str]) -> None:
    """The tracked pre-commit hook that runs `ogy check` on the staged tree, and `core.hooksPath` pointing at it."""
    rel = f"{HOOKS_DIR}/pre-commit"
    text = HOOK.format(ogy=invocation(repo))
    path = repo / rel
    if not path.exists() or path.read_text() != text:
        atomic_write_text(path, text)
        written.append(rel)
    path.chmod(0o755)
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
        raise InitRefused(f"{rel} is not JSON ({error}); fix it and run again") from error
    if not isinstance(data, dict):
        raise InitRefused(f"{rel} is not a JSON object")
    return data


def _dump(data: dict[str, object]) -> str:
    return json.dumps(data, indent=2) + "\n"


def _mapping(data: dict[str, object], key: str, rel: str) -> dict[str, object]:
    found = data.setdefault(key, {})
    if not isinstance(found, dict):
        raise InitRefused(f"{rel}: {key} is not an object")
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
        raise InitRefused(f"{rel}: permissions.deny is not a list")
    wide = f"/{KB_DIR}/**"
    folder = f"/{KB_DIR}/**/*.yml"  # the YAML only: a README beside it is for people to edit
    deny[:] = [rule for rule in deny if rule not in (f"Edit({wide})", f"Write({wide})")]  # what an earlier init wrote
    deny.extend(rule for rule in (f"Edit({folder})", f"Write({folder})") if rule not in deny)
    _put(repo, rel, _dump(data), written)


def init(repo: Path, ontology: str | None = None) -> Initialised:
    """Set `repo` up; run again to repair it. Refuses (InitRefused, OntologyError) before writing when it cannot go on."""
    name = _settings(repo, ontology)
    packaged(name)
    written: list[str] = []
    for rel in (".mcp.json", ".claude/settings.json"):
        _json(repo, rel)  # an unreadable file refuses before anything is written
    if not (repo / config.CONFIG_FILE).exists():
        _put(repo, config.CONFIG_FILE, any_yaml.dump({"ontology": name}), written)
    for rel, text in STARTS.items():
        if not (repo / KB_DIR / rel).exists():
            atomic_write_text(repo / KB_DIR / rel, text)
            written.append(f"{KB_DIR}/{rel}")
    _block(repo, "AGENTS.md", written)
    if (repo / "CLAUDE.md").exists():
        _block(repo, "CLAUDE.md", written)
    _mcp(repo, written)
    _deny(repo, written)
    _hook(repo, written)
    return Initialised(name, KB_DIR, written)


def doctor(repo: Path) -> list[str]:
    """`init --check`: what is not set up in this repository, one line each, and how to mend it; empty when it is all in place.
    Writes nothing and refuses nothing: a file it cannot read is a line too."""
    lines: list[str] = []
    if not (repo / config.CONFIG_FILE).is_file():
        lines.append(f"missing {config.CONFIG_FILE}: run `ogy init`")
    lines.extend(f"missing {KB_DIR}/{rel}: run `ogy init`" for rel in STARTS if not (repo / KB_DIR / rel).is_file())
    for rel in ("AGENTS.md", "CLAUDE.md"):
        path = repo / rel
        if rel == "AGENTS.md" or path.exists():
            have = path.read_text() if path.exists() else ""
            if replace_region(have, BLOCK.format(ogy=invocation(repo)), start_marker=START, end_marker=END) != have:
                lines.append(f"{rel} has no current ogy block: run `ogy init`")
    if not (repo / HOOKS_DIR / "pre-commit").is_file():
        lines.append(f"missing {HOOKS_DIR}/pre-commit (checks the knowledge base on commit): run `ogy init`")
    elif git_dir(repo) is not None and config_get(repo, "core.hooksPath") != HOOKS_DIR:
        lines.append(f"git does not use {HOOKS_DIR}: run `ogy init`")
    try:
        server = _mapping(_json(repo, ".mcp.json"), "mcpServers", ".mcp.json").get("ogy")
        deny = _mapping(_json(repo, ".claude/settings.json"), "permissions", ".claude/settings.json").get("deny")
    except InitRefused as error:
        return [*lines, str(error)]
    if server is None:
        lines.append(".mcp.json has no ogy server: run `ogy init`")
    elif is_ogy_repo(repo) and server != _server(repo):
        lines.append(".mcp.json runs the published ogy, not this checkout: delete its ogy entry and run `ogy init`")
    rules = [f"Edit(/{KB_DIR}/**/*.yml)", f"Write(/{KB_DIR}/**/*.yml)"]
    if not isinstance(deny, list) or any(rule not in deny for rule in rules):
        lines.append(f".claude/settings.json does not deny editing {KB_DIR}/**/*.yml: run `ogy init`")
    return lines
