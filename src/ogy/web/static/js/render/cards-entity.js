import { card, esc, literal, mention, prose, summary } from "./mentions.js";

export function lifecycleHTML(view, entity) {
  const transitions = view.parts(entity.id, ["transition"]);
  const touched = new Set(transitions.flatMap(n => [...view.targets(n.id, "from"), ...view.targets(n.id, "to")].map(n => n.id)));
  const isolated = view.parts(entity.id, ["state"]).filter(n => !touched.has(n.id));
  const pill = n => `<span class="state-pill">${mention(n)}</span>`;
  return `<section class="lifecycle" data-lifecycle="${esc(entity.id)}"><label>states / transitions</label>
    ${isolated.map(pill).join("")}${transitions.map(transition => {
      const firers = view.nodes.filter(n => ["case", "choice", "timeout"].includes(n.kind)
        && n.fx.some(f => f.do === "transition" && f.onid === transition.id));
      const from = view.targets(transition.id, "from");
      const source = from.length ? from.map(pill).join("") : '<span class="source-marker" aria-label="from: none"></span>';
      const triggers = firers.length ? firers.map(n => mention(n)).join("") : "No recorded trigger";
      return `<section class="lifecycle-move${firers.length ? "" : " unused"}" data-transition="${esc(transition.id)}">
        <div class="lifecycle-route">${source}
        <span class="lifecycle-arrow" aria-hidden="true">→</span>${view.targets(transition.id, "to").map(pill).join("")}</div>
        <div class="local-role">${mention(transition)}</div><div class="firer-slot">${triggers}</div></section>`;
    }).join("")}</section>`;
}
export function entityHTML(view, node, detail) {
  let body = prose(node) + summary(view, node);
  if (detail) {
    const attributes = view.parts(node.id, ["attribute"]);
    if (attributes.length) body += `<section class="local-parts" data-parts="attribute"><label>attributes</label>
      ${attributes.map(n => `<div>${mention(n)}${n.atype ? ` · ${literal(n.atype)}` : ""}</div>`).join("")}</section>`;
    body += lifecycleHTML(view, node);
  }
  return card(node, body);
}
