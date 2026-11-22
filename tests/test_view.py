"""`ogy view`: the product as one web page, read from the entries."""

lazy from collections.abc import Callable
lazy from pathlib import Path

lazy from tests.conftest import Kb

from ogy import cli
from ogy.view import render


def test_the_page_tells_each_area_and_opens_a_workflow_to_its_steps(kb: Callable[..., Kb]) -> None:
    page = render(kb().snapshot)
    assert 'id="product-app"' in page and 'href="#software-app"' in page  # a tile and a section per area
    assert "What members of the tool library do." in page
    assert "The member asks." in page and "Sign in &rarr; done" in page  # the step and where its choice leads
    assert "Members sign in" in page  # the decision's option


def test_a_sentence_is_escaped(kb: Callable[..., Kb]) -> None:
    page = render(kb({"product/app/area.yml": "says: <script>alert(1)</script> & more.\n"}).snapshot)
    assert "<script>alert(1)</script>" not in page and "&lt;script&gt;alert(1)&lt;/script&gt; &amp; more." in page


def test_view_writes_the_page_where_asked_and_changes_no_entry(kb: Callable[..., Kb], tmp_path: Path) -> None:
    repo, out = kb().repo(), tmp_path / "map.html"
    code, lines = cli.run(["serve", "--repo", str(repo), "--out", str(out)])
    assert code == 0 and lines[0] == f"wrote {out}"
    assert out.read_text(encoding="utf-8").startswith("<!doctype html>")
