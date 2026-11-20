"""Fail when the facts of exercise.md lean on the vocabulary of any arm.

Usage: python3 -I check-neutral.py        (run from anywhere; reads its own folder)

Two checks over the text between "## Facts" and "## Your output" (code spans left out). Both also match plain
inflections, so that "named", "names" and "naming" all match `name`:

1. Names. No kind name and no field name of any arm. Names come from the "Map of kinds" block of every
   inputs/<arm>.md (the word before a line's colon and the field words after it; enum members in brackets and the
   "as above" filler left out; from the legend line, the fields every kind takes) and from names-extra.txt.
   ALLOWED lists the names no English sentence avoids. All of them are field names in every arm built so far.
2. Arm-only words. No content word that the map and glossary of some arm's input use and those of another arm's
   input do not (the like/unlike lines, a reworded glossary line), unless it is a STOP word or is listed with a
   reason in overlap-allowed.txt.
"""

import re
import sys
from pathlib import Path

ALLOWED = {"of", "is", "at", "on", "when", "then", "for", "do", "after", "from", "to"}
STOP = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "not",
    "no",
    "nor",
    "of",
    "is",
    "are",
    "was",
    "be",
    "been",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "to",
    "from",
    "in",
    "on",
    "at",
    "by",
    "for",
    "with",
    "without",
    "as",
    "so",
    "than",
    "then",
    "when",
    "which",
    "who",
    "whose",
    "what",
    "where",
    "how",
    "why",
    "we",
    "us",
    "our",
    "you",
    "your",
    "they",
    "their",
    "them",
    "he",
    "she",
    "his",
    "her",
    "i",
    "me",
    "my",
    "one",
    "two",
    "three",
    "any",
    "all",
    "each",
    "every",
    "some",
    "other",
    "others",
    "more",
    "most",
    "less",
    "only",
    "also",
    "never",
    "ever",
    "always",
    "can",
    "may",
    "must",
    "will",
    "would",
    "should",
    "could",
    "do",
    "does",
    "did",
    "done",
    "has",
    "have",
    "had",
    "there",
    "here",
    "up",
    "down",
    "out",
    "over",
    "under",
    "into",
    "between",
    "before",
    "after",
    "once",
    "again",
    "per",
    "if",
    "else",
    "until",
    "while",
    "because",
    "about",
    "against",
    "own",
    "same",
    "such",
    "just",
    "yet",
    "still",
    "like",
    "unlike",
}
HERE = Path(__file__).resolve().parent


def forms(word: str) -> set[str]:
    """The word and its plain inflections: plural, past, -ing, with a dropped e or a doubled last letter."""
    base = word.removesuffix("e")
    out = {word, word + "s", word + "es", word + "d", base + "ed", base + "ing", word + "ing"}
    out |= {word + word[-1] + "ed", word + word[-1] + "ing"}
    if word.endswith("y"):
        out |= {word[:-1] + "ies", word[:-1] + "ied"}
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
    return set(words(text.split("# Exercise", 1)[0]))


def listed(name: str) -> set[str]:
    lines = (HERE / name).read_text().splitlines()
    return {line.split()[0] for line in lines if line.strip() and not line.startswith("#")}


def main() -> int:
    inputs = sorted((HERE / "inputs").glob("*.md"))
    texts = [path.read_text() for path in inputs]
    names = set().union(*(map_names(text) for text in texts)) | listed("names-extra.txt")
    names -= ALLOWED
    banned = {form: name for name in names for form in forms(name) if form not in ALLOWED}
    given = [given_words(text) for text in texts]
    shared = set.intersection(*given) if given else set()
    arm_only = set().union(*given) - shared - STOP - names - listed("overlap-allowed.txt")
    only = {form: word for word in arm_only for form in forms(word) if form not in STOP}

    facts = (HERE / "exercise.md").read_text().split("## Facts", 1)[1].split("## Your output", 1)[0]
    fact_words = set(words(re.sub(r"`[^`]*`", " ", facts)))
    name_hits = sorted(f"{w} ({banned[w]})" if w != banned[w] else w for w in fact_words if w in banned)
    line_hits = sorted(w for w in fact_words if w in only and w not in banned)
    sys.stdout.write(
        f"arms read: {' '.join(p.stem for p in inputs) or 'none'}; names checked: {len(names)}; arm-only words: {len(arm_only)}\n"
    )
    if name_hits:
        sys.stdout.write(("names used in the facts: " + ", ".join(name_hits)) + "\n")
    if line_hits:
        sys.stdout.write(("arm-only words used in the facts: " + ", ".join(line_hits)) + "\n")
    if name_hits or line_hits:
        return 1
    sys.stdout.write(("facts are neutral") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
