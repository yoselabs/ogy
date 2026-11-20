"""`ogy init` and `ogy.yml`: set-up that is idempotent and never clobbers, and settings read as flag defaults."""

import json
import os
import shlex
lazy from pathlib import Path

import pytest
from git_porcelain import run_git
from tests.conftest import GOOD, commit, ogy

from ogy import cli, config, init

AGENTS = "# Rules\n\nKeep it short.\n"


def read(repo: Path, rel: str) -> str:
    return (repo / rel).read_text()


def test_init_sets_everything_up(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(AGENTS)
    code, lines = cli.run(["--repo", str(tmp_path), "init"])
    assert code == cli.OK and lines[0] == "ogy is set up for the software ontology in docs/kb/"
    assert read(tmp_path, "ogy.yml") == "ontology: software\n"
    assert (tmp_path / "docs/kb/product/shared/area.yml").is_file()
    assert "rigid-where-checked" in read(tmp_path, "docs/kb/constitution/principles.yml")
    agents = read(tmp_path, "AGENTS.md")
    assert agents.startswith(AGENTS.rstrip()) and "<!-- BEGIN OGY -->" in agents and "ogy glossary" in agents
    assert "prints the constitution" in agents
    assert not (tmp_path / "CLAUDE.md").exists()
    assert json.loads(read(tmp_path, ".mcp.json"))["mcpServers"]["ogy"]["args"][-2:] == ["ogy", "mcp"]
    assert json.loads(read(tmp_path, ".claude/settings.json"))["permissions"]["deny"] == [
        "Edit(/docs/kb/**/*.yml)",
        "Write(/docs/kb/**/*.yml)",
    ]
    waiting = (cli.OK, ["ok", "waiting for you: 1 (ogy review)"])  # the starters wait for the owner
    assert cli.run(["--repo", str(tmp_path), "--rev", ".", "check"]) == waiting


def test_init_is_idempotent_and_keeps_the_rest(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text(AGENTS)
    (tmp_path / ".mcp.json").write_text(json.dumps({"mcpServers": {"other": {"command": "x"}}}))
    (tmp_path / ".claude").mkdir()
    existing = {"permissions": {"deny": ["Read(.env)"], "allow": ["Bash(ls)"]}, "model": "m"}
    (tmp_path / ".claude/settings.json").write_text(json.dumps(existing))
    cli.run(["--repo", str(tmp_path), "init"])
    first = {p.relative_to(tmp_path).as_posix(): p.read_text() for p in sorted(tmp_path.rglob("*")) if p.is_file()}
    code, lines = cli.run(["--repo", str(tmp_path), "init"])
    again = {p.relative_to(tmp_path).as_posix(): p.read_text() for p in sorted(tmp_path.rglob("*")) if p.is_file()}
    assert code == cli.OK and again == first and not [line for line in lines if line.startswith("wrote")]
    assert read(tmp_path, "CLAUDE.md").count("BEGIN OGY") == 1 and "Keep it short." in read(tmp_path, "CLAUDE.md")
    assert set(json.loads(read(tmp_path, ".mcp.json"))["mcpServers"]) == {"other", "ogy"}
    settings = json.loads(read(tmp_path, ".claude/settings.json"))
    assert settings["permissions"]["deny"] == ["Read(.env)", "Edit(/docs/kb/**/*.yml)", "Write(/docs/kb/**/*.yml)"]
    assert settings["permissions"]["allow"] == ["Bash(ls)"]
    assert settings["model"] == "m"


def test_the_folder_is_always_docs_kb_and_nothing_moves_it(tmp_path: Path) -> None:
    code, _ = cli.run(["--repo", str(tmp_path), "init", "--ontology", "software"])
    assert code == cli.OK and read(tmp_path, "ogy.yml") == "ontology: software\n"
    assert (tmp_path / "docs/kb/product/shared/area.yml").is_file() and "Edit(/docs/kb/**/*.yml)" in read(tmp_path, ".claude/settings.json")
    agents = read(tmp_path, "AGENTS.md")
    assert "`docs/kb/`: `constitution/`, `product/<area>/` and `software/<area>/`, nothing else\nat its top." in agents
    assert "Each layer has the area `shared`" in agents
    with pytest.raises(SystemExit):  # there is no --kb flag
        cli.run(["--repo", str(tmp_path), "init", "--kb", "other"])
    (tmp_path / "ogy.yml").write_text("ontology: software\nkb: other\n")  # and no `kb:` setting
    code, lines = ogy(tmp_path, "check")
    assert code == cli.USAGE and "unknown setting kb" in lines[0]


def test_init_refuses_an_unreadable_file_and_an_unknown_ontology(tmp_path: Path) -> None:
    (tmp_path / ".mcp.json").write_text("{not json")
    code, lines = cli.run(["--repo", str(tmp_path), "init"])
    assert code == cli.REFUSED and "not JSON" in lines[0] and not (tmp_path / "ogy.yml").exists()
    (tmp_path / ".mcp.json").unlink()
    assert cli.run(["--repo", str(tmp_path), "init", "--ontology", "nothing"])[0] == cli.USAGE
    assert not (tmp_path / "ogy.yml").exists()


def test_ogy_yml_gives_the_defaults_and_flags_override_it(tmp_path: Path) -> None:
    for rel, text in GOOD.items():
        (tmp_path / "docs/kb" / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs/kb" / rel).write_text(text)
    (tmp_path / "ogy.yml").write_text("ontology: software\nrev: .\n")
    assert ogy(tmp_path, "check") == (cli.OK, ["ok"])
    assert ogy(tmp_path / "elsewhere", "check")[0] == cli.REFUSED  # no such folder is no green check
    assert ogy(tmp_path, "show", "product/app/actor/member")[0] == cli.OK
    assert ogy(tmp_path, "--ontology", "nothing", "check")[0] == cli.USAGE


@pytest.mark.parametrize("text", ["- a\n", "kb: [x]\n", "kb: docs/kb\n", "colour: red\n", "ontology: [\n"])
def test_a_bad_ogy_yml_is_a_usage_error(tmp_path: Path, text: str) -> None:
    (tmp_path / "ogy.yml").write_text(text)
    code, lines = ogy(tmp_path, "check")
    assert code == cli.USAGE and lines[0].startswith("bad settings")


def test_config_path_can_be_moved_by_the_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "ogy.yml").write_text("ontology: here\n")
    other = tmp_path / "other.yml"
    other.write_text("ontology: there\n")
    assert config.read(tmp_path).ontology == "here"
    monkeypatch.setenv(config.CONFIG_ENV, str(other))
    assert config.read(tmp_path).ontology == "there"


def test_the_commands_the_agents_block_names_parse_and_bootstrap_the_first_actor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ogy.init.shutil.which", lambda _: "/usr/bin/ogy")
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    assert cli.run(["--repo", str(tmp_path), "init", "--land", "main"])[0] == cli.OK
    block = read(tmp_path, "AGENTS.md")
    assert "ogy check --rev ." not in block  # a global flag after the command is `unrecognized arguments`
    flags = [snippet for snippet in block.split("`") if snippet.startswith(("ogy --rev ", "ogy check"))]
    assert flags, "the block names the flag form"
    parser = cli.parser()
    for snippet in flags:
        assert parser.parse_args(shlex.split(snippet)[1:] if "<" not in snippet else ["--rev", "HEAD", "show", "x"])
    actor = next(snippet for snippet in block.split("`") if snippet.startswith('ogy put \'[{"address": "product/'))
    argv = shlex.split(actor.replace("<area>", "owner-area").replace("...", "A person."))[1:]
    code, lines = cli.run(["--repo", str(tmp_path), *argv])  # an actor needs no evidence
    assert code == cli.OK and lines == ["added product/owner-area/area/owner-area", "added product/owner-area/actor/human"], lines
    answer = next(snippet for snippet in block.split("`") if snippet.startswith("ogy answer <decision>"))
    assert parser.parse_args(shlex.split(answer.replace("<decision>", "d").replace("<option>", "o").replace("<", "").replace(">", ""))[1:])
    assert cli.run(["--repo", str(tmp_path), "check"]) == (cli.OK, ["ok", "waiting for you: 1 (ogy review)"])


def test_init_denies_only_the_yaml_and_replaces_the_rule_an_earlier_init_wrote(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude/settings.json").write_text(
        json.dumps({"permissions": {"deny": ["Edit(/docs/kb/**)", "Write(/docs/kb/**)", "Read(.env)"]}})
    )
    cli.run(["--repo", str(tmp_path), "init"])
    deny = json.loads(read(tmp_path, ".claude/settings.json"))["permissions"]["deny"]
    assert deny == ["Read(.env)", "Edit(/docs/kb/**/*.yml)", "Write(/docs/kb/**/*.yml)"]  # docs/kb/README.md stays editable


def test_the_block_names_the_invocation_that_runs_here(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ogy.init.shutil.which", lambda _: None)
    cli.run(["--repo", str(tmp_path), "init"])
    assert "`uvx --from git+https://github.com/yoselabs/ogy ogy glossary`" in read(tmp_path, "AGENTS.md")
    monkeypatch.setattr("ogy.init.shutil.which", lambda _: "/usr/bin/ogy")
    cli.run(["--repo", str(tmp_path), "init"])
    assert "`ogy glossary`" in read(tmp_path, "AGENTS.md") and "uvx" not in read(tmp_path, "AGENTS.md")


def test_in_ogys_own_repository_the_block_and_the_server_run_the_checkout(tmp_path: Path) -> None:
    (tmp_path / "src/ogy").mkdir(parents=True)
    (tmp_path / "src/ogy/__main__.py").write_text("")
    (tmp_path / ".mcp.json").write_text(json.dumps({"mcpServers": {"ogy": init.SERVER}}))  # the published default of an older init
    cli.run(["--repo", str(tmp_path), "init"])
    assert "`just ogy glossary`" in read(tmp_path, "AGENTS.md")
    server = json.loads(read(tmp_path, ".mcp.json"))["mcpServers"]["ogy"]
    assert server["command"] == "uv" and server["args"][-3:] == ["-m", "ogy", "mcp"]
    (tmp_path / ".mcp.json").write_text(json.dumps({"mcpServers": {"ogy": {"command": "mine"}}}))
    cli.run(["--repo", str(tmp_path), "init"])
    assert json.loads(read(tmp_path, ".mcp.json"))["mcpServers"]["ogy"] == {"command": "mine"}  # the person's own entry is kept


def test_init_check_is_the_doctor_and_writes_nothing(tmp_path: Path) -> None:
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--check"])
    assert code == cli.FINDINGS and any("missing ogy.yml" in line for line in lines) and not (tmp_path / "ogy.yml").exists()
    cli.run(["--repo", str(tmp_path), "init"])
    assert cli.run(["--repo", str(tmp_path), "init", "--check"]) == (cli.OK, ["ogy is set up here"])
    (tmp_path / ".claude/settings.json").write_text("{}")
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--check"])
    assert code == cli.FINDINGS and lines == [".claude/settings.json does not deny editing docs/kb/**/*.yml: run `ogy init`"]
    (tmp_path / "src/ogy").mkdir(parents=True)
    (tmp_path / "src/ogy/__main__.py").write_text("")
    assert any("not this checkout" in line for line in cli.run(["--repo", str(tmp_path), "init", "--check"])[1])


def test_init_records_the_remotes_default_branch_as_land_on_a_feature_branch(tmp_path: Path) -> None:
    """Fable's second review, problem 4: the land branch is what `ogy init` wrote in `ogy.yml`, never a guess at `main`; on a
    feature branch it is the remote's default branch, not the branch checked out."""
    origin, here = tmp_path / "origin", tmp_path / "here"
    origin.mkdir()
    run_git(origin, "init", "-q", "-b", "trunk", ambient=os.environ)
    (origin / "README.md").write_text("A project.\n")
    commit(origin, "first")
    run_git(tmp_path, "clone", "-q", str(origin), str(here), ambient=os.environ)
    run_git(here, "switch", "-q", "-c", "feature", ambient=os.environ)
    (here / "ogy.yml").write_text("ontology: software\n")
    code, lines = cli.run(["--repo", str(here), "init"])
    assert code == cli.OK and "wrote ogy.yml" in lines, lines
    assert read(here, "ogy.yml") == "ontology: software\nland: trunk\n"
    assert cli.run(["--repo", str(here), "init", "--check"]) == (cli.OK, ["ogy is set up here"])
    run_git(here, "switch", "-q", "-c", "later", ambient=os.environ)
    assert not [line for line in cli.run(["--repo", str(here), "init"])[1] if line.startswith("wrote")]  # kept, not re-guessed
    (here / "ogy.yml").write_text("ontology: software\n")
    lines = cli.run(["--repo", str(here), "init", "--check"])[1]
    assert lines == ["ogy.yml names no land branch (`land:`): run `ogy init`"], lines


def test_init_with_no_remote_refuses_to_guess_the_land_branch_until_it_is_given(tmp_path: Path) -> None:
    run_git(tmp_path, "init", "-q", "-b", "feature", ambient=os.environ)
    code, lines = cli.run(["--repo", str(tmp_path), "init"])
    assert code == cli.REFUSED and any("--land <branch>" in line for line in lines), lines
    assert sorted(p.name for p in tmp_path.iterdir()) == [".git"]  # refused before writing anything
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "trunk"])
    assert code == cli.OK and read(tmp_path, "ogy.yml") == "ontology: software\nland: trunk\n", lines
    assert cli.run(["--repo", str(tmp_path), "init"])[0] == cli.OK  # held in ogy.yml now
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "main"])
    assert code == cli.REFUSED and lines == ["not set up: ogy.yml already says land: trunk, not main"], lines


def test_init_installs_the_hooks_that_run_ogy_hook(tmp_path: Path) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "main"])
    hook = tmp_path / ".githooks/pre-commit"
    assert code == cli.OK and ".githooks/pre-commit" in "".join(lines) and ".githooks/pre-push" in "".join(lines)
    assert hook.stat().st_mode & 0o111 and 'hook pre-commit "$@"' in hook.read_text()
    assert "diff --cached" not in hook.read_text()  # every commit: a code rename can break a `code:` source
    assert run_git(tmp_path, "config", "core.hooksPath", ambient=os.environ).strip() == ".githooks"
    assert not [line for line in cli.run(["--repo", str(tmp_path), "init"])[1] if line.startswith("wrote")]  # idempotent
    hook.unlink()
    assert any("pre-commit" in line for line in cli.run(["--repo", str(tmp_path), "init", "--check"])[1])


def test_init_starts_with_the_ontologys_entries_and_never_re_adds_a_removed_one(repo: Path) -> None:
    """Fable's review, problem 5: a starter removed before any commit held it (the base never had it) is still recorded, so
    `ogy init` does not add it again; the branch's check accepts the item though the base has no such entry."""
    run_git(repo, "checkout", "-q", "-b", "later", ambient=os.environ)
    assert cli.run(["--repo", str(repo), "init"])[0] == cli.OK
    actors = read(repo, "docs/kb/product/shared/actors.yml")
    assert "id: owner" in actors and "nature: human" in actors and "id: agent" in actors and "agreed" not in actors
    code, lines = cli.run(["--repo", str(repo), "--rev", ".", "remove", "product/shared/actor/agent", "--why", "No agents here"])
    assert code == cli.OK and "recorded in product/shared/removed.yml" in lines[0], lines
    assert cli.run(["--repo", str(repo), "init"])[0] == cli.OK
    assert "id: agent" not in read(repo, "docs/kb/product/shared/actors.yml")
    assert not any("actor/agent" in line for line in cli.run(["--repo", str(repo), "init", "--check"])[1])
    commit(repo, "init without the agent")
    assert ogy(repo, "--rev", ".", "check") == (cli.OK, ["ok", "waiting for you: 1 (ogy review)"])


def test_a_starter_removed_before_the_first_commit_is_recorded(tmp_path: Path) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    assert cli.run(["--repo", str(tmp_path), "init", "--land", "main"])[0] == cli.OK
    code, lines = cli.run(["--repo", str(tmp_path), "--rev", ".", "remove", "product/shared/actor/agent", "--why", "No agents here"])
    assert code == cli.OK and "recorded in product/shared/removed.yml" in lines[0], lines
    assert cli.run(["--repo", str(tmp_path), "init"])[0] == cli.OK
    assert "id: agent" not in read(tmp_path, "docs/kb/product/shared/actors.yml")
    assert cli.run(["--repo", str(tmp_path), "--rev", ".", "check"]) == (cli.OK, ["ok", "waiting for you: 1 (ogy review)"])


@pytest.mark.parametrize(
    ("rel", "text", "fault"),
    [
        (".mcp.json", '{"mcpServers": []}', ".mcp.json: mcpServers is not an object"),
        (".claude/settings.json", '{"permissions": []}', ".claude/settings.json: permissions is not an object"),
        (".claude/settings.json", '{"permissions": {"deny": {}}}', ".claude/settings.json: permissions.deny is not a list"),
    ],
)
def test_a_refusal_on_the_shape_of_a_file_writes_nothing(tmp_path: Path, rel: str, text: str, fault: str) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    (tmp_path / rel).parent.mkdir(exist_ok=True)
    (tmp_path / rel).write_text(text)
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "main"])
    assert code == cli.REFUSED and lines == [f"not set up: {fault}"], lines
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted({".git", rel.split("/", 1)[0]})  # no ogy.yml, AGENTS.md or docs/
    assert read(tmp_path, rel) == text
    assert run_git(tmp_path, "config", "--default", "", "core.hooksPath", ambient=os.environ).strip() == ""


@pytest.mark.parametrize("rel", ["AGENTS.md", "CLAUDE.md", ".mcp.json", ".claude/settings.json"])
def test_a_file_that_is_not_utf8_is_refused_by_name_and_nothing_is_written(tmp_path: Path, rel: str) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    (tmp_path / rel).parent.mkdir(exist_ok=True)
    (tmp_path / rel).write_bytes(b"\xff\xfe not utf-8")
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "main"])
    assert code == cli.REFUSED and len(lines) == 1 and lines[0].startswith(f"not set up: {rel} ") and "UTF-8" in lines[0], lines
    assert not (tmp_path / "ogy.yml").exists() and not (tmp_path / "docs").exists()
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--check"])
    assert code == cli.FINDINGS and any(line.startswith(f"{rel} ") and "UTF-8" in line for line in lines), lines


@pytest.mark.parametrize("rel", [".githooks", ".claude"])
def test_a_file_where_init_needs_a_folder_is_refused_before_any_write(tmp_path: Path, rel: str) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    (tmp_path / rel).write_text("mine\n")
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "main"])
    assert code == cli.REFUSED and lines == [f"not set up: {rel} is a file, not a folder; move it and run again"], lines
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted([".git", rel]) and read(tmp_path, rel) == "mine\n"
    assert run_git(tmp_path, "config", "--default", "", "core.hooksPath", ambient=os.environ).strip() == ""


PREK = (
    "# the gate kit's hooks\nrepos:\n- repo: local\n  hooks:\n  - id: gate  # the whole gate\n    entry: just check\n"
    "    language: system\n    stages: [pre-push]\n"
)


def test_in_a_prek_repo_init_merges_one_pre_commit_entry_and_leaves_core_hooks_path(tmp_path: Path) -> None:
    """Decision init-hook-owner, follow-the-repo: prek owns the hooks, so init adds its entry and claims no core.hooksPath; the
    pre-push check stays in the repository's gate entry, and the doctor asks for none beside it."""
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    (tmp_path / ".pre-commit-config.yaml").write_text(PREK)
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "main"])
    assert code == cli.OK and "wrote .pre-commit-config.yaml" in lines, lines
    text = read(tmp_path, ".pre-commit-config.yaml")
    assert text.startswith(PREK) and "entry: ogy hook pre-commit" in text.replace(init.PUBLISHED, "ogy")
    assert "stages:\n    - pre-commit" in text and text.count("hook pre-commit") == 1
    assert not (tmp_path / ".githooks").exists()
    assert run_git(tmp_path, "config", "--default", "", "core.hooksPath", ambient=os.environ).strip() == ""
    assert cli.run(["--repo", str(tmp_path), "init", "--check"]) == (cli.OK, ["ogy is set up here"])
    assert not [line for line in cli.run(["--repo", str(tmp_path), "init"])[1] if line.startswith("wrote")]  # idempotent


def test_a_prek_entry_that_already_runs_ogy_hook_is_kept_and_a_missing_one_is_reported(tmp_path: Path) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    own = PREK + "- repo: local\n  hooks:\n  - id: kb\n    entry: just ogy hook pre-commit\n    language: system\n"
    (tmp_path / ".pre-commit-config.yaml").write_text(own)
    assert cli.run(["--repo", str(tmp_path), "init", "--land", "main"])[0] == cli.OK
    assert read(tmp_path, ".pre-commit-config.yaml") == own  # ogy's own form, not added twice
    (tmp_path / ".pre-commit-config.yaml").write_text(PREK)
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--check"])
    assert code == cli.FINDINGS and lines == [".pre-commit-config.yaml has no hook that runs `ogy hook pre-commit`: run `ogy init`"]
    run_git(tmp_path, "config", "core.hooksPath", ".githooks", ambient=os.environ)
    lines = cli.run(["--repo", str(tmp_path), "init", "--check"])[1]
    assert "git uses .githooks, not prek's hooks: run `git config --unset core.hooksPath`, then `prek install`" in lines, lines


@pytest.mark.parametrize(
    ("text", "fault"),
    [
        ("repos: [\n", "is not YAML"),
        ("repos: {}\n", "repos is not a list"),
        ("repos: [{repo: local, hooks: []}]\n", "repos is not a block list"),
    ],
)
def test_a_prek_config_init_cannot_merge_into_is_refused_before_any_write(tmp_path: Path, text: str, fault: str) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    (tmp_path / ".pre-commit-config.yaml").write_text(text)
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "main"])
    assert code == cli.REFUSED and len(lines) == 1 and fault in lines[0], lines
    assert sorted(p.name for p in tmp_path.iterdir()) == [".git", ".pre-commit-config.yaml"]


def test_with_no_prek_config_init_refuses_when_another_tool_owns_core_hooks_path(tmp_path: Path) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main", ambient=os.environ)
    run_git(tmp_path, "config", "core.hooksPath", ".husky", ambient=os.environ)
    code, lines = cli.run(["--repo", str(tmp_path), "init", "--land", "main"])
    assert code == cli.REFUSED and len(lines) == 1 and "core.hooksPath is .husky" in lines[0], lines
    assert sorted(p.name for p in tmp_path.iterdir()) == [".git"]
    assert run_git(tmp_path, "config", "core.hooksPath", ambient=os.environ).strip() == ".husky"
