import { glyph, h } from "../ui/dom.js";
import { buildIndex, search } from "./search/index.js";
import { renderResults } from "./search/render.js";
import { words } from "./search/words.js";

const apple = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
const typing = (target) => target?.closest?.("input, textarea, select, [contenteditable]");

// The search overlay: Ctrl K (or the header button, or /) opens it, arrows walk the results, Enter opens one, Esc closes it.
// Entries are found from the inspection document on this page: nothing is asked of the server per keystroke.
export function mountSearch({ router, store, inspection }) {
  const input = h("input", {
    type: "search",
    role: "combobox",
    class: "search-input",
    placeholder: words.placeholder,
    "aria-label": words.label,
    "aria-expanded": "true",
    "aria-controls": "search-list",
    "aria-autocomplete": "list",
    autocomplete: "off",
    spellcheck: "false",
  });
  const close = h("button", { type: "button", class: "btn", onclick: () => dialog.close() }, words.close);
  const list = h("div", { id: "search-list", class: "search-list", role: "listbox", "aria-label": words.title });
  const note = h("p", { class: "search-note", "data-part": "search-note" });
  const live = h("p", { class: "sr-only", role: "status", "aria-live": "polite" });
  const keys = h(
    "p",
    { class: "search-keys" },
    h("kbd", {}, "↑↓"),
    ` ${words.move}  `,
    h("kbd", {}, "Enter"),
    ` ${words.open}  `,
    h("kbd", {}, "Esc"),
    ` ${words.dismiss}`,
  );
  const dialog = h(
    "dialog",
    { class: "finder", "aria-label": words.title, "data-part": "search" },
    h("div", { class: "search-bar" }, glyph("search"), input, close),
    list,
    note,
    live,
    keys,
  );
  document.body.append(dialog);

  let index = null;
  let indexed = null;
  let walk = [];
  let active = 0;
  let open = new Set();

  function setActive(next, scroll = true) {
    walk[active]?.removeAttribute("aria-selected");
    active = walk.length ? (next + walk.length) % walk.length : 0;
    const row = walk[active];
    if (row) {
      row.setAttribute("aria-selected", "true");
      input.setAttribute("aria-activedescendant", row.id);
      if (scroll) row.scrollIntoView({ block: "nearest" });
    } else input.removeAttribute("aria-activedescendant");
  }

  function say(text) {
    list.replaceChildren();
    walk = [];
    note.textContent = text;
    setActive(0);
  }

  function paint() {
    const { model } = store.getState();
    const query = input.value;
    note.textContent = "";
    live.textContent = "";
    if (inspection.error) return say(words.failed);
    if (!model) return say(words.loading);
    if (indexed !== model) {
      index = buildIndex(model);
      indexed = model;
    }
    const groups = search(index, query);
    walk = renderResults(list, groups, query, open);
    if (!query.trim()) note.textContent = words.hint;
    else if (!groups.length) note.textContent = `${words.none} “${query.trim()}”. ${words.noneHelp}`;
    else live.textContent = `${groups.reduce((sum, group) => sum + group.items.length, 0)} ${words.results}`;
    setActive(0);
  }

  function choose() {
    const row = walk[active];
    if (!row) return;
    if (row.dataset.more) {
      open.add(row.dataset.more);
      const before = active;
      paint();
      return setActive(before);
    }
    dialog.close();
    location.hash = `#/${row.dataset.address}`;
  }

  input.addEventListener("input", () => {
    open = new Set();
    paint();
  });
  input.addEventListener("keydown", (event) => {
    const step = { ArrowDown: 1, ArrowUp: -1 }[event.key];
    if (step) {
      event.preventDefault();
      setActive(active + step);
    } else if (event.key === "Enter") {
      event.preventDefault();
      choose();
    }
  });
  list.addEventListener("click", (event) => {
    const row = event.target.closest(".result, .more");
    if (!row) return;
    event.preventDefault();
    setActive(walk.indexOf(row), false);
    choose();
  });
  list.addEventListener("pointermove", (event) => {
    const row = event.target.closest(".result, .more");
    if (row && walk[active] !== row) setActive(walk.indexOf(row), false);
  });
  // A click on the dimmed page behind the box closes it.
  dialog.addEventListener("click", (event) => event.target === dialog && dialog.close());
  router.subscribe(() => dialog.open && dialog.close());
  store.subscribe(() => dialog.open && paint());

  function show() {
    if (!dialog.open) {
      dialog.showModal();
      open = new Set();
      paint();
    }
    input.focus();
    input.select();
  }
  document.addEventListener("keydown", (event) => {
    const chord = (event.ctrlKey || event.metaKey) && !event.altKey && event.key.toLowerCase() === "k";
    const slash = event.key === "/" && !event.ctrlKey && !event.metaKey && !typing(event.target) && !dialog.open;
    if (!chord && !slash) return;
    event.preventDefault();
    if (chord && dialog.open) dialog.close();
    else show();
  });
  const button = document.querySelector("#header .search");
  button?.removeAttribute("disabled");
  button?.addEventListener("click", show);
  button?.setAttribute("aria-keyshortcuts", apple ? "Meta+K" : "Control+K");
}
