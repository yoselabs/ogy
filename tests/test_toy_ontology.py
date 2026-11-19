"""The acceptance test of a generic engine: a toy ontology in which every kind, field, layer, harm tag, evidence scheme, shared
area and fixed folder has another name than the software ontology's, read from a folder on disk. check, review, reply, answer,
put, remove, glossary and init work on it unchanged."""

from pathlib import Path

import any_yaml
import pytest
from git_porcelain import run_git
from tests.conftest import IDENTITY, ogy

from ogy import cli
from ogy.ontology import Ontology, named, packaged

TOY = Path(__file__).parent / "fixtures" / "toy-ontology"
LIMIT = "business/shop/ruling/limit"
FILES = {
    "app.py": "def buy():\n    return True\n",
    "docs/kb/charter/tenets.yml": "- {id: plain-words, tells: A sentence says one thing in plain words., reasoning: Read once.}\n",
    "docs/kb/business/common/region.yml": "tells: What two regions of this layer both use.\n",
    "docs/kb/business/common/people.yml": "- {id: boss, tells: The person who rules on the questions., sort: human}\n",
    "docs/kb/business/shop/region.yml": "tells: Buying things in the shop.\n",
    "docs/kb/business/shop/people.yml": "- {id: shopper, tells: A person who buys., sort: human, source: ['py:app.py#buy']}\n",
    "docs/kb/business/shop/words.yml": "- {id: basket, spelling: basket, tells: What a shopper holds before paying., shun: [cart]}\n",
    "docs/kb/business/shop/journey/buy.yml": """\
tells: A shopper buys.
first: pick
source: ['py:app.py#buy']
stages:
  pick:
    tells: The shopper picks.
    who: business/shop/person/shopper
    moves:
      go: {caption: Buy, next: done}
finishes:
  done: {tells: Bought.}
""",
    "docs/kb/business/shop/norm/limit.yml": "tells: A basket holds at most ten things.\nmoney: true\n",
    f"docs/kb/{LIMIT}.yml": """\
ask: How many things may a basket hold?
background: Shops differ.
picks:
  ten: {caption: Ten, gives: {business/shop/norm/limit: {tells: A basket holds at most ten things.}}}
  twenty: {caption: Twenty, gives: {business/shop/norm/limit: {tells: A basket holds at most twenty things.}}}
hunch: {picked: ten, grounds: Small shops.}
""",
    "docs/kb/business/shop/ruling/folders.yml": """\
ask: Do regions get subfolders?
layout: true
picks: {flat: {caption: No}, deep: {caption: Yes}}
hunch: {picked: flat, grounds: Keep it flat.}
""",
    "docs/kb/tech/shop/region.yml": "tells: The pages of the shop.\n",
    "docs/kb/tech/shop/screen/page.yml": (
        "tells: The buying page.\nserves_stages: [business/shop/journey/buy/stage/pick]\nsource: ['py:app.py#buy']\n"),
}


def _names(ontology: Ontology) -> set[str]:
    found = {*ontology.kinds, *ontology.layers, *ontology.common, *ontology.declared.harms, *ontology.declared.evidence, ontology.shared}
    for kind in ontology.kinds.values():
        found |= {*kind.fields, *(item for item in (kind.key, kind.file, kind.area) if item)}
    return found


@pytest.fixture
def toy(tmp_path: Path) -> Path:
    run_git(tmp_path, "init", "-q", "-b", "main")
    for rel, text in {**FILES, "ogy.yml": f"ontology: {TOY}\n"}.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    run_git(tmp_path, *IDENTITY, "add", "-A")
    run_git(tmp_path, *IDENTITY, "commit", "-q", "-m", "toy")
    return tmp_path


def w(repo: Path, *argv: str) -> tuple[int, list[str]]:
    return ogy(repo, "--rev", ".", *argv)


def said(*argv: str) -> tuple[str, ...]:
    return (*argv, "--said", "Fine", "--where", "ai:test/1")


def read(repo: Path, rel: str) -> object:
    return any_yaml.load((repo / "docs/kb" / rel).read_text())


def test_the_toy_ontology_shares_no_name_with_the_software_one() -> None:
    toy = named(str(TOY), Path("."))
    assert _names(toy) & _names(packaged()) == set()
    assert toy.layers == ("business", "tech") and toy.roles.agreed == "accepted" and toy.declared.asked_alone == ("layout",)


def test_check_and_the_glossary_read_the_toy_names(toy: Path) -> None:
    assert w(toy, "check")[0] == cli.OK
    code, lines = w(toy, "glossary")
    assert code == cli.OK and lines[:2] == ["charter (every decision is judged against these):",
                                            "  plain-words: A sentence says one thing in plain words."]
    assert "    reasoning: Read once." in lines and "  basket: What a shopper holds before paying." in lines and "    shun: cart" in lines


def test_put_adds_and_refuses_by_the_toy_roles(toy: Path) -> None:
    code, lines = w(toy, "put", '{"address": "business/shop/person/clerk", "tells": "Fills a cart.", "sort": "human"}')
    assert code == cli.REFUSED and "avoided-word" in lines[0] and "'cart'" in lines[0]
    long = " ".join(["word"] * 10)
    code, lines = w(toy, "put", f'{{"address": "business/shop/word_entry/till", "spelling": "till", "tells": "{long}"}}')
    assert code == cli.REFUSED and "a word_entry says one line of under 10 words, not 10" in lines[0]
    code, lines = w(toy, "put", '{"address": "business/shop/norm/receipt", "tells": "A purchase prints a receipt."}')
    assert code == cli.REFUSED and "no source, no reason, no decision settling it and no person's yes" in lines[0]
    entry = '{"address": "business/shop/norm/receipt", "tells": "A purchase prints a receipt.", "reason": ["charter/tenet/plain-words"]}'
    assert w(toy, "put", entry)[0] == cli.OK and w(toy, "check")[0] == cli.OK


def test_answer_writes_a_verdict_and_the_boss_accepts_what_it_gives(toy: Path) -> None:
    code, _ = w(toy, *said("answer", LIMIT, "twenty"))
    assert code == cli.OK and w(toy, "check")[0] == cli.OK
    ruling, norm = read(toy, f"{LIMIT}.yml"), read(toy, "business/shop/norm/limit.yml")
    assert isinstance(ruling, dict) and isinstance(norm, dict)
    assert [{key: item[key] for key in ("picked", "gist", "place")} for item in ruling["verdicts"]] == [
        {"picked": "twenty", "gist": "Fine", "place": "ai:test/1"}]
    assert norm["tells"] == "A basket holds at most twenty things." and set(norm["accepted"]) == {"moment", "place", "gist", "hash"}


def test_review_asks_the_layout_ruling_alone_and_reply_answers_it(toy: Path) -> None:
    code, lines = w(toy, "review")
    text = "\n".join(lines)
    assert code == cli.OK and "Q1. question  business/shop/ruling/folders  (layout)" in text and "Why it comes up: Shops differ." in text
    assert "Structural, not covered by yes or yes all: Q1; each needs its own letter." in text
    code, lines = w(toy, *said("reply", "yes all"))
    assert code == cli.OK and "business/shop/ruling/folders is structural" in lines[0]
    assert w(toy, *said("reply", "Q1 a"))[0] == cli.OK
    folders = read(toy, "business/shop/ruling/folders.yml")
    assert isinstance(folders, dict) and folders["verdicts"][0]["picked"] == "flat"
    boss = read(toy, "business/common/people.yml")
    assert isinstance(boss, list) and "accepted" in boss[0] and w(toy, "check")[0] == cli.OK


def test_no_to_a_card_asks_a_ruling_in_the_toy_names(toy: Path) -> None:
    w(toy, "review")
    assert w(toy, *said("reply", "yes all"))[0] == cli.OK
    entry = '{"address": "business/shop/norm/receipt", "tells": "A purchase prints a receipt.", "reason": ["charter/tenet/plain-words"]}'
    w(toy, "put", entry)
    code, lines = w(toy, "review")
    assert code == cli.OK and "1. yes  business/shop/norm/receipt" in lines
    code, lines = w(toy, *said("reply", "no 1"))
    assert code == cli.OK and lines == ["no 1: business/shop/norm/receipt is now a question: business/shop/ruling/reconsider-receipt"]
    asked = read(toy, "business/shop/ruling/reconsider-receipt.yml")
    assert isinstance(asked, dict) and set(asked) == {"ask", "background", "picks", "hunch"}
    assert asked["picks"]["keep"] == {"caption": "Keep it as it is",
                                      "gives": {"business/shop/norm/receipt": {"tells": "A purchase prints a receipt."}}}
    assert asked["hunch"] == {"picked": "keep", "grounds": "Built as it is until the owner answers."} and w(toy, "check")[0] == cli.OK


def test_remove_records_the_entry_in_its_ledger(toy: Path) -> None:
    code, _ = w(toy, "remove", "tech/shop/screen/page", "--why", "not needed")
    assert code == cli.OK and not (toy / "docs/kb/tech/shop/screen/page.yml").exists()
    ledger = read(toy, "tech/shop/removed.yml")
    assert isinstance(ledger, dict) and [(item["id"], item["said"]) for item in ledger["items"]] == [
        ("tech/shop/screen/page", "The buying page.")]
    code, lines = w(toy, "find", "page", "--removed")
    assert code == cli.OK and any("tech/shop/screen/page" in line for line in lines)


def test_init_writes_what_the_toy_folder_declares(tmp_path: Path) -> None:
    code, _ = cli.run(["--repo", str(tmp_path), "init", "--ontology", str(TOY)])
    assert code == cli.OK
    assert read(tmp_path, "business/common/region.yml") == {"tells": "What two regions of this layer both use."}
    tenets = read(tmp_path, "charter/tenets.yml")
    assert isinstance(tenets, list) and [item["id"] for item in tenets] == ["plain-words"]
    assert "## Toy knowledge base" in (tmp_path / "AGENTS.md").read_text()
    assert cli.run(["--repo", str(tmp_path), "init", "--check"])[0] == cli.OK


def test_the_flow_and_the_kind_printers_follow_the_toy_names(toy: Path) -> None:
    code, lines = w(toy, "diagram", "business/shop/journey/buy")
    assert code == cli.OK and '  journey_buy_stage_pick -- "Buy" --> journey_buy_finish_done' in lines
    code, lines = w(toy, "kinds", "--readers")
    assert code == cli.OK and "word_entry.spelling: check word-clash, fingerprint, printer glossary" in lines
    assert "move.caption: check avoided-word, fingerprint, printer diagram, printer review" in lines
    code, lines = w(toy, "kinds", "--map")
    assert code == cli.OK and lines[0].endswith("every kind also takes heading, source, reason, held_by, tests, accepted")


def test_migrate_follows_a_toy_kind_and_common_field_renamed(toy: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    """The toy ontology renames its kind norm to canon (`was`) and its common field held_by to bound_by (`renamed`)."""
    folder = tmp_path_factory.mktemp("toy-renamed")
    for item in (TOY / "kinds").iterdir():
        text = item.read_text().replace("[norm, person]", "[canon, person]")
        name = "canon" if item.name == "norm.yml" else item.stem
        text = text.replace("kind: norm\n", "kind: canon\nwas: {kind: norm}\n")
        (folder / "kinds").mkdir(exist_ok=True)
        (folder / "kinds" / f"{name}.yml").write_text(text)
    declared = (TOY / "ontology.yml").read_text().replace("  held_by: {type: links, to: [norm], note: true}",
                                                         "  bound_by: {type: links, to: [canon], note: true}")
    (folder / "ontology.yml").write_text(declared.replace("roles:", "renamed: {held_by: bound_by}\nroles:"))
    journey = toy / "docs/kb/business/shop/journey/buy.yml"
    journey.write_text(journey.read_text() + "held_by: [business/shop/norm/limit]\n")
    run_git(toy, *IDENTITY, "commit", "-qam", "held to the limit")
    (toy / "ogy.yml").write_text(f"ontology: {folder}\n")
    found = w(toy, "check")[1]
    assert any(line.startswith("needs-migration: business/shop/norm/limit.yml") for line in found)
    assert any("held_by is now bound_by" in line for line in found)
    assert w(toy, "migrate")[0] == cli.OK and w(toy, "check")[1][0] == "ok"
    bought = read(toy, "business/shop/journey/buy.yml")
    assert isinstance(bought, dict) and bought["bound_by"] == ["business/shop/canon/limit"] and "held_by" not in bought
    assert (toy / "docs/kb/business/shop/canon/limit.yml").is_file() and not (toy / "docs/kb/business/shop/norm").exists()
    assert "business/shop/canon/limit" in (toy / f"docs/kb/{LIMIT}.yml").read_text()  # the ruling gives the new address
