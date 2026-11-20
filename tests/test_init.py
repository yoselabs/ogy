"""`ogy init` and `ogy.yml`: set-up that is idempotent and never clobbers, and settings read as flag defaults."""

import json
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
    run_git(tmp_path, "init", "-q", "-b", "main")
    assert cli.run(["--repo", str(tmp_path), "init"])[0] == cli.OK
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


def test_init_installs_a_pre_commit_hook_that_checks_the_staged_tree(tmp_path: Path) -> None:
    run_git(tmp_path, "init", "-q", "-b", "main")
    code, lines = cli.run(["--repo", str(tmp_path), "init"])
    hook = tmp_path / ".githooks/pre-commit"
    assert code == cli.OK and ".githooks/pre-commit" in "".join(lines) and hook.stat().st_mode & 0o111
    text = hook.read_text()
    assert "git write-tree" in text and "git commit-tree" in text and '--rev "$commit" check' in text
    assert "diff --cached" not in text  # every commit: a code rename can break a `code:` source
    assert run_git(tmp_path, "config", "core.hooksPath").strip() == ".githooks"
    assert not [line for line in cli.run(["--repo", str(tmp_path), "init"])[1] if line.startswith("wrote")]  # idempotent
    hook.unlink()
    assert any("pre-commit" in line for line in cli.run(["--repo", str(tmp_path), "init", "--check"])[1])


def test_init_starts_with_the_ontologys_entries_and_never_re_adds_a_removed_one(repo: Path) -> None:
    assert cli.run(["--repo", str(repo), "init"])[0] == cli.OK
    actors = read(repo, "docs/kb/product/shared/actors.yml")
    assert "id: owner" in actors and "nature: human" in actors and "id: agent" in actors and "agreed" not in actors
    commit(repo, "init")  # a removal is recorded against what was committed
    code, lines = cli.run(["--repo", str(repo), "--rev", ".", "remove", "product/shared/actor/agent", "--why", "No agents here"])
    assert code == cli.OK, lines
    assert cli.run(["--repo", str(repo), "init"])[0] == cli.OK
    assert "id: agent" not in read(repo, "docs/kb/product/shared/actors.yml")
    assert not any("actor/agent" in line for line in cli.run(["--repo", str(repo), "init", "--check"])[1])
