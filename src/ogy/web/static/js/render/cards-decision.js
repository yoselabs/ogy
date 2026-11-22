import { card, esc, facts, literal, mention, prose } from "./mentions.js";

function recordHTML(view, record) {
  const fields = record.detail.fields;
  return `<div class="decision-record">${mention(record)}${facts(view, record, ["chose", "delegated"])}
    ${["sets", "said", "at", "note", "why", "heard"]
      .filter((key) => Object.hasOwn(fields, key))
      .map((key) => `<p data-decision-field="${key}"><span class="fact-label">${key}: </span>${literal(fields[key])}</p>`)
      .join("")}</div>`;
}
export function decisionHTML(view, node, detail) {
  const answers = view.parts(node.id, ["answer"]);
  const dated = answers.every((n) => typeof n.at === "string" && Number.isFinite(Date.parse(n.at)));
  const ordered = dated ? [...answers].sort((a, b) => Date.parse(b.at) - Date.parse(a.at)) : answers;
  const uniqueLatest = dated && ordered.length && (!ordered[1] || Date.parse(ordered[0].at) !== Date.parse(ordered[1].at));
  const visibleAnswers = detail || !uniqueLatest ? ordered : ordered.slice(0, 1);
  let body = `<p class="question">${esc(node.question || node.says)}</p>`;
  body += `<section class="decision-section" data-decision-section="answers"><label>Answers</label>
    ${visibleAnswers.map((n) => recordHTML(view, n)).join("") || '<p class="missing">none</p>'}</section>`;
  const proposals = view.parts(node.id, ["proposal"]);
  if (proposals.length)
    body += `<section class="decision-section" data-decision-section="proposal"><label>Proposals</label>
    ${proposals.map((n) => recordHTML(view, n)).join("")}</section>`;
  if (detail) {
    if (node.context) body += `<p>${esc(node.context)}</p>`;
    body += `<section class="decision-section"><label>Options</label>${view
      .parts(node.id, ["option"])
      .map((n) => `<div>${mention(n)}${prose(n)}${Object.hasOwn(n, "sets") ? literal(n.sets) : ""}</div>`)
      .join("")}</section>`;
  }
  return card(node, body);
}
