"""`ogy view`: the product as one self-contained web page, computed from the entries on demand, never committed.

A sitemap of every area, each one told as a short narrative (goals, capabilities, workflows, things it keeps), and each
workflow, thing, interface and decision opening to its parts. Nothing here is a rule: it only reads the snapshot.
"""

from html import escape

from ogy.flowcheck import graph, link
from ogy.model import Address
from ogy.viewpage import PAGE
lazy from ogy.snapshot import Snapshot

# The kinds an area page lists, in the order a reader meets them: why, what, how, what it keeps, who and where, why this way.
SECTIONS: tuple[tuple[str, str], ...] = (
    ("goal", "Goals"),
    ("capability", "What it can do"),
    ("workflow", "Workflows"),
    ("entity", "Things it keeps"),
    ("actor", "Who is involved"),
    ("interface", "Where people reach it"),
    ("rule", "Rules"),
    ("decision", "Decisions"),
)
LAYERS = ("product", "software")


def slug(text: str) -> str:
    return text.replace("/", "-")


def said(snapshot: Snapshot, address: Address) -> str:
    """What the entry says: its sentence, else its question (a decision) or its words."""
    fields = snapshot.entries[address].fields
    for name in ("says", "question", "label", "title"):
        value = fields.get(name)
        if isinstance(value, str):
            return value
    return snapshot.sentence(address) or address.key


def plain(text: str) -> str:
    """A sentence to continue another: no closing full stop, first letter lower (names such as Git keep theirs)."""
    text = text.rstrip(".")
    return text[:1].lower() + text[1:]


def named(address: Address) -> str:
    return address.key or address.kind


def tag(name: str, body: str, css: str = "") -> str:
    return f'<{name} class="{css}">{body}</{name}>' if css else f"<{name}>{body}</{name}>"


def fold(title: str, sentence: str, body: str, *, css: str = "") -> str:
    """One entry that opens: its name and sentence on the line, its parts inside."""
    summary = f"<summary><b>{escape(title)}</b> <span>{escape(sentence)}</span></summary>"
    return f'<details class="{css}">{summary}{body}</details>'


def listing(items: list[str]) -> str:
    return tag("ul", "".join(tag("li", item) for item in items)) if items else ""


def workflow(snapshot: Snapshot, address: Address) -> str:
    """The steps in order: who acts, what they can choose, and where each choice leads."""
    flow = snapshot.kind_of(address).flow
    if flow is None:
        return ""
    walk = graph(snapshot, flow, address)
    start = [named(step) for step in link(snapshot, address, flow.start)]
    items = []
    for step in walk.steps:
        who = [named(actor) for actor in link(snapshot, step, flow.actor)]
        line = f"<b>{escape(named(step))}</b> {escape(said(snapshot, step))}"
        if who:
            line += f' <i class="who">{escape(", ".join(who))}</i>'
        rows = [
            f"{escape(str(snapshot.entries[row].fields.get('label') or said(snapshot, row)))} "
            f"&rarr; {escape(', '.join(named(target) for target in link(snapshot, row, flow.then)))}"
            for kind in (flow.choice, flow.case, flow.timeout)
            for row in walk.rows[step][kind]
        ]
        items.append(line + listing(rows))
    ends = [f"<b>{escape(named(end))}</b> {escape(said(snapshot, end))}" for end in walk.ends]
    first = f'<p class="start">starts at <b>{escape(", ".join(start))}</b></p>' if start else ""
    return first + listing(items) + (tag("h4", "Ends") + listing(ends) if ends else "")


def entity(snapshot: Snapshot, address: Address) -> str:
    parts = snapshot.links.parts
    blocks = []
    for kind, title in (("attribute", "Facts kept"), ("state", "States"), ("transition", "Changes")):
        found = [f"<b>{escape(named(part))}</b> {escape(said(snapshot, part))}" for part in parts(address, kind)]
        if found:
            blocks.append(tag("h4", title) + listing(found))
    return "".join(blocks)


def interface(snapshot: Snapshot, address: Address) -> str:
    fields = snapshot.entries[address].fields
    head = [f"<code>{escape(str(fields['invoked_as']))}</code>"] if fields.get("invoked_as") else []
    served = [f"{escape(named(step.parent() or step))}: {escape(named(step))}" for step in link(snapshot, address, "serves")]
    return listing([*head, f"form {escape(str(fields.get('form', '')))}", *([f"serves {', '.join(served)}"] if served else [])])


def decision(snapshot: Snapshot, address: Address) -> str:
    options = [f"<b>{escape(named(option))}</b> {escape(said(snapshot, option))}" for option in snapshot.links.parts(address, "option")]
    return tag("h4", "Options") + listing(options)


DETAIL = {"workflow": workflow, "entity": entity, "interface": interface, "decision": decision}


def card(snapshot: Snapshot, address: Address) -> str:
    detail = DETAIL.get(address.kind)
    body = detail(snapshot, address) if detail else ""
    if not body:
        return tag("li", f"<b>{escape(named(address))}</b> {escape(said(snapshot, address))}")
    return tag("li", fold(named(address), said(snapshot, address), body, css=address.kind))


def narrative(snapshot: Snapshot, members: dict[str, list[Address]]) -> str:
    """Two or three plain sentences built from the area's own entries: why it exists, what it can do, how one result is reached."""
    goals, abilities, flows = members.get("goal", []), members.get("capability", []), members.get("workflow", [])
    sentences = [f"It exists so that {plain(said(snapshot, goals[0]))}."] if goals else []
    if abilities:
        first = [plain(said(snapshot, ability)).split(";")[0] for ability in abilities[:3]]  # the first clause: the rest is in the fold
        sentences.append("It can: " + "; ".join(first) + (f" (and {len(abilities) - 3} more)" if len(abilities) > 3 else "") + ".")
    if flows:
        many = "s" if len(flows) != 1 else ""
        sentences.append(f"Results are reached through {len(flows)} workflow{many}, the first being: {plain(said(snapshot, flows[0]))}.")
    return " ".join(sentences)


def area(snapshot: Snapshot, home: str, members: dict[str, list[Address]]) -> str:
    layer, name = home.split("/")
    body = []
    story = narrative(snapshot, members)
    if story:
        body.append(tag("p", escape(story), "story"))
    for kind, title in SECTIONS:
        found = members.get(kind, [])
        if found:
            cards = "".join(card(snapshot, a) for a in found)
            body.append(tag("h3", f"{escape(title)} <small>{len(found)}</small>") + tag("ul", cards))
    own = Address(layer, name, (("area", name),))
    unlike = snapshot.entries[own].text("unlike") if own in snapshot.entries else None
    note = tag("p", f"Not here: {escape(unlike)}", "unlike") if unlike else ""
    says = said(snapshot, own) if own in snapshot.entries else ""
    head = f'<h2><span class="layer">{layer}</span> {escape(name)}</h2>' + tag("p", escape(says), "says") + note
    return f'<section class="area" id="{slug(home)}" data-layer="{layer}">{head}{"".join(body)}</section>'


def members_by_home(snapshot: Snapshot) -> dict[str, dict[str, list[Address]]]:
    found: dict[str, dict[str, list[Address]]] = {}
    for address in sorted(snapshot.entries):
        if address.layer in LAYERS and len(address.path) == 1:
            found.setdefault(address.home, {}).setdefault(address.kind, []).append(address)
    return found


def tile(home: str, members: dict[str, list[Address]], says: str) -> str:
    counts = " &middot; ".join(f"{len(members[kind])} {escape(kind)}" for kind, _ in SECTIONS if members.get(kind))
    layer, name = home.split("/")
    link_ = f'<a class="tile" href="#{slug(home)}" data-layer="{layer}">'
    return f"{link_}<b>{escape(name)}</b><span>{escape(says)}</span><em>{counts}</em></a>"


def render(snapshot: Snapshot, *, title: str = "Product map") -> str:
    """The whole page: a sitemap of tiles, one per area and layer, then each area told and opening to its parts."""
    found = members_by_home(snapshot)
    tiles: dict[str, list[str]] = {layer: [] for layer in LAYERS}
    areas: list[str] = []
    for home, members in found.items():
        layer, name = home.split("/")
        head = Address(layer, name, (("area", name),))
        says = said(snapshot, head) if head in snapshot.entries else ""
        tiles[layer].append(tile(home, members, says))
        areas.append(area(snapshot, home, members))
    sitemap = "".join(tag("h2", layer) + tag("div", "".join(tiles[layer]), "tiles") for layer in LAYERS if tiles[layer])
    return PAGE.replace("{{title}}", escape(title)).replace("{{sitemap}}", sitemap).replace("{{areas}}", "".join(areas))
