"""Checks for kinds with `flow:`: a workflow is a graph of steps whose rows (choices, cases, a timeout) name `then:`."""

from collections import deque
from dataclasses import dataclass

from ogy.kinds import Flow
from ogy.model import Address, Finding, Problem
from ogy.snapshot import Snapshot
from ogy.source import Source


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
    targets = {step: {target for kind in rows[step].values() for row in kind for target in link(snapshot, row, flow.then)}
               for step in steps}
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
            self.offered(step)
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

    def offered(self, step: Address) -> None:
        choices = set(self.graph.rows[step][self.flow.choice])
        servers = [address for address in self.snapshot.links.backward(step, self.flow.serves) if address.kind in self.flow.servers]
        if not choices or not servers:
            return
        offered: set[Address] = set()
        for server in servers:
            listed = link(self.snapshot, server, self.flow.offers)
            offered |= set(listed) if self.has(server, self.flow.offers) else choices
        missing = sorted(str(choice) for choice in choices - offered)
        if missing:
            self.add(Problem.NOT_OFFERED, step, f"no serving view or command offers {missing}")

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
        led = {address for address in flows if address not in started and any(
            _top(source) in started for field in (flow.then, flow.calls) for source in snapshot.links.backward(address, field))}
        started |= led
        grown = bool(led)
    return [Finding(Problem.ORPHAN, snapshot.entries[address].path, "nothing starts it: no actor on its first step, no "
                    f"{' or '.join(flow.roots)}, and no started workflow leads to it", address)
            for address in flows if address not in started]


def check_flows(snapshot: Snapshot, _source: Source) -> list[Finding]:
    findings: list[Finding] = []
    for kind in snapshot.ontology.kinds.values():
        if kind.flow is None:
            continue
        for address in sorted(snapshot.entries):
            if address.kind == kind.kind:
                findings.extend(FlowChecker(snapshot, kind.flow, address).run())
        findings.extend(orphans(snapshot, kind.flow, kind.kind))
    return findings
