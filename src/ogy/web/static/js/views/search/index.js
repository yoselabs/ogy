import { identity } from "../../model/descriptor.js";

// Kinds in the order a tie between groups is broken: what the owner looks for first goes first, the paperwork last.
const KIND_ORDER = [
  "goal",
  "capability",
  "workflow",
  "entity",
  "actor",
  "term",
  "rule",
  "quantity",
  "setting",
  "interface",
  "handler",
  "dependency",
  "decision",
];
const LAST = new Set(["option", "proposal", "answer"]);

export const kindRank = (kind) => (LAST.has(kind) ? 1000 : KIND_ORDER.includes(kind) ? KIND_ORDER.indexOf(kind) : 500);
const plain = (text) =>
  String(text ?? "")
    .toLowerCase()
    .replace(/[-_/]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();

function ownerPath(model, node) {
  const path = [];
  for (let at = node.parent && model.byId.get(node.parent); at; at = at.parent && model.byId.get(at.parent))
    path.unshift(identity(at).title);
  return path;
}

// Where a result leads: an entry to its own address, a part (no address of its own) to the entry that holds it.
function target(model, node) {
  let at = node;
  while (at && !at.address) at = at.parent && model.byId.get(at.parent);
  return at?.address || null;
}

// One pass over the document, done when it changes: lowercase copies of every searched field, so a keystroke only compares strings.
export function buildIndex(model) {
  return model.nodes
    .map((node) => {
      const { title } = identity(node);
      const goes = target(model, node);
      if (!goes) return null;
      const path = ownerPath(model, node);
      return {
        node,
        title,
        goes,
        context: node.top ? node.area : path.join(" › "),
        part: !node.top,
        kind: node.kind,
        t: plain(title),
        k: plain(node.key),
        a: plain(node.address),
        s: plain([node.question, node.says, node.label, node.word].filter((value) => typeof value === "string").join(" ")),
      };
    })
    .filter(Boolean);
}

const atWord = (text, token) => text.startsWith(token) || text.includes(` ${token}`);

// A name that is the query beats a name that holds it, which beats a key, an address, then a sentence. A part ranks under an entry.
function score(item, full, tokens) {
  if (item.t === full) return 1000 - (item.part ? 40 : 0);
  if (item.k === full) return 900 - (item.part ? 40 : 0);
  let total = item.t.startsWith(full) ? 700 : atWord(item.t, full) ? 600 : item.t.includes(full) ? 500 : 0;
  for (const token of tokens) {
    const here = atWord(item.t, token)
      ? 120
      : item.t.includes(token)
        ? 100
        : item.k.includes(token)
          ? 60
          : item.a.includes(token)
            ? 40
            : item.s.includes(token)
              ? 20
              : 0;
    if (!here) return 0;
    total += here;
  }
  return total - (item.part ? 40 : 0);
}

// Matches grouped by kind: the group holding the best match first; inside a group, best score then shorter name.
export function search(index, query) {
  const full = plain(query);
  if (!full) return [];
  const tokens = full.split(" ");
  const groups = new Map();
  for (const item of index) {
    const value = score(item, full, tokens);
    if (!value) continue;
    if (!groups.has(item.kind)) groups.set(item.kind, { kind: item.kind, best: 0, items: [] });
    const group = groups.get(item.kind);
    group.best = Math.max(group.best, value);
    group.items.push({ item, value });
  }
  for (const group of groups.values()) {
    group.items.sort((a, b) => b.value - a.value || a.item.t.length - b.item.t.length || a.item.a.localeCompare(b.item.a));
    group.items = group.items.map((entry) => entry.item);
  }
  return [...groups.values()].sort((a, b) => b.best - a.best || kindRank(a.kind) - kindRank(b.kind));
}
