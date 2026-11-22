import { setRows } from "./format.js";

const byDate = (a, b) => String(b.at).localeCompare(String(a.at));

// Everything the page shows, as plain data: the inspection document gives the authored parts, standing gives status and reach.
export function decisionView(model, standing, address) {
  const node = model.byId.get(address);
  if (!node || node.kind !== "decision") return null;
  const parts = model.nodes.filter((part) => part.parent === address);
  const row = standing?.decisions?.[address] || null;
  const proposal = parts.find((part) => part.kind === "proposal") || null;
  const options = parts
    .filter((part) => part.kind === "option")
    .map((option) => ({
      address: option.address,
      key: option.key,
      label: option.label || "",
      rows: setRows(option.sets),
      reach: row?.options?.[option.address] || null,
    }));
  const answers = (Array.isArray(node.answers) ? node.answers : [])
    .map((answer) => ({ ...answer, optionAddress: `${address}/option/${answer.chose}` }))
    .sort(byDate);
  return {
    address,
    question: node.question || node.says || "",
    context: node.context || "",
    status: row ? { state: row.status, chose: row.chose, at: row.at, delegated: row.delegated } : null,
    entry: standing?.entries?.[address] || null,
    options,
    sameReach:
      options.length > 1 && options.every((o) => o.reach && JSON.stringify(o.reach.reach) === JSON.stringify(options[0].reach.reach)),
    proposal: proposal && {
      option: proposal.chose ? `${address}/option/${proposal.chose}` : null,
      why: proposal.why || "",
      heard: proposal.heard || "",
      rows: setRows(proposal.sets),
    },
    answers,
    standingLoaded: Boolean(standing),
  };
}

// The first waiting decision other than this one, in the order standing lists them.
export function nextWaiting(standing, address) {
  const entry = Object.entries(standing?.decisions || {}).find(([key, row]) => key !== address && row.status === "waiting");
  return entry ? entry[0] : null;
}
