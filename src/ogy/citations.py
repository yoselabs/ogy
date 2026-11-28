"""What cites an answered decision, so that one whose answer sets no entry stops being work (decision
software/cli/decision/answered-uncited-is-work, answered computed; decision software/cli/decision/where-a-code-answer-lands,
answered code-cites). A decision is cited by a kind file or field (`because`), by an entry (`because`), or by code: the text
"decision <address>" in a docstring of a tracked source file of a scheme that reads symbols. Computed, never stored.

Built here: decision software/cli/decision/answered-uncited-is-work.
"""

import re
lazy from collections.abc import Collection, Mapping

from ogy.declared import Reader
from ogy.kindreasons import cited as kind_cited
from ogy.settle import decisions
lazy from ogy.model import Address
lazy from ogy.snapshot import Snapshot

__all__ = ["code_suffixes", "in_code", "uncited"]

DOCSTRING = re.compile(r'"""(.*?)"""', re.DOTALL)
CITE = re.compile(r"\bdecision\s+([a-z0-9_-]+/[a-z0-9_-]+/decision/[a-z0-9_-]+)")


def code_suffixes(snapshot: Snapshot) -> tuple[str, ...]:
    """The file suffixes of the evidence schemes that read code symbols: where a docstring may cite a decision."""
    schemes = snapshot.ontology.declared.evidence.values()
    return tuple(sorted({suffix for scheme in schemes if scheme.reads is Reader.SYMBOL for suffix in scheme.files}))


def in_code(texts: Mapping[str, str]) -> set[str]:
    """Every decision address a docstring names as "decision <address>"."""
    return {found for text in texts.values() for doc in DOCSTRING.findall(text) for found in CITE.findall(doc)}


def uncited(snapshot: Snapshot, code: Collection[str]) -> list[Address]:
    """The answered decisions whose answer in force sets no entry and that nothing cites: work left."""
    because = snapshot.ontology.roles.because
    cited = kind_cited(snapshot.ontology) | set(code)
    cited |= {str(target) for address in snapshot.entries for target in snapshot.links.forward(address, because)}
    found = []
    for decision in decisions(snapshot):
        force = decision.in_force
        if force is not None and force.by_answer and not force.sets and str(decision.address) not in cited:
            found.append(decision.address)
    return sorted(found)
