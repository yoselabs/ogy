import { decisionHTML } from "./cards-decision.js";
import { entityHTML } from "./cards-entity.js";
import { rowHTML, stepHTML, workflowHTML } from "./cards-flow.js";
import { card, esc, facts, literal, mention, prose, summary } from "./mentions.js";

function fieldsHTML(view, node) {
  const linked = new Set(view.links(node.id).map((e) => e.f)),
    slots = new Set(Object.keys(node.detail.parts));
  const skip = new Set([node.detail.sentenceField, "title", "word", "question", "context", "agreed", ...linked, ...slots]);
  return Object.entries(node.detail.fields)
    .filter(([key]) => !skip.has(key))
    .map(([key, value]) => `<div class="compact-fact"><span class="fact-label">${esc(key)}</span>${literal(value)}</div>`)
    .join("");
}
export function renderCard(view, node, level = "detail") {
  const detail = level === "detail";
  if (level === "summary") return card(node, summary(view, node), `${node.kind === "workflow" ? "workflow-summary " : ""}board-summary`);
  if (node.kind === "workflow") return workflowHTML(view, node);
  if (["step", "end"].includes(node.kind)) return stepHTML(view, node, detail);
  if (["case", "choice", "timeout"].includes(node.kind)) return card(node, rowHTML(view, node));
  if (node.kind === "entity") return entityHTML(view, node, detail);
  if (node.kind === "decision") return decisionHTML(view, node, detail);
  let body = prose(node) + fieldsHTML(view, node) + facts(view, node);
  if (detail)
    for (const slot of Object.values(node.detail.parts)) {
      const parts = slot.ids.map((id) => view.byId.get(id)).filter(Boolean);
      if (parts.length)
        body += `<section class="local-parts"><label>${esc(slot.kind)}</label>
      ${parts.map((n) => `<div>${mention(n)}</div>`).join("")}</section>`;
    }
  return card(node, body);
}
