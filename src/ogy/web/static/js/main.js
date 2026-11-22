import { inspectionClient } from "./api.js";
import { createScene } from "./canvas/scene.js";
import { store } from "./state.js";

export const scene = createScene(document.getElementById("stage"), store);
store.subscribe((state) => {
  scene.render(state);
  document.getElementById("status").textContent = `${state.doc.entries.length} entries`;
});
// Only native click delivery navigates; mouseup and hover never replace cards.
document.getElementById("stage").addEventListener("click", (event) => {
  const target = event.target.closest("[data-open-entry],[data-goto]");
  if (target) scene.select(target.dataset.openEntry || target.dataset.goto);
});
document.getElementById("stage").addEventListener("keydown", (event) => {
  const target = event.target.closest("[data-goto]");
  if (target && ["Enter", " "].includes(event.key)) {
    event.preventDefault();
    scene.select(target.dataset.goto);
  }
});
try {
  store.dispatch({ type: "applyDocument", document: await inspectionClient()() });
  scene.fitAll();
} catch (error) {
  document.getElementById("status").textContent = `Inspection unavailable. Open the URL printed by ogy serve again. ${error.message}`;
}
