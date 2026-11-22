import { adapt } from "../model/adapt.js";

// The board's model with the sketch's records added to the inspection document, and each drawn node marked `sketch`. The real model is
// never touched: this one is built apart, kept for one version of the knowledge base and one sketch, and thrown away with them.
let kept = { key: null, model: null };

export function sketchModel(doc, sketch) {
  const key = `${doc.snapshot.version}|${sketch.since}`;
  if (kept.key === key) return kept.model;
  const merged = adapt({
    ...doc,
    entries: [...doc.entries, ...sketch.entries],
    parts: [...doc.parts, ...sketch.parts],
    relations: [...doc.relations, ...sketch.relations],
  });
  const drawn = new Set(sketch.entries.map((record) => record.address));
  for (const node of merged.nodes) if (drawn.has(node.id) || drawn.has(node.parent)) node.sketch = true;
  kept = { key, model: merged };
  return merged;
}

// What the page draws: each workflow that holds something sketched (a new workflow, or an existing one that gets a new step) as a
// flow, and every other new top entry as a card.
export function sketched(model) {
  const top = model.nodes.filter((node) => node.sketch && node.top);
  const owners = new Set(top.filter((node) => node.kind === "workflow"));
  for (const node of model.nodes.filter((part) => part.sketch && !part.top)) {
    let owner = node;
    while (owner.parent) owner = model.byId.get(owner.parent) || { top: true };
    if (owner.kind === "workflow") owners.add(owner);
  }
  return { workflows: [...owners], others: top.filter((node) => node.kind !== "workflow") };
}
