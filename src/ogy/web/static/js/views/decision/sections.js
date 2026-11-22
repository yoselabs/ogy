import { authored } from "../../ui/authored.js";
import { h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { words as shell } from "../../ui/words.js";
import { day, nodeFor } from "./format.js";
import { words } from "./words.js";

const link = (model, address, self = false) => mention(nodeFor(model, address), { self });

// One set entry: the entry as a mention, then what the option puts into it, or that it does not exist under that option.
function setLine(model, row) {
  const body = row.fields
    ? row.fields.map(([name, value]) => h("span", { class: "set-field" }, `${name}: `, authored(value)))
    : [h("span", { class: "set-field" }, words.notExisting)];
  return h("li", { class: "set-row" }, link(model, row.address), body);
}

export function setList(model, rows) {
  return h(
    "ul",
    { class: "set-list", "data-part": "sets" },
    rows.map((row) => setLine(model, row)),
  );
}

// The status line is the page's first line: waiting, or the answer with its date, who gave it and whether it carries a note.
export function statusLine(model, view) {
  const status = h("p", { class: "status-line", "data-part": "status", "data-state": view.status?.state || "unknown" });
  if (!view.status) {
    status.append(view.standingError ? words.statusUnknown : shell.loading);
    return status;
  }
  if (view.status.state === "waiting") {
    status.append(h("strong", {}, words.waitingForYou));
    return status;
  }
  const newest = view.answers[0];
  const lead = view.status.delegated ? words.answeredForYou : words.answered;
  status.append(h("strong", {}, `${lead}, ${day(view.status.at)}: `), link(model, view.status.chose));
  if (newest?.note) status.append(h("span", { class: "hedge" }, ` (${words.withNote})`));
  return status;
}

function reachList(model, reach) {
  const items = reach.reach.map((address) => h("li", {}, link(model, address)));
  const more = reach.count - reach.reach.length;
  if (more > 0) items.push(h("li", { class: "reach-more" }, words.reachMore(more)));
  return h("ul", { class: "reach-list" }, items);
}

// "Potentially affects": reachability only, in the computed style; collapsed above five entries.
export function reachBlock(model, reach, { same = false } = {}) {
  const title = h("span", { class: "reach-title" }, words.reach, same ? ` (${words.reachSame})` : "");
  if (!reach) return h("div", { class: "reach", "data-part": "reach" }, title, h("p", { class: "loading" }, words.loadingReach));
  if (reach.count === 0) return h("div", { class: "reach", "data-part": "reach" }, title, h("p", { class: "reach-none" }, words.reachNone));
  if (reach.count <= 5) return h("div", { class: "reach", "data-part": "reach" }, title, reachList(model, reach));
  return h(
    "details",
    { class: "reach", "data-part": "reach" },
    h("summary", {}, title, " ", h("span", { class: "reach-count" }, words.reachShow(reach.count))),
    reachList(model, reach),
  );
}

function optionRow(model, view, option, { selected, formId, onChoose }) {
  const id = `option-${option.key}`;
  const state = view.status?.chose === option.address ? "chosen" : "other";
  const proposed = view.proposal?.option === option.address;
  const radio = h("input", {
    type: "radio",
    name: "option",
    id,
    value: option.address,
    form: formId,
    checked: selected === option.address,
    onchange: () => onChoose(option.address),
  });
  return h(
    "li",
    { class: "option", "data-option": option.address, "data-state": state },
    h(
      "div",
      { class: "option-head" },
      radio,
      h("label", { for: id }, link(model, option.address, true)),
      state === "chosen" ? h("span", { class: "pill pill-chosen", "data-mark": "chosen" }, words.chosen) : null,
      proposed ? h("span", { class: "pill", "data-mark": "proposed" }, words.proposed) : null,
    ),
    option.rows.length ? setList(model, option.rows) : h("p", { class: "sets-nothing" }, words.setsNothing),
    view.sameReach ? null : reachBlock(model, option.reach),
  );
}

// The options are the radio group; the answer form further down owns them through its `form` attribute.
export function optionsBlock(model, view, controls) {
  if (!view.options.length) {
    return h(
      "section",
      { class: "block", "data-part": "options" },
      h("h2", {}, words.options),
      h("p", { class: "empty" }, words.noOptions),
    );
  }
  const first = view.options[0];
  return h(
    "section",
    { class: "block", "data-part": "options" },
    h("h2", { id: "options-title" }, words.options),
    h(
      "ul",
      { class: "options", role: "radiogroup", "aria-labelledby": "options-title" },
      view.options.map((option) => optionRow(model, view, option, controls)),
    ),
    view.sameReach ? reachBlock(model, first.reach, { same: true }) : null,
  );
}

export function proposalBlock(model, view) {
  const proposal = view.proposal;
  if (!proposal) return null;
  const line = h("p", { class: "proposal-line" }, h("strong", {}, words.proposedLine));
  if (proposal.option) {
    line.append(" ", link(model, proposal.option));
    if (proposal.why) line.append(` ${words.because} `, authored(proposal.why));
  }
  const block = h("section", { class: "block", "data-part": "proposal" }, h("h2", {}, words.proposal), line);
  if (proposal.rows.length) block.append(setList(model, proposal.rows));
  if (!proposal.option && proposal.why)
    block.append(h("p", { class: "proposal-why" }, `${words.becauseSentence} `, authored(proposal.why)));
  if (proposal.heard) {
    const heard = h("p", { class: "heard" }, `${words.heard} `, authored(proposal.heard));
    if (proposal.option) heard.append(`. ${words.readAs} `, link(model, proposal.option));
    block.append(heard);
  }
  return block;
}

function answerRow(model, answer) {
  return h(
    "li",
    { class: "answer", "data-part": "history-entry" },
    h("p", { class: "answer-head" }, h("time", {}, day(answer.at)), " ", link(model, answer.optionAddress)),
    h("p", { class: "answer-said" }, `${words.heard} `, authored(answer.said)),
    answer.note ? h("p", { class: "answer-note", "data-part": "note" }, `${words.note}: `, authored(answer.note)) : null,
    answer.delegated
      ? h("p", { class: "answer-delegated", "data-part": "delegated" }, `${words.delegated}: `, link(model, answer.delegated))
      : null,
  );
}

export function historyBlock(model, view) {
  return h(
    "section",
    { class: "block", "data-part": "history" },
    h("h2", {}, words.history),
    view.answers.length
      ? h(
          "ol",
          { class: "answers" },
          view.answers.map((answer) => answerRow(model, answer)),
        )
      : h("p", { class: "empty" }, words.noHistory),
  );
}

export function questionBlock(view) {
  return h(
    "section",
    { class: "block" },
    authored(view.question, "h1", { class: "question", "data-part": "question" }),
    view.context ? h("div", { class: "context", "data-part": "context" }, h("h2", {}, words.why), authored(view.context, "p")) : null,
  );
}
