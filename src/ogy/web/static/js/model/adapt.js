import { absent, descriptors, text } from "./descriptor.js";

export function locatorId(locator) {
  return `${locator.owner}#${encodeURIComponent(locator.field)}/${locator.index}`;
}

function node(record, vocabulary) {
  const address = text(record.address) || null;
  const fields = record.fields;
  const id = address || locatorId(record.locator);
  const parent = text(record.parent) || null;
  const kind = vocabulary.kinds[record.kind];
  return {
    ...fields,
    id,
    address,
    key: text(record.key) || (record.locator ? `${record.locator.field} ${record.locator.index + 1}` : id.split("/").at(-1)),
    kind: record.kind,
    layer: record.layer,
    area: record.layer ? `${record.layer}/${record.area}` : record.area,
    parent,
    top: parent === null,
    title: text(record.title),
    says: text(record.sentence),
    when: text(fields.when?.text),
    atype: fields.type,
    invoked: fields.invoked_as,
    reads: [],
    fx: [],
    detail: {
      fields,
      absentFields: record.absent_fields,
      availability: Object.fromEntries([
        ...Object.keys(record.absent_fields || {}).map((name) => [name, "none"]),
        ...Object.keys(fields).map((name) => [name, "known"]),
      ]),
      sentenceField: absent(record.sentence_field) ? null : record.sentence_field,
      sentence: absent(record.sentence) ? null : record.sentence,
      sentenceAvailability: absent(record.sentence) ? "none" : "known",
      parts: Object.fromEntries((kind?.parts || []).map((part) => [part.path, { kind: part.kind, ids: [], complete: true }])),
      effects: [],
      expressions: {},
      source: { location: record.source, locator: record.locator || null },
    },
  };
}

function relations(document) {
  return document.relations.map((relation, index) => ({
    id: `relation:${index}`,
    s: typeof relation.source === "string" ? relation.source : locatorId(relation.source),
    t: text(relation.target) || null,
    f: relation.field,
    value: relation.value,
    source: relation.witness,
    unresolved: absent(relation.target) ? relation.target : null,
  }));
}

function enrich(nodes, edges) {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  for (const n of nodes) {
    const type = edges.find((edge) => edge.s === n.id && edge.f === "of");
    if (type) n.of = type.t;
    const children = nodes.filter((part) => part.parent === n.id);
    for (const part of Object.values(n.detail.parts)) {
      part.ids = children.filter((child) => child.kind === part.kind).map((child) => child.id);
      part.availability = part.ids.length ? "known" : "none";
    }
    for (const expression of ["when", "derived"]) {
      const value = n.detail.fields[expression];
      const witnesses = edges.filter((edge) => edge.s === n.id && edge.f === expression);
      n.detail.expressions[expression] = { text: text(value?.text), reads: witnesses.map((edge) => edge.t), witnesses };
      if (expression === "when") n.reads = witnesses.map((edge) => edge.t).filter(Boolean);
    }
    const effects = children.filter((part) => part.kind === "effect");
    n.detail.effects = effects.map((part) => ({
      rowId: n.id,
      index: part.detail.source.locator?.index,
      locator: part.detail.source.locator,
      fields: part.detail.fields,
      availability: "known",
      valueAvailability: Object.hasOwn(part.detail.fields, "value") ? "known" : "none",
      source: part.detail.source,
    }));
    n.fx = effects.map((part) => {
      const target = edges.find((edge) => edge.s === part.id && edge.f === "on");
      return { ...part.detail.fields, onid: target?.t || null, source: part.detail.source };
    });
  }
  return byId;
}

export function adapt(document) {
  if (document.schema !== 2) throw new Error(`Unsupported inspection version: ${document.schema}`);
  const vocabulary = descriptors(document.ontology);
  const nodes = [...document.entries, ...document.parts].map((record) => node(record, vocabulary));
  const edges = relations(document);
  const byId = enrich(nodes, edges);
  return { nodes, edges, byId, vocabulary, snapshot: document.snapshot, source: document };
}
