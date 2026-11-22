import { h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { flowStrip, gap, head, says } from "./parts.js";
import { words } from "./words.js";

// One workflow: its head, its sentence and the strip of its steps and ends.
function workflowItem(view, facts, workflow) {
  return h(
    "li",
    { class: "wf", "data-part": "workflow", "data-address": workflow.address },
    head(workflow, facts),
    says(workflow),
    flowStrip(view.flows.get(workflow.id) || []),
  );
}

function workflowCell(view, facts, row) {
  const cell = h("div", { class: "cell wf-cell", "data-cell": "workflow" });
  if (row.shownUnder) {
    cell.append(h("p", { class: "note" }, `${words.shownUnder} `, mention(row.shownUnder)));
    return cell;
  }
  if (row.none) cell.append(gap(words.noWorkflow));
  if (row.workflows.length)
    cell.append(
      h(
        "ul",
        { class: "wf-list" },
        row.workflows.map((workflow) => workflowItem(view, facts, workflow)),
      ),
    );
  if (row.elsewhere.length) {
    cell.append(h("p", { class: "note" }, `${words.elsewhere} `, ...row.elsewhere.flatMap((workflow) => [mention(workflow), " "])));
  }
  return cell;
}

function capabilityRow(view, facts, row) {
  return h(
    "div",
    { class: "chain-row" },
    h("div", { class: "cell cap-cell", "data-cell": "capability" }, head(row.capability, facts), says(row.capability)),
    workflowCell(view, facts, row),
  );
}

// Workflows no capability realizes share one row: the missing capability is said once.
function looseRow(view, facts, workflows) {
  return h(
    "div",
    { class: "chain-row" },
    h("div", { class: "cell cap-cell", "data-cell": "capability" }, gap(words.looseWorkflow)),
    h(
      "div",
      { class: "cell wf-cell", "data-cell": "workflow" },
      h(
        "ul",
        { class: "wf-list" },
        workflows.map((workflow) => workflowItem(view, facts, workflow)),
      ),
    ),
  );
}

function group(goalCell, rows, extra = {}) {
  return h(
    "article",
    { class: "chain-group", ...extra },
    h("div", { class: "cell goal-cell", "data-cell": "goal" }, goalCell),
    h("div", { class: "chain-rows" }, rows),
  );
}

// The why-chain table: goal | capability | workflow, one group per goal, gaps shown as owed work.
function table(view, facts) {
  const { goalRows, noGoal } = view.chain;
  const groups = goalRows.map(({ goal, capabilities }) =>
    group(
      [head(goal, facts), says(goal)],
      capabilities.length
        ? capabilities.map((row) => capabilityRow(view, facts, row))
        : h("div", { class: "chain-row" }, h("div", { class: "cell cap-cell span", "data-cell": "capability" }, gap(words.noCapability))),
      { "data-address": goal.address },
    ),
  );
  if (noGoal.capabilities.length || noGoal.workflows.length) {
    groups.push(
      group(
        gap(words.noGoal),
        [
          ...noGoal.capabilities.map((row) => capabilityRow(view, facts, row)),
          ...(noGoal.workflows.length ? [looseRow(view, facts, noGoal.workflows)] : []),
        ],
        { "data-part": "no-goal" },
      ),
    );
  }
  const columns = ["goal", "capability", "workflow"].map((kind) => h("span", { class: "kind-word" }, kind));
  return h("div", { class: "chain", "data-part": "chain" }, h("div", { class: "chain-head", "aria-hidden": "true" }, columns), groups);
}

// The why-chain where the layer has goals; otherwise the workflows alone (software has no goals to be missing).
export function chainSection(view, facts) {
  const { chain } = view;
  if (chain.hasGoals) {
    const empty = !chain.goalRows.length && !chain.noGoal.capabilities.length && !chain.noGoal.workflows.length;
    return empty ? null : h("section", { class: "block", "data-part": "why" }, h("h2", {}, words.why), table(view, facts));
  }
  if (!chain.workflows.length) return null;
  return h(
    "section",
    { class: "block", "data-part": "why" },
    h("h2", {}, words.workflows),
    h(
      "ul",
      { class: "wf-list wf-plain" },
      chain.workflows.map((workflow) => workflowItem(view, facts, workflow)),
    ),
  );
}
