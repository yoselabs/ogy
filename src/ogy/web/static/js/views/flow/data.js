import { identity } from "../../model/descriptor.js";

// The workflow page's graph as plain data, from the inspection document's own links:
// a workflow `start`s at a step, and every case, choice and timeout of a step says `then`.
const ROWS = new Set(["case", "choice", "timeout"]);
export const START = "start";

function thenOf(model) {
  const map = new Map();
  for (const edge of model.edges) {
    if (edge.f !== "then" || !edge.t) continue;
    if (!map.has(edge.s)) map.set(edge.s, []);
    map.get(edge.s).push(edge.t);
  }
  return map;
}

// What a row says on its edge: a choice its label, a case its key, a timeout its kind word; the condition is the hover text.
function labelOf(row) {
  const title = row.kind === "timeout" ? row.kind : identity(row).title;
  return { text: title, title: row.when || null };
}

export function flowView(model, address) {
  const workflow = model.byId.get(address);
  if (!workflow || workflow.kind !== "workflow") return null;
  const prefix = `${address}/`;
  const parts = model.nodes.filter((node) => node.parent === address || node.parent?.startsWith(prefix));
  const inside = parts.filter((node) => (node.kind === "step" || node.kind === "end") && node.parent === address);
  const known = new Map(inside.map((node) => [node.id, node]));
  const then = thenOf(model);
  const nodes = inside.map((node) => ({ id: node.id, node, external: false }));
  const edges = [];
  const outside = new Map();
  const target = (id) => {
    if (known.has(id)) return id;
    const found = model.byId.get(id);
    if (!found) return null;
    if (!outside.has(id)) outside.set(id, { id, node: found, external: true });
    return id;
  };
  const start = workflow.start ? `${prefix}step/${workflow.start}` : null;
  if (start && known.has(start)) {
    nodes.push({ id: START, node: null, external: false, stub: true });
    edges.push({ id: `${START}>${start}`, from: START, to: start, label: null, row: null });
  }
  for (const step of inside.filter((node) => node.kind === "step")) {
    for (const row of parts.filter((part) => part.parent === step.address && ROWS.has(part.kind))) {
      for (const [index, to] of (then.get(row.id) || []).entries()) {
        const id = target(to);
        if (id) edges.push({ id: `${row.id}>${index}`, from: step.id, to: id, label: labelOf(row), row });
      }
    }
  }
  return { workflow, nodes: [...nodes, ...outside.values()], edges };
}
