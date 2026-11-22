"""Standing facts share the CLI's classifications and the board's conditional reads."""

import shutil
from pathlib import Path

from starlette.testclient import TestClient

from ogy import ops, wire
from ogy.target import Target
from ogy.web.serve import application
from ogy.writes import locked

LIBRARY = Path(__file__).parent / "fixtures/tool-library"
HEADERS = {"X-Ogy-Token": "test-secret"}


def test_standing_matches_cli_and_includes_every_decision(repo):
    """Given the tool library, standing exposes the CLI facts and delegated answers."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    overview = ops.run_status(target, None, with_coverage=False).value
    work = ops.run_work(target, None).value
    dropped = ops.run_dropped(target).value
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        assert client.get("/api/standing", headers={"X-Ogy-Token": "wrong"}).status_code == 401
        response = client.get("/api/standing")
        assert response.status_code == 200
        data = response.json()
        assert data["computed"] is True
        assert data["version"] == client.get("/api/version").json()["version"]
        assert data["totals"] == {
            "waiting": sum(h.questions for h in overview.areas),
            "owed": len(work),
            "unagreed": sum(h.ai for h in overview.areas),
            "changed": sum(h.changed for h in overview.areas),
            "dropped": len(dropped),
            "findings": overview.findings,
        }
        assert len(data["work"]) == len(work)
        assert len(data["dropped"]) == len(dropped)
        for header in overview.areas:
            area = data["areas"][header.area]
            assert area == {name: getattr(header, name) for name in ("questions", "answered", "ai", "docs", "code", "you", "changed")}
        snapshot = target.read()[1]
        decisions = {str(a) for a in snapshot.entries if a.kind == "decision"}
        assert set(data["decisions"]) == decisions
        rounding = data["decisions"]["product/lending/decision/fee-rounding"]
        assert rounding["status"] == "answered"
        assert rounding["chose"].endswith("/option/up")
        assert rounding["delegated"] == "product/lending/decision/fee-details"
        assert rounding["at"]
        for header in overview.areas:
            entries = [v for a, v in data["entries"].items() if a.startswith(header.area + "/")]
            assert sum(v["source"] == "ai" and not v["changed"] for v in entries) == header.ai
            assert sum(v["changed"] for v in entries) == header.changed
        assert client.get("/api/standing", headers={"If-None-Match": response.headers["etag"]}).status_code == 304
        with locked(target, "trial"):
            assert client.get("/api/standing", headers={"If-None-Match": response.headers["etag"]}).status_code == 400
        assert wire.status(overview) == wire.status(ops.run_status(target).value)


def test_answer_invalidates_standing_version(repo):
    """Given cached standing, a new answer changes its version and chosen option."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        before = client.get("/api/standing")
        ops.run_answer(
            target,
            "product/lending/decision/fee-rounding",
            "up",
            "Round up to whole days",
            "ai:test/standing",
            at="2099-11-23T12:00:00+00:00",
        )
        after = client.get("/api/standing", headers={"If-None-Match": before.headers["etag"]})
        assert after.status_code == 200
        assert after.json()["version"] != before.json()["version"]
        assert after.json()["decisions"]["product/lending/decision/fee-rounding"]["delegated"] is None
