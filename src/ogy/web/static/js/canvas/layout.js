import { workflowColumns } from "../model/models.js";
import { renderCard } from "../render/detail.js";
import { referenceScale } from "./levels.js";
import { pack } from "./pack.js";

function measure(html, width, host) {
  host.style.width = `${width}px`; host.innerHTML = html;
  return Math.ceil(Math.max(host.getBoundingClientRect().height, host.firstElementChild?.scrollHeight || 0)) + 4;
}
function sizeBlock(view, node, level, host) {
  const reference = referenceScale(level);
  const width = level === "summary" ? (node.kind === "workflow" ? 280 : 180) : node.kind === "workflow" ? 360 : 300;
  const html = renderCard(view, node, level), height = measure(html, width, host);
  const block = { id: node.id, node, x: 0, y: 0, w: width / reference, h: height / reference, width, height, html, slots: [] };
  if (node.kind !== "workflow" || level === "summary") return block;
  let x = 24, bottom = block.h;
  for (const column of workflowColumns(view, node)) {
    let y = block.height / reference + 32;
    for (const step of column) {
      const content = renderCard(view, step, level), h = measure(content, 360, host);
      block.slots.push({ id: step.id, node: step, x, y, w: 360 / reference, h: h / reference, width: 360, height: h, html: content });
      y += h / reference + 40; bottom = Math.max(bottom, y);
    }
    x += 360 / reference + 80;
  }
  block.w = Math.max(block.w, x); block.h = bottom + 24;
  return block;
}
export function createLayouts(view) {
  const cache = new Map();
  return level => {
    if (cache.has(level)) return cache.get(level);
    const host = document.createElement("div"); host.className = "board-measure";
    document.body.append(host);
    try {
      const blocks = view.nodes.filter(n => n.top).map(n => sizeBlock(view, n, level, host));
      const result = pack(blocks, level); cache.set(level, result); return result;
    } finally { host.remove(); }
  };
}
