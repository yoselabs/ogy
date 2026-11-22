"""The waiting list view keeps to the shell's rules: one mention path, marked KB text, the viewer's fixed words, one route line."""

import re
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "src/ogy/web/static"


def view() -> str:
    return (STATIC / "js/views/waiting.js").read_text(encoding="utf-8")


def test_the_waiting_view_draws_entries_with_the_one_mention_and_marks_kb_text():
    """Given the view's source, every title is a mention and every question or area name is wrapped as authored text."""
    text = view()
    assert 'from "../ui/mention.js"' in text
    assert 'from "../ui/authored.js"' in text
    assert "authored(question" in text
    assert "authored(group.area" in text
    assert re.search(r"#[0-9a-fA-F]{3,8}\b", text) is None


def test_every_word_the_view_shows_is_in_the_viewers_fixed_list():
    """Given `words.x` uses in the view, each name exists in words.js, so no word is invented in the view."""
    used = set(re.findall(r"\bwords\.(?!js\b)(\w+)", view()))
    listed = set(re.findall(r"^\s+(\w+):", (STATIC / "js/ui/words.js").read_text(encoding="utf-8"), re.MULTILINE))
    assert used
    assert sorted(used - listed) == []


def test_the_route_is_one_entry_in_the_route_table_and_the_rail_reuses_the_list():
    """Given the router table, the waiting page is claimed with one line; the rail draws the same list."""
    main = (STATIC / "js/main.js").read_text(encoding="utf-8")
    assert main.count("waitingRoute") == 2
    assert "bindWaiting" in (STATIC / "js/shell/rail.js").read_text(encoding="utf-8")
