const paths = {
  goal: "M6 1v10M1 6h10M2 2l8 8M10 2l-8 8",
  capability: "M1 3h10v8H1zM4 3V1h4v2",
  workflow: "M1 2h4v3H1zM7 7h4v3H7zM5 3h4v4",
  entity: "M1 2h10v8H1zM1 5h10M5 5v5",
  actor: "M8 3a2 2 0 1 1-4 0 2 2 0 0 1 4 0M2 11V9a4 4 0 0 1 8 0v2",
  decision: "M6 1l5 5-5 5-5-5z",
  transition: "M1 6h9M6 2l4 4-4 4",
  create: "M6 1v10M1 6h10",
  write: "m1 8 7-7 3 3-7 7H1zM6 3l3 3",
  delete: "m2 2 8 8M10 2l-8 8",
  tell: "M1 2h10v8H1zM1 2l5 4 5-4",
};
export function icon(kind, operation = false) {
  return `<svg class="${operation ? "operation-icon" : "kind-icon"}" viewBox="0 0 12 12" aria-hidden="true">
    <path d="${paths[kind] || "M2 2h8v8H2z"}"/></svg>`;
}
