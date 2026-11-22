import "../../../vendor/elk.bundled.js";
import { authored } from "../../ui/authored.js";
import { cardHeader } from "../../ui/card-header.js";
import { glyph, h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { pathStrip as owners } from "../../ui/path.js";
import { words } from "./words.js";

// The lifecycle as a drawn graph: states are nodes, each transition an edge labelled with who fires it. ELK places nodes,
// routes edges and reserves room for the labels; this file only measures what ELK needs and draws what it returns.
const SVG = "http://www.w3.org/2000/svg";
const SHOWN = 2;
// A graph that would have to shrink below this is not drawn: type under 80% of its size is not read.
const LEAST = 0.8;
let elk = null;

// workflow › step › case: the owners of a row that fires a transition.
export const pathStrip = (path) => owners(path, { "data-part": "fired-by" });

export function owedTag() {
  return h("span", { class: "lc-owed", "data-part": "owed-tag" }, glyph("owed"), h("span", {}, words.owed));
}

function stateNode(state, facts) {
  return h(
    "div",
    { class: "lc-node", "data-local-id": state.id, "data-address": state.address, "data-part": "state" },
    cardHeader(state, facts.marks(state.address)),
    state.says ? authored(state.says, "p", { class: "says" }) : null,
  );
}

function labelOf(transition, index) {
  const shown = transition.firedBy.slice(0, SHOWN);
  const rest = transition.firedBy.length - shown.length;
  return h(
    "div",
    {
      class: `lc-label${transition.owed ? " is-owed" : ""}`,
      "data-local-id": `label/${transition.node.id}/${index}`,
      "data-part": "transition-label",
      "data-address": transition.node.address,
    },
    h("div", { class: "lc-label-head" }, mention(transition.node, { self: true }), transition.owed ? owedTag() : null),
    shown.map(pathStrip),
    rest > 0 ? h("small", { class: "lc-more" }, `+${rest} ${words.more}`) : null,
  );
}

function elements(view, facts) {
  const nodes = new Map(view.states.map((state) => [state.id, stateNode(state, facts)]));
  const edges = [];
  for (const transition of view.transitions) {
    if (!transition.to || !nodes.has(transition.to.id)) continue;
    const from = transition.from.filter((state) => nodes.has(state.id));
    // A transition without `from` creates the entity: a hollow dot is its source.
    const sources = from.length ? from.map((state) => state.id) : [`start/${transition.node.id}`];
    for (const [index, source] of sources.entries()) {
      if (source.startsWith("start/")) nodes.set(source, h("div", { class: "lc-start", "data-part": "start", "aria-hidden": "true" }));
      edges.push({ id: `${transition.node.id}/${index}`, source, target: transition.to.id, transition, label: labelOf(transition, index) });
    }
  }
  return { nodes, edges };
}

function size(element) {
  return { width: element.offsetWidth, height: element.offsetHeight };
}

function edgePath(section) {
  const points = [section.startPoint, ...(section.bendPoints || []), section.endPoint];
  return points.map((point, index) => `${index ? "L" : "M"}${point.x} ${point.y}`).join(" ");
}

function svgOf(width, height, routes) {
  const svg = document.createElementNS(SVG, "svg");
  svg.setAttribute("class", "lc-svg");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.style.width = `${width}px`;
  svg.style.height = `${height}px`;
  const marker = (name) =>
    `<marker id="lc-arrow-${name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path class="lc-arrow lc-arrow-${name}" d="M0 0L10 5L0 10z"/></marker>`;
  svg.innerHTML = `<defs>${marker("fired")}${marker("owed")}</defs>`;
  for (const route of routes) {
    const path = document.createElementNS(SVG, "path");
    const kind = route.owed ? "owed" : "fired";
    path.setAttribute("class", `lc-edge is-${kind}`);
    path.setAttribute("d", route.d);
    path.setAttribute("marker-end", `url(#lc-arrow-${kind})`);
    path.setAttribute("data-transition", route.address);
    svg.append(path);
  }
  return svg;
}

// One ELK run in one direction. The label and node widths are set first and measured after, so ELK reserves what is drawn.
async function layoutOnce(host, nodes, edges, vertical) {
  const width = host.clientWidth;
  const node = Math.min(216, width - 32);
  host.style.setProperty("--lc-node", `${node}px`);
  host.style.setProperty("--lc-label-max", `${vertical ? Math.max(160, width - 32 - node / 2 - 8) : 300}px`);
  elk ||= new window.ELK();
  return elk.layout({
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": vertical ? "DOWN" : "RIGHT",
      "elk.edgeRouting": "ORTHOGONAL",
      "elk.padding": "[top=16,left=16,bottom=16,right=16]",
      "elk.spacing.nodeNode": "40",
      "elk.layered.spacing.nodeNodeBetweenLayers": "32",
      "elk.layered.spacing.edgeNodeBetweenLayers": "16",
      "elk.layered.spacing.edgeEdgeBetweenLayers": "16",
      "elk.spacing.edgeEdge": "16",
      "elk.spacing.edgeNode": "24",
      "elk.spacing.edgeLabel": "8",
      "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
    },
    children: [...nodes].map(([id, element]) => ({ id, ...size(element) })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target],
      // ELK reserves room for a label only when it has text; the text is never drawn from here.
      labels: [{ id: `${edge.id}/label`, text: edge.transition.node.key, ...size(edge.label) }],
    })),
  });
}

// Where the graph cannot be drawn legibly the states are named and the list under it says the rest.
function fallback(host, view, scale) {
  host.style.height = "";
  host.replaceChildren(
    h(
      "div",
      { class: "lc-fallback", "data-part": "diagram-fallback" },
      h(
        "p",
        { class: "lc-states", "data-part": "states" },
        view.states.map((state) => mention(state, { self: true })),
      ),
      h("p", { class: "note" }, words.tooWide),
    ),
  );
  return { width: 0, height: 0, scale, edges: 0, direction: "list" };
}

// Draws the lifecycle into `host` (a block of the page's width). Left to right when that fits, else top to bottom.
export async function drawLifecycle(host, view, facts) {
  const { nodes, edges } = elements(view, facts);
  const stage = h("div", { class: "lc-stage", "data-part": "diagram" });
  stage.append(...nodes.values(), ...edges.map((edge) => edge.label));
  host.replaceChildren(stage);
  let vertical = host.clientWidth < 640;
  let laid = await layoutOnce(host, nodes, edges, vertical);
  if (!vertical && laid.width > host.clientWidth * 1.05) {
    vertical = true;
    laid = await layoutOnce(host, nodes, edges, vertical);
  }
  const scale = Math.min(1, host.clientWidth / laid.width);
  if (scale < LEAST) return fallback(host, view, scale);
  stage.dataset.direction = vertical ? "down" : "right";
  for (const child of laid.children) {
    const element = nodes.get(child.id);
    element.style.left = `${child.x}px`;
    element.style.top = `${child.y}px`;
  }
  const routes = [];
  for (const out of laid.edges) {
    const edge = edges.find((candidate) => candidate.id === out.id);
    const label = out.labels[0];
    edge.label.style.left = `${label.x}px`;
    edge.label.style.top = `${label.y}px`;
    routes.push({ d: edgePath(out.sections[0]), owed: edge.transition.owed, address: edge.transition.node.address });
  }
  stage.style.width = `${laid.width}px`;
  stage.style.height = `${laid.height}px`;
  stage.style.transform = scale < 1 ? `scale(${scale})` : "";
  host.style.height = `${Math.ceil(laid.height * scale)}px`;
  stage.prepend(svgOf(laid.width, laid.height, routes));
  stage.classList.add("is-laid");
  return { width: laid.width, height: laid.height, scale, edges: routes.length, direction: stage.dataset.direction };
}
