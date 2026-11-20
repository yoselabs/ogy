"""The eval scripts are run directly (`python3 -I <script>`); each answers `--help` with its usage and refuses an unknown flag."""

import runpy
import sys
from pathlib import Path

import pytest

SCRIPTS = [
    "evals/blind.py",
    "evals/naming/v2/blind.py",
    "evals/naming/v2/blame-list.py",
    "evals/naming/v2/check-run.py",
    "evals/naming/v2/guess-rate.py",
    "evals/naming/v2/tally.py",
]
ROOT = Path(__file__).resolve().parent.parent


def run_script(script: str, flag: str, monkeypatch: pytest.MonkeyPatch) -> int:
    monkeypatch.setattr(sys, "argv", [script, flag])
    with pytest.raises(SystemExit) as stopped:
        runpy.run_path(str(ROOT / script), run_name="__main__")
    return int(stopped.value.code or 0)


@pytest.mark.parametrize("script", SCRIPTS)
def test_help_exits_zero_and_prints_usage(script: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    assert run_script(script, "--help", monkeypatch) == 0
    assert capsys.readouterr().out.startswith("usage:")


@pytest.mark.parametrize("script", SCRIPTS)
def test_unknown_flag_exits_two_and_writes_nothing(script: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    assert run_script(script, "--no-such-flag", monkeypatch) == 2
    assert list(tmp_path.iterdir()) == []
