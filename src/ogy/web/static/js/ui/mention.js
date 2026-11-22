import { identity } from "../model/descriptor.js";
import { glyph, h } from "./dom.js";
import { authored } from "./authored.js";

// The only place an entry's name is drawn: icon and title. Kind is told by the icon and, in a card header, by the corner word.
// `self` marks the entry a header names itself (no link); `href` points the link at a page other than the entry's own (an area tile).
export function mention(node, { self = false, href = null } = {}) {
  if (!node) return null;
  const token = identity(node);
  const classes = `mention kind-${node.kind}${self ? "" : " lk"}`;
  const content = [glyph(node.kind), authored(token.title, "span", { "data-identity-text": true })];
  if (self) return h("span", { class: classes, "data-entry-id": node.id, "data-renderer": "title-token" }, content);
  return h(
    "a",
    {
      class: classes,
      href: href || `#/${node.address || node.id}`,
      "data-entry-id": node.id,
      "data-renderer": "mention",
      "aria-label": token.accessibleName,
    },
    content,
  );
}
