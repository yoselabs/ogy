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
    targets: dict[Address, set[Address]]  # step -> what its own `then:`, its rows' `then:` and its guards' `else:` name


def link(snapshot: Snapshot, address: Address, field: str) -> list[Address]:
    """What the entry's link field names, resolved (a full address, or a local key of a nearby part)."""
    return sorted(snapshot.links.forward(address, field))


def graph(snapshot: Snapshot, flow: Flow, container: Address) -> Graph:
    parts = snapshot.links.parts
    steps = parts(container, flow.step)
    rows = {step: {kind: parts(step, kind) for kind in (flow.choice, flow.case, flow.timeout)} for step in steps}
    targets = {step: {*link(snapshot, step, flow.then),
                      *(target for kind in rows[step].values() for row in kind for target in link(snapshot, row, flow.then)),
                      *(target for guard in snapshot.links.backward(step, flow.guarded) if guard.kind == flow.guard
                        for target in link(snapshot, guard, flow.denied))}
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
        """Actor step: choices (`requires` keeps one without `when:`), maybe a timeout. Calling step: cases. System step: cases or
        a plain `then:`."""
        flow, rows = self.flow, self.graph.rows[step]
        choices, cases, timeouts = rows[flow.choice], rows[flow.case], rows[flow.timeout]
        then, calls = self.has(step, flow.then), self.has(step, flow.calls)
        if self.has(step, flow.actor):
            if not choices or bool(cases) or then or calls:
                self.add(Problem.STEP_SHAPE, step, "an actor step offers choices and nothing else")
            return
        if choices or timeouts:
            self.add(Problem.STEP_SHAPE, step, "only an actor step has choices or a timeout")
        if calls and (then or not cases):
            self.add(Problem.STEP_SHAPE, step, "a calling step continues by cases over the callee's ends")
        if not calls and bool(cases) == then:
            self.add(Problem.STEP_SHAPE, step, "a system step has cases or one `then:`, not both")
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


def orphans(snapshot: Snapshot, flow: Flow, kind: str) -> list[Finding]:
    """A workflow that is only ever called (trigger `called`) and that nothing hands off to or calls."""
    found: list[Finding] = []
    for address in sorted(snapshot.entries):
        if address.kind != kind or snapshot.entries[address].fields.get(flow.trigger) != flow.called:
            continue
        callers = [source for field in (flow.then, flow.calls) for source in snapshot.links.backward(address, field)]
        if not callers:
            found.append(Finding(Problem.ORPHAN, snapshot.entries[address].path, "nothing hands off to or calls it", address))
    return found


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
