// The area page's facts as plain data, derived from the inspection document with the ontology's own links:
// a workflow `realizes` a capability, a capability `realizes` a goal, a step's cases, choices and timeouts say `then`.
const byKey = (a, b) => String(a.key).localeCompare(String(b.key));
const CHAIN = new Set(["area", "goal", "capability", "workflow", "entity"]);

function linksOf(model, field) {
  const map = new Map();
  for (const edge of model.edges) {
    if (edge.f !== field || !edge.t) continue;
    if (!map.has(edge.s)) map.set(edge.s, []);
    map.get(edge.s).push(edge.t);
  }
  return map;
}

// Steps and ends of a workflow in the order a reader meets them: from `start`, along `then`, branches in turn.
function flowOf(model, workflow, then) {
  const prefix = `${workflow.address}/`;
  const parts = model.nodes.filter((node) => node.address?.startsWith(prefix) || node.parent?.startsWith(prefix));
  const flow = parts.filter((node) => node.kind === "step" || node.kind === "end");
  const wanted = new Set(flow.map((node) => node.address));
  const out = (step) => parts.filter((part) => part.parent === step.address).flatMap((part) => then.get(part.id) || []);
  const order = [];
  const seen = new Set();
  const queue = workflow.start ? [`${prefix}step/${workflow.start}`] : [];
  while (queue.length) {
    const address = queue.shift();
    if (seen.has(address) || !wanted.has(address)) continue;
    seen.add(address);
    const node = model.byId.get(address);
    order.push(node);
    if (node.kind === "step") queue.push(...out(node));
  }
  return [...order, ...flow.filter((node) => !seen.has(node.address)).sort(byKey)];
}

// Entity states in lifecycle order: the states nothing enters first, then along the transitions.
function lifecycleOf(model, entity, links) {
  const kids = model.nodes.filter((node) => node.parent === entity.address);
  const states = kids.filter((node) => node.kind === "state").sort(byKey);
  const transitions = kids.filter((node) => node.kind === "transition");
  const into = new Set(transitions.flatMap((transition) => links.to.get(transition.id) || []));
  const queue = states.filter((state) => !into.has(state.address)).map((state) => state.address);
  if (!queue.length && states.length) queue.push(states[0].address);
  const order = [];
  while (queue.length) {
    const address = queue.shift();
    if (order.includes(address) || !model.byId.has(address)) continue;
    order.push(address);
    for (const transition of transitions) {
      if ((links.from.get(transition.id) || []).includes(address)) queue.push(...(links.to.get(transition.id) || []));
    }
  }
  const rest = states.filter((state) => !order.includes(state.address));
  return { states: [...order.map((address) => model.byId.get(address)), ...rest], transitions };
}

function groupOthers(top) {
  const kinds = new Map();
  for (const node of top) {
    if (CHAIN.has(node.kind)) continue;
    if (!kinds.has(node.kind)) kinds.set(node.kind, []);
    kinds.get(node.kind).push(node);
  }
  return [...kinds]
    .map(([kind, nodes]) => ({ kind, nodes: nodes.sort(byKey) }))
    .sort((a, b) => b.nodes.length - a.nodes.length || a.kind.localeCompare(b.kind));
}

// The why-chain: one row per goal, its capabilities, and the workflows of this area each capability's workflows realize.
// A capability that realizes several goals lists its workflows under the first goal only; the others point to it.
function chainOf(model, scope, hasGoals, here, links) {
  const of = (kind) => here.filter((node) => node.top && node.kind === kind).sort(byKey);
  const node = (address) => model.byId.get(address);
  const capabilityOf = (workflow) =>
    (links.realizes.get(workflow.id) || []).map(node).find((found) => found?.kind === "capability") || null;
  const goalsOf = (capability) => (links.realizes.get(capability.id) || []).map(node).filter((found) => found?.kind === "goal");
  const everyWorkflow = model.nodes.filter((found) => found.kind === "workflow");
  const workflowsOf = (capability) => everyWorkflow.filter((workflow) => capabilityOf(workflow)?.id === capability.id);
  const workflows = of("workflow");

  const capabilities = new Map();
  for (const workflow of workflows) {
    const capability = capabilityOf(workflow);
    if (capability) capabilities.set(capability.id, capability);
  }
  for (const capability of of("capability")) capabilities.set(capability.id, capability);
  const goals = new Map(of("goal").map((goal) => [goal.id, goal]));
  for (const found of model.nodes) {
    if (found.kind !== "capability") continue;
    const realized = goalsOf(found);
    if (realized.some((goal) => goals.has(goal.id))) capabilities.set(found.id, found);
  }
  for (const capability of capabilities.values()) for (const goal of goalsOf(capability)) goals.set(goal.id, goal);

  const placed = new Set();
  const row = (capability, goal) => {
    const own = workflowsOf(capability);
    const first = !placed.has(capability.id);
    placed.add(capability.id);
    return {
      capability,
      workflows: first ? own.filter((workflow) => workflow.area === scope) : [],
      elsewhere: first ? own.filter((workflow) => workflow.area !== scope) : [],
      shownUnder: first ? null : goal,
      none: first && !own.length,
    };
  };
  const goalRows = [...goals.values()].sort(byKey).map((goal) => {
    const caps = [...capabilities.values()].filter((capability) => goalsOf(capability).some((found) => found.id === goal.id));
    return { goal, capabilities: caps.sort(byKey).map((capability) => row(capability, goal)) };
  });
  const orphans = [...capabilities.values()].filter((capability) => !placed.has(capability.id)).sort(byKey);
  const noGoal = {
    capabilities: orphans.map((capability) => row(capability, null)),
    workflows: workflows.filter((workflow) => !capabilityOf(workflow)),
  };
  return { hasGoals, goalRows, noGoal, workflows };
}

// Everything the page draws, or null when no entry belongs to the area.
export function areaView(model, layer, area) {
  const scope = `${layer}/${area}`;
  const here = model.nodes.filter((node) => node.area === scope);
  if (!here.length) return null;
  const links = { realizes: linksOf(model, "realizes"), from: linksOf(model, "from"), to: linksOf(model, "to") };
  const then = linksOf(model, "then");
  const hasGoals = Boolean(model.vocabulary.kinds.goal?.layers?.includes(layer));
  const chain = chainOf(model, scope, hasGoals, here, links);
  const top = here.filter((node) => node.top);
  return {
    scope,
    entry: here.find((found) => found.kind === "area") || null,
    chain,
    flows: new Map(chain.workflows.map((workflow) => [workflow.id, flowOf(model, workflow, then)])),
    entities: top
      .filter((node) => node.kind === "entity")
      .sort(byKey)
      .map((entity) => ({ entity, ...lifecycleOf(model, entity, links) })),
    others: groupOthers(top),
  };
}
