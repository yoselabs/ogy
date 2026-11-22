import { identity } from "../model/descriptor.js";
import { mention as makeMention } from "../ui/mention.js";

export function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}
export function literal(value) {
  return `<code data-renderer="literal">${esc(typeof value === "object" ? JSON.stringify(value) : value)}</code>`;
}
// Every structured name in every context passes through the one mention function.
export function mention(node, self = null) {
  if (!node) return "";
  return makeMention(node, { self: node.id === self, scene: true }).outerHTML;
}
export function header(node) {
  return `<header>${mention(node, node.id)}<small>${esc(node.kind)}</small></header>`;
}
export function openButton(node) {
  return `<button type="button" class="open-affordance" data-open-entry="${esc(node.id)}"
    aria-label="Open ${esc(identity(node).accessibleName)}" title="Open details">↗</button>`;
}
export function card(node, body, extra = "") {
  return `<article class="local-card ${extra}" data-local-id="${esc(node.id)}" data-kind="${esc(node.kind)}"
    ${node.address ? `data-address="${esc(node.address)}"` : ""}
    ${node.kind === "end" ? `data-result="${esc(node.result)}"` : ""}>${header(node)}${body}${openButton(node)}</article>`;
}
export function prose(node) {
  return node.says ? `<p data-renderer="authored-prose">${esc(node.says)}</p>` : "";
}
export function count(label, nodes) {
  if (!nodes.length) return "";
  return `<span class="local-count" data-count="${nodes.length}" data-count-ids="${esc(JSON.stringify(nodes.map((n) => n.id)))}">
    ${esc(label)}: ${nodes.length}</span>`;
}
export function summary(view, node) {
  const byKind = new Map();
  for (const part of view.descendants(node.id)) {
    if (!byKind.has(part.kind)) byKind.set(part.kind, []);
    byKind.get(part.kind).push(part);
  }
  return `<div class="local-counts">${[...byKind].map(([kind, nodes]) => count(kind, nodes)).join("")}</div>`;
}
export function fact(view, edge) {
  return `<div class="compact-fact" data-fact-id="${esc(edge.id)}"><span class="fact-label">${esc(edge.f)}</span>
    ${view.byId.has(edge.t) ? mention(view.byId.get(edge.t)) : literal(edge.value)}</div>`;
}
export function facts(view, node, fields = null) {
  return view
    .links(node.id)
    .filter((e) => !fields || fields.includes(e.f))
    .map((e) => fact(view, e))
    .join("");
}
