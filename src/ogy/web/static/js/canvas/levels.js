// Disclosure depends on detail class, never selection or viewport dimensions.
export function detailClass(scale) {
  return scale < 0.38 ? "summary" : scale < 0.8 ? "structure" : "detail";
}
export function referenceScale(level) {
  return level === "summary" ? 0.35 : 0.65;
}
export function visible(rect, camera, width, height) {
  const x = rect.x * camera.scale + camera.x,
    y = rect.y * camera.scale + camera.y;
  return x + rect.w * camera.scale > 0 && y + rect.h * camera.scale > 0 && x < width && y < height;
}
