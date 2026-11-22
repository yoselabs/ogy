import { edgeLayer } from "../../graph/edges.js";
import { layoutGraph } from "../../graph/elk-layout.js";
import { authored } from "../../ui/authored.js";
import { h } from "../../ui/dom.js";
import { identity } from "../../model/descriptor.js";
import { rolledUp } from "./data.js";
import { nodeElement } from "./node.js";
import { words } from "./words.js";

const PORT_PITCH = 20;
const PORT_PAD = 16;

// A label is the case or choice key; one that stands for several rows ends in a count that opens the step's rows.
function labelElement(edge, select) {
  const { text, title, more, step } = edge.label;
  const count = more
    ? h(
        "button",
        {
          type: "button",
          class: "route-more",
          "data-count": more.length,
          "aria-label": `${more.length} ${words.moreRows}: ${more.map((row) => identity(row).title).join(", ")}`,
          onclick: () => select(step),
        },
        `+${more.length}`,
      )
    : null;
  return h("div", { class: "route-label", "data-edge-label": edge.id, title }, authored(text), count);
}

// Real sizes first: the nodes and labels are built in a hidden layer and measured, so ELK lays out the boxes the page will draw.
function measured(view, edges, options) {
  const nodes = view.nodes.map((item) => ({ item, element: nodeElement(item, options) }));
  const labels = edges.filter((edge) => edge.label).map((edge) => ({ edge, element: labelElement(edge, options.select) }));
  const probe = h(
    "div",
    { class: "flow-measure", "aria-hidden": "true" },
    nodes.map((n) => n.element),
    labels.map((l) => l.element),
  );
  return { nodes, labels, probe };
}

function graphOf(view, edges, built) {
  const ports = new Map(view.nodes.map((item) => [item.id, { in: [], out: [] }]));
  const laid = edges.map((edge) => {
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
  return { nodes, edges: laid };
}

// Draws the graph into `canvas`; resolves with the layout so a check can read it.
// options: level (1 to 3), marks(address), hrefOf(id), select(id).
export async function drawFlow(canvas, view, direction, options) {
  const edges = options.level === 1 ? rolledUp(view.edges) : view.edges;
  const built = measured(view, edges, options);
  canvas.replaceChildren(built.probe);
  const { nodes, edges: graphEdges } = graphOf(view, edges, built);
  const laid = await layoutGraph(nodes, graphEdges, direction);
  const size = new Map(nodes.map((node) => [node.id, node]));
  const layer = edgeLayer(
    laid.width,
    laid.height,
    edges.map((edge) => ({ id: edge.id, from: edge.from, to: edge.to, class: edge.class })),
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
