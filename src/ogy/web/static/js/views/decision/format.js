const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// The date as it was recorded, never shifted by the viewer's time zone.
export function day(iso) {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || "");
  return match ? `${Number(match[3])} ${MONTHS[Number(match[2]) - 1]} ${match[1]}` : "";
}

// An address that no entry in the document answers (a set entry not written yet, a removed option) still gets its mention.
export function nodeFor(model, address) {
  const known = model.byId.get(address);
  if (known) return known;
  const parts = address.split("/");
  return { id: address, address, key: parts.at(-1), kind: parts.length >= 4 ? parts.at(-2) : "entry", title: "" };
}

export function valueText(value) {
  return value !== null && typeof value === "object" ? JSON.stringify(value) : String(value);
}

// What an option sets: per address, the field values, or `null` when the entry does not exist under that option.
export function setRows(sets) {
  if (!sets || typeof sets !== "object") return [];
  return Object.entries(sets).map(([address, fields]) => ({
    address,
    fields: fields && typeof fields === "object" ? Object.entries(fields).map(([name, value]) => [name, valueText(value)]) : null,
  }));
}
