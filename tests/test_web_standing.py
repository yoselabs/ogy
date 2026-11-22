"""Standing facts share the CLI's classifications and the board's conditional reads."""

import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from starlette.testclient import TestClient

from ogy import ops, wire
from ogy.target import Target
from ogy.web import reach as reach_module
from ogy.web import standing as standing_module
from ogy.web.cache import InspectionCache
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
        assert (data["repository"], data["revision"]) == (repo.resolve().name, "worktree")
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


def _put_unset_decision(target):
    ops.run_put(
        target,
        [
            {
                "address": "product/lending/decision/reach-probe",
                "question": "Does the probe set anything?",
                "options": {"yes": {"label": "Yes, but it names nothing"}, "later": {"label": "Not yet", "sets": {}}},
                "proposal": {"chose": "yes", "why": "The probe only reads."},
            }
        ],
    )


def _option(data, decision, key):
    address = decision if "/" in decision else f"product/lending/decision/{decision}"
    return data["decisions"][address]["options"][f"{address}/option/{key}"]


def test_option_reach_equals_impact_and_differs_between_decisions(repo):
    """Given decisions that set different entries, each reach equals what `ops` impact returns for what is set."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        data = client.get("/api/standing").json()
    rule, fee = _option(data, "late-fee", "two"), _option(data, "software/lending/decision/mailer", "smtp")
    assert rule["sets"] == ["product/lending/quantity/late-fee"]
    assert fee["sets"] == ["software/lending/dependency/mailer"]
    for option in (rule, fee):
        done = ops.run_impact(target, option["sets"][0]).value
        assert option["reach"] == sorted(str(a) for a in done.reaches | done.reached_by)
        assert option["count"] == len(option["reach"]) > 0
        assert option["truncated"] is False
    assert rule["reach"] != fee["reach"]
    assert _option(data, "late-fee", "one")["reach"] == rule["reach"]


def test_option_that_sets_nothing_says_so(repo):
    """Given options with no sets, each says an explicit empty reach and no guess."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    _put_unset_decision(target)
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        data = client.get("/api/standing").json()
    for key in ("yes", "later"):
        assert _option(data, "reach-probe", key) == {"sets": [], "reach": [], "count": 0, "truncated": False}


def test_option_reach_is_truncated_past_the_limit_and_cached(repo, monkeypatch):
    """Given a long reach, the list stops at the limit with the full count; an unchanged read does not compute it again."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    monkeypatch.setattr(reach_module, "LIMIT", 1)
    calls = []
    real = reach_module.reach
    monkeypatch.setattr("ogy.web.cache.reach", lambda snapshot: calls.append(1) or real(snapshot))
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        first = client.get("/api/standing").json()
        client.get("/api/standing")
        assert len(calls) == 1
    rule = _option(first, "late-fee", "two")
    assert rule["truncated"] is True
    assert len(rule["reach"]) == 1 < rule["count"]


def test_reach_is_fast_and_standing_small_on_this_repository():
    """Given this repository's own knowledge base, the whole-KB reach takes well under 3 s and standing stays under 1 MB."""
    target = Target(Path(__file__).parent.parent)
    snapshot = target.read()[1]
    started = time.perf_counter()
    found = reach_module.reach(snapshot)
    assert time.perf_counter() - started < 3
    assert found
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        response = client.get("/api/standing")
    assert response.status_code == 200
    assert len(response.content) < 1_000_000


def _counting(monkeypatch):
    calls = []
    real = standing_module.standing
    monkeypatch.setattr("ogy.web.cache.standing", lambda *args: calls.append(1) or real(*args))
    return calls


def test_standing_is_served_from_cache_until_a_file_changes(repo, monkeypatch):
    """Given an unchanged KB, a second request does not compute; an edit does, and the result equals the uncached function."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    target = Target(repo)
    calls = _counting(monkeypatch)
    with TestClient(application(target, "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        first = client.get("/api/standing")
        assert client.get("/api/standing").content == first.content
        assert client.get("/api/standing", headers={"If-None-Match": first.headers["etag"]}).status_code == 304
        assert len(calls) == 1
        ops.run_answer(target, "product/lending/decision/fee-rounding", "up", "Round up", "ai:test/cache", at="2099-11-23T12:00:00+00:00")
        second = client.get("/api/standing").json()
        assert len(calls) == 2
        assert second["version"] != first.json()["version"]
    expected = standing_module.standing(target, reach_module.reach(target.read()[1]))
    assert {k: v for k, v in second.items() if k != "version"} == expected


def test_concurrent_standing_requests_compute_once(repo, monkeypatch):
    """Given requests arriving together, one computation serves them all."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    cache = InspectionCache(Target(repo))
    calls = []
    real = standing_module.standing

    def slow(*args):
        calls.append(1)
        time.sleep(0.2)
        return real(*args)

    monkeypatch.setattr("ogy.web.cache.standing", slow)
    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(lambda _: cache.standing_response()[1], range(8)))
    assert len(calls) == 1
    assert len(set(results)) == 1
