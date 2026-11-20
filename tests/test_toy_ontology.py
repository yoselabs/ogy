"""The acceptance test of a generic engine: a toy ontology in which every kind, field, layer, harm tag, evidence scheme, shared
area and fixed folder has another name than the software ontology's, read from a folder on disk. check, review, reply, answer,
put, remove, glossary and init work on it unchanged."""

from pathlib import Path

import any_yaml
import pytest
from git_porcelain import run_git
from tests.conftest import IDENTITY, ogy

from ogy import built, cli, ops, writes
from ogy.model import Address, parse_address
from ogy.ontology import Ontology, named, packaged
from ogy.snapshot import Snapshot, build
from ogy.target import Target

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


def test_requirements_cycles_and_requirements_that_are_work_follow_the_toy_names(toy: Path) -> None:
    """A finish reached by a move captioned Buy (`<-next?caption=Buy|Pay`) or of an invoked journey (`^`, `<-invokes`) unless
    quiet (`if_unset`); a stage a person acts at with no screen is work, not a finding; a screen never nests itself."""
    buy, page = toy / "docs/kb/business/shop/journey/buy.yml", toy / "docs/kb/tech/shop/screen/page.yml"
    buy.write_text(buy.read_text().replace("caption: Buy", "caption: Look"))
    assert [line.split(":")[0] for line in w(toy, "check")[1] if not line.startswith("waiting")] == ["unmet-requirement"]
    buy.write_text(buy.read_text().replace("done: {tells: Bought.}", "done: {tells: Bought., quiet: true}"))
    assert w(toy, "check")[0] == cli.OK
    page.write_text(page.read_text() + "nests: [tech/shop/screen/page]\n")
    assert any(line.startswith("link-cycle: tech/shop/screen/page.yml") for line in w(toy, "check")[1])
    page.unlink()
    assert w(toy, "check")[0] == cli.OK
    assert "unserved: business/shop/journey/buy/stage/pick (now -, built -) a stage a person acts at has a screen" in w(toy, "work")[1]


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
    assert "move.caption: check avoided-word, fingerprint, printer diagram, printer review, requires" in lines
    code, lines = w(toy, "kinds", "--map")
    assert code == cli.OK and lines[0].endswith("every kind also takes heading, source, reason, held_by, tests, accepted")


def test_migrate_follows_a_toy_kind_and_common_field_renamed(toy: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    """The toy ontology renames its kind norm to canon (`was`) and its common field held_by to bound_by (`renamed`)."""
    folder = tmp_path_factory.mktemp("toy-renamed")
    for item in (TOY / "kinds").iterdir():
        text = item.read_text().replace("[norm, person]", "[canon, person]").replace("held_by", "bound_by")
        name = "canon" if item.name == "norm.yml" else item.stem
        text = text.replace("kind: norm\n", "kind: canon\nwas: {kind: norm}\n")
        (folder / "kinds").mkdir(exist_ok=True)
        (folder / "kinds" / f"{name}.yml").write_text(text)
    declared = (TOY / "ontology.yml").read_text().replace("  held_by: {type: links, to: [norm], note: true,",
                                                         "  bound_by: {type: links, to: [canon], note: true,")
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


PICK = "business/shop/journey/buy/stage/pick"
NORM = "business/shop/norm/limit"


def _held(norm: str = NORM, tells: str = "A basket holds at most ten things.", rank: str = "") -> Snapshot:
    """The toy shop with its move held to a norm (`input: {held_by: content}`) and a branch held to one (`address`)."""
    texts = {rel.removeprefix("docs/kb/"): text for rel, text in FILES.items() if rel.startswith("docs/kb/")}
    journey = texts["business/shop/journey/buy.yml"].replace("next: done}", f"next: done, held_by: [{norm}]}}")
    branch = f"    branches:\n      on: {{next: done, held_by: [{norm}]{rank}}}\n"
    texts["business/shop/journey/buy.yml"] = journey.replace("    moves:", branch + "    moves:")
    texts[f"{NORM}.yml"] = f"tells: {tells}\nmoney: true\n"
    texts["business/shop/norm/other.yml"] = "tells: Another norm.\n"
    return build(named(str(TOY), Path(".")), texts)


def _at(snapshot: Snapshot, text: str) -> Address:
    address = parse_address(text, snapshot.ontology)
    assert address is not None and address in snapshot.entries, text
    return address


def test_a_content_input_makes_the_build_stale_and_an_address_input_only_on_a_relink() -> None:
    before, reworded, relinked = _held(), _held(tells="A basket holds at most twenty things."), _held("business/shop/norm/other")
    move, branch = f"{PICK}/move/go", f"{PICK}/branch/on"
    def hashes(snapshot: Snapshot, text: str) -> tuple[str, str]:
        return snapshot.fingerprint(_at(snapshot, text)), snapshot.build_hash(_at(snapshot, text))
    assert hashes(reworded, move)[0] == hashes(before, move)[0]  # the meaning holds: nothing goes back to the owner
    assert hashes(reworded, move)[1] != hashes(before, move)[1]  # content: the norm changed, the move is work
    assert hashes(reworded, branch) == hashes(before, branch)  # address: the norm's words are no input of the branch
    assert hashes(relinked, branch)[0] == hashes(before, branch)[0] and hashes(relinked, branch)[1] != hashes(before, branch)[1]
    assert hashes(reworded, PICK)[1] != hashes(before, PICK)[1]  # a stage reads its moves (`input: {move: content}`)


def test_a_reverse_input_reads_what_links_here_only_where_set() -> None:
    before, ranked = _held(), _held(rank=", rank: 2")
    norm = _at(before, NORM)
    assert ranked.fingerprint(norm) == before.fingerprint(norm)
    assert ranked.build_hash(norm) != before.build_hash(norm)  # `input_from: {held_by: {fields: [rank]}}`


def _folder(root: Path, kinds: dict[str, str], servers: str) -> Path:
    """The toy ontology with its kinds `{name: text}` added or replaced (an empty text leaves one out), served by `servers`."""
    (root / "kinds").mkdir(parents=True)
    (root / "ontology.yml").write_text((TOY / "ontology.yml").read_text())
    texts = {item.stem: item.read_text() for item in (TOY / "kinds").iterdir()} | kinds
    for name, text in texts.items():
        if text:
            (root / "kinds" / f"{name}.yml").write_text(text.replace("servers: [screen]", f"servers: {servers}").replace(
                "kinds: [screen]", f"kinds: {servers}"))
    return root


def test_migrate_merges_two_toy_kinds_into_one(toy: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    """A toy kind console beside screen, then both merged into surface (`was` lists them): a console's `typed_as` is `typed`."""
    screen = "".join(line for line in (TOY / "kinds/screen.yml").read_text().splitlines(keepends=True) if "nests" not in line)
    console = screen.replace("kind: screen", "kind: console").replace("  shows_moves:", "  typed_as: {}\n  shows_moves:")
    surface = "was: [{kind: screen}, {kind: console, renamed: {typed_as: typed}}]\n" + screen.replace(
        "kind: screen", "kind: surface").replace("  shows_moves:", "  typed: {}\n  shows_moves:")
    two = _folder(tmp_path_factory.mktemp("toy-console"), {"console": console}, "[screen, console]")
    one = _folder(tmp_path_factory.mktemp("toy-merged"), {"screen": "", "surface": surface}, "[surface]")
    (toy / "ogy.yml").write_text(f"ontology: {two}\n")
    (toy / "docs/kb/tech/shop/console/till.yml").parent.mkdir(parents=True)
    (toy / "docs/kb/tech/shop/console/till.yml").write_text(
        "tells: The till.\nserves_stages: [business/shop/journey/buy/stage/pick]\ntyped_as: buy\nsource: ['py:app.py#buy']\n")
    (toy / "docs/kb/tech/shop/norm").mkdir()
    (toy / "docs/kb/tech/shop/norm/quick.yml").write_text("tells: Paying takes a minute.\nreason: [tech/shop/console/till]\n")
    old, served = Target(toy, ontology=str(two)), ("tech/shop/screen/page", "tech/shop/console/till")
    writes.agree(old, writes.said("Yes", "ai:test/1", None), list(served))
    for text in served:
        at = parse_address(text, old.kinds())
        assert at is not None
        built.stamp(toy / "docs/kb", old.read()[1].entries[at].path, text, built.Line(old.read()[1].build_hash(at)))
    assert w(toy, "check")[0] == cli.OK
    run_git(toy, *IDENTITY, "add", "-A")
    run_git(toy, *IDENTITY, "commit", "-qm", "a console")
    base = run_git(toy, "rev-parse", "HEAD").strip()
    (toy / "ogy.yml").write_text(f"ontology: {one}\n")
    assert any(line.startswith("needs-migration: tech/shop/console/till.yml") for line in w(toy, "check")[1])
    assert w(toy, "migrate")[0] == cli.OK and w(toy, "check")[1][0] == "ok"
    till = read(toy, "tech/shop/surface/till.yml")
    assert isinstance(till, dict) and till["typed"] == "buy" and "typed_as" not in till
    assert (toy / "docs/kb/tech/shop/surface/page.yml").is_file() and not (toy / "docs/kb/tech/shop/screen").exists()
    norm = read(toy, "tech/shop/norm/quick.yml")
    assert isinstance(norm, dict) and norm["reason"] == ["tech/shop/surface/till"]
    now = Target(toy, ontology=str(one))
    snapshot, work = now.read()[1], {item.address for item in ops.run_work(now).value}
    for text in ("tech/shop/surface/page", "tech/shop/surface/till"):
        at = parse_address(text, now.kinds())
        assert at is not None and snapshot.entries[at].fields["accepted"]["hash"] == snapshot.fingerprint(at) and at not in work
    run_git(toy, *IDENTITY, "add", "-A")
    run_git(toy, *IDENTITY, "commit", "-qm", "merged")
    assert not ops.run_check(Target(toy, rev="HEAD", ontology=str(one)), base=base).value


def test_a_kind_gaining_an_input_field_makes_no_work_and_unsetting_an_input_does(tmp_path: Path) -> None:
    extra = "fields:\n  extra: {type: links, to: [norm], input: content}\n"
    stage = (TOY / "kinds" / "stage.yml").read_text().replace("fields:\n", extra, 1)
    grown = named(str(_folder(tmp_path / "grown", {"stage": stage}, "[screen]")), Path("."))
    before = _held()
    texts = {rel.removeprefix("docs/kb/"): text for rel, text in FILES.items() if rel.startswith("docs/kb/")}
    same, plain = build(grown, texts), build(named(str(TOY), Path(".")), texts)
    assert same.build_hash(_at(same, PICK)) == plain.build_hash(_at(plain, PICK))  # a new, unset input adds nothing: no work
    move = f"{PICK}/move/go"
    assert before.build_hash(_at(before, move)) != plain.build_hash(_at(plain, move))  # set -> unset of `held_by` moves the hash


def test_a_link_into_a_later_toy_layer_is_a_finding(toy: Path) -> None:
    """`link_direction: later-to-earlier`: tech names business; a business entry naming tech is `layer-direction`."""
    norm = toy / "docs/kb/business/shop/norm/limit.yml"
    norm.write_text(norm.read_text() + "reason: [tech/shop/screen/page]\n")
    assert [line.split(":")[0] for line in w(toy, "check")[1] if not line.startswith("waiting")] == ["layer-direction"]


def test_a_stage_a_machine_acts_at_comes_back_through_a_screen_wired_to_the_machine(toy: Path) -> None:
    """`if_reaches: [who?sort=machine]` (a forward hop kept by the target's field), then a path that comes back to the stage
    itself (`same`): a stage a machine acts at is served by a screen wired to that machine."""
    people, page = toy / "docs/kb/business/shop/people.yml", toy / "docs/kb/tech/shop/screen/page.yml"
    people.write_text(people.read_text().replace("sort: human", "sort: machine"))
    assert [line.split(":")[0] for line in w(toy, "check")[1] if not line.startswith("waiting")] == ["unmet-requirement"]
    page.write_text(page.read_text() + "wired_to: [business/shop/person/shopper]\n")
    assert w(toy, "check")[0] == cli.OK
