// The Map's facts as plain data: one tile per area of a layer, from one pass over the inspection model.
// Counts are the area's own entries by kind (parts are counted in their owner); goals are the area's own and those its capabilities realize.
const byKey = (a, b) => String(a.key).localeCompare(String(b.key));
const FIRST = ["goal", "capability", "workflow", "entity"];
const SHARED = "shared";

function realizesOf(model) {
  const map = new Map();
  for (const edge of model.edges) {
    if (edge.f !== "realizes" || !edge.t) continue;
    if (!map.has(edge.s)) map.set(edge.s, []);
    map.get(edge.s).push(edge.t);
  }
  return map;
}

function order(counts) {
  const rank = (kind) => (FIRST.includes(kind) ? FIRST.indexOf(kind) : FIRST.length);
  return [...counts]
    .map(([kind, count]) => ({ kind, count }))
    .sort((a, b) => rank(a.kind) - rank(b.kind) || b.count - a.count || a.kind.localeCompare(b.kind));
}

export function mapView(model, layer) {
  const tiles = new Map();
  const tile = (node) => {
    if (!tiles.has(node.area))
      tiles.set(node.area, {
        scope: node.area,
        area: node.area.split("/")[1],
        entry: null,
        counts: new Map(),
        goals: new Map(),
        capabilities: [],
      });
    return tiles.get(node.area);
  };
  for (const node of model.nodes) {
    if (node.layer !== layer || !node.top) continue;
    const found = tile(node);
    if (node.kind === "area") {
      found.entry = node;
      continue;
    }
    found.counts.set(node.kind, (found.counts.get(node.kind) || 0) + 1);
    if (node.kind === "goal") found.goals.set(node.id, node);
    else if (node.kind === "capability") found.capabilities.push(node);
  }
  const realizes = realizesOf(model);
  const hasGoals = Boolean(model.vocabulary.kinds.goal?.layers?.includes(layer));
  const list = [...tiles.values()].map((found) => {
    for (const capability of found.capabilities)
      for (const target of realizes.get(capability.id) || []) {
        const goal = model.byId.get(target);
        if (goal?.kind === "goal") found.goals.set(goal.id, goal);
      }
    return {
      scope: found.scope,
      area: found.area,
      entry: found.entry,
      says: found.entry?.says || "",
      kinds: order(found.counts),
      total: [...found.counts.values()].reduce((sum, count) => sum + count, 0),
      goals: [...found.goals.values()].sort(byKey),
      wantsGoal: hasGoals && found.area !== SHARED,
    };
  });
  return list.sort((a, b) => (a.area === SHARED) - (b.area === SHARED) || a.area.localeCompare(b.area));
}
