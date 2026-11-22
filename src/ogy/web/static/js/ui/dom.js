import { icon } from "../model/icons.js";

// The one element builder: attributes by name, listeners as onclick and the like, children flattened.
export function h(tag, props = {}, ...children) {
  const element = document.createElement(tag);
  for (const [name, value] of Object.entries(props)) {
    if (value == null || value === false) continue;
    if (name === "class") element.className = value;
    else if (name.startsWith("on")) element.addEventListener(name.slice(2), value);
    else element.setAttribute(name, value === true ? "" : value);
  }
  element.append(...children.flat().filter((child) => child != null && child !== false));
  return element;
}

export function glyph(name, operation = false) {
  const holder = document.createElement("template");
  holder.innerHTML = icon(name, operation);
  return holder.content.firstElementChild;
}

export function clear(element) {
  element.replaceChildren();
  return element;
}
