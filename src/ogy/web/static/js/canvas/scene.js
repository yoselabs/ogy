import { models } from "../model/models.js";
import { count, esc, mention } from "../render/mentions.js";
import { createLayouts } from "./layout.js";
import { fit } from "./camera.js";
import { detailClass, referenceScale, visible } from "./levels.js";

function slotHTML(slot, reference) {
  return `<foreignObject x="${slot.x}" y="${slot.y}" width="${slot.width / reference}"
    height="${slot.height / reference}" data-slot-id="${esc(slot.id)}">
    <div xmlns="http://www.w3.org/1999/xhtml"
      style="width:${slot.width}px;transform:scale(${1 / reference});transform-origin:0 0">${slot.html}</div></foreignObject>`;
}
function overview(view) {
  const layers = [...new Set(view.nodes.map((n) => n.layer || "constitution"))];
  return `<div class="layer-overview">${layers
    .map((layer) => {
      const nodes = view.nodes.filter((n) => (n.layer || "constitution") === layer);
      const workflows = nodes.filter((n) => n.kind === "workflow");
      const kinds = [...new Set(nodes.filter((n) => n.kind !== "workflow").map((n) => n.kind))];
      return `<article class="layer-summary"><h2>${esc(layer)}</h2><p>${nodes.length} entries</p>
      ${workflows.map((n) => `<div class="layer-workflow">${mention(n)}</div>`).join("")}
      <div class="layer-counts">${kinds
        .map((kind) =>
          count(
            kind,
            nodes.filter((n) => n.kind === kind),
          ),
        )
        .join("")}</div></article>`;
    })
    .join("")}</div>`;
}
export function createScene(stage, store) {
  const svg = stage.querySelector("svg"),
    viewport = stage.querySelector("#vp"),
    outer = stage.querySelector("#overview");
  let model = null,
    view = null,
    layouts = null,
    blocks = [];
  function render(state) {
    if (!state.model) return;
    if (model !== state.model) {
      model = state.model;
      view = models(model);
      layouts = createLayouts(view);
    }
    const camera = state.camera,
      level = detailClass(camera.scale),
      reference = referenceScale(level);
    blocks = layouts(level);
    const wide = stage.clientWidth,
      high = stage.clientHeight;
    outer.hidden = camera.scale >= 0.15;
    svg.toggleAttribute("hidden", !outer.hidden);
    if (!outer.hidden) {
      outer.innerHTML = overview(view);
      return;
    }
    const markup = blocks
      .filter((b) => visible(b, camera, wide, high))
      .map((block) => {
        const frame = block.node.kind === "workflow";
        const slots = block.slots.filter((slot) => visible({ ...slot, x: slot.x + block.x, y: slot.y + block.y }, camera, wide, high));
        const head = { id: block.id, x: 0, y: 0, width: block.width, height: block.height, html: block.html };
        return `<g class="blk ${frame ? "local-frame" : "note"}" data-id="${esc(block.id)}" transform="translate(${block.x},${block.y})">
        ${frame ? `<rect class="f" width="${block.w}" height="${block.h}" rx="12"/>` : ""}
        ${slotHTML(head, reference)}${slots.map((slot) => slotHTML(slot, reference)).join("")}</g>`;
      })
      .join("");
    // Camera-only selection preserves native mouse click targets until click delivery.
    if (viewport.dataset.scene !== markup) {
      viewport.innerHTML = markup;
      viewport.dataset.scene = markup;
    }
    viewport.setAttribute("transform", `translate(${camera.x},${camera.y}) scale(${camera.scale})`);
    for (const element of viewport.querySelectorAll("[data-local-id]")) {
      element.classList.toggle("selected", element.dataset.localId === state.selection);
    }
    svg.dataset.level = level;
  }
  function fitAll() {
    store.dispatch({ type: "camera", camera: fit(layouts("summary"), stage.clientWidth, stage.clientHeight) });
  }
  function select(id) {
    const node = view?.byId.get(id);
    if (!node) return;
    store.dispatch({ type: "select", address: id });
    const level = "detail",
      block = layouts(level).find((b) => b.id === view.owner(id)?.id);
    if (!block) return;
    const slot = block.slots.find((s) => s.id === id || s.id === node.parent);
    const rect = slot
      ? { ...slot, x: slot.x + block.x, y: slot.y + block.y }
      : { ...block, w: block.width / referenceScale(level), h: block.height / referenceScale(level) };
    const scale = 0.85;
    const camera = { scale, x: 24 - rect.x * scale, y: 24 - rect.y * scale };
    store.dispatch({ type: "camera", camera });
  }
  return {
    render,
    fitAll,
    select,
    layout: (level) => layouts(level),
    get view() {
      return view;
    },
  };
}
