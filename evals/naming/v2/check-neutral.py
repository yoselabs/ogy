"""Fail when the facts of exercise.md lean on the vocabulary of any arm.

Usage: python3 -I check-neutral.py        (run from anywhere; reads its own folder)

Three checks over the text between "## Facts" and "## Your output" (code spans left out). All also match plain
inflections, so that "named", "names" and "naming" all match `name`; a name is also matched through the word it is
built on (`shows` through "show", `handler` through "handles"):

1. Names. No kind name and no field name of any arm. Names come from the "Map of kinds" block of every
   inputs/<arm>.md (the word before a line's colon and the field words after it; enum members in brackets and the
   "as above" filler left out; from the legend line, the fields every kind takes) and from names-extra.txt.
   ALLOWED lists the names no English sentence avoids. All of them are field names in every arm built so far.
2. Enum members. No member that the map of some arm prints in brackets and the map of another arm does not
   (`http` and `message` of one arm's `form`, `one` and `list` of another's `type`): such a word hands one arm a
   field value. A member every arm prints (`number`, `write`) favours none and is not checked.
3. Arm-only words. No content word that the map and glossary of some arm's input use and those of another arm's
   input do not (the like/unlike lines, a reworded glossary line). The prompt above the map is not read.

Checks 2 and 3 skip a STOP word and a word listed with its reason in overlap-allowed.txt.
"""

import re
import sys
from pathlib import Path

ALLOWED = {"of", "is", "at", "on", "when", "then", "for", "do", "after", "from", "to"}
STOP = {
    "a", "an", "the", "and", "or", "but", "not", "no", "nor", "of", "is", "are", "was", "be", "been", "it", "its", "this", "that",
    "these", "those", "to", "from", "in", "on", "at", "by", "for", "with", "without", "as", "so", "than", "then", "when", "which",
    "who", "whose", "what", "where", "how", "why", "we", "us", "our", "you", "your", "they", "their", "them", "he", "she", "his",
    "her", "i", "me", "my", "one", "two", "three", "any", "all", "each", "every", "some", "other", "others", "more", "most", "less",
    "only", "also", "never", "ever", "always", "can", "may", "must", "will", "would", "should", "could", "do", "does", "did", "done",
    "has", "have", "had", "there", "here", "up", "down", "out", "over", "under", "into", "between", "before", "after", "once",
    "again", "per", "if", "else", "until", "while", "because", "about", "against", "own", "same", "such", "just", "yet", "still",
    "like", "unlike"
}
HERE = Path(__file__).resolve().parent


def forms(word: str) -> set[str]:
    """The word and its plain inflections: plural, past, -ing, with a dropped e or a doubled last letter."""
    base = word[:-1] if word.endswith("e") else word
    out = {word, word + "s", word + "es", word + "d", base + "ed", base + "ing", word + "ing"}
    out |= {word + word[-1] + "ed", word + word[-1] + "ing"}
    if word.endswith("y"):
        out |= {word[:-1] + "ies", word[:-1] + "ied"}
    return out


def roots(name: str) -> set[str]:
    """A name and what it is built on: `shows` is also show, `handler` also handle, `satisfies` also satisfy."""
    out = {name}
    if name.endswith("ies") and len(name) > 5:
        out.add(name[:-3] + "y")
    if name.endswith("es") and len(name) > 4:
        out.add(name[:-1])
    if name.endswith("s") and not name.endswith("ss") and len(name) > 3:
        out.add(name[:-1])
    if name.endswith("er") and len(name) > 5:
        out |= {name[:-1], name[:-2]}
    return out


def words(text: str) -> list[str]:
    return re.findall(r"[a-z_]+", text.lower())


def map_names(text: str) -> set[str]:
    block = text.split("## Map of kinds", 1)[1].split("## Glossary", 1)[0]
    names: set[str] = set()
    for line in block.splitlines():
        if line.startswith(("rules:", "kinds, like and unlike:")):
            break
        if line.startswith("!"):  # the legend line: only the fields every kind takes
            names.update(words(line.partition("every kind also takes")[2]))
            continue
        head, _, fields = line.partition(":")
        if not fields.strip() or fields.strip() == "as above":
            continue
        names.update(words(head.replace("[]", "")))
        names.update(words(re.sub(r"\([^)]*\)", " ", fields)))
    return names


def given_words(text: str) -> set[str]:
    """The words of the map and the glossary of one input: not the prompt above them, not the exercise below."""
    return set(words(text.split("## Map of kinds", 1)[1].split("# Exercise", 1)[0]))


def map_members(text: str) -> set[str]:
    """The enum members a map prints in brackets: `form(web|cli|http)` gives web, cli, http."""
    block = text.split("## Map of kinds", 1)[1].split("## Glossary", 1)[0].split("\nrules:", 1)[0]
    return {word for group in re.findall(r"\(([a-z_|]+)\)", block) for word in group.split("|")}


def listed(name: str) -> set[str]:
    lines = (HERE / name).read_text().splitlines()
    return {line.split()[0] for line in lines if line.strip() and not line.startswith("#")}


def main() -> int:
    inputs = sorted((HERE / "inputs").glob("*.md"))
    texts = [path.read_text() for path in inputs]
    names = set().union(*(map_names(text) for text in texts)) | listed("names-extra.txt")
    names -= ALLOWED
    banned = {form: name for name in names for root in roots(name) for form in forms(root) if form not in ALLOWED}
    given = [given_words(text) for text in texts]
    shared = set.intersection(*given) if given else set()
    allowed = listed("overlap-allowed.txt")
    members = [map_members(text) for text in texts]
    some_members = (set().union(*members) - set.intersection(*members) if members else set()) - names
    member_forms = {form: word for word in some_members - allowed for form in forms(word)}
    arm_only = set().union(*given) - shared - STOP - names - allowed - some_members
    only = {form: word for word in arm_only for form in forms(word) if form not in STOP}

    facts = (HERE / "exercise.md").read_text().split("## Facts", 1)[1].split("## Your output", 1)[0]
    fact_words = set(words(re.sub(r"`[^`]*`", " ", facts)))
    name_hits = sorted(f"{w} ({banned[w]})" if w != banned[w] else w for w in fact_words if w in banned)
    member_hits = sorted(w for w in fact_words if w in member_forms and w not in banned)
    line_hits = sorted(w for w in fact_words if w in only and w not in banned)
    print(f"arms read: {' '.join(p.stem for p in inputs) or 'none'}; names checked: {len(names)}; "
          f"members only some arms print: {len(some_members)}; arm-only words: {len(arm_only)}")
    if name_hits:
        print("names used in the facts: " + ", ".join(name_hits))
    if member_hits:
        print("enum members only some arms print, used in the facts: " + ", ".join(member_hits))
    if line_hits:
        print("arm-only words used in the facts: " + ", ".join(line_hits))
    if name_hits or member_hits or line_hits:
        return 1
    print("facts are neutral")
    return 0


if __name__ == "__main__":
    sys.exit(main())
