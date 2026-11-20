"""Checks for kinds with `flow:`: a workflow is a graph of steps whose rows (choices, cases, a timeout) name `then:`."""

from collections import deque
from dataclasses import dataclass

from ogy.model import Address, Finding, Problem
lazy from ogy.kinds import Flow
lazy from ogy.snapshot import Snapshot
lazy from ogy.source import Source


@dataclass(frozen=True)
class Graph:
    """One workflow: its steps and ends, each step's rows, and every step's targets."""

    container: Address
    steps: list[Address]
    ends: list[Address]
    rows: dict[Address, dict[str, list[Address]]]  # step -> row kind -> rows
    targets: dict[Address, set[Address]]  # step -> what its own `then:` and its rows' `then:` name


def link(snapshot: Snapshot, address: Address, field: str) -> list[Address]:
    """What the entry's link field names, resolved (a full address, or a local key of a nearby part)."""
    return sorted(snapshot.links.forward(address, field))


def graph(snapshot: Snapshot, flow: Flow, container: Address) -> Graph:
    parts = snapshot.links.parts
    steps = parts(container, flow.step)
    rows = {step: {kind: parts(step, kind) for kind in (flow.choice, flow.case, flow.timeout)} for step in steps}
    targets = {
        step: {target for kind in rows[step].values() for row in kind for target in link(snapshot, row, flow.then)} for step in steps
    }
    return Graph(container, steps, parts(container, flow.end), rows, targets)


class FlowChecker:
    def __init__(self, snapshot: Snapshot, flow: Flow, container: Address) -> None:
        self.snapshot = snapshot
        self.flow = flow
        self.graph = graph(snapshot, flow, container)
        self.findings: list[Finding] = []

    def add(self, problem: Problem, address: Address, detail: str) -> None:
        self.findings.append(Finding(problem, self.snapshot.entries[address].path, detail, address))

    def run(self) -> list[Finding]:
        for step in self.graph.steps:
            self.shape(step)
            self.coverage(step)
        self.reach()
        return self.findings

    def has(self, address: Address, field: str) -> bool:
        return self.snapshot.entries[address].fields.get(field) is not None

    def shape(self, step: Address) -> None:
        """Actor step: choices (`requires` keeps one without `when:`), maybe a timeout. Calling step: cases over the callee's
        ends. System step: cases, the one `otherwise` case when it only goes on (decision exits-on-rows)."""
        flow, rows = self.flow, self.graph.rows[step]
        choices, cases, timeouts = rows[flow.choice], rows[flow.case], rows[flow.timeout]
        calls = self.has(step, flow.calls)
        if self.has(step, flow.actor):
            if not choices or bool(cases) or calls:
                self.add(Problem.STEP_SHAPE, step, "an actor step offers choices and nothing else")
            return
        if choices or timeouts:
            self.add(Problem.STEP_SHAPE, step, "only an actor step has choices or a timeout")
        if calls and not cases:
            self.add(Problem.STEP_SHAPE, step, "a calling step continues by cases over the callee's ends")
        if not calls and not cases:
            self.add(Problem.STEP_SHAPE, step, f"a system step goes on by its cases; one that only goes on has one `{flow.otherwise}` case")
        if cases and not calls:
            self.system_cases(step, cases)

    def system_cases(self, step: Address, cases: list[Address]) -> None:
        """One `otherwise` case with no `when:`; every other case has `when:` and an `order`, and no two share one."""
        flow = self.flow
        others = [row for row in cases if row.key == flow.otherwise]
        rest = [row for row in cases if row not in others]
        if len(others) != 1 or any(self.has(row, flow.when) for row in others):
            self.add(Problem.STEP_SHAPE, step, f"exactly one `{flow.otherwise}` case, with no `when:`")
        if any(not self.has(row, flow.when) for row in rest):
            self.add(Problem.STEP_SHAPE, step, "every other case has `when:`")
        orders = [self.snapshot.entries[row].fields.get(flow.order) for row in rest]
        if any(order is None for order in orders) or len(set(orders)) != len(orders):
            self.add(Problem.STEP_SHAPE, step, f"every case but `{flow.otherwise}` has its own `{flow.order}`")

    def coverage(self, step: Address) -> None:
        """A calling step names every end of the callee in `covers_ends`; no catch-all counts, so a new end is noticed."""
        for callee in link(self.snapshot, step, self.flow.calls):
            named = {target for row in self.graph.rows[step][self.flow.case] for target in link(self.snapshot, row, self.flow.covers)}
            missing = [str(end) for end in self.snapshot.links.parts(callee, self.flow.end) if end not in named]
            if missing:
                self.add(Problem.UNCOVERED_END, step, f"no case for the callee's ends {missing}")

    def reach(self) -> None:
        g = self.graph
        start = link(self.snapshot, g.container, self.flow.start)
        seen = set(start)
        queue = deque(start)
        while queue:
            for target in g.targets.get(queue.popleft(), ()):
                if target in g.targets and target not in seen:
                    seen.add(target)
                    queue.append(target)
        for step in g.steps:
            if step not in seen:
                self.add(Problem.UNREACHABLE, step, "no path from the workflow's start")
        done = {step for step in g.steps if any(t.kind != self.flow.step or t not in g.targets for t in g.targets[step])}
        changed = True
        while changed:
            grown = {step for step in g.steps if step not in done and g.targets[step] & done}
            changed = bool(grown)
            done |= grown
        for step in g.steps:
            if step not in done:
                self.add(Problem.NO_END, step, "no path to an end or a hand-off")
        reached = {target for step in seen for target in g.targets[step]}
        for end in g.ends:
            if end not in reached:
                self.add(Problem.END_UNREACHED, end, "no reachable step ends here")


def unoffered(snapshot: Snapshot) -> list[tuple[Address, Address, list[str]]]:
    """(interface, step, choices) for each serving interface that lists `offers` and leaves out a choice of the step it serves
    that no other serving interface offers: work for the interface's layer, as an interface without `offers` offers every
    choice and goes stale when the choices change."""
    found: list[tuple[Address, Address, list[str]]] = []
    for kind in snapshot.ontology.kinds.values():
        flow = kind.flow
        if flow is None:
            continue
        for step in (address for address in sorted(snapshot.entries) if address.kind == flow.step):
            choices = set(snapshot.links.parts(step, flow.choice))
            servers = sorted(a for a in snapshot.links.backward(step, flow.serves) if a.kind in flow.servers)
            listing = [s for s in servers if snapshot.entries[s].fields.get(flow.offers) is not None]
            if not choices or not servers or len(listing) < len(servers):
                continue  # one serving interface without `offers` offers every choice
            offered = {choice for server in listing for choice in link(snapshot, server, flow.offers)}
            if missing := sorted(str(choice) for choice in choices - offered):
                found += [(server, step, missing) for server in listing]
    return found


def _top(address: Address) -> Address:
    while (parent := address.parent()) is not None:
        address = parent
    return address


def _root(snapshot: Snapshot, flow: Flow, address: Address) -> bool:
    """Started from outside: an actor on its first step, or a `roots` field (a schedule, an event) set."""
    if any(snapshot.entries[address].fields.get(name) for name in flow.roots):
        return True
    return any(link(snapshot, start, flow.actor) for start in link(snapshot, address, flow.start))


def orphans(snapshot: Snapshot, flow: Flow, kind: str) -> list[Finding]:
    """Who starts a workflow is computed, never declared: a root, or led to (`then`, `calls`) from a started workflow.
    Two workflows that only lead to each other are not started."""
    flows = [address for address in sorted(snapshot.entries) if address.kind == kind and address.parent() is None]
    started = {address for address in flows if _root(snapshot, flow, address)}
    grown = True
    while grown:
        led = {
            address
            for address in flows
            if address not in started
            and any(_top(source) in started for field in (flow.then, flow.calls) for source in snapshot.links.backward(address, field))
        }
        started |= led
        grown = bool(led)
    return [
        Finding(
            Problem.NEVER_STARTED,
            snapshot.entries[address].path,
            f"nothing starts it: no actor on its first step, no {' or '.join(flow.roots)}, and no started workflow leads to it",
            address,
        )
        for address in flows
        if address not in started
    ]


# A layer that is not finished yet, not a wrong entry: refused only when it lands (`ogy check --landing`), so a half
# workflow commits on a branch.
UNFINISHED = frozenset({Problem.END_UNREACHED, Problem.NEVER_STARTED})


def check_flows(snapshot: Snapshot, source: Source) -> list[Finding]:
    """The faults of the flows: what the author can fix in their own layer now."""
    return [item for item in _flows(snapshot, source) if item.problem not in UNFINISHED]


def check_unfinished_flows(snapshot: Snapshot, source: Source) -> list[Finding]:
    """For landing only: an end no reachable step leads to, a workflow nothing starts."""
    return [item for item in _flows(snapshot, source) if item.problem in UNFINISHED]


def _flows(snapshot: Snapshot, _source: Source) -> list[Finding]:
    findings: list[Finding] = []
    for kind in snapshot.ontology.kinds.values():
        if kind.flow is None:
            continue
        for address in sorted(snapshot.entries):
            if address.kind == kind.kind:
                findings.extend(FlowChecker(snapshot, kind.flow, address).run())
        findings.extend(orphans(snapshot, kind.flow, kind.kind))
    return findings
