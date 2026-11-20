"""The wired commands: checks registered, review, glossary, spec, show, work left, remove, removed and history."""

import shutil
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest
from tests.conftest import Kb, commit, ogy

from ogy import cli, ops
from ogy.model import Problem
from ogy.ontology import Ontology, parse_kinds
from ogy.review import dropped, review
from ogy.snapshot import build
from ogy.status import harm

V5 = Path(__file__).parent / "fixtures"
type MakeKb = Callable[[Mapping[str, str | None] | None], Kb]
BASE_PROBLEMS = ("removed-unrecorded", "bad-snapshot", "bad-removed", "edited-", "id-reused", "link-to-removed")


def example(tmp_path: Path) -> list[str]:
    """The tool-library example as a repository (its knowledge base under `docs/kb`), as global flags."""
    shutil.copytree(V5 / "example-tool-library", tmp_path / "docs/kb")
    return ["--repo", str(tmp_path), "--rev", "."]


def codes(kb: Kb, landing: bool = False) -> set[Problem]:
    return {problem for problem, _ in kb.findings(landing=landing)}


def test_checks_are_registered_for_evidence_stored_state_and_one_sentence(kb: MakeKb) -> None:
    actor = "- {{id: {}, says: A person., nature: human{}}}\n"
    changed = {"product/app/actors.yml": actor.format("member", ", src: [code:nowhere.py#f]") + actor.format("other",
                                                                                                                   ", status: open")
               + actor.format("third", ", \"why?\": x")}
    assert {Problem.MISSING_CODE, Problem.STORED_STATE, Problem.BAD_KEY} <= codes(kb(changed))
    twice = {"product/app/actors.yml": actor.format("member", "") + actor.format("other", "")}
    assert Problem.DUPLICATE_SAYS in codes(kb(twice))


def test_decisions_terms_and_ledgers_are_registered(kb: MakeKb) -> None:
    decision = "question: Q?\noptions:\n  a: {label: A, sets: {product/app/quantity/fee: {is: 1}}}\n"
    found = codes(kb({"product/app/quantities.yml": "- {id: fee, says: The fee., is: 2, unit: EUR}\n",
                      "product/app/decision/q.yml": decision,
                      "product/shared/glossary.yml": "- {id: land, word: land, says: To finish., avoid: [merge]}\n",
                      "product/app/removed.yml": "format: 1\n"}), landing=True)
    assert {Problem.NO_PROPOSAL, Problem.TERM_NOT_AGREED, Problem.BAD_REMOVED} <= found


def test_review_asks_at_most_seven_and_counts(kb: MakeKb) -> None:
    actors = "".join(f"- {{id: p{n}, says: Person {n}., nature: human}}\n" for n in range(9))
    snapshot = kb({"product/app/actors.yml": actors}).snapshot
    short, everything = review(snapshot), review(snapshot, everything=True)
    assert len(short.cards) == 7 and short.waiting == len(everything.cards) - 7 and len(everything.cards) >= 9
    assert short.headers[0].ai >= 9 and str(short.headers[0]).startswith("product/app   0 questions open · ")
    assert dropped(snapshot, []).proposed_no == ()


def test_harm_is_read_from_the_kind_files(kb: MakeKb, ontology: Ontology) -> None:
    snapshot = kb(None).snapshot
    assert harm(snapshot, snapshot.resolve("product/app/actor/member") or snapshot_error()) is None
    text = "kind: risky\nabout: x\nharm: [irreversible, tells-outside]\nshape: file\nlayers: [product]\nfields:\n  says: {}\n"
    kinds = parse_kinds({"kinds/risky.yml": text}, ontology.declared)
    risky = build(kinds, {"product/app/risky/x.yml": "says: x\n"})
    assert harm(risky, next(iter(risky.entries))) == "tells-outside"


def snapshot_error() -> None:
    raise AssertionError("missing entry")


def test_glossary_and_kinds_print_from_the_data(kb: MakeKb) -> None:
    root = kb({"product/shared/glossary.yml": "- {id: land, word: land, says: To finish., avoid: [merge]}\n",
               "product/app/glossary.yml": "- {id: fee, word: fee, says: What a loan costs.}\n",
               "software/app/glossary.yml": "- {id: page, word: page, says: What a member sees.}\n"}).repo()
    target = ["--repo", str(root), "--rev", "."]
    land = ["product/shared:", "  land: To finish.", "    avoid: merge"]
    code, whole = cli.run([*target, "glossary"])
    assert code == cli.OK and whole[:whole.index("")] == [*land, "product/app:", "  fee: What a loan costs.", "software/app:",
                                                          "  page: What a member sees."]
    assert "  quantity: like an ISO 80000 quantity value: a number times a unit, decided once; unlike a measured reading or a " \
        "running count, which are attributes; a DDD value object" in whole
    assert cli.run([*target, "glossary", "software/app"]) == (cli.OK, [*land, "software/app:", "  page: What a member sees."])
    assert cli.run([*target, "glossary", "product/shared"]) == (cli.OK, land)
    assert cli.run([*target, "glossary", "app"])[0] == cli.NOT_FOUND  # an area is named with its layer
    lines = cli.run([*target, "kinds"])[1]
    assert "dependency: a library or service the product depends on and does not own" in lines
    assert "  like: a package or service dependency: something we call and do not own" in lines
    assert "  harm if wrong: tells-outside" in lines


def test_show_joins_status_decision_sources_and_built_record(tmp_path: Path) -> None:
    example_flags = example(tmp_path)
    code, lines = cli.run([*example_flags, "show", "product/library/quantity/late-fee"])
    assert code == cli.OK
    assert any(line.startswith("status (computed): decided by you, 2026-11-24") for line in lines)
    assert any(line.startswith("Decided in (computed): product/library/decision/late-fee (in force: two, by you)") for line in lines)
    assert "You said (paraphrased): Yes to card 1" in lines
    rule = cli.run([*example_flags, "show", "product/library/rule/late-fee-per-day"])[1]  # D15: the rule is proved, not the number
    built = next(line for line in rule if line.startswith("built ("))
    assert built.startswith("built (built/product/library/rule/late-fee-per-day.yml): own f56adef51e68 = now")
    assert built.endswith("work left: none")
    shown = cli.run([*example_flags, "show", "product/library/decision/late-fee"])[1]
    assert "Settles (computed): product/library/quantity/late-fee" in shown


def test_show_of_an_address_decided_no(kb: MakeKb) -> None:
    decision = "question: Q?\noptions:\n  no: {label: No, sets: {product/app/quantity/gone: null}}\nproposal: {chose: no, why: x}\n"
    root = kb({"product/app/decision/q.yml": decision}).repo()
    code, lines = cli.run(["--repo", str(root), "--rev", ".", "show", "product/app/quantity/gone"])
    assert code == cli.OK and lines == ["product/app/quantity/gone: does not exist: decided no in product/app/decision/q (by AI)"]
    assert "product/app/decision/q" in cli.run(["--repo", str(root), "--rev", ".", "dropped"])[1][0]


def test_work_reads_built_record_and_lists_removal_work(repo: Path) -> None:
    page = ops.run_show(ops.Target(repo), "software/app/interface/page").value.build_hash
    line = "{own: %s, covers: [], sourced: {}}\n"
    (repo / "docs/kb/built/software/app/interface").mkdir(parents=True)
    (repo / "docs/kb/built/software/app/interface/page.yml").write_text(f"software/app/interface/page: {line % page}")
    (repo / "docs/kb/built/software/app/interface/gone.yml").write_text(f"software/app/interface/gone: {line % 'aaaaaaaaaaaa'}")
    (repo / "docs/kb/built/software/app/handler").mkdir(parents=True)
    (repo / "docs/kb/built/software/app/handler/lend.yml").write_text(f"software/app/handler/lend: {line % 'bbbbbbbbbbbb'}")
    commit(repo, "built")
    _, lines = ogy(repo, "work")
    assert not any("software/app/interface/page" in text for text in lines)
    assert "removed: software/app/interface/gone (now -, built aaaaaaaaaaaa) no ledger item" in lines
    # D15: a handler needs no proof; its line is removal work until `ogy migrate` deletes it
    assert "removed: software/app/handler/lend (now -, built bbbbbbbbbbbb) needs no proof: `ogy migrate` deletes the line" in lines
    assert "deleted the built line of software/app/handler/lend: it needs no proof" in ogy(repo, "migrate")[1]
    assert not any("software/app/handler/lend" in text for text in ogy(repo, "work")[1])
    (repo / "docs/kb/built/software/app/handler/bad.yml").write_text("software/app/handler/bad: {own: x, extra: 1}\n")
    assert ogy(repo, "--rev", ".", "check")[1][0].startswith("stored-state: built/software/app/handler/bad.yml")


def test_remove_records_the_item_and_refuses_linked_entries(repo: Path) -> None:
    code, lines = ogy(repo, "--rev", ".", "remove", "product/app/quantity/fee", "--why", "not needed")
    assert code == cli.REFUSED
    assert lines == ["not removed: product/app/workflow/borrow/step/ask/timeout links to product/app/quantity/fee (after)"]
    code, lines = ogy(repo, "--rev", ".", "remove", "software/app/handler/lend", "--why", "not needed")
    assert code == cli.OK and not (repo / "docs/kb/software/app/handler/lend.yml").exists()
    assert (repo / "docs/kb/software/app/removed.yml").read_text().startswith("format: 1\nitems:\n")
    _, found = ogy(repo, "--rev", ".", "find", "lend")
    assert found[0].startswith("software/app/handler/lend   handler   removed ") and "why: not needed" in found[0]
    assert not [line for line in ogy(repo, "--rev", ".", "check", "--base", "HEAD")[1] if line.startswith(BASE_PROBLEMS)]


def test_remove_part_keeps_its_place_and_the_id_is_not_reused(repo: Path) -> None:
    ogy(repo, "--rev", ".", "remove", "software/app/handler/lend", "--why", "not needed")
    code, _ = ogy(repo, "--rev", ".", "remove", "product/app/workflow/borrow/step/ask/choice/go", "--why", "not needed")
    assert code == cli.OK
    run = ops.run_find(ops.Target(repo, rev="."), [], parent="product/app/workflow/borrow/step/ask")
    assert [row.address for row in run.value if row.state == "removed"] == [
        "product/app/workflow/borrow/step/ask/choice/go"]
    path = repo / "docs/kb/product/app/workflow/borrow.yml"
    path.write_text(path.read_text().replace("choices: {}", "choices: {go: {label: Again, then: done}}"))
    assert (Problem.ID_REUSED, "product/app/workflow/borrow/step/ask/choice/go") in {
        (item.problem, str(item.address)) for item in ops.run_check(ops.Target(repo, rev=".")).value}


def test_a_deletion_without_an_item_is_found_against_the_base(repo: Path) -> None:
    (repo / "docs/kb/software/app/handler/lend.yml").unlink()
    code, lines = ogy(repo, "--rev", ".", "check", "--base", "HEAD")
    assert code == cli.FINDINGS
    assert any(line.startswith("removed-unrecorded: software/app/handler/lend.yml software/app/handler/lend") for line in lines)


def test_history_is_computed_from_git_and_the_ledger(repo: Path) -> None:
    ogy(repo, "--rev", ".", "remove", "software/app/handler/lend", "--why", "not needed")
    commit(repo, "remove lend")
    _, lines = ogy(repo, "history", "software/app/handler/lend")
    assert any("added software/app/handler/lend" in line and "first" in line for line in lines)
    assert any("removed software/app/handler/lend" in line and "remove lend" in line for line in lines)
    assert any(line.startswith("20") and "ogy  removed (why: not needed; replaced by: None)" in line for line in lines)


def test_remove_always_needs_a_why_and_plain_words_are_listed_by_dropped(repo: Path) -> None:
    before = (repo / "docs/kb/software/app/handler/lend.yml").read_text()
    with pytest.raises(SystemExit):
        ogy(repo, "--rev", ".", "remove", "software/app/handler/lend")  # --why is required
    code, lines = ogy(repo, "--rev", ".", "remove", "software/app/handler/lend", "--why", "  ")
    assert code == cli.REFUSED and "why is required" in lines[0]
    assert (repo / "docs/kb/software/app/handler/lend.yml").read_text() == before
    assert ogy(repo, "--rev", ".", "remove", "software/app/handler/lend", "--why", "We no longer lend tools.")[0] == cli.OK
    assert ogy(repo, "dropped")[1] == ["removed with plain words, not a decision: software/app/handler/lend"]
    assert "removed with plain words\tsoftware/app/handler/lend" in cli.run(["--repo", str(repo), "dropped"], agent=True)[1][0]
    assert not [line for line in ogy(repo, "--rev", ".", "check", "--base", "HEAD")[1] if line.startswith(BASE_PROBLEMS)]
