"""The board's write routes: an owner's click is an answer; every refusal writes nothing."""

import json
import shutil
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ogy import ops
from ogy.settle import decisions
from ogy.target import Target
from ogy.web.serve import application
from ogy.web.standing import standing

LIBRARY = Path(__file__).parent / "fixtures/tool-library"
BASE = "http://127.0.0.1:8123"
BROWSER = {"Origin": BASE, "Content-Type": "application/json"}


def _waiting(target):
    rows = standing(target, {})["decisions"].items()
    return sorted(address for address, row in rows if row["status"] == "waiting" and address.rsplit("/", 1)[1] in {"first", "second"})


def _option(target, address):
    found = next(item for item in decisions(target.read()[1]) if str(item.address) == address)
    return next(iter(found.options))


def _tree(repo):
    return {str(path.relative_to(repo)): path.read_bytes() for path in (repo / "docs").rglob("*") if path.is_file()}


def _question(name: str) -> dict[object, object]:
    return {
        "address": f"product/lending/decision/{name}",
        "question": f"Is {name} wanted?",
        "proposal": {"chose": "yes", "why": "Simpler."},
        "options": {"yes": {"label": "Yes", "sets": {}}, "no": {"label": "No", "sets": {}}},
    }


@pytest.fixture
def board(repo):
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    ops.run_put(target, [_question("first"), _question("second")])
    service = application(target, "test-secret")
    with TestClient(service, base_url=BASE) as client:
        client.get("/?t=" + service.exchange_code)  # the browser's cookie, as the console link gives it
        yield client, target, repo


def _body(client, target, **changes):
    address = _waiting(target)[0]
    body = {"decision": address, "option": _option(target, address), "said": "ok", "version": client.get("/api/version").json()["version"]}
    return {**body, **changes}


def test_a_click_is_recorded_with_said_note_where_and_shows_on_the_next_read(board):
    """Given a waiting decision, a same-origin answer is stored by the answer operation and visible without reload."""
    client, target, _ = board
    body = _body(client, target, said=" Fine,  this one ", note="for now")
    waiting = len(_waiting(target))
    response = client.post("/api/answer", json=body, headers=BROWSER)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["recorded"] == {"decision": body["decision"], "option": body["option"], "said": "Fine, this one", "note": "for now"}
    assert data["version"] != body["version"]
    assert client.get("/api/version").json()["version"] == data["version"]
    assert len(_waiting(target)) == waiting - 1
    entry = client.get("/api/entry/" + body["decision"]).json()
    answer = entry["fields"]["answers"][-1]
    assert answer["said"] == "Fine, this one"
    assert answer["note"] == "for now"
    assert answer["where"].startswith("path:ogy-board/")
    assert "delegated" not in answer


@pytest.mark.parametrize(
    ("headers", "status"),
    [
        ({"Origin": "http://evil.example", "Content-Type": "application/json"}, 403),
        ({"Content-Type": "application/json"}, 403),
        ({"Origin": BASE, "Content-Type": "text/plain"}, 415),
        ({"Origin": BASE}, 415),
    ],
    ids=["cross-origin", "no-origin", "text-body", "no-content-type"],
)
def test_browser_provenance_failures_write_nothing(board, headers, status):
    """Given a cookie request without same-origin JSON, the route refuses before any write."""
    client, target, repo = board
    before = _tree(repo)
    response = client.post("/api/answer", content=json.dumps(_body(client, target)), headers=headers)
    assert response.status_code == status
    assert _tree(repo) == before


def test_a_stale_version_is_a_409_and_writes_nothing(board):
    """Given a page read before another write, its answer is refused with the reason."""
    client, target, repo = board
    body = _body(client, target)
    other = _waiting(target)[1]
    ops.run_answer(target, other, _option(target, other), "x", "ai:test/1")
    before = _tree(repo)
    response = client.post("/api/answer", json=body, headers=BROWSER)
    assert response.status_code == 409
    assert "changed since" in response.json()["error"][0]
    assert _tree(repo) == before


@pytest.mark.parametrize("missing", ["said", "version", "decision", "option"])
@pytest.mark.parametrize("blank", [True, False], ids=["blank", "absent"])
def test_a_missing_field_is_a_400_and_writes_nothing(board, missing, blank):
    """Given a request without a required field (or a blank paraphrase), nothing is written."""
    client, target, repo = board
    body = _body(client, target)
    if blank:
        body[missing] = "  "
    else:
        del body[missing]
    before = _tree(repo)
    response = client.post("/api/answer", json=body, headers=BROWSER)
    assert response.status_code == 400
    assert missing in response.json()["error"][0]
    assert _tree(repo) == before


def test_an_unknown_option_and_a_non_object_body_are_refused(board):
    """Given a bad option or a JSON list, nothing is written."""
    client, target, repo = board
    before = _tree(repo)
    assert client.post("/api/answer", json=_body(client, target, option="nope"), headers=BROWSER).status_code == 400
    assert client.post("/api/answer", json=[1], headers=BROWSER).status_code == 400
    assert client.post("/api/answer", content="{", headers=BROWSER).status_code == 400
    assert _tree(repo) == before


def test_the_token_header_still_reaches_the_route_but_the_cookie_alone_needs_provenance(board):
    """Given no credentials, the route is unauthorised."""
    client, target, repo = board
    before = _tree(repo)
    with TestClient(client.app, base_url=BASE) as anonymous:
        assert anonymous.post("/api/answer", json=_body(client, target), headers=BROWSER).status_code == 401
    assert _tree(repo) == before


def test_reply_route_is_stale_checked_and_needs_a_round(board):
    """Given no round, a reply is refused; a stale version is a 409."""
    client, _, repo = board
    version = client.get("/api/version").json()["version"]
    before = _tree(repo)
    base = {"text": "yes all", "said": "ok", "version": version}
    assert client.post("/api/reply", json=base, headers=BROWSER).status_code == 400
    assert client.post("/api/reply", json={**base, "round": "r1", "version": "0" * 64}, headers=BROWSER).status_code == 409
    assert _tree(repo) == before
