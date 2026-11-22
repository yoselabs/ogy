import { adapt } from "./model/adapt.js";

export function createStore() {
  let state = { doc: null, model: null, version: null, selection: null, pins: [], spotlight: null, camera: { x: 0, y: 0, scale: 1 } };
  const listeners = new Set();
  function dispatch(action) {
    switch (action.type) {
      case "applyDocument": {
        const model = adapt(action.document);
        const previous = state.model?.byId || new Map();
        const changed = model.nodes.filter((node) => JSON.stringify(node) !== JSON.stringify(previous.get(node.id))).map((node) => node.id);
        const removed = [...previous.keys()].filter((id) => !model.byId.has(id));
        const present = (id) => (model.byId.has(id) ? id : null);
        state = {
          ...state,
          doc: action.document,
          model,
          version: action.document.snapshot.version,
          selection: present(state.selection),
          pins: state.pins.filter(present),
          spotlight: present(state.spotlight),
          changes: { changed, removed },
        };
        break;
      }
      case "select":
        state = { ...state, selection: action.address };
        break;
      case "pin":
        state = { ...state, pins: [...new Set([...state.pins, action.address])] };
        break;
      case "unpin":
        state = { ...state, pins: state.pins.filter((id) => id !== action.address) };
        break;
      case "spotlight":
        state = { ...state, spotlight: action.address };
        break;
      case "clearSpotlight":
        state = { ...state, spotlight: null };
        break;
      case "camera":
        state = { ...state, camera: { ...state.camera, ...action.camera } };
        break;
      default:
        throw new Error(`Unknown board action: ${action.type}`);
    }
    for (const listener of listeners) listener(state);
    return state;
  }
  return { dispatch, getState: () => state, subscribe: (listener) => (listeners.add(listener), () => listeners.delete(listener)) };
}

export const store = createStore();
