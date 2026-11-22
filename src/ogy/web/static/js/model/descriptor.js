export function absent(value) {
  return value?.["\u0000ogy"]?.type === "absent";
}

export function text(value) {
  return typeof value === "string" ? value : "";
}

export function descriptors(ontology) {
  const common = ontology.declared.common;
  const kinds = Object.fromEntries(
    Object.entries(ontology.kinds).map(([name, kind]) => [
      name,
      {
        ...kind,
        label: name,
        fields: { ...common, ...kind.fields },
        parts: kind.parts.map((name) => {
          const part = ontology.kinds[name];
          return { kind: name, path: part.key, holding: part.holds, shape: part.shape };
        }),
      },
    ]),
  );
  return { kinds, common, roles: ontology.declared.roles, source: ontology };
}

// All future mention serializers use this identity, including search and pinned cards.
export function identity(node) {
  const key = node.key.replace(/[-_]/g, " ");
  const fallback = /^(ogy|git|uv|just|pytest|npm|pip|--)/.test(key) ? key : key.replace(/^./, (letter) => letter.toUpperCase());
  const label = ["choice", "option"].includes(node.kind) ? text(node.label) : "";
  const title = text(node.title) || label || (node.kind === "term" ? text(node.word) : "") || fallback;
  return { address: node.address, title, kind: node.kind, accessibleName: `${title} · ${node.kind}` };
}
