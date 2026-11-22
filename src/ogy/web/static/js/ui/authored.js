import { h } from "./dom.js";

// Text that comes from a KB field is marked, so a check can tell it from the viewer's own words.
export function authored(text, tag = "span", props = {}) {
  return h(tag, { ...props, "data-authored": true }, text);
}
