import { authored } from "../../ui/authored.js";
import { h } from "../../ui/dom.js";
import { mention } from "../../ui/mention.js";
import { nodeFor } from "./format.js";
import { words } from "./words.js";

export const FORM_ID = "answer-form";

// The refusal text the server wrote, or what the connection says when it wrote none.
async function refusal(response) {
  const body = await response.json().catch(() => ({}));
  const text = Array.isArray(body.error) ? body.error.join(" ") : body.error || `HTTP ${response.status}`;
  return text.replace(/^refused:\s*/, "");
}

// The answer form. A click is an answer: the paraphrase starts as the option's label and is the owner's to change.
// It is built once per page visit; `update` follows the data without losing what was typed.
export function createAnswerForm({ address, version, onWritten, onRefused, onAgain, nextAddress }) {
  const state = { option: null, view: null, model: null, said: "", note: "", touched: false, busy: false, readback: null };
  const saidInput = h("input", { type: "text", id: "said", name: "said", autocomplete: "off", "aria-describedby": "said-hint" });
  const noteInput = h("input", { type: "text", id: "note", name: "note", autocomplete: "off", "aria-describedby": "note-hint" });
  const chosen = h("p", { class: "chosen-line", "data-part": "chosen" });
  const preview = h("div", { class: "preview", "data-part": "preview" });
  const submit = h("button", { type: "submit", class: "btn pri", "data-action": "record" }, words.record);
  const refused = h("p", { class: "refusal", role: "alert", "data-part": "refusal", hidden: true });
  const readback = h("div", { class: "readback", role: "status", "data-part": "readback", hidden: true });
  const heading = h("h2", {}, words.answerHeading);
  const form = h(
    "form",
    { id: FORM_ID, class: "answer-form", "data-part": "answer-form", novalidate: true },
    heading,
    chosen,
    h("div", { class: "field" }, h("label", { for: "said" }, words.said), saidInput, h("small", { id: "said-hint" }, words.saidHint)),
    h("div", { class: "field" }, h("label", { for: "note" }, words.noteField), noteInput, h("small", { id: "note-hint" }, words.noteHint)),
    preview,
    h("div", { class: "form-actions" }, submit),
    refused,
  );
  const section = h("section", { class: "block", "data-part": "answer-section" }, form);

  const optionOf = () => state.view?.options.find((option) => option.address === state.option) || null;

  function paint() {
    const option = optionOf();
    const noOptions = !state.view?.options.length;
    section.hidden = noOptions;
    heading.textContent = state.view?.answers.length ? words.answerAgain : words.answerHeading;
    chosen.replaceChildren(
      ...(option ? [`${words.chosenOption}: `, mention(nodeFor(state.model, option.address), { self: true })] : [words.chooseAbove]),
    );
    if (saidInput.value !== state.said) saidInput.value = state.said;
    if (noteInput.value !== state.note) noteInput.value = state.note;
    const ready = Boolean(option) && state.said.trim() !== "" && !state.busy;
    submit.disabled = !ready;
    submit.textContent = state.busy ? words.recording : words.record;
    preview.replaceChildren(
      ...(ready || (option && state.said.trim())
        ? [
            h("strong", {}, `${words.willRecord}: `),
            mention(nodeFor(state.model, option.address), { self: true }),
            ". ",
            `${words.heard} `,
            authored(state.said.trim()),
            state.note.trim() ? [`. ${words.note}: `, authored(state.note.trim())] : null,
          ]
            .flat()
            .filter(Boolean)
        : []),
    );
  }

  function choose(optionAddress) {
    state.option = optionAddress;
    const option = optionOf();
    if (!state.touched) state.said = option ? option.label : "";
    paint();
  }

  saidInput.addEventListener("input", () => {
    state.said = saidInput.value;
    state.touched = true;
    paint();
  });
  noteInput.addEventListener("input", () => {
    state.note = noteInput.value;
    paint();
  });

  async function showReadback(data, option) {
    const recorded = data.recorded;
    const lines = [
      h(
        "p",
        { class: "readback-line", "data-part": "readback-line" },
        h("strong", {}, `${words.recorded} `),
        mention(nodeFor(state.model, option.address)),
        `. ${words.heard} `,
        authored(recorded.said),
        recorded.note ? [`. ${words.note}: `, authored(recorded.note)] : null,
      ),
    ];
    const next = h("p", { class: "readback-next", "data-part": "next" });
    const again = h("button", { type: "button", class: "btn", "data-action": "again" }, words.notMeant);
    again.addEventListener("click", () => {
      state.readback = null;
      readback.hidden = true;
      readback.replaceChildren();
      state.option = null;
      state.touched = false;
      state.said = "";
      paint();
      onAgain();
    });
    readback.replaceChildren(...lines, next, again);
    readback.hidden = false;
    state.readback = { next };
  }

  // Called once the standing facts are fresh: the link to the next waiting decision.
  function paintNext(model, nextAddr) {
    const slot = state.readback?.next;
    if (!slot) return;
    slot.replaceChildren(...(nextAddr ? [`${words.nextWaiting} `, mention(nodeFor(model, nextAddr))] : [words.nothingWaits]));
  }

  async function record(event) {
    event.preventDefault();
    const option = optionOf();
    if (!option || !state.said.trim() || state.busy) return;
    state.busy = true;
    refused.hidden = true;
    paint();
    const body = {
      decision: address,
      option: option.key,
      said: state.said.trim(),
      note: state.note.trim() || undefined,
      version: version(),
    };
    try {
      const response = await fetch("/api/answer", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        refused.textContent = `${words.refused} ${await refusal(response)}`;
        refused.hidden = false;
        state.busy = false;
        paint();
        refused.scrollIntoView({ block: "nearest" });
        onRefused();
        return;
      }
      const data = await response.json();
      state.busy = false;
      state.note = "";
      state.said = "";
      state.touched = false;
      state.option = null;
      await showReadback(data, option);
      paint();
      readback.scrollIntoView({ block: "nearest" });
      await onWritten(data);
      paintNext(state.model, nextAddress());
    } catch (error) {
      refused.textContent = `${words.refused} ${error.message}`;
      refused.hidden = false;
      state.busy = false;
      paint();
    }
  }
  form.addEventListener("submit", record);

  return {
    element: section,
    readback,
    choose,
    selected: () => state.option,
    update(view, model) {
      state.view = view;
      state.model = model;
      if (state.option && !optionOf()) state.option = null;
      paint();
      if (state.readback) paintNext(model, nextAddress());
    },
  };
}
