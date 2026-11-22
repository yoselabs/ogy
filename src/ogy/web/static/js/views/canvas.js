import { createScene } from "../canvas/scene.js";
import { h } from "../ui/dom.js";

// The old pan-and-zoom board, mounted unchanged until the Map replaces it. Native click delivery only.
export function mountCanvas(main, { store, inspection }) {
  const stage = h("div", { id: "stage", class: "board-canvas" });
  stage.innerHTML =
    '<svg id="board" aria-label="Entries" xmlns="http://www.w3.org/2000/svg"><g id="vp"></g></svg><div id="overview" hidden></div>';
  main.replaceChildren(stage);
  const scene = createScene(stage, store);
  let fitted = false;
  const draw = (state) => {
    scene.render(state);
    if (state.model && !fitted) {
      fitted = true;
      scene.fitAll();
    }
  };
  stage.addEventListener("click", (event) => {
    const target = event.target.closest("[data-open-entry],[data-goto]");
    if (!target) return;
    event.preventDefault();
    scene.select(target.dataset.openEntry || target.dataset.goto);
  });
  const off = store.subscribe(draw);
  draw(store.getState());
  if (inspection.error) stage.replaceChildren(h("p", { role: "status", class: "empty" }, inspection.error.message));
  return () => off();
}
