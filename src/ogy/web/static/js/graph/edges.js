// One SVG layer under the DOM nodes: a path per edge, drawn from the points the layout returned.
const NS = "http://www.w3.org/2000/svg";
const RADIUS = 6;

function svg(tag, attributes = {}) {
  const element = document.createElementNS(NS, tag);
  for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, value);
  return element;
}

// Orthogonal points as a path with the corners rounded; the first and last points stay exactly where the layout put them.
export function pathOf(points) {
  if (points.length < 2) return "";
  let d = `M${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const before = points[i - 1];
    const corner = points[i];
    const after = points[i + 1];
    const inLength = Math.hypot(corner.x - before.x, corner.y - before.y);
    const outLength = Math.hypot(after.x - corner.x, after.y - corner.y);
    const r = Math.min(RADIUS, inLength / 2, outLength / 2);
    const enter = { x: corner.x - ((corner.x - before.x) / inLength) * r, y: corner.y - ((corner.y - before.y) / inLength) * r };
    const leave = { x: corner.x + ((after.x - corner.x) / outLength) * r, y: corner.y + ((after.y - corner.y) / outLength) * r };
    d += ` L${enter.x} ${enter.y} Q${corner.x} ${corner.y} ${leave.x} ${leave.y}`;
  }
  const last = points.at(-1);
  return `${d} L${last.x} ${last.y}`;
}

// The layer for one graph: `edges` carry id, from, to and the extra class names; `routes` come from the layout.
export function edgeLayer(width, height, edges, routes) {
  const layer = svg("svg", { class: "edge-layer", width, height, viewBox: `0 0 ${width} ${height}`, "aria-hidden": "true" });
  const defs = svg("defs");
  const head = svg("marker", {
    id: "edge-head",
    viewBox: "0 0 10 10",
    refX: "10",
    refY: "5",
    markerWidth: "8",
    markerHeight: "8",
    orient: "auto",
  });
  head.append(svg("path", { d: "M0 1 L10 5 L0 9 z", class: "edge-head" }));
  defs.append(head);
  layer.append(defs);
  for (const edge of edges) {
    const route = routes.get(edge.id);
    if (!route?.points.length) continue;
    layer.append(
      svg("path", {
        class: `edge ${edge.class || ""}`.trim(),
        d: pathOf(route.points),
        "marker-end": "url(#edge-head)",
        "data-edge": edge.id,
        "data-from": edge.from,
        "data-to": edge.to,
      }),
    );
  }
  return layer;
}
