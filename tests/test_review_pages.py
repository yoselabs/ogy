"""Words nobody agreed yet wait for the owner (an error only on a land), and `review --from docs|code` pages them."""

from pathlib import Path

from git_porcelain import run_git
from tests.conftest import commit
from tests.test_reply import r, round_of
from tests.test_writes import w

from ogy import cli

TERMS = ("- {id: land, word: land, says: To finish a delivery., avoid: [merge, complete], src: [doc:<rev>:docs/spec.md#land]}\n"
         "- {id: gate, word: gate, says: The check before a land., src: [doc:<rev>:docs/spec.md#land]}\n")
SLOT = "- {id: slot, word: slot, says: A place to work., src: [doc:<rev>:docs/spec.md#work]}\n"  # a word two areas use
SPEC = "# Spec\n\n## Land\n\nLand is finishing.\n\n## Work\n\nA slot is a place.\n"
PROPOSES = ("question: Name it?\noptions:\n  a: {{label: A, sets: {{product/app/term/{word}: {{says: {says}}}}}}}\n"
            "proposal: {{chose: a, why: b}}\n")
SAYS = {"land": "To finish a delivery.", "gate": "The check before a land."}


def terms(repo: Path, text: str = TERMS) -> Path:
    """The glossary `text` of the area app in `repo`, and a shared word; its `doc:` links pin the commit that holds the spec (a `<rev>`
    in the text)."""
    (repo / "docs").mkdir(exist_ok=True)
    if not (repo / "docs/spec.md").exists():
        (repo / "docs/spec.md").write_text(SPEC)
        commit(repo, "the spec")
    rev = run_git(repo, "log", "-1", "--format=%H", "--", "docs/spec.md").strip()
    (repo / "docs/kb/product/shared").mkdir(parents=True, exist_ok=True)
    (repo / "docs/kb/product/shared/area.yml").write_text("says: What two areas use.\n")
    (repo / "docs/kb/product/shared/glossary.yml").write_text(SLOT.replace("<rev>", rev))
    (repo / "docs/kb/product/app/glossary.yml").write_text(text.replace("<rev>", rev))
    return repo


def test_unagreed_terms_wait_and_are_errors_only_on_a_land(repo: Path) -> None:
    terms(repo)
    code, lines = w(repo, "check")
    assert code == cli.OK and lines == ["ok", "waiting for you: 3 (ogy review)"]
    assert "waiting for you: 3 (ogy review)" in w(repo, "status")[1]
    code, lines = w(repo, "check", "--landing")
    assert code == cli.FINDINGS and len([line for line in lines if line.startswith("term-not-agreed")]) == 3, lines
    assert w(repo, "check", "app")[1][-1] == "waiting for you: 2 (ogy review)"


def test_a_proposed_word_blocks_only_the_change_that_adds_it(repo: Path) -> None:
    terms(repo, TERMS.splitlines(keepends=True)[0])
    (repo / "docs/kb/product/app/decision").mkdir()
    (repo / "docs/kb/product/app/decision/old.yml").write_text(PROPOSES.format(word="land", says=SAYS["land"]))
    base = commit(repo, "a word is proposed")
    terms(repo, "".join(TERMS.splitlines(keepends=True)[:2]))
    (repo / "docs/kb/product/app/decision/new.yml").write_text(PROPOSES.format(word="gate", says=SAYS["gate"]))
    code, lines = w(repo, "check", "--landing", "--base", base)
    proposed = [line for line in lines if line.startswith("proposed-term")]
    assert code == cli.FINDINGS and len(proposed) == 1 and "product/app/term/gate" in proposed[0], lines
    both = [line for line in w(repo, "check", "--landing")[1] if line.startswith("proposed-term")]
    assert len(both) == 2  # without a base every proposed word blocks


def test_review_from_docs_pages_by_section_and_yes_agrees_to_the_page(repo: Path) -> None:
    terms(repo)
    code, lines = w(repo, "review", "--from", "docs")
    text = "\n".join(lines)
    assert code == cli.OK and "page 1 of 2: product/app: terms" in text, lines
    assert "land: To finish a delivery." in text and "not: merge; complete" in text
    assert "From docs: doc:" in text and ":docs/spec.md#land" in text
    assert "slot" not in text and lines[0].startswith("round r")
    assert r(repo, "yes", "--round", round_of(lines))[1] == ["yes: agreed to 2 sentence(s)"]
    again = w(repo, "review", "--from", "docs")[1]
    assert "page 1 of 1: product/shared: terms" in "\n".join(again) and "gate" not in "\n".join(again)
    assert w(repo, "review", "--from", "docs", "--page", "2")[0] == cli.NOT_FOUND
    assert "waiting for you: 1" in w(repo, "status")[1][-4]


def test_review_from_docs_yes_with_numbers(repo: Path) -> None:
    terms(repo)
    lines = w(repo, "review", "--from", "docs")[1]
    assert r(repo, "yes 2", "--round", round_of(lines))[0] == cli.OK
    left = "\n".join(w(repo, "review", "--from", "docs")[1])
    assert "gate: The check" in left and "land: To finish" not in left


def test_review_from_code_pages_by_area_and_filters_by_area(repo: Path) -> None:
    (repo / "docs/kb/product/app/capabilities.yml").write_text(
        "- {id: borrow, says: A member borrows., src: [code:src/x.py#f]}\n")
    (repo / "src").mkdir()
    (repo / "src/x.py").write_text("def f():\n    pass\n")
    lines = w(repo, "review", "--from", "code")[1]
    assert any(line.startswith("page 1 of 2: product/app: from code") for line in lines)  # the fixture is from code too
    assert "From code: code:src/x.py#f" in "\n".join(lines)
    assert "nothing from docs is waiting for you" in "\n".join(w(repo, "review", "app", "--from", "docs")[1])


def test_review_screen_puts_the_guess_first_and_counts_decisions_apart(repo: Path) -> None:
    decision = "question: How much?\noptions:\n  low: {label: Low, sets: {product/app/quantity/fee: {is: 1}}}\n"
    (repo / "docs/kb/product/app/decision").mkdir()
    (repo / "docs/kb/product/app/decision/fee.yml").write_text(
        decision + "  high: {label: High, sets: {product/app/quantity/fee: {is: 2}}}\n"
        "proposal: {chose: high, why: fees are small}\n")
    lines = w(repo, "review")[1]
    text = "\n".join(lines)
    assert lines[0].startswith("round r") and "1 questions open · 0 answered by you | entries:" in lines[1]
    assert text.index("A. High  (recommended)") < text.index("B. Low") and "AI proposal because: fees are small" in text
    assert "Q1: <your words>" in text
    md = "\n".join(w(repo, "review", "--md")[1])
    assert md.startswith("## ogy review, round `r") and "### Q1. question" in md and "Round: `r" in md


def test_a_decision_reads_answered_by_you_with_the_date(repo: Path) -> None:
    (repo / "docs/kb/product/app/decision").mkdir()
    (repo / "docs/kb/product/app/decision/fee.yml").write_text(PROPOSES.format(word="x", says="Said.").replace("product/app/term/x",
                                                                                                               "product/app/quantity/fee")
                                                  .replace("says: Said.", "is: 3"))
    done = w(repo, "answer", "product/app/decision/fee", "a", "--said", "Option a", "--where", "ai:claude/1",
             "--at", "2026-11-12T10:05:00+01:00")
    assert done[0] == cli.OK, done
    shown = w(repo, "show", "product/app/decision/fee")[1]
    assert any(line.startswith("status (computed): answered by you, 2026-11-12") for line in shown), shown
    assert "1 answered by you | entries:" in "\n".join(w(repo, "status")[1])


def test_a_question_without_options_is_answered_in_words(repo: Path) -> None:
    (repo / "docs/kb/product/app/decision").mkdir()
    (repo / "docs/kb/product/app/decision/name.yml").write_text("question: What should it be called?\n")
    lines = w(repo, "review")[1]
    assert "Answer in words: Q1: <your words>" in "\n".join(lines)
    code, said = r(repo, "Q1: call it a slot", "--round", round_of(lines))
    assert code == cli.OK and "no option yet" in said[0], said
    assert r(repo, "Q1 a", "--round", round_of(lines))[0] == cli.REFUSED


def test_anchors_lists_a_files_headings_and_missing_doc_offers_the_nearest(repo: Path) -> None:
    terms(repo)
    rev = run_git(repo, "log", "-1", "--format=%H", "--", "docs/spec.md").strip()
    code, lines = w(repo, "anchors", "docs/spec.md")
    assert code == cli.OK and lines == ["spec   # Spec", "land     ## Land", "work     ## Work"]
    assert w(repo, "anchors", "docs/none.md")[0] == cli.NOT_FOUND
    (repo / "docs/kb/product/app/glossary.yml").write_text(
        ("- {id: land, word: land, says: To end., src: [doc:<rev>:docs/spec.md#lnad]}\n"
         "- {id: gate, word: gate, says: A check., src: [doc:<rev>:docs/spec.md#zzz]}\n").replace("<rev>", rev))
    found = [line for line in w(repo, "check")[1] if line.startswith("missing-doc")]
    assert any("(did you mean land" in line for line in found) and any("`ogy anchors docs/spec.md` lists them" in line for line in found)
