"""`ogy migrate` when what an agreement holds is computed another way: a step's agreement now covers the rows read with it,
a term's the sentence it names (`Snapshot.agreed_print`). An agreement whose hash is still the entry's plain fingerprint is
re-set to the new hash only when the entry and every part read with it are as they were in the commit that wrote the
agreement; otherwise it stays as it is, and the entry comes back to the owner as changed since agreed."""

from pathlib import Path

from git_porcelain import RealRepo
from git_porcelain.errors import GitError

from ogy.fieldtypes import AGREED_HASH
from ogy.kindchange import migrated
from ogy.model import Address
from ogy.ontology import Ontology
from ogy.retype import applied
from ogy.snapshot import Snapshot, build, load
from ogy.source import GitSource

LIMIT = 500  # commits read back from HEAD to find the one that wrote an agreement


def _stamp(snapshot: Snapshot, address: Address) -> str | None:
    agreed = snapshot.entries[address].fields.get(snapshot.ontology.roles.agreed)
    found = agreed.get(AGREED_HASH) if isinstance(agreed, dict) else None
    return found if isinstance(found, str) else None


def _writer(repo: Path, kb: str, ontology: Ontology, rel: str, address: Address, stamp: str, shas: list[str]) -> str | None:
    """The oldest commit of the unbroken run back from HEAD whose file holds the entry agreed with `stamp`."""
    found = None
    for sha in shas:
        text = GitSource(repo, sha, kb).read([rel]).get(rel)
        then = build(ontology, applied(ontology, {rel: text})) if text is not None else None
        if then is None or address not in then.entries or _stamp(then, address) != stamp:
            break
        found = sha
    return found


def proven(repo: Path, kb: str, snapshot: Snapshot) -> dict[Address, dict[str, object]]:
    """Each agreement written under the plain fingerprint whose entry, with the parts read with it, is unchanged since the
    commit that wrote it -> the agreement re-set to the hash it is agreed under now."""
    stale = [address for address in sorted(snapshot.entries) if (stamp := _stamp(snapshot, address)) is not None
             and stamp == snapshot.fingerprint(address) != snapshot.agreed_print(address)]
    if not stale:
        return {}
    try:
        shas = [entry.sha for entry in RealRepo(repo).history(["HEAD"], limit=LIMIT)]
    except GitError:
        return {}
    then: dict[str, Snapshot] = {}
    found: dict[Address, dict[str, object]] = {}
    for address in stale:
        stamp, agreed = _stamp(snapshot, address), snapshot.entries[address].fields.get(snapshot.ontology.roles.agreed)
        sha = _writer(repo, kb, snapshot.ontology, snapshot.entries[address].path, address, stamp or "", shas)
        if sha is None or not isinstance(agreed, dict):
            continue
        if sha not in then:
            then[sha] = migrated(load(GitSource(repo, sha, kb), snapshot.ontology, retyped=True))
        if address in then[sha].entries and then[sha].agreed_print(address) == snapshot.agreed_print(address):
            found[address] = {**agreed, AGREED_HASH: snapshot.agreed_print(address)}
    return found
