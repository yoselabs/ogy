// One glyph per ontology kind, per effect operation and per status mark or control; tests keep every path distinct.
const kinds = {
  actor: "M8 2.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM3 14c0-3 2.2-5 5-5s5 2 5 5",
  answer: "M2 3h12v8H7l-3 3v-3H2z",
  area: "M2 4h5l1.5 1.5H14v8H2z",
  attribute: "M2 5h12M2 8h12M2 11h8",
  capability: "M8 1.5l5.5 3v7L8 14.5l-5.5-3v-7z",
  case: "M3 8h4l5-4M7 8l5 4",
  choice: "M2.5 3h11v4h-11zM2.5 9h11v4h-11z",
  decision: "M8 1.5l6.5 6.5L8 14.5 1.5 8z",
  dependency: "M6 2v4M10 2v4M4.5 6h7v3a3.5 3.5 0 0 1-7 0zM8 12.5V15",
  effect: "M9 1.5L3.5 9H8l-1 5.5L12.5 7H8z",
  end: "M4 2v12M4 3h8l-2 3 2 3H4",
  entity: "M2 3h12v10H2zM2 6.5h12M6 6.5V13",
  enum: "M5 4h9M5 8h9M5 12h9M2 4h.01M2 8h.01M2 12h.01",
  goal: "M8 1.5l1.9 4 4.3.5-3.2 3 .9 4.3L8 11.1l-3.9 2.2.9-4.3-3.2-3 4.3-.5z",
  pain: "M9 1.5L3.5 9H7.5L6.5 14.5L12.5 7H8.5Z",
  handler:
    "M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M12.6 3.4l-1.4 1.4M4.8 11.2l-1.4 1.4",
  interface: "M3 5h10M10 2.5L13 5l-3 2.5M13 11H3M6 8.5L3 11l3 2.5",
  option: "M8 2.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11z",
  principle: "M3 14h10M4 14V6M8 14V6M12 14V6M2 6l6-4 6 4",
  proposal: "M3 2h7l3 3v9H3zM10 2v3h3M6 9h4",
  quantity: "M5.5 2l-1 12M11.5 2l-1 12M2.5 6h12M1.5 10h12",
  rule: "M8 1.5L13.5 4v4c0 3-2.3 5-5.5 6.5C4.8 13 2.5 11 2.5 8V4z",
  setting: "M2 4h12M2 12h12M10 2v4M5 10v4",
  state: "M5 4h6a4 4 0 0 1 0 8H5A4 4 0 0 1 5 4z",
  step: "M2 4h9l3 4-3 4H2z",
  term: "M2 8.5V2.5h6l6 6-5.5 5.5zM5.5 5.5h.01",
  timeout: "M8 2a6 6 0 1 0 0 12A6 6 0 0 0 8 2zM8 4.5V8l2.5 1.5",
  transition: "M2 8h10M8.5 4.5L12 8l-3.5 3.5",
  workaround: "M2 12c0-6 4-8 7-8h5M11 1.5L14 4l-3 2.5",
  workflow: "M2 3h4v3H2zM10 10h4v3h-4zM6 4.5h2.5v7H10",
};
// What an effect does to its target: create, delete, write, transition, tell.
const operations = {
  create: "M8 2v12M2 8h12",
  delete: "M3 3l10 10M13 3L3 13",
  "do-transition": "M2 8h8M7 5l3 3-3 3M13 3v10",
  tell: "M2 3.5h12v9H2zM2 3.5l6 5 6-5",
  write: "M2 14l1-4 7.5-7.5 3 3L6 13zM9 4l3 3",
};
// Status marks of the strip and card headers, and the viewer's own controls.
const marks = {
  back: "M13 8H3M7 4L3 8l4 4",
  changed: "M13 8a5 5 0 1 1-1.5-3.5M13 2v3h-3",
  dropped: "M3 4.5h10M6.5 4.5V2.5h3v2M4.5 4.5l.7 9h5.6l.7-9",
  findings: "M5 2.5h6v2H5zM3.5 3.5h9v10.5h-9zM6 8l4 3M10 8l-4 3",
  owed: "M8 2L14.5 13.5h-13zM8 6.5v3.5M8 12h.01",
  search: "M7 2.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9zM10.5 10.5L14 14",
  unagreed: "M5.5 6a2.5 2.5 0 1 1 3.8 2.1C8.5 8.6 8 9 8 10.5M8 13h.01",
  waiting: "M4 2h8M4 14h8M5 2c0 3 3 4 3 6s-3 3-3 6M11 2c0 3-3 4-3 6s3 3 3 6",
};
export const glyphs = { ...kinds, ...Object.fromEntries(Object.entries(operations).map(([name, path]) => [name, path])), ...marks };
export const kindNames = Object.keys(kinds);
export const operationNames = Object.keys(operations);
export const markNames = Object.keys(marks);

const stroke = 'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"';
export function icon(name, operation = false) {
  const key = operation && name === "transition" ? "do-transition" : name;
  return `<svg class="${operation ? "operation-icon" : "kind-icon"} ic" viewBox="0 0 16 16" ${stroke} aria-hidden="true" focusable="false">
    <path d="${glyphs[key] || "M3 3h10v10H3z"}"/></svg>`;
}
