// The one layout step: ELK lays out nodes, ports and edge labels; nothing here moves a point by hand.
// Input:  nodes [{ id, width, height, out: [portId], in: [portId] }], edges [{ id, from, fromPort, to, toPort, label: {width, height} | null }].
// Output: { width, height, nodes: Map id -> {x, y}, edges: Map id -> { points, label: {x, y} | null } }.
const ELK_URL = "/vendor/elk.bundled.js";
let loading = null;

// elkjs ships as a classic script that sets `ELK` on the window; it is loaded once, from the board's own server.
function loadElk() {
  if (window.ELK) return Promise.resolve(window.ELK);
  loading ||= new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = ELK_URL;
    script.onload = () => resolve(window.ELK);
    script.onerror = () => reject(new Error("The layout library could not be loaded."));
    document.head.append(script);
  });
  return loading;
}

const SPACING = {
  layer: 14,
  node: 28,
  edgeNode: 16,
  edgeEdge: 12,
  portPort: 14,
  label: 6,
  pad: 8,
};

function options(direction) {
  return {
    "elk.algorithm": "layered",
    "elk.direction": direction,
    "elk.edgeRouting": "ORTHOGONAL",
    "elk.padding": `[top=${SPACING.pad},left=${SPACING.pad},bottom=${SPACING.pad},right=${SPACING.pad}]`,
    "elk.spacing.nodeNode": String(SPACING.node),
    "elk.spacing.edgeNode": String(SPACING.edgeNode),
    "elk.spacing.edgeEdge": String(SPACING.edgeEdge),
    "elk.spacing.portPort": String(SPACING.portPort),
    "elk.spacing.edgeLabel": String(SPACING.label),
    "elk.layered.spacing.nodeNodeBetweenLayers": String(SPACING.layer),
    "elk.layered.spacing.edgeNodeBetweenLayers": String(SPACING.edgeNode),
    "elk.layered.spacing.edgeEdgeBetweenLayers": String(SPACING.edgeEdge),
    "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
    "elk.edgeLabels.placement": "CENTER",
    "elk.edgeLabels.inline": "true",
  };
}

// Ports sit on the side the direction runs towards (out) and from (in): east and west, or south and north.
const SIDES = { RIGHT: { out: "EAST", in: "WEST" }, DOWN: { out: "SOUTH", in: "NORTH" } };

function elkGraph(nodes, edges, direction) {
  const sides = SIDES[direction];
  const port = (id, side) => ({ id, width: 0, height: 0, layoutOptions: { "elk.port.side": side } });
  return {
    id: "root",
    layoutOptions: options(direction),
    children: nodes.map((node) => ({
      id: node.id,
      width: node.width,
      height: node.height,
      layoutOptions: { "elk.portConstraints": "FIXED_SIDE", "elk.portAlignment.default": "DISTRIBUTED" },
      ports: [...node.in.map((id) => port(id, sides.in)), ...node.out.map((id) => port(id, sides.out))],
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.fromPort],
      targets: [edge.toPort],
      labels: edge.label
        ? [
            {
              text: edge.id,
              width: edge.label.width,
              height: edge.label.height,
              layoutOptions: { "elk.edgeLabels.placement": "CENTER", "elk.edgeLabels.inline": "true" },
            },
          ]
        : [],
    })),
  };
}

function polyline(edge) {
  const section = edge.sections?.[0];
  if (!section) return [];
  return [section.startPoint, ...(section.bendPoints || []), section.endPoint].map(({ x, y }) => ({ x, y }));
}

export async function layoutGraph(nodes, edges, direction) {
  const ELK = await loadElk();
  const laid = await new ELK().layout(elkGraph(nodes, edges, direction));
  return {
    width: laid.width,
    height: laid.height,
    nodes: new Map(laid.children.map((node) => [node.id, { x: node.x, y: node.y }])),
    edges: new Map(
      laid.edges.map((edge) => [
        edge.id,
        { points: polyline(edge), label: edge.labels?.[0] ? { x: edge.labels[0].x, y: edge.labels[0].y } : null },
      ]),
    ),
  };
}
