"""The integration gaps: no-evidence (E1, E4), missing-proof (E5), delivery in history (B4), harm on fields, one link finding, `ogy mcp`."""

import asyncio
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest
from process_lock import ProcessLock
from tests.conftest import AGREED, GOOD, SOURCE, Kb, commit, ogy

from ogy import cli, ops, removal
from ogy.history import delivery_commit
from ogy.kinds import FieldSpec
from ogy.mcp_server import build
from ogy.model import Problem
from ogy.ontology import Ontology, packaged
from ogy.snapshot import load
from ogy.status import harm

type MakeKb = Callable[[Mapping[str, str | None] | None], Kb]
ACTOR = "- {{id: {}, says: {}, nature: human{}}}\n"
CAPABILITY = "- {{id: {}, says: {}{}}}\n"


def evidence(kb: Kb) -> set[str]:
    return {address for problem, address in kb.findings(evidence=True) if problem is Problem.NO_EVIDENCE}


def test_entry_without_src_or_because_is_no_evidence(kb: MakeKb) -> None:
    assert evidence(kb({})) == set()
    agreed = CAPABILITY.format("borrow", "A member can borrow.", ", agreed: " + AGREED)
    assert evidence(kb({"product/app/capabilities.yml": agreed})) == set()  # a person's yes is evidence
    bare = CAPABILITY.format("borrow", "A member can borrow.", "")
    assert evidence(kb({"product/app/capabilities.yml": bare})) == {"product/app/capability/borrow"}


def test_an_actor_needs_no_evidence(kb: MakeKb) -> None:
    actors = ACTOR.format("member", "A person.", "") + ACTOR.format("owner", "The person who owns the product.", "")
    assert evidence(kb({"product/app/actors.yml": actors})) == set()


def test_because_chain_must_reach_a_source(kb: MakeKb) -> None:
    bare = CAPABILITY.format("other", "Someone else can.", "")
    chain = CAPABILITY.format("borrow", "A member can borrow.", ", because: [product/app/capability/other]")
    assert evidence(kb({"product/app/capabilities.yml": bare + chain})) == {"product/app/capability/other", "product/app/capability/borrow"}
    sourced = CAPABILITY.format("other", "Someone else can.", ", src: [" + SOURCE + "]")
    assert evidence(kb({"product/app/capabilities.yml": sourced + chain})) == set()


def test_a_decision_settling_the_entry_stands_for_its_src(kb: MakeKb) -> None:
    values = "- {id: fee, says: The fee., is: 2, unit: EUR}\n"
    decision = ("question: Q?\nsrc: [" + SOURCE + "]\noptions:\n  a: {label: A, sets: {product/app/value/fee: {is: 1}}}\n"
                "guess: {chose: a, why: Likely.}\n")
    assert evidence(kb({"product/app/values.yml": values})) == {"product/app/value/fee"}
    assert evidence(kb({"product/app/values.yml": values, "product/app/decision/q.yml": decision})) == set()


def test_proof_is_path_and_function(kb: MakeKb) -> None:
    def actor(proof: str) -> dict[str, str]:
        return {"product/app/actors.yml": ACTOR.format("member", "A person.", f", src: [{SOURCE}], proof: {proof}")}

    ok = kb(actor("[tests/test_a.py::test_a, tests/test_a.py::TestA::test_b]")).findings()
    assert (Problem.MISSING_PROOF, "product/app/actor/member") not in ok
    for bad in ("[test_a]", "[tests/test_a.py]", "['{test: t, from: x}']", "[/etc/x.py::f]"):
        assert (Problem.MISSING_PROOF, "product/app/actor/member") in kb(actor(bad)).findings(), bad


def test_harm_may_be_declared_on_a_field(kb: MakeKb) -> None:
    ontology = packaged()
    value = ontology.kinds["value"]
    kinds = {**ontology.kinds, "value": value.model_copy(update={"fields": {**value.fields, "is": FieldSpec(harm=("moves-money",))}})}
    base = kb({"product/app/values.yml": "- {id: fee, says: The fee., is: 2, unit: EUR, src: [" + SOURCE + "]}\n"})
    loaded = load(base.source, Ontology(kinds, ontology.declared))
    fee = next(a for a in loaded.entries if a.kind == "value")
    assert harm(loaded, fee) == "moves-money"
    assert harm(base.snapshot, fee) is None


def test_a_link_to_a_removed_address_is_one_finding(repo: Path) -> None:
    ogy(repo, "--rev", ".", "remove", "software/app/operation/lend", "--why", "not needed")
    (repo / "docs/kb/software/app/view/page.yml").write_text(
        "says: The page.\nserves: [product/app/workflow/borrow/step/ask]\nsrc: ['code:app.py#lend']\n"
        "because: [software/app/operation/lend]\n")
    _, lines = ogy(repo, "--rev", ".", "check")
    assert [line.split(":")[0] for line in lines if "software/app/operation/lend" in line] == ["dangling-link"]


def test_history_has_the_built_rows_and_the_delivery_commit(repo: Path) -> None:
    line = "software/app/operation/lend: {own: aaaaaaaaaaaa, deps: {}, covers: [], sourced: {}}\n"
    (repo / "docs/kb/built/software/app/operation").mkdir(parents=True)
    (repo / "docs/kb/built/software/app/operation/lend.yml").write_text(line)
    commit(repo, "deliver lend")
    run = ops.run_history(ops.Target(repo), "software/app/operation/lend").value
    assert any(row.what == "built: own aaaaaaaaaaaa software/app/operation/lend" and "deliver lend" in row.where for row in run.rows)
    assert "deliver lend" in (delivery_commit(run.rows, "software/app/operation/lend") or "")


def test_remove_runs_under_one_lock_and_resumes_after_a_crash(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    git = repo / ".git"
    with ProcessLock.acquire(git / "ogy.lock", reentrant=False):
        code, lines = ogy(repo, "--rev", ".", "remove", "software/app/operation/lend", "--why", "not needed")
    assert code == cli.REFUSED and "another ogy write holds" in lines[0] and (repo / "docs/kb/software/app/operation/lend.yml").exists()

    def crash(*_: object) -> list[str]:
        raise OSError("crash between the two writes")

    monkeypatch.setattr(removal.Editor, "remove", crash)
    with pytest.raises(OSError):
        ogy(repo, "--rev", ".", "remove", "software/app/operation/lend", "--why", "not needed")
    monkeypatch.undo()
    assert (repo / "docs/kb/software/app/operation/lend.yml").exists()  # ledger written, entry still live
    code, _ = ogy(repo, "--rev", ".", "remove", "software/app/operation/lend", "--why", "not needed")
    assert code == cli.OK and not (repo / "docs/kb/software/app/operation/lend.yml").exists()
    assert (repo / "docs/kb/software/app/removed.yml").read_text().count("id: software/app/operation/lend") == 1


def test_mcp_is_a_subcommand_and_no_tool() -> None:
    assert "mcp" in cli.parser().format_help()
    assert "mcp" not in {tool.name for tool in asyncio.run(build().list_tools())}


def test_agents_get_tables(tmp_path: Path) -> None:
    for rel, text in {**GOOD, "product/app/capabilities.yml": CAPABILITY.format("borrow", "A member can borrow.", "")}.items():
        (tmp_path / "docs/kb" / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs/kb" / rel).write_text(text)
    result = asyncio.run(build().call_tool("check", {"repo": str(tmp_path), "rev": "."}))
    output = (result.structured_content or {}).get("output", "")
    assert output.splitlines()[0] == "problem\tpath\taddress\tdetail" and "no-evidence" in output
