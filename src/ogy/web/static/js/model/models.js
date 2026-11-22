// Rendering indexes the inspection graph without changing authored nodes.
export function models(model) {
  const children = new Map(), outgoing = new Map(), incoming = new Map();
  for (const node of model.nodes) {
    if (!children.has(node.parent)) children.set(node.parent, []);
    children.get(node.parent).push(node);
  }
  for (const edge of model.edges) {
    if (!outgoing.has(edge.s)) outgoing.set(edge.s, []);
    if (!incoming.has(edge.t)) incoming.set(edge.t, []);
    outgoing.get(edge.s).push(edge); incoming.get(edge.t).push(edge);
  }
  const parts = (id, kinds) => (children.get(id) || []).filter(n => !kinds || kinds.includes(n.kind));
  const links = (id, field) => (outgoing.get(id) || []).filter(e => !field || e.f === field);
  const targets = (id, field) => links(id, field).map(e => model.byId.get(e.t)).filter(Boolean);
  function owner(id) {
    let node = model.byId.get(id);
    while (node?.parent && model.byId.has(node.parent)) node = model.byId.get(node.parent);
    return node;
  }
  function descendants(id) {
    const result = [], queue = [...parts(id)], seen = new Set([id]);
    while (queue.length) {
      const node = queue.shift();
      if (seen.has(node.id)) continue;
      seen.add(node.id); result.push(node); queue.push(...parts(node.id));
    }
    return result;
  }
  return { ...model, children, outgoing, incoming, parts, links, targets, owner, descendants };
}

export function workflowColumns(view, workflow) {
  const steps = view.parts(workflow.id, ["step", "end"]), ids = new Set(steps.map(n => n.id));
  const start = view.targets(workflow.id, "start")[0], ranks = new Map(), queue = start ? [start.id] : [];
  if (start) ranks.set(start.id, 0);
  while (queue.length) {
    const id = queue.shift();
    for (const source of [id, ...view.parts(id).map(n => n.id)]) for (const target of view.targets(source, "then")) {
      if (!ids.has(target.id) || ranks.has(target.id)) continue;
      ranks.set(target.id, ranks.get(id) + 1); queue.push(target.id);
    }
  }
  const columns = new Map();
  for (const step of steps) {
    const rank = ranks.get(step.id) ?? ranks.size;
    if (!columns.has(rank)) columns.set(rank, []);
    columns.get(rank).push(step);
  }
  return [...columns].sort(([a], [b]) => a - b).map(([, nodes]) => nodes);
}
