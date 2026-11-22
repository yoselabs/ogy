// What a step does, read from the inspection document's own links: who acts, which interface serves it, what its rows change,
// which workflow it runs and how each way that workflow can end leads on.
const ROWS = new Set(["case", "choice", "timeout"]);

const linked = (model, id, field) =>
  model.edges
    .filter((edge) => edge.s === id && edge.f === field && edge.t)
    .map((edge) => model.byId.get(edge.t))
    .filter(Boolean);

// Where a row leads: the entries its `then` names.
export const thenOf = (model, row) => linked(model, row.id, "then");

export const rowsOf = (model, step) => model.nodes.filter((part) => part.parent === step.address && ROWS.has(part.kind));

// The entry an effect's target belongs to: a transition or an attribute to its entity, anything else to itself.
export function ownerOf(model, target) {
  if (!target) return null;
  return ["transition", "attribute", "state"].includes(target.kind) ? model.byId.get(target.parent) || target : target;
}

function effectsOf(model, rows) {
  return rows.flatMap((row) =>
    row.fx.map((effect) => {
      const target = effect.onid ? model.byId.get(effect.onid) : null;
      const transition = target?.kind === "transition";
      return {
        row,
        do: effect.do,
        target,
        owner: ownerOf(model, target),
        from: transition ? linked(model, target.id, "from") : [],
        to: transition ? linked(model, target.id, "to") : [],
      };
    }),
  );
}

// A calling step: the callee, and for each row the ends of the callee it covers with where it leads.
function callOf(model, step, rows) {
  const callee = linked(model, step.id, "calls")[0];
  if (!callee) return null;
  const ways = rows.map((row) => ({
    row,
    ends: linked(model, row.id, "covers_ends"),
    then: linked(model, row.id, "then")[0] || null,
  }));
  return { callee, ways };
}

export function stepFacts(model, step) {
  const rows = rowsOf(model, step);
  return {
    rows,
    actor: linked(model, step.id, "actor")[0] || null,
    interfaces: model.edges
      .filter((edge) => edge.f === "serves" && edge.t === step.id)
      .map((edge) => model.byId.get(edge.s))
      .filter(Boolean),
    effects: effectsOf(model, rows),
    call: callOf(model, step, rows),
  };
}

// Everything a workflow touches, once per owner: the entity, actor or dependency and the operations done to it.
export function touchedBy(facts) {
  const touched = new Map();
  for (const effect of facts.flatMap((one) => one.effects)) {
    if (!effect.owner) continue;
    if (!touched.has(effect.owner.id)) touched.set(effect.owner.id, { owner: effect.owner, ops: new Set() });
    touched.get(effect.owner.id).ops.add(effect.do);
  }
  return [...touched.values()];
}
