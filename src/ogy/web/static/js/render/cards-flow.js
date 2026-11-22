import { icon } from "../model/icons.js";
import { card, esc, facts, header, literal, mention, openButton, prose, summary } from "./mentions.js";

export function effectGroups(view, row) {
  const groups = new Map();
  function group(id) {
    if (!groups.has(id)) groups.set(id, { id, effects: [], reads: [] });
    return groups.get(id);
  }
  row.fx.forEach((effect, index) => {
    const target = view.byId.get(effect.onid);
    const owner = ["attribute", "transition", "state"].includes(target?.kind) ? view.byId.get(target.parent) : target;
    group(owner?.id || effect.onid).effects.push({ effect, index, target });
  });
  for (const id of row.reads) group(id).reads.push(id);
  return [...groups.values()];
}
export function effectBadge(view, row, group) {
  if (!group.effects.length) return `<div class="local-role role-chip">${mention(view.byId.get(group.id))}<span>reads</span></div>`;
  const ops = [...new Set(group.effects.map(item => item.effect.do))];
  const created = ops.includes("create") || group.effects.some(item => item.effect.do === "transition"
    && !view.targets(item.target?.id, "from").length);
  const deleted = ops.includes("delete");
  const right = group.effects.map(({ effect, target, index }) => {
    if (effect.do === "transition") return `<div class="slice-transition">${mention(target)}<span class="slice-notch">›</span>
      ${view.targets(target?.id, "to").map(n => `<span class="state-pill">${mention(n)}</span>`).join("")}</div>`;
    if (effect.do === "write") return `<div class="write-line" data-write-index="${index}">
      ${target?.id !== group.id ? mention(target) : ""}${Object.hasOwn(effect, "value") ? literal(effect.value) : ""}</div>`;
    return "";
  }).join("");
  const operation = deleted ? "delete" : created ? "create" : ops[0];
  return `<div class="effect-badge${created ? " effect-create" : ""}${deleted ? " effect-delete" : ""}"
    data-effect-row="${esc(row.id)}" data-effect-indices="${group.effects.map(item => item.index).join(" ")}"
    data-operations="${esc(ops.join(" "))}" role="group" aria-label="effects · ${esc(ops.join(" · "))}">
    <div class="effect-left">${icon(operation, true)}${mention(view.byId.get(group.id))}</div>
    ${right ? `<div class="effect-right">${right}</div>` : ""}
    <div class="effect-roles">${group.reads.length ? "reads · " : ""}${esc(ops.join(" · "))}</div></div>`;
}
export function rowHTML(view, row) {
  return `<section class="local-row flow-row" data-row-id="${esc(row.id)}">${header(row)}${prose(row)}
    ${row.when && row.when !== row.says ? `<p>when: ${esc(row.when)}</p>` : ""}
    ${effectGroups(view, row).map(group => effectBadge(view, row, group)).join("")}
    ${facts(view, row, ["after", "covers_ends", "then"])}${openButton(row)}</section>`;
}
export function interfaceHTML(view, node) {
  return `<section class="interface-contract" data-interface-id="${esc(node.id)}">${mention(node)}
    ${node.form ? `<small>${esc(node.form)}</small>` : ""}
    ${node.invoked ? `<div>Invoked as: ${literal(node.invoked)}</div>` : ""}
    ${facts(view, node, ["offers", "accepts", "shows", "includes", "allows"])}</section>`;
}
export function stepHTML(view, node, detail) {
  if (node.kind === "end") return card(node, prose(node) + `<p>result: ${literal(node.result)}</p>`);
  let body = prose(node) + facts(view, node, ["actor"]);
  body += (view.incoming.get(node.id) || []).filter(e => e.f === "serves").map(e => interfaceHTML(view, view.byId.get(e.s))).join("");
  const calls = view.targets(node.id, "calls");
  if (calls.length) body += `<section class="calls-region"><label>Calls</label>${calls.map(n => mention(n)).join("")}</section>`;
  const rows = view.parts(node.id, ["case", "choice", "timeout"]);
  body += detail ? `<section class="cases-region">${rows.map(row => rowHTML(view, row)).join("")}</section>` : summary(view, node);
  return card(node, body + facts(view, node, ["then"]));
}
export function workflowHTML(view, node) {
  return card(node, prose(node) + summary(view, node) + facts(view, node, ["event", "schedule", "start"]), "workflow-summary");
}
