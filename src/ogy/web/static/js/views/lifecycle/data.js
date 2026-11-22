import { ownersOf } from "../../ui/path.js";

// One entity's lifecycle as plain data: its states, and each transition with the states it joins and the rows that fire it.
// A row fires a transition when one of its effects does `transition` on it; the row's owners up to the workflow are its path.
const byKey = (a, b) => String(a.key).localeCompare(String(b.key));

export function lifecycleView(model, layer, area, key) {
  const entity = model.byId.get(`${layer}/${area}/entity/${key}`);
  if (entity?.kind !== "entity") return null;
  const parts = model.nodes.filter((node) => node.parent === entity.address);
  const states = parts.filter((node) => node.kind === "state").sort(byKey);
  const linked = (id, field) =>
    model.edges
      .filter((edge) => edge.s === id && edge.f === field && edge.t)
      .map((edge) => model.byId.get(edge.t))
      .filter(Boolean);
  const transitions = parts
    .filter((node) => node.kind === "transition")
    .sort(byKey)
    .map((node) => {
      const firedBy = model.nodes
        .filter((row) => row.fx.some((effect) => effect.do === "transition" && effect.onid === node.id))
        .map((row) => ownersOf(model, row));
      const events = model.edges.filter((edge) => edge.f === "event" && edge.t === node.id).map((edge) => model.byId.get(edge.s));
      return {
        node,
        from: linked(node.id, "from"),
        to: linked(node.id, "to")[0] || null,
        firedBy,
        events: events.filter(Boolean),
        owed: !firedBy.length,
      };
    });
  return { entity, states, transitions };
}
