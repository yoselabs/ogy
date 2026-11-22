import { edgeLayer } from "../../graph/edges.js";
import { layoutGraph } from "../../graph/elk-layout.js";
import { cardHeader } from "../../ui/card-header.js";
import { authored } from "../../ui/authored.js";
import { glyph, h } from "../../ui/dom.js";
import { words } from "./words.js";

const PORT_PITCH = 20;
const PORT_PAD = 16;

function nodeElement(item, facts) {
  if (item.stub) return h("div", { class: "flow-node flow-start", "data-node": item.id }, h("span", {}, words.start));
  const { node } = item;
  const classes = ["flow-node", `kind-${node.kind}`];
  if (node.kind === "end") classes.push(`end-${node.result}`);
  if (item.external) classes.push("is-external");
  const header = cardHeader(node, facts.marks(node.address));
  if (node.kind === "end") header.querySelector(".kind-word").append(` · ${node.result}`);
  return h("div", { class: classes.join(" "), "data-node": item.id, "data-address": node.address || null }, header);
}

function labelElement(edge) {
  return h("div", { class: "route-label", "data-edge-label": edge.id, title: edge.label.title }, authored(edge.label.text));
}

// Real sizes first: the nodes and labels are built in a hidden layer and measured, so ELK lays out the boxes the page will draw.
function measured(view, facts) {
  const nodes = view.nodes.map((item) => ({ item, element: nodeElement(item, facts) }));
  const labels = view.edges.filter((edge) => edge.label).map((edge) => ({ edge, element: labelElement(edge) }));
  const probe = h(
    "div",
    { class: "flow-measure", "aria-hidden": "true" },
    nodes.map((n) => n.element),
    labels.map((l) => l.element),
  );
  return { nodes, labels, probe };
}

function graphOf(view, built) {
  const ports = new Map(view.nodes.map((item) => [item.id, { in: [], out: [] }]));
  const edges = view.edges.map((edge) => {
    const fromPort = `${edge.id}:out`;
    const toPort = `${edge.id}:in`;
    ports.get(edge.from).out.push(fromPort);
    ports.get(edge.to).in.push(toPort);
    const label = built.labels.find((found) => found.edge === edge)?.element;
    return { id: edge.id, fromPort, toPort, label: label ? { width: label.offsetWidth, height: label.offsetHeight } : null };
  });
  const nodes = built.nodes.map(({ item, element }) => {
    const here = ports.get(item.id);
    const wanted = Math.max(here.in.length, here.out.length) * PORT_PITCH + PORT_PAD * 2;
    return { id: item.id, width: element.offsetWidth, height: Math.max(element.offsetHeight, wanted), ...here };
  });
  return { nodes, edges };
}

// Draws the graph into `canvas`; resolves with the layout so a check can read it.
export async function drawFlow(canvas, view, facts, direction) {
  const built = measured(view, facts);
  canvas.replaceChildren(built.probe);
  const { nodes, edges } = graphOf(view, built);
  const laid = await layoutGraph(nodes, edges, direction);
  const size = new Map(nodes.map((node) => [node.id, node]));
  const layer = edgeLayer(
    laid.width,
    laid.height,
    view.edges.map((edge) => ({ id: edge.id, from: edge.from, to: edge.to, class: edge.class })),
    laid.edges,
  );
  const placed = built.nodes.map(({ item, element }) => {
    const at = laid.nodes.get(item.id);
    Object.assign(element.style, {
      left: `${at.x}px`,
      top: `${at.y}px`,
      width: `${size.get(item.id).width}px`,
      height: `${size.get(item.id).height}px`,
    });
    return element;
  });
  const labels = built.labels.map(({ edge, element }) => {
    const at = laid.edges.get(edge.id)?.label;
    if (at) Object.assign(element.style, { left: `${at.x}px`, top: `${at.y}px` });
    return element;
  });
  canvas.style.width = `${laid.width}px`;
  canvas.style.height = `${laid.height}px`;
  canvas.replaceChildren(layer, ...placed, ...labels);
  return laid;
}
