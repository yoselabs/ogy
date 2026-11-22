"""Inspection caching must preserve freshness, including malformed and tool-written inputs."""

import shutil
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ogy.target import Target
from ogy.web import cache
from ogy.web.serve import application

LIBRARY = Path(__file__).parent / "fixtures/tool-library"
HEADERS = {"X-Ogy-Token": "test-secret"}


def test_inspection_encodes_once_and_rechecks_all_input_files(repo, monkeypatch):
    """Given cached inspection, conditional reads reuse bytes until KB, config or ontology changes."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    ontology = Path(__file__).resolve().parents[1] / "src/ogy/ontologies/software"
    shutil.copytree(ontology, repo / "ontology")
    calls = []
    encodings = []
    original = cache.inspect
    dumps = cache.json.dumps

    def inspected(snapshot):
        calls.append(snapshot)
        return original(snapshot)

    monkeypatch.setattr(cache, "inspect", inspected)

    def encoded(value, *args, **kwargs):
        if isinstance(value, dict) and value.get("schema") == 2:
            encodings.append(value)
        return dumps(value, *args, **kwargs)

    monkeypatch.setattr(cache.json, "dumps", encoded)
    service = application(Target(repo, ontology="./ontology"), "test-secret")
    with TestClient(service, base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        before = client.get("/api/inspection")
        assert before.status_code == 200
        assert client.get("/api/inspection").content == before.content
        assert len(calls) == 1
        assert len(encodings) == 1
        for relative in ("docs/kb/product/lending/area.yml", "ogy.yml", "ontology/kinds/entity.yml"):
            path = repo / relative
            path.write_text((path.read_text() if path.exists() else "") + "\n# new input identity\n")
            after = client.get("/api/inspection", headers={"If-None-Match": before.headers["etag"]})
            assert after.status_code == 200
            assert after.headers["etag"] != before.headers["etag"]
            before = after
        assert len(calls) == 4
        assert len(encodings) == 4


def test_all_read_routes_share_a_cached_document_and_conditional_responses(repo, monkeypatch):
    """Given unchanged input ids, version and entry requests do not reparse YAML or rebuild inspection."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    calls = []
    original = cache.inspect

    def inspected(snapshot):
        calls.append(snapshot)
        return original(snapshot)

    monkeypatch.setattr(cache, "inspect", inspected)
    with TestClient(application(Target(repo), "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        document = client.get("/api/inspection").json()
        for route in ("/api/version", "/api/entry/" + document["entries"][0]["address"], "/api/inspection"):
            first = client.get(route)
            assert first.status_code == 200
            conditional = client.get(route, headers={"If-None-Match": first.headers["etag"]})
            assert conditional.status_code == 304 and conditional.content == b""
        assert len(calls) == 1


@pytest.mark.parametrize("value", [".nan", "{1: number, text: word}", "{2026-11-22: day}", "!!set {a: null}", "!!binary aGk="])
def test_yaml_values_outside_json_produce_findings_and_explicit_markers(repo, value):
    """Given unusual YAML, each endpoint remains JSON and inspection explains the value."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    (repo / "docs/kb/product/lending/area.yml").write_text(f"says: Tool loans.\nextra: {value}\n")
    with TestClient(application(Target(repo), "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        document = client.get("/api/inspection")
        assert document.status_code == 200
        assert document.json()["findings"]
        entry = next(item for item in document.json()["entries"] if item["address"] == "product/lending/area/lending")
        assert "\x00ogy" in entry["fields"]["extra"]
        assert client.get("/api/version").status_code == 200
        assert client.get("/api/entry/" + entry["address"]).status_code == 200


def test_invalid_utf8_is_a_finding_instead_of_authored_replacement_text(repo):
    """Given undecodable bytes, inspection reports bad-yaml and invents no replacement character."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    (repo / "docs/kb/product/lending/area.yml").write_bytes(b"says: invalid \xff\n")
    with TestClient(application(Target(repo), "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        response = client.get("/api/inspection")
        assert response.status_code == 200
        assert any(item["problem"] == "bad-yaml" for item in response.json()["findings"])
        assert "\ufffd" not in response.text


@pytest.mark.parametrize("relative", ["product/lending/removed.yml", "built/product/lending/actors.yml"])
def test_tool_written_state_invalidates_the_version_even_without_entry_changes(repo, relative):
    """Given changed removed or built files, a client's old token and ETag are obsolete."""
    shutil.copytree(LIBRARY, repo, dirs_exist_ok=True)
    with TestClient(application(Target(repo), "test-secret"), base_url="http://127.0.0.1:8123", headers=HEADERS) as client:
        before = client.get("/api/version")
        path = repo / "docs/kb" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# changed tool-written state\n")
        after = client.get("/api/version")
        assert after.json()["version"] != before.json()["version"]
        assert after.headers["etag"] != before.headers.get("etag")
