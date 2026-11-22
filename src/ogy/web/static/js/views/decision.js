import { inspectionClient } from "../api.js";
import { cardHeader, marksFor } from "../ui/card-header.js";
import { h } from "../ui/dom.js";
import { words as shell } from "../ui/words.js";
import { decisionView, nextWaiting } from "./decision/data.js";
import { createAnswerForm, FORM_ID } from "./decision/form.js";
import { nodeFor } from "./decision/format.js";
import { historyBlock, optionsBlock, proposalBlock, questionBlock, statusLine } from "./decision/sections.js";
import { words } from "./decision/words.js";

// A decision, or one of its options (the same page, with that option marked).
const ADDRESS = /^([^/]+\/[^/]+\/decision\/[^/]+)(?:\/option\/([^/]+))?$/;

// The decision page, #/<layer>/<area>/decision/<id>: status, question, why, options, proposal, answers, then the form.
export const decisionRoute = {
  test: (path) => ADDRESS.test(path),
  get layer() {
    const first = location.hash.replace(/^#\/?/, "").split("/")[0];
    return first === "product" || first === "software" ? first : null;
  },
  mount: mountDecision,
  crumbs: (route) => [{ text: shell.board, href: "#/" }, { text: route.segments.slice(0, 2).join("/") }, { text: route.segments[3] }],
};

function notice(main, ...children) {
  main.replaceChildren(h("section", { class: "page notice decision" }, ...children));
}

export function mountDecision(main, { store, live, inspection, route }) {
  const [, address, optionKey] = ADDRESS.exec(route.path);
  let targeted = false;
  const reloadInspection = inspectionClient();
  const page = h("section", { class: "page decision", "data-part": "decision", "data-address": address });
  let signature = null;
  let reloading = false;
  let loaded = null;

  const form = createAnswerForm({
    address,
    version: () => store.getState().version,
    nextAddress: () => nextWaiting(live.state.data, address),
    onAgain: () => page.querySelector('input[name="option"]')?.focus(),
    onRefused: () => reload(),
    onWritten: async (written) => {
      await reload();
      for (let attempt = 0; attempt < 4; attempt++) {
        await live.refresh();
        if (live.state.data?.version === written.version) break;
        await new Promise((resolve) => setTimeout(resolve, 400));
      }
    },
  });

  async function reload() {
    if (reloading) return;
    reloading = true;
    try {
      store.dispatch({ type: "applyDocument", document: await reloadInspection() });
    } catch {
      // The next poll asks again; what is on screen stays.
    }
    reloading = false;
  }

  function body(model, view) {
    const head = h("header", { class: "page-head" }, statusLine(model, view), cardHeader(nodeFor(model, address), marksFor(view.entry)));
    const controls = { selected: form.selected(), formId: FORM_ID, onChoose: form.choose };
    return [head, questionBlock(view), optionsBlock(model, view, controls), proposalBlock(model, view), historyBlock(model, view)];
  }

  // Only what the data changed is rebuilt: the form and the read-back stay in place, so typing and focus survive a refresh.
  function paint(model, view) {
    const [head, ...rest] = body(model, view).filter(Boolean);
    for (const child of [...page.children]) if (child !== form.element && child !== form.readback) child.remove();
    if (form.readback.parentNode !== page) page.append(form.readback);
    if (form.element.parentNode !== page) page.append(form.element);
    form.readback.before(head);
    form.element.before(...rest);
  }

  function target() {
    if (!optionKey || targeted) return;
    const row = page.querySelector(`[data-option$="/option/${CSS.escape(optionKey)}"]`);
    if (!row) return;
    targeted = true;
    row.classList.add("is-target");
    row.scrollIntoView({ block: "center" });
  }

  function render() {
    page.removeAttribute("aria-busy");
    if (inspection.error)
      return notice(main, h("p", { role: "status", class: "empty" }, words.couldNotRead, " ", inspection.error.message));
    const { model } = store.getState();
    if (page.parentNode !== main) main.replaceChildren(page);
    if (!model) {
      page.setAttribute("aria-busy", "true");
      return page.replaceChildren(h("p", { role: "status", class: "loading", "data-part": "loading" }, words.loadingDecision));
    }
    // Standing that belongs to another snapshot than the document on screen is not shown: status and reach say Loading.
    const fresh = live.state.data?.version === model.snapshot.version ? live.state.data : null;
    const view = decisionView(model, fresh, address);
    if (!view) {
      return notice(main, h("h1", {}, shell.notFound), h("p", {}, `${words.noDecision} `, h("code", {}, `#/${address}`), "."));
    }
    view.standingError = Boolean(live.state.error) && !live.state.data;
    const next = JSON.stringify([view, model.snapshot.version]);
    if (next === signature && page.querySelector("[data-part=status]")) return;
    signature = next;
    const focused = document.activeElement?.closest?.("[data-option]") ? document.activeElement.id : null;
    paint(model, view);
    form.update(view, model);
    if (focused) document.getElementById(focused)?.focus();
    target();
  }

  // The inspection document is read again when the standing facts move to a snapshot it has not seen.
  const offLive = live.subscribe(({ data }) => {
    if (data && data.version !== loaded && store.getState().version !== data.version) {
      loaded = data.version;
      reload();
    }
    render();
  });
  const offStore = store.subscribe(render);
  render();
  return () => {
    offLive();
    offStore();
  };
}
